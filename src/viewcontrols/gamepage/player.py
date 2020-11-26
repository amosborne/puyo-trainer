from models import Direc, PopState, grid2graphics
from copy import deepcopy
from PyQt5.QtCore import QTimer
from constants import POP_SPEED
from viewcontrols.gamepage.game import SoloGameView


def animate(func):
    def wrapper(self):
        if not self.timer.isActive():
            try:
                func(self)
                self.puzzle.apply_rules(force=True)
                self.animate()
            except IndexError:
                pass

    return wrapper


class GameVC:
    def __init__(self, skin, puzzle, view):
        self.skin = skin
        self.puzzle = puzzle
        self.view = view
        self.draw_index = 0
        self.animate()

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


class PlayVC(GameVC):
    def __init__(self, skin, puzzle, view):
        view.pressX.connect(self.rotateRight)
        view.pressZ.connect(self.rotateLeft)
        view.pressRight.connect(self.shiftRight)
        view.pressLeft.connect(self.shiftLeft)
        view.pressUp.connect(self.revertMove)
        view.pressDown.connect(self.makeMove)

        super().__init__(skin, puzzle, view)

    @animate
    def rotateRight(self):
        move = self.puzzle.moves[self.draw_index]
        move.direc = Direc.rotate_cw(move.direc)

    @animate
    def rotateLeft(self):
        move = self.puzzle.moves[self.draw_index]
        move.direc = Direc.rotate_ccw(move.direc)

    @animate
    def shiftRight(self):
        self.puzzle.moves[self.draw_index].col += 1

    @animate
    def shiftLeft(self):
        self.puzzle.moves[self.draw_index].col -= 1

    @animate
    def makeMove(self):
        self.puzzle.board.apply_move(self.puzzle.moves[self.draw_index])
        self.draw_index += 1

    @animate
    def revertMove(self):
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
