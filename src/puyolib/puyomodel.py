from enum import Enum, auto
from collections import namedtuple, defaultdict

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

    def rect(self, adjmatch):
        row = SKIN_ROW_MAP[self]
        if self is Puyo.NONE:
            area = (NONE_COL, row, 1, 1)
        elif self is Puyo.GARBAGE:
            area = (GARBAGE_COL, row, 1, 1)
        else:
            col = SKIN_COL_MAP[adjmatch]
            area = (col, row, 1, 1)
        return tuple((i * SKIN_SIZE for i in area))


# A data model of a puyo puzzle. Contains a board, drawpile, and movelist.
class PuyoPuzzleModel:
    def __init__(self, board):
        self.nrows = len(board)
        self.ncols = len(board[0])
        self.board = board

    def new(nrows, ncols):
        board = [[Puyo.BLUE] * ncols for _ in range(nrows)]
        return PuyoPuzzleModel(board)

    def getBoardGraphics(self):
        rects = [[(0, 0, 0, 0)] * self.ncols for _ in range(self.nrows)]
        opacities = [[1] * self.ncols for _ in range(self.nrows)]
        for row_idx in range(self.nrows):
            for col_idx in range(self.ncols):
                puyo = self.board[row_idx][col_idx]

                # hidden row is opaque, with no adjacencies
                if row_idx == self.nrows - 1:
                    rects[row_idx][col_idx] = puyo.rect(
                        AdjMatch(north=False, south=False, east=False, west=False)
                    )
                    opacities[row_idx][col_idx] = 0.5
                    continue

                # visible board area with edge cases
                if row_idx < self.nrows - 2:
                    north = puyo is self.board[row_idx + 1][col_idx]
                else:
                    north = False
                if row_idx > 0:
                    south = puyo is self.board[row_idx - 1][col_idx]
                else:
                    south = False
                if col_idx < self.ncols - 1:
                    east = puyo is self.board[row_idx][col_idx + 1]
                else:
                    east = False
                if col_idx > 0:
                    west = puyo is self.board[row_idx][col_idx - 1]
                else:
                    west = False

                rects[row_idx][col_idx] = puyo.rect(AdjMatch(north, south, east, west))

        return (rects, opacities)


# The following constants are defined per the standard PPVS2 skin PNG image file.
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
