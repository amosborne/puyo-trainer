from enum import Enum, auto
from collections import namedtuple
import numpy as np


"""
The module creates data models for handling and displaying puyo
puzzles.
"""


# An enum class which can cycle amongst its members.
class EnumCycle(Enum):
    def _next(self, k):
        cls = self.__class__
        members = list(cls)
        index = members.index(self) + k
        if index >= len(members):
            index = 0
        elif index < 0:
            index = len(members) - 1
        return members[index]

    def next(self, cond=lambda _: True, k=1):
        enum = self._next(k)
        while not cond(enum):
            enum = enum._next(k)
        return enum

    def prev(self, cond=lambda _: True):
        return self.next(cond, k=-1)


# An enumeration of the different puyo types.
class Puyo(EnumCycle):
    NONE = auto()
    RED = auto()
    GREEN = auto()
    BLUE = auto()
    YELLOW = auto()
    PURPLE = auto()
    GARBAGE = auto()

    def __str__(self):
        if self is Puyo.NONE:
            return "  "
        return self.name[0] + self.name[1].lower()


class Direc(Enum):
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()

    def rotateR(self):
        cls = self.__class__
        members = list(cls)
        index = members.index(self) + 1
        if index >= len(members):
            index = 0
        return members[index]

    def rotateL(self):
        cls = self.__class__
        members = list(cls)
        index = members.index(self) - 1
        if index < 0:
            index = len(members) - 1
        return members[index]


# A puyo move is defined by the column the first puyo is located in
# combined with the orientation which points the second puyo.
Move = namedtuple("Move", ["puyos", "col", "direc"])


def move2hovergrid(size, move=None):
    hovergrid = np.full(size, Puyo.NONE).astype(Puyo)

    if move is None:
        return hovergrid

    puyos = move.puyos.copy()

    if move.direc is Direc.NORTH or move.direc is Direc.EAST:
        if move.direc is Direc.EAST:
            puyos = np.rot90(puyos, k=1)
            crow = int((size[0] - 1) / 2 + 1)
        else:
            crow = size[0]
        rslice = slice(crow - puyos.shape[0], crow)
        cslice = slice(move.col, move.col + puyos.shape[1])
    elif move.direc is Direc.SOUTH or move.direc is Direc.WEST:
        if move.direc is Direc.SOUTH:
            puyos = np.rot90(puyos, k=2)
            crow = int((size[0] - 1) / 2 + 1)
        else:
            puyos = np.rot90(puyos, k=-1)
            crow = size[0] - 1
        rslice = slice(crow - puyos.shape[0], crow)
        cslice = slice(move.col - puyos.shape[1] + 1, move.col + 1)

    hovergrid[rslice, cslice] = puyos
    return hovergrid
