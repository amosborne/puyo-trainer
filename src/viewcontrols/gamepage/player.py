from models import Direc
from copy import deepcopy
from PyQt5.QtCore import QTimer
from constants import POP_SPEED


def try_and_update(func):
    def wrapper(self):
        if self.timer.isActive():
            return
        try:
            func(self)
            self.model.apply_rules(force=True)
            self._animatePop(True)
        except IndexError:
            pass

    return wrapper


class GameVC:
    def __init__(self, puzzle, view):
        self.model = puzzle
        self.view = view

        view.pressX.connect(self.rotateRight)
        view.pressZ.connect(self.rotateLeft)
        view.pressRight.connect(self.shiftRight)
        view.pressLeft.connect(self.shiftLeft)
        view.pressUp.connect(self.revertMove)
        view.pressDown.connect(self.makeMove)

        timer = QTimer(self.view)
        timer.setSingleShot(True)
        timer.setInterval(POP_SPEED * 1000)
        self.timer = timer

    @try_and_update
    def rotateRight(self):
        move = self.model.moves[self.draw_index]
        move.direc = Direc.rotate_cw(move.direc)

    @try_and_update
    def rotateLeft(self):
        move = self.model.moves[self.draw_index]
        move.direc = Direc.rotate_ccw(move.direc)

    @try_and_update
    def shiftRight(self):
        self.model.moves[self.draw_index].col += 1

    @try_and_update
    def shiftLeft(self):
        self.model.moves[self.draw_index].col -= 1

    @try_and_update
    def makeMove(self):
        self.model.board.apply_move(self.model.moves[self.draw_index])
        self.draw_index += 1

    @try_and_update
    def revertMove(self):
        if self.draw_index > 0:
            self.draw_index -= 1
            self.model.board.revert_move()

    def reset(self):
        self.draw_index = 0
        self._animatePop(True)

    def _animatePop(self, popearly):
        try:
            move = self.model.moves[self.draw_index]
        except IndexError:
            move = None

        self.model.hover.assign_move(move)

        self.view.board.ghosts = set()
        popset = self.view.board.grid.pop_set(self.model.module.pop_limit)

        timer = QTimer(self.view)
        timer.setSingleShot(True)
        timer.setInterval(POP_SPEED * 1000)
        self.timer = timer

        if popset:
            self.view.board.popset = popset
            self.view.board.popearly = popearly
            self.view.updateView(self.draw_index)

            if popearly:
                self.timer.timeout.connect(lambda: self._animatePop(False))
            else:
                self.model.board.execute_pop(self.model.module.pop_limit)
                self.timer.timeout.connect(lambda: self._animatePop(True))

            self.timer.start()

        else:
            if move is not None:
                future_board = deepcopy(self.model.board)
                future_board.apply_move(move)
                self.view.board.ghosts = future_board - self.model.board
            else:
                self.view.board.ghosts = set()

            self.view.board.popset = set()
            self.view.updateView(self.draw_index)
