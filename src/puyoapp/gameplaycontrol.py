from puyolib.puyomodel import Move, Direc


class GameplayVC:
    def __init__(self, puzzlemodel, hoverarea, view):

        view.keypressed.connect(lambda x: self.processKey(x))

        self.model = puzzlemodel
        self.hoverarea = hoverarea
        self.view = view

    def processKey(self, key):
        # puyos, col, direc = self.move
        # if key == 88:  # X
        #     self.move = Move(puyos=puyos, col=col, direc=direc.rotateR())
        #     self.gameplayview.setMoveGraphics(self.move)
        # if key == 90:  # Z
        #     self.move = Move(puyos=puyos, col=col, direc=direc.rotateL())
        #     self.gameplayview.setMoveGraphics(self.move)
        # if key == 16777236:  # KEY RIGHT
        #     print("right")
        # if key == 16777234:  # KEY LEFT
        #     print("left")
        # if key == 16777237:  # KEY DOWN
        #     print("down")
        # if key == 16777235:  # KEY UP
        #     print("up")
        pass

    def takeControl(self):
        puyos = self.model.drawpile[0]
        move = Move(puyos, col=2, direc=Direc.NORTH)
        self.hoverarea.assignMove(move)
        self.view.updateView(draw_index=1)
