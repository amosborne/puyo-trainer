from enum import IntEnum, auto
from collections import namedtuple, defaultdict

"""
Defines an enumeration for defining a single puyo and
helpful functions for handling their specific properties.
"""

AdjMatch = namedtuple("AdjMatch", ["north", "south", "east", "west"])


class Puyo(IntEnum):
    NONE = 0
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4
    PURPLE = 5
    GARBAGE = 6

    def cycle(puyo):
        return Puyo((puyo + 1) % len(Puyo))

    def rect(puyo, adjmatch):
        row = SKIN_ROW_MAP[puyo]
        if puyo is Puyo.NONE:
            area = (NONE_COL, row, 1, 1)
        elif puyo is Puyo.GARBAGE:
            area = (GARBAGE_COL, row, 1, 1)
        else:
            col = SKIN_COL_MAP[adjmatch]
            area = (col, row, 1, 1)
        return tuple((i * SKIN_SIZE for i in area))


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
