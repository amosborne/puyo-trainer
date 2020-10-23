from enum import Enum, auto
from collections import namedtuple, defaultdict
import numpy as np

"""
The module creates a data model for handling puyos.
The data model maintains a board, a drawpile, and a movelist.
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


# A data model of a puyo puzzle. Contains a board, drawpile, and movelist.
class PuyoPuzzleModel:
    def __init__(self, board, nhide):
        self.board = board
        self.nhide = nhide

    def new(size, nhide):
        board = np.full((size[0] + nhide, size[1]), Puyo.NONE).astype(Puyo)
        return PuyoPuzzleModel(board, nhide)


# A model for retrieving stationary puyo graphics. Supports PPVS2 skin files.
class PuyoGridGraphicsModel:
    AdjMatch = namedtuple("AdjMatch", ["north", "south", "east", "west"])

    SKIN_SIZE = 32
    SKIN_ROW_MAP = defaultdict(int)
    SKIN_ROW_MAP[Puyo.RED] = 0
    SKIN_ROW_MAP[Puyo.GREEN] = 1
    SKIN_ROW_MAP[Puyo.BLUE] = 2
    SKIN_ROW_MAP[Puyo.YELLOW] = 3
    SKIN_ROW_MAP[Puyo.PURPLE] = 4
    SKIN_ROW_MAP[Puyo.GARBAGE] = 12
    SKIN_ROW_MAP[Puyo.NONE] = 9

    GARBAGE_COL = 6
    NONE_COL = 0

    SKIN_COL_MAP = defaultdict(int)
    SKIN_COL_MAP[AdjMatch(north=False, south=False, east=False, west=False)] = 0
    SKIN_COL_MAP[AdjMatch(north=False, south=True, east=False, west=False)] = 1
    SKIN_COL_MAP[AdjMatch(north=True, south=False, east=False, west=False)] = 2
    SKIN_COL_MAP[AdjMatch(north=True, south=True, east=False, west=False)] = 3
    SKIN_COL_MAP[AdjMatch(north=False, south=False, east=True, west=False)] = 4
    SKIN_COL_MAP[AdjMatch(north=False, south=True, east=True, west=False)] = 5
    SKIN_COL_MAP[AdjMatch(north=True, south=False, east=True, west=False)] = 6
    SKIN_COL_MAP[AdjMatch(north=True, south=True, east=True, west=False)] = 7
    SKIN_COL_MAP[AdjMatch(north=False, south=False, east=False, west=True)] = 8
    SKIN_COL_MAP[AdjMatch(north=False, south=True, east=False, west=True)] = 9
    SKIN_COL_MAP[AdjMatch(north=True, south=False, east=False, west=True)] = 10
    SKIN_COL_MAP[AdjMatch(north=True, south=True, east=False, west=True)] = 11
    SKIN_COL_MAP[AdjMatch(north=False, south=False, east=True, west=True)] = 12
    SKIN_COL_MAP[AdjMatch(north=False, south=True, east=True, west=True)] = 13
    SKIN_COL_MAP[AdjMatch(north=True, south=False, east=True, west=True)] = 14
    SKIN_COL_MAP[AdjMatch(north=True, south=True, east=True, west=True)] = 15

    def __init__(self, skin):
        self.skin = skin

    def graphic(self, board, nhide, pos):
        def rect(puyo, adjmatch):
            row = self.SKIN_ROW_MAP[puyo]
            if puyo is Puyo.NONE:
                area = (self.NONE_COL, row, 1, 1)
            elif puyo is Puyo.GARBAGE:
                area = (self.GARBAGE_COL, row, 1, 1)
            else:
                col = self.SKIN_COL_MAP[adjmatch]
                area = (col, row, 1, 1)
            return tuple((i * self.SKIN_SIZE for i in area))

        puyo = board[pos]
        row, col = pos
        if row >= (board.shape[0] - nhide):
            adjmatch = self.AdjMatch(north=False, south=False, east=False, west=False)
            puyo_opacity = 0.5
        else:
            if row < (board.shape[0] - nhide - 1):
                mnorth = puyo is board[row + 1, col]
            else:
                mnorth = False
            if row > 0:
                msouth = puyo is board[row - 1, col]
            else:
                msouth = False
            if col < board.shape[1] - 1:
                meast = puyo is board[row, col + 1]
            else:
                meast = False
            if col > 0:
                mwest = puyo is board[row, col - 1]
            else:
                mwest = False

            adjmatch = self.AdjMatch(north=mnorth, south=msouth, east=meast, west=mwest)
            puyo_opacity = 1

        puyo_rect = rect(puyo, adjmatch)
        return (puyo_rect, puyo_opacity)
