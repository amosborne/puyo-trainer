from puyolib.puyographicmodel import PuyoGraphicModel  # model
from puyoui.editorview import EditorView  # view


class EditorVC:
    def __init__(self, puzzlemodel, skin):

        # Initialize the editor view with the graphic model links.
        board_graphic = PuyoGraphicModel(skin, puzzlemodel.board)
        drawpile_graphic = []
        for elem in puzzlemodel.drawpile:
            elem[0, 0] = elem[0, 0].nextColor()
            elem[1, 0] = elem[1, 0].nextColor()
            elem_graphic = PuyoGraphicModel(skin, elem)
            drawpile_graphic.append(elem_graphic)

        self.skin = skin
        self.view = EditorView(board_graphic, drawpile_graphic)

        self.puzzlemodel = puzzlemodel
        self.board_graphic = board_graphic

        # Bind all the GUI callbacks.
        self.bindDefineView()

        # editorview.show()

        # self.gamecontrol = GameplayController(
        #     puzzlemodel, editorview.solverview.gameplayview
        # )

        # self.bindDefineView()
        # self.bindSolverView()

    def bindDefineView(self):
        model = self.puzzlemodel
        view = self.view.defineview

        def clearBoard():
            model.board.reset()
            view.updateView()

        def resetDrawpile():
            model.resetDrawpile()
            view.setDrawpileGraphics(model.drawpile)

        def changeBoardElem(pos):
            model.board[pos] = model.board[pos].next()
            view.updateView()

        def changeDrawpileElem(idx_pos):
            index, pos = idx_pos
            puyo = model.drawpile[index][pos]
            if pos in {(0, 0), (1, 0)}:
                model.drawpile[index][pos] = puyo.nextColor()
            else:
                model.drawpile[index][pos] = puyo.nextNonGarbage()
            view.updateView()

        def insertDrawpileElem(index):
            index += 1
            model.insertDrawpileElem(index)
            graphic = PuyoGraphicModel(self.skin, model.drawpile[index])
            view.drawpile_view.insertElement(index, graphic)

        def delDrawpileElem(index):
            if len(model.drawpile) > 2:
                model.deleteDrawpileElem(index)
                view.drawpile_view.deleteElement(index)

        def startSolution():
            self.editorview.centralWidget().setCurrentWidget(self.editorview.solverview)

        view.click_board_puyos.connect(changeBoardElem)
        view.click_drawpile_puyos.connect(changeDrawpileElem)
        view.click_drawpile_insert.connect(insertDrawpileElem)
        view.click_drawpile_delete.connect(delDrawpileElem)
        # view.click_reset_drawpile.connect(resetDrawpile)
        view.click_clear_board.connect(clearBoard)
        # view.click_start.connect(startSolution)

    def bindSolverView(self):
        model = self.puzzlemodel
        view = self.editorview.solverview

        def exitSolver():
            self.editorview.centralWidget().setCurrentWidget(self.editorview.defineview)

        view.back_button.clicked.connect(exitSolver)
        view.save_button.clicked.connect(lambda: print("save and exit!"))
