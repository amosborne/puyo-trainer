from puyolib.puyomodel import Move, Direc


class GameplayVC:
    def __init__(self, puzzlemodel, hoverarea, view):

        view.keypressed.connect(lambda x: self.processKey(x))

        self.model = puzzlemodel
        self.hoverarea = hoverarea
        self.view = view

    def processKey(self, key):
        if key == 88:  # X
            self.move = self.move._replace(direc=self.move.direc.rotateR())
            self.move = self.hoverarea.assignMove(self.move)
            self.view.updateView(draw_index=self.draw_index)

        elif key == 90:  # Z
            self.move = self.move._replace(direc=self.move.direc.rotateL())
            self.move = self.hoverarea.assignMove(self.move)
            self.view.updateView(draw_index=self.draw_index)

        elif key == 16777236:  # KEY RIGHT
            self.move = self.move._replace(col=self.move.col + 1)
            self.move = self.hoverarea.assignMove(self.move)
            self.view.updateView(draw_index=self.draw_index)

        elif key == 16777234:  # KEY LEFT
            self.move = self.move._replace(col=self.move.col - 1)
            self.move = self.hoverarea.assignMove(self.move)
            self.view.updateView(draw_index=self.draw_index)
        # if key == 16777237:  # KEY DOWN
        #     print("down")
        # if key == 16777235:  # KEY UP
        #     print("up")

    def takeControl(self):
        self.draw_index = 1
        self.move = Move(
            puyos=self.model.drawpile[self.draw_index - 1], col=2, direc=Direc.NORTH
        )
        self.hoverarea.assignMove(self.move)
        self.view.updateView(draw_index=self.draw_index)
