from models import Direc
from copy import deepcopy
from PyQt5.QtCore import QTimer
from constants import POP_SPEED


def try_and_update(func):
    def wrapper(self):
        try:
            func(self)
            self.model.apply_rules(force=True)
            self._updateView()
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
        def animate_pop(popset, popearly):
            self.view.board.popset = popset
            self.view.board.popearly = popearly
            self.view.updateView(self.draw_index)

        self.model.board.apply_move(self.model.moves[self.draw_index])
        self.draw_index += 1

        popset = self.model.board.pop_set(self.model.module.pop_limit)
        animate_pop(popset, popearly=True)
        return

        while popset:
            # self.view.updateView(self.draw_index)
            # print("start animation")
            # QTimer.singleShot(POP_SPEED * 1000, lambda: animate_pop(popset, True))
            # QTimer.singleShot(POP_SPEED * 1000, lambda: animate_pop(popset, False))
            # QTimer.singleShot(POP_SPEED * 1000, lambda: None)
            # print("stop animation")
            #     self.view.board.popset = popset

            #     self.view.board.popearly = True
            #     self.view.updateView(self.draw_index)
            #     sleep(POP_SPEED)

            #     self.view.board.popearly = False
            #     self.view.updateView(self.draw_index)
            #     sleep(POP_SPEED)

            self.model.board.execute_pop(self.model.module.pop_limit)
            self.view.board.popset = set()
            popset = self.model.board.pop_set(self.model.module.pop_limit)

    @try_and_update
    def revertMove(self):
        if self.draw_index > 0:
            self.draw_index -= 1
            self.model.board.revert_move()

    def reset(self):
        self.draw_index = 0
        self._updateView()

    def _updateView(self):
        try:
            move = self.model.moves[self.draw_index]
        except IndexError:
            move = None

        self.model.hover.assign_move(move)

        if move is not None:
            future_board = deepcopy(self.model.board)
            future_board.apply_move(move)
            self.view.board.ghosts = future_board - self.model.board
        else:
            self.view.board.ghosts = set()

        self.view.updateView(self.draw_index)
