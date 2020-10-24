from collections import namedtuple, defaultdict
from puyolib.puyomodel import Puyo, Direc
from puyolib.puyogridmodel import adjacency_direction


# An abstraction layer between a grid of puyos and their graphical presentation.
# This module is designed to work with 512x512px skin files from PPVS2.
class PuyoGraphicModel:
    def __init__(self, skin, gridmodel, ghosts=set()):
        self.skin = skin
        self.gridmodel = gridmodel
        self.ghosts = ghosts

    # Iteration through ghosts not yet implemented.
    def __iter__(self):
        for elem in self.gridmodel:
            px_row = SKIN_ROW_MAP[elem.puyo]

            if elem.puyo is Puyo.NONE:
                px_col = NONE_COL
            elif elem.puyo is Puyo.GARBAGE:
                px_col = GARBAGE_COL
            else:
                adj_set = self.gridmodel.getAdjacent(elem.pos)
                adj_set = {adj for adj in adj_set if adj.puyo is elem.puyo}

                north, south, east, west = (False, False, False, False)
                if not self.gridmodel.isHidden(elem.pos):
                    for adj in adj_set:
                        if self.gridmodel.isHidden(adj.pos):
                            continue
                        direc = adjacency_direction(elem.pos, adj.pos)
                        north = True if direc is Direc.NORTH else north
                        south = True if direc is Direc.SOUTH else south
                        east = True if direc is Direc.EAST else east
                        west = True if direc is Direc.WEST else west

                adj_match = AdjMatch(north, south, east, west)
                px_col = SKIN_COL_MAP[adj_match]

            rect = tuple(px * SKIN_SIZE for px in (px_col, px_row, 1, 1))
            if self.gridmodel.isHidden(elem.pos) and elem.puyo is not Puyo.NONE:
                opacity = 0.5
            else:
                opacity = 1

            yield Graphic(elem.pos, rect, opacity)


Graphic = namedtuple("Graphic", "pos, rect, opacity")

AdjMatch = namedtuple("AdjMatch", "north, south, east, west")

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
