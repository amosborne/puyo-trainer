from puyolib.puyogridmodel import PuyoHoverAreaModel  # model
from puyolib.puyographicmodel import PuyoGraphicModel  # model
from puyoui.editorview import EditorView  # view
from puyoapp.gameplaycontrol import GameplayVC  # controller


# View-controller of the puzzle editor GUI.
# Manages view callbacks and keeps the model and view synchronized.
class EditorVC:
    def __init__(self, puzzlemodel, skin):
        board_graphic = PuyoGraphicModel(skin, puzzlemodel.board)
        drawpile_graphics = []

        elem = puzzlemodel.newDrawpileElem()  # hack

        hoverarea = PuyoHoverAreaModel(puzzlemodel.board, elem)
        hoverarea_graphics = PuyoGraphicModel(skin, hoverarea)

        self.view = EditorView(board_graphic, drawpile_graphics, hoverarea_graphics)

        self.game_controller = GameplayVC(puzzlemodel, hoverarea, self.view.solverview)

        self.skin = skin
        self.model = puzzlemodel
        self.bindDefineView()
        self.bindSolverView()

    def bindDefineView(self):
        model = self.model
        view = self.view.defineview

        def updateView(func):
            def decorated(*args):
                func(*args)
                view.updateView()

            return decorated

        @updateView
        def changeBoardElem(pos):
            model.board[pos] = model.board[pos].next()

        @updateView
        def changeDrawpileElem(idx_pos):
            index, pos = idx_pos
            model.drawpile[index][pos] = model.drawpile[index][pos].next()

        @updateView
        def insertDrawpileElem(index=-1):
            elem = model.newDrawpileElem(index + 1)
            view.drawpile.insert(index + 1, PuyoGraphicModel(self.skin, elem))

        @updateView
        def deleteDrawpileElem(index):
            if len(model.drawpile) > 2:
                del model.drawpile[index]
                del view.drawpile[index]

        @updateView
        def clearBoard():
            model.board.reset()

        def resetDrawpile():
            del model.drawpile[:]
            del view.drawpile[:]
            insertDrawpileElem()
            insertDrawpileElem()

        def startSolution():
            self.view.centralWidget().setCurrentWidget(self.view.solverview)
            self.game_controller.takeControl()

        resetDrawpile()

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

        view.click_back.connect(exitSolver)
        view.click_save.connect(lambda: print("save and exit!"))
