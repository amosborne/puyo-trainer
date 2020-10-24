from puyoapp.gameplaycontrol import GameplayController


class EditorController:
    def __init__(self, puzzlemodel, editorview):
        editorview.show()

        self.puzzlemodel = puzzlemodel
        self.editorview = editorview
        self.bindDefineView()
        self.bindSolverView()

    def bindDefineView(self):
        model = self.puzzlemodel
        view = self.editorview.defineview

        def clearBoard():
            model.clearBoard()
            view.setBoardGraphics(model.board)

        def resetDrawpile():
            model.resetDrawpile()
            view.setDrawpileGraphics(model.drawpile)

        def changeBoardElem(pos):
            puyo = model.board[pos]
            model.board[pos] = puyo.next()
            view.setBoardGraphics(model.board)

        def changeDrawpileElem(pos):
            puyo = model.drawpile[pos]
            model.drawpile[pos] = puyo.nextColor()
            view.setDrawpileGraphics(model.drawpile)

        def insertDrawpileElem(index):
            model.newDrawpileElem(index + 1)
            view.setDrawpileGraphics(model.drawpile)

        def delDrawpileElem(index):
            if model.drawpile.shape[0] > 2:
                model.delDrawpileElem(index)
                view.setDrawpileGraphics(model.drawpile)

        def startSolution():
            self.editorview.centralWidget().setCurrentWidget(self.editorview.solverview)
            GameplayController(model, self.editorview.solverview.gameplayview)

        view.click_board_puyos.connect(changeBoardElem)
        view.click_drawpile_puyos.connect(changeDrawpileElem)
        view.click_drawpile_insert.connect(insertDrawpileElem)
        view.click_drawpile_delete.connect(delDrawpileElem)
        view.click_reset_drawpile.connect(resetDrawpile)
        view.click_clear_board.connect(clearBoard)
        view.click_start.connect(startSolution)

    def bindSolverView(self):
        model = self.puzzlemodel
        view = self.editorview.solverview

        def exitSolver():
            self.editorview.centralWidget().setCurrentWidget(self.editorview.defineview)

        view.back_button.clicked.connect(exitSolver)
        view.save_button.clicked.connect(lambda: print("save and exit!"))
