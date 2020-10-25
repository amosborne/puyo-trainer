from puyolib.puyographicmodel import PuyoGraphicModel  # model
from puyoui.editorview import EditorView  # view


# View-controller of the puzzle editor GUI.
# Manages view callbacks and keeps the model and view synchronized.
class EditorVC:
    def __init__(self, puzzlemodel, skin):

        # Initialize the editor view with direct access to the graphic models.
        board_graphic = PuyoGraphicModel(skin, puzzlemodel.board)
        drawpile_graphics = []
        for elem in puzzlemodel.drawpile:
            elem_graphic = PuyoGraphicModel(skin, elem)
            drawpile_graphics.append(elem_graphic)

        self.skin = skin
        self.view = EditorView(board_graphic, drawpile_graphics)
        self.puzzlemodel = puzzlemodel

        # Bind all the GUI callbacks.
        self.bindDefineView()

    def insertDrawpileElement(self, index):
        pass

    def bindDefineView(self):
        model = self.puzzlemodel
        view = self.view.defineview

        def clearBoard():
            model.board.reset()
            view.updateView()

        def resetDrawpile():
            for elem in model.drawpile:
                elem.reset()
            view.updateView()

        def changeBoardElem(pos):
            model.board[pos] = model.board[pos].next()
            view.updateView()

        def changeDrawpileElem(idx_pos):
            index, pos = idx_pos
            model.drawpile[index][pos] = model.drawpile[index][pos].next()
            view.updateView()

        def insertDrawpileElem(index):
            elem = model.newDrawpileElem(index + 1)
            view.drawpile.insert(index + 1, PuyoGraphicModel(self.skin, elem))
            view.updateView()

        def deleteDrawpileElem(index):
            if len(model.drawpile) > 2:
                del model.drawpile[index]
                del view.drawpile[index]
                view.updateView()

        def startSolution():
            self.editorview.centralWidget().setCurrentWidget(self.editorview.solverview)

        view.click_board_puyos.connect(changeBoardElem)
        view.click_drawpile_puyos.connect(changeDrawpileElem)
        view.click_drawpile_insert.connect(insertDrawpileElem)
        view.click_drawpile_delete.connect(deleteDrawpileElem)
        view.click_reset_drawpile.connect(resetDrawpile)
        view.click_clear_board.connect(clearBoard)
        # view.click_start.connect(startSolution)

    def bindSolverView(self):
        model = self.puzzlemodel
        view = self.editorview.solverview

        def exitSolver():
            self.editorview.centralWidget().setCurrentWidget(self.editorview.defineview)

        view.back_button.clicked.connect(exitSolver)
        view.save_button.clicked.connect(lambda: print("save and exit!"))
