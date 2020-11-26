from models import Direc, PopState, grid2graphics
from copy import deepcopy
from PyQt5.QtCore import QTimer, Qt, QObject, pyqtSignal
from constants import POP_SPEED
from viewcontrols.gamepage.game import SoloGameView, TestWindow
import random
from viewcontrols.qtutils import ErrorPopup

"""
In the interest of completing the first working version of this software,
this file in particular turned into a massive hack.

Not that the order in which signals are connected is CRITICAL because
signals are executed in order. This is how the test controller can 
function by splicing multiple subcontrollers together.
"""


def animate(func):
    def wrapper(self):
        if not self.timer.isActive() and not self.lock:
            try:
                func(self)
                self.puzzle.apply_rules(force=True)
                self.animate()
                self.process_complete.emit()
                self.lock = self.prelock
                self.prelock = False
            except IndexError:
                pass

    return wrapper


class GameVC(QObject):
    process_complete = pyqtSignal()
    animation_start = pyqtSignal()
    animation_end = pyqtSignal()

    def __init__(self, skin, puzzle, view):
        super().__init__()
        self.lock = False
        self.prelock = False
        self.haslock = False
        self.skin = skin
        self.puzzle = puzzle
        self.view = view
        self.draw_index = 0
        self.animate()

    def setLock(self):
        self.prelock = True

    def releaseLock(self):
        self.lock = False

    def setPuzzle(self, puzzle):
        self.puzzle = puzzle
        self.reset()

    def reset(self):
        self.draw_index = 0
        self.animate()
        self.view.setFocus()

    def animate(self, popstate=PopState.PREPOP):
        # Create a timer for the pop animation.
        timer = QTimer(self.view)
        timer.setSingleShot(True)
        timer.setInterval(POP_SPEED * 1000)
        self.timer = timer

        # Check for a pop and animate (recursively).
        popset = self.puzzle.board.pop_set(self.puzzle.module.pop_limit)
        if popset:
            if not self.haslock:
                self.animation_start.emit()
                self.haslock = True

            # Empty the hover grid.
            self.puzzle.hover.assign_move(None)
            hover_gfx = grid2graphics(self.skin, self.puzzle.hover)

            # Get the visible drawpile.
            draw_gfx = [grid2graphics(self.skin, mv.grid) for mv in self.puzzle.moves]
            draw_gfx = draw_gfx[self.draw_index : self.draw_index + 2]

            # Calculate remaining.
            nremaining = len(self.puzzle.moves) - self.draw_index

            # Get the board graphics.
            board_gfx = grid2graphics(
                skin=self.skin,
                grid=self.puzzle.board,
                ghosts=set(),
                pops=popset,
                popstate=popstate,
            )

            self.view.setGraphics(board_gfx, draw_gfx, hover_gfx, nremaining)

            # Start the timer to update the animation at the next pop state.
            self.timer.timeout.connect(lambda: self.animate(popstate._next()))
            self.timer.start()

            # If at the final pop state in the animation, execute the pop.
            if popstate is PopState.POPLATER:
                self.puzzle.board.execute_pop(self.puzzle.module.pop_limit)

        else:
            # Assign a move, if available, to the hover grid.
            try:
                move = self.puzzle.moves[self.draw_index]
            except IndexError:
                move = None

            self.puzzle.hover.assign_move(move)
            hover_gfx = grid2graphics(self.skin, self.puzzle.hover)

            # Get the visible drawpile.
            draw_gfx = [grid2graphics(self.skin, mv.grid) for mv in self.puzzle.moves]
            draw_gfx = draw_gfx[self.draw_index + 1 : self.draw_index + 3]

            # Calculate remaining.
            nremaining = len(self.puzzle.moves) - self.draw_index

            # Find the ghosts.
            if move is not None:
                future_board = deepcopy(self.puzzle.board)
                future_board.apply_move(move)
                ghosts = future_board - self.puzzle.board
            else:
                ghosts = set()

            # Get the board graphics.
            board_gfx = grid2graphics(self.skin, self.puzzle.board, ghosts)

            self.view.setGraphics(board_gfx, draw_gfx, hover_gfx, nremaining)
            self.animation_end.emit()
            self.haslock = False


class PlayVC(GameVC):
    pressUp_xstrap = pyqtSignal()
    pressDown_xstrap = pyqtSignal()

    def __init__(self, skin, puzzle, view, revertable=True, shiftable=True):
        view.pressX.connect(self.rotateRight)
        view.pressZ.connect(self.rotateLeft)
        view.pressRight.connect(self.shiftRight)
        view.pressLeft.connect(self.shiftLeft)

        self.revertable = revertable
        self.shiftable = shiftable
        super().__init__(skin, puzzle, view)

        view.pressUp.connect(self.xstrap_signal(self.pressUp_xstrap))
        view.pressDown.connect(self.xstrap_signal(self.pressDown_xstrap))
        view.pressUp.connect(self.revertMove)
        view.pressDown.connect(self.makeMove)

    def xstrap_signal(self, signal):
        def xstrap():
            if not self.timer.isActive():
                signal.emit()

        return xstrap

    @animate
    def rotateRight(self):
        if not self.shiftable:
            return
        move = self.puzzle.moves[self.draw_index]
        move.direc = Direc.rotate_cw(move.direc)

    @animate
    def rotateLeft(self):
        if not self.shiftable:
            return
        move = self.puzzle.moves[self.draw_index]
        move.direc = Direc.rotate_ccw(move.direc)

    @animate
    def shiftRight(self):
        if not self.shiftable:
            return
        self.puzzle.moves[self.draw_index].col += 1

    @animate
    def shiftLeft(self):
        if not self.shiftable:
            return
        self.puzzle.moves[self.draw_index].col -= 1

    @animate
    def makeMove(self):
        self.puzzle.board.apply_move(self.puzzle.moves[self.draw_index])
        self.draw_index += 1

    @animate
    def revertMove(self):
        if not self.revertable:
            return
        if self.draw_index > 0:
            self.draw_index -= 1
            self.puzzle.board.revert_move()


class ReviewVC(GameVC):
    def __init__(self, skin, puzzle, text, parent=None):
        board = grid2graphics(skin, puzzle.board)
        drawpile = [grid2graphics(skin, move.grid) for move in puzzle.moves]
        hover = grid2graphics(skin, puzzle.hover)

        win = SoloGameView(board, drawpile, hover, 0, text, parent)
        super().__init__(skin, puzzle, win.gameview)

        win.gameview.pressUp.connect(self.revertMove)
        win.gameview.pressDown.connect(self.makeMove)

        win.show()

        self.win = win

    @animate
    def makeMove(self):
        self.puzzle.board.apply_move(self.puzzle.moves[self.draw_index])
        self.draw_index += 1

    @animate
    def revertMove(self):
        if self.draw_index > 0:
            self.draw_index -= 1
            self.puzzle.board.revert_move()


class TesterVC:
    def __init__(self, skin, module, nmoves, nreview, parent=None):
        self.skin = skin
        self.module = module
        self.nmoves = nmoves
        self.nreview = nreview

        self.history = []

        # Initialize the window.
        self.pickPuzzle()
        self.win = TestWindow(
            board1=grid2graphics(skin, self.puzzle_response.board),
            drawpile1=[
                grid2graphics(skin, move.grid) for move in self.puzzle_response.moves
            ],
            hover1=grid2graphics(skin, self.puzzle_response.hover),
            nremain1=0,
            board2=grid2graphics(skin, self.puzzle_solution.board),
            drawpile2=[
                grid2graphics(skin, move.grid) for move in self.puzzle_solution.moves
            ],
            hover2=grid2graphics(skin, self.puzzle_solution.hover),
            nremain2=0,
            parent=parent,
        )

        # Wire up the sub-controllers.
        self.play_control = PlayVC(
            skin, self.puzzle_response, self.win.test.gameview, revertable=False
        )
        self.review_response_control = PlayVC(
            skin, self.puzzle_response, self.win.review.gameview1, shiftable=False
        )
        self.review_solution_control = PlayVC(
            skin, self.puzzle_response, self.win.review.gameview2, shiftable=False
        )

        self.review_solution_control.animation_start.connect(
            self.review_response_control.setLock
        )
        self.review_solution_control.animation_end.connect(
            self.review_response_control.releaseLock
        )

        # cross strap hack
        self.win.review.gameview2.setFocusPolicy(Qt.NoFocus)
        self.review_response_control.pressDown_xstrap.connect(
            self.win.review.gameview2.pressDown
        )
        self.review_response_control.pressUp_xstrap.connect(
            self.win.review.gameview2.pressUp
        )
        self.win.test.gameview.pressSpace.connect(self.proceed2review)
        self.win.review.gameview1.pressSpace.connect(self.proceed2test)

        self.review_response_control.process_complete.connect(self.reviewEval)

        self.win.show()

    def reviewEval(self):
        self.win.review.setCorrect(
            self.puzzle_response.board == self.puzzle_solution.board
        )

    def proceed2review(self):
        # check if there is an ongoing animation
        if self.play_control.timer.isActive():
            return

        # check to see if the test is complete
        if not len(self.puzzle_response.moves) == len(
            self.puzzle_response.board._boardlist
        ):
            ErrorPopup("Finish the test before continuing.", parent=self.win)
            return

        # check to see if it is time to review
        self.puzzle_response.board.revert()
        self.history.append((self.puzzle_response, self.puzzle_solution))

        if len(self.history) == self.nreview:
            self.newReview()
        else:
            self.newTest()

    def newTest(self):
        self.win.centralWidget().setCurrentWidget(self.win.test)
        self.pickPuzzle()
        self.play_control.setPuzzle(self.puzzle_response)

    def proceed2test(self):
        if self.review_response_control.timer.isActive():
            return
        if self.review_solution_control.timer.isActive():
            return

        if self.history:
            self.newReview()
        else:
            self.newTest()

    def newReview(self):
        self.puzzle_response, self.puzzle_solution = self.history.pop(0)
        self.review_solution_control.setPuzzle(self.puzzle_solution)
        self.review_response_control.setPuzzle(self.puzzle_response)
        self.win.centralWidget().setCurrentWidget(self.win.review)
        self.reviewEval()

    def pickPuzzle(self):
        # pick a random puzzle with a random color map. apply moves as necessary
        self.puzzle_response = deepcopy(
            random.choice(list(self.module.puzzles.values()))
        )

        self.puzzle_response.randomize_color()

        while len(self.puzzle_response.moves) > self.nmoves:
            self.puzzle_response.board.apply_move(self.puzzle_response.moves.pop(0))
            self.puzzle_response.board._boardlist = []

        self.puzzle_solution = deepcopy(self.puzzle_response)

        for move in self.puzzle_response.moves:
            move.col = 2
            move.direc = Direc.NORTH
