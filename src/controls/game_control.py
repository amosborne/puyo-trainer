from models.puyo_model import Direc
from models.grid_model import Move
from copy import deepcopy


class GameVC:
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

    def rotateRight(self):
        if self.move:
            self.move = self.move._replace(direc=self.move.direc.rotateR())
            self._updateView()

    def rotateLeft(self):
        if self.move:
            self.move = self.move._replace(direc=self.move.direc.rotateL())
            self._updateView()

    def shiftRight(self):
        if self.move:
            self.move = self.move._replace(col=self.move.col + 1)
            self._updateView()

    def shiftLeft(self):
        if self.move:
            self.move = self.move._replace(col=self.move.col - 1)
            self._updateView()

    def makeMove(self):
        if self.move:
            self.model.board.applyMove(self.move)
            self.draw_index += 1
            if self.draw_index > len(self.model.drawpile):
                self.move = None
            else:
                self.move = self._defaultMove()
            self._updateView()

    def revertMove(self):
        if self.draw_index > 1:
            self.draw_index -= 1
            self.move = self.model.board.revertMove()
            self._updateView()

    def reset(self):
        self.draw_index = 1
        self.move = self._defaultMove()
        self._updateView()

    def _defaultMove(self):
        puyos = self.model.drawpile[self.draw_index - 1]
        return Move(puyos, col=2, direc=Direc.NORTH)

    def _updateView(self):
        self.move = self.hoverarea.assignMove(self.move)

        if self.move:
            future_board = deepcopy(self.model.board)
            future_board.applyMove(self.move)
            self.view.board.ghosts = future_board - self.model.board
        else:
            self.view.board.ghosts = set()

        self.view.updateView(self.draw_index)
