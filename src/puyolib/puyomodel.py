from enum import Enum, auto
from collections import namedtuple, defaultdict
import numpy as np

"""
The module creates data models for handling and displaying puyo
puzzles.
"""

# An enumeration of the different puyo types.
class Puyo(Enum):
    NONE = auto()
    RED = auto()
    GREEN = auto()
    BLUE = auto()
    YELLOW = auto()
    PURPLE = auto()
    GARBAGE = auto()

    def next(self):
        cls = self.__class__
        members = list(cls)
        index = members.index(self) + 1
        if index >= len(members):
            index = 0
        return members[index]

    def nextColor(self):
        puyo = self.next()
        while puyo is Puyo.NONE or puyo is Puyo.GARBAGE:
            puyo = puyo.next()
        return puyo

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


# A data model of a puyo puzzle. Contains a board, drawpile, and movelist.
# New puyo puzzles start with two elements in the drawpile.
class PuyoPuzzleModel:
    def __init__(self, board, nhide, drawpile):
        self.board = board
        self.nhide = nhide
        self.drawpile = drawpile

    def new(size, nhide):
        board = np.full((size[0] + nhide, size[1]), Puyo.NONE).astype(Puyo)
        drawpile = np.full((2, 3, 2), Puyo.RED).astype(Puyo)
        return PuyoPuzzleModel(board, nhide, drawpile)

    def clearBoard(self):
        self.board = np.full(self.board.shape, Puyo.NONE).astype(Puyo)

    def resetDrawpile(self):
        self.drawpile = np.full((2, 2, 1), Puyo.RED).astype(Puyo)

    def newDrawpileElem(self, index):
        self.drawpile = np.insert(
            self.drawpile, index, np.full((2, 1), Puyo.RED).astype(Puyo), axis=0
        )

    def delDrawpileElem(self, index):
        self.drawpile = np.delete(self.drawpile, index, axis=0)
