from puyolib.puyomodel import Move, Direc


def apply_move(func):
    def decorator(self):
        if self.move is not None:
            func(self)
        self.move = self.hoverarea.assignMove(self.move)
        self.view.updateView(self.draw_index)

    return decorator


class GameplayVC:
    def __init__(self, puzzlemodel, hoverarea, view):
        self.model = puzzlemodel
        self.hoverarea = hoverarea
        self.view = view

        view.pressX.connect(self.rotateRight)
        view.pressZ.connect(self.rotateLeft)
        view.pressRight.connect(self.shiftRight)
        view.pressLeft.connect(self.shiftLeft)
        view.pressUp.connect(self.revertMove)
        view.pressDown.connect(self.makeMove)

    @apply_move
    def rotateRight(self):
        self.move = self.move._replace(direc=self.move.direc.rotateR())

    @apply_move
    def rotateLeft(self):
        self.move = self.move._replace(direc=self.move.direc.rotateL())

    @apply_move
    def shiftRight(self):
        self.move = self.move._replace(col=self.move.col + 1)

    @apply_move
    def shiftLeft(self):
        self.move = self.move._replace(col=self.move.col - 1)

    @apply_move
    def makeMove(self):
        self.model.board.applyMove(self.move)
        self.draw_index += 1
        if self.draw_index > len(self.model.drawpile):
            self.move = None
        else:
            self.move = self._defaultMove()

    def revertMove(self):
        if self.draw_index > 1:
            self.draw_index -= 1
            self.move = self.model.board.revertMove()
            self.move = self.hoverarea.assignMove(self.move)
            self.view.updateView(self.draw_index)

    def reset(self):
        self.draw_index = 1
        self.move = self._defaultMove()
        self.move = self.hoverarea.assignMove(self.move)
        self.view.updateView(self.draw_index)

    def _defaultMove(self):
        puyos = self.model.drawpile[self.draw_index - 1]
        return Move(puyos, col=2, direc=Direc.NORTH)
