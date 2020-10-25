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

    # # Subtraction of two puyo grid models (assuming the same full size)
    # # returns the set of (pos, puyo) for which self has a puyo and other
    # # does not. This is primarily intended for determining ghost puyo
    # # locations given a post-move and pre-move puyo board model.
    # def __sub__(self, other):
    #     delta = set()

    #     for elem in self:
    #         other_puyo = other[elem.pos]
    #         if elem.puyo is not Puyo.NONE and other_puyo is Puyo.NONE:
    #             delta.add(elem)

    #     return delta

    # def copy(self):
    #     return deepcopy(self)

    def shape(self):
        return self.board.shape

    def grid(self):
        return self.board

    def reset(self):
        self[:] = Puyo.NONE

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

    # Drawpile elements are restricted from having certain puyos in
    # specific positions (assumes a minimum size of (2,1)).
    def __setitem__(self, key, value):
        self.board[key] = value
        for elem in self:
            if self.restrict(elem.pos, elem.puyo):
                puyo = elem.puyo
                while self.restrict(elem.pos, puyo):
                    puyo = puyo.next(lambda puyo: not self.restrict(elem.pos, puyo))
                self.board[elem.pos] = puyo

    def restrict(self, pos, puyo):
        if pos in {(0, 0), (1, 0)} and puyo is Puyo.NONE:
            return True
        elif puyo is Puyo.GARBAGE:
            return True

    def shape(self):
        row_sz, col_sz = (0, 0)
        for elem in self:
            if elem.puyo is not Puyo.NONE:
                row_sz = elem.pos[0] if elem.pos[0] > row_sz else row_sz
                col_sz = elem.pos[1] if elem.pos[1] > col_sz else col_sz

        return (row_sz + 1, col_sz + 1)

    def grid(self):
        return self[0 : self.shape()[0], 0 : self.shape()[1]]


# Note: this class does not check that the drawpile elements can fit the board.
class PuyoHoverAreaModel(AbstractPuyoGridModel):
    def __init__(self, board, drawpile_elem):
        size = (2 * max(drawpile_elem.board.shape) - 1, board.shape()[1])
        super().__init__(size, nhide=0)

        self.crow = int((size[0] + 1) / 2 - 1)

    def assignMove(self, move=None):
        self.reset()
        if move is None:
            return

        # For each orientation, check there isn't an edge collision.
        # If there is a collision, slide the move horizontally to fit.
        if move.direc is Direc.NORTH:
            if move.col + move.puyos.shape()[1] > self.shape()[1]:
                return self.assignMove(move._replace(col=move.col - 1))
            elif move.col < 0:
                return self.assignMove(move._replace(col=move.col + 1))

        elif move.direc is Direc.SOUTH:
            if move.col - move.puyos.shape()[1] + 1 < 0:
                return self.assignMove(move._replace(col=move.col + 1))
            elif move.col >= self.shape()[1]:
                return self.assignMove(move._replace(col=move.col - 1))

        elif move.direc is Direc.EAST:
            if move.col + move.puyos.shape()[0] > self.shape()[1]:
                return self.assignMove(move._replace(col=move.col - 1))
            elif move.col < 0:
                return self.assignMove(move._replace(col=move.col + 1))

        elif move.direc is Direc.WEST:
            if move.col - move.puyos.shape()[0] + 1 < 0:
                return self.assignMove(move._replace(col=move.col + 1))
            elif move.col >= self.shape()[0]:
                return self.assignMove(move._replace(col=move.col - 1))

        # Apply the move to the hover area grid by slicing.
        if move.direc is Direc.NORTH:
            puyos = move.puyos.grid()
            rslice = slice(self.crow, self.crow + move.puyos.shape()[0])
            cslice = slice(move.col, move.col + move.puyos.shape()[1])

        if move.direc is Direc.SOUTH:
            puyos = np.rot90(move.puyos.grid(), k=2)
            rslice = slice(self.crow - move.puyos.shape()[0] + 1, self.crow + 1)
            cslice = slice(move.col - move.puyos.shape()[1] + 1, move.col + 1)

        if move.direc is Direc.EAST:
            puyos = np.rot90(move.puyos.grid(), k=1)
            rslice = slice(self.crow - move.puyos.shape()[1] + 1, self.crow + 1)
            cslice = slice(move.col, move.col + move.puyos.shape()[0])

        if move.direc is Direc.WEST:
            puyos = np.rot90(move.puyos.grid(), k=-1)
            rslice = slice(self.crow, self.crow + move.puyos.shape()[1])
            cslice = slice(move.col - move.puyos.shape()[0] + 1, move.col + 1)

        self[rslice, cslice] = puyos
        return move


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
