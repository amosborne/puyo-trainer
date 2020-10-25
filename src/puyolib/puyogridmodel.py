import numpy as np
from collections import namedtuple
from copy import deepcopy
from pandas import DataFrame
from puyolib.puyomodel import Puyo, Direc


PuyoGridElem = namedtuple("PuyoGridElem", "pos, puyo")


# A class structure for controlling and interrogating a grid of puyos.
class AbstractPuyoGridModel:
    def __init__(self, size, nhide):
        fullsize = (size[0] + nhide, size[1])
        self.board = np.empty(fullsize).astype(Puyo)
        self.reset()
        self.nhide = nhide

    def __iter__(self):
        return (PuyoGridElem(pos, puyo) for (pos, puyo) in np.ndenumerate(self.board))

    def __getitem__(self, key):
        return self.board[key]

    def __setitem__(self, key, value):
        self.board[key] = value

    def __str__(self):
        board_flipped = np.flipud(self.board)
        height, width = board_flipped.shape

        col_names = ["c" + str(i + 1) for i in range(width)]
        row_names1 = ["r" + str(i + 1) for i in range(height - self.nhide)]
        row_names2 = ["h" + str(i + 1) for i in range(self.nhide)]

        dataframe = DataFrame(board_flipped)
        dataframe.columns = col_names
        dataframe.index = row_names2 + list(reversed(row_names1))

        return dataframe.__str__()

    # Subtraction of two puyo grid models (assuming the same full size)
    # returns the set of (pos, puyo) for which self has a puyo and other
    # does not. This is primarily intended for determining ghost puyo
    # locations given a post-move and pre-move puyo board model.
    def __sub__(self, other):
        delta = set()

        for elem in self:
            other_puyo = other[elem.pos]
            if elem.puyo is not Puyo.NONE and other_puyo is Puyo.NONE:
                delta.add(elem)

        return delta

    def copy(self):
        return deepcopy(self)

    def reset(self):
        self.board[:] = Puyo.NONE

    def isHidden(self, key):
        return key[0] >= self.board.shape[0] - self.nhide

    def getAdjacent(self, key):
        adj = set()

        for elem in self:
            if elem.puyo is not Puyo.NONE and adjacency_direction(key, elem.pos):
                adj.add(elem)

        return adj


class PuyoBoardModel(AbstractPuyoGridModel):
    def applyMove(move):
        pass


class PuyoDrawpileElemModel(AbstractPuyoGridModel):
    def __init__(self, size):
        super().__init__(size, nhide=0)


class PuyoHoverAreaModel(AbstractPuyoGridModel):
    pass


def adjacency_direction(pos1, pos2):
    if pos1[1] == pos2[1] and pos1[0] + 1 == pos2[0]:
        return Direc.NORTH
    elif pos1[1] == pos2[1] and pos1[0] - 1 == pos2[0]:
        return Direc.SOUTH
    elif pos1[0] == pos2[0] and pos1[1] + 1 == pos2[1]:
        return Direc.EAST
    elif pos1[0] == pos2[0] and pos1[1] - 1 == pos2[1]:
        return Direc.WEST
    else:
        return None
