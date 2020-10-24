class GameplayController:
    def __init__(self, puzzlemodel, gameplayview):
        self.puzzlemodel = puzzlemodel
        self.gameplayview = gameplayview

        gameplayview.setBoardGraphics(puzzlemodel.board)
        gameplayview.setDrawpileGraphics(puzzlemodel.drawpile, 0)
