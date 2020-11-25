from models import grid2graphics, Puyo
from viewcontrols.gamepage.edit import EditorView  # view
from viewcontrols.gamepage.player import PlayVC  # sub-view-controller
from viewcontrols.qtutils import ErrorPopup

# View-controller of the puzzle editor GUI.
# Manages view callbacks and keeps the model and view synchronized.
class EditorVC:
    def __init__(self, puzzle, skin, parent=None):
        self.skin = skin
        self.puzzle = puzzle

        board, drawpile = self._generatePuzzleDefineGraphics()
        hover = grid2graphics(skin, puzzle.hover)

        self.view = EditorView(board, drawpile, hover, parent)
        self.view.setWindowTitle("New Puzzle (" + puzzle.path + ")")

        self.game_controller = PlayVC(skin, puzzle, self.view.solverview.gameview)

        self.bindDefineView()
        self.bindSolverView()

        self.view.show()

    def _generatePuzzleDefineGraphics(self):
        board = grid2graphics(self.skin, self.puzzle.board)
        drawpile = [grid2graphics(self.skin, move.grid) for move in self.puzzle.moves]
        return board, drawpile

    def bindDefineView(self):
        puzzle = self.puzzle
        view = self.view.defineview

        def update(func):
            def decorated(*args):
                func(*args)
                puzzle.apply_rules(force=True)
                view.setGraphics(*self._generatePuzzleDefineGraphics())

            return decorated

        @update
        def changeGridElem(grid, pos):
            grid[pos] = grid[pos].next_(cond=lambda p: p is not Puyo.NONE)

        @update
        def clearGridElem(grid, pos):
            grid[pos] = Puyo.NONE

        @update
        def insertDrawpileElem(index):
            puzzle.new_move(index + 1)

        @update
        def deleteDrawpileElem(index):
            del puzzle.moves[index]

        @update
        def clearBoard():
            puzzle.board.reset()

        @update
        def resetDrawpile():
            puzzle.moves.clear()

        def startSolution():
            if puzzle.apply_rules():
                self.view.centralWidget().setCurrentWidget(self.view.solverview)
                self.game_controller.reset()
            else:
                ErrorPopup(
                    (
                        "Malformed initial board. Check:\n"
                        "- Color count\n"
                        "- Floating puyos\n"
                        "- Pop groups."
                    )
                )

        view.leftclick_board.connect(lambda pos: changeGridElem(puzzle.board, pos))
        view.rightclick_board.connect(lambda pos: clearGridElem(puzzle.board, pos))
        view.leftclick_drawpile.connect(
            lambda idx, pos: changeGridElem(puzzle.moves[idx].grid, pos)
        )
        view.rightclick_drawpile.connect(
            lambda idx, pos: clearGridElem(puzzle.moves[idx].grid, pos)
        )
        view.insert.connect(insertDrawpileElem)
        view.delete.connect(deleteDrawpileElem)
        view.reset.connect(resetDrawpile)
        view.clear.connect(clearBoard)
        view.start.connect(startSolution)

    def bindSolverView(self):
        model = self.puzzle
        view = self.view.solverview

        def exitSolver():
            self.view.centralWidget().setCurrentWidget(self.view.defineview)
            model.board.revert()

        def savePuzzle():
            # check if all moves have been input
            if not len(self.puzzle.moves) == len(self.puzzle.board._boardlist):
                ErrorPopup("Input all moves prior to saving.")
            else:
                self.puzzle.save()
                self.view.close()

        view.back.connect(exitSolver)
        view.save.connect(savePuzzle)
