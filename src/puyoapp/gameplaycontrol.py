from puyolib.puyomodel import Move, Direc


class GameplayController:
    def __init__(self, puzzlemodel, gameplayview):
        self.puzzlemodel = puzzlemodel
        self.gameplayview = gameplayview

        gameplayview.setBoardGraphics(puzzlemodel.board)
        gameplayview.setDrawpileGraphics(puzzlemodel.drawpile, 0)

        self.move = Move(puyos=puzzlemodel.drawpile[0], col=2, direc=Direc.NORTH)
        gameplayview.setMoveGraphics(self.move)

        gameplayview.keypressed.connect(lambda x: self.processKey(x))

    def processKey(self, key):
        puyos, col, direc = self.move
        if key == 88:  # X
            self.move = Move(puyos=puyos, col=col, direc=direc.rotateR())
            self.gameplayview.setMoveGraphics(self.move)
        if key == 90:  # Z
            self.move = Move(puyos=puyos, col=col, direc=direc.rotateL())
            self.gameplayview.setMoveGraphics(self.move)
        if key == 16777236:  # KEY RIGHT
            print("right")
        if key == 16777234:  # KEY LEFT
            print("left")
        if key == 16777237:  # KEY DOWN
            print("down")
        if key == 16777235:  # KEY UP
            print("up")
