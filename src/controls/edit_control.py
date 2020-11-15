from models.graphic_model import PuyoGraphicModel  # model
from views.edit_view import EditorView  # view
from controls.game_control import GameVC  # controller


# View-controller of the puzzle editor GUI.
# Manages view callbacks and keeps the model and view synchronized.
class EditorVC:
    def __init__(self, puzzle, skin):
        board_graphic = PuyoGraphicModel(skin, puzzle.board)
        move_graphics = [PuyoGraphicModel(skin, move.grid) for move in puzzle.moves]
        hover_graphics = PuyoGraphicModel(skin, puzzle.hover)

        self.view = EditorView(board_graphic, move_graphics, hover_graphics)

        # self.game_controller = GameVC(puzzle, self.view.solverview.gameview)

        self.skin = skin
        self.puzzle = puzzle
        self.bindDefineView()
        # self.bindSolverView()

    def bindDefineView(self):
        model = self.puzzle
        view = self.view.defineview

        def updateView(func):
            def decorated(*args):
                func(*args)
                model.apply_rules(force=True)
                del view.drawpile[:]
                view.drawpile.extend(
                    [PuyoGraphicModel(self.skin, move.grid) for move in model.moves]
                )
                view.updateView()
                print(model)

            return decorated

        @updateView
        def changeBoardElem(pos):
            model.board[pos] = model.board[pos].next_()

        @updateView
        def changeDrawpileElem(idx_pos):
            index, pos = idx_pos
            model.moves[index].grid[pos] = model.moves[index].grid[pos].next_()

        @updateView
        def insertDrawpileElem(index=-1):
            move = model.new_move(index + 1)

        @updateView
        def deleteDrawpileElem(index):
            del model.moves[index]

        @updateView
        def clearBoard():
            model.board.reset()

        @updateView
        def resetDrawpile():
            del model.moves[:]

        def startSolution():
            self.view.centralWidget().setCurrentWidget(self.view.solverview)
            self.game_controller.reset()

        view.click_board_puyos.connect(changeBoardElem)
        view.click_drawpile_puyos.connect(changeDrawpileElem)
        view.click_drawpile_insert.connect(insertDrawpileElem)
        view.click_drawpile_delete.connect(deleteDrawpileElem)
        view.click_reset_drawpile.connect(resetDrawpile)
        view.click_clear_board.connect(clearBoard)
        view.click_start.connect(startSolution)

    def bindSolverView(self):
        model = self.model
        view = self.view.solverview

        def exitSolver():
            self.view.centralWidget().setCurrentWidget(self.view.defineview)
            model.board.revert()

        view.click_back.connect(exitSolver)
        view.click_save.connect(lambda: print("save and exit!"))
