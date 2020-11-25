from collections import namedtuple, defaultdict
from itertools import chain
from models import Puyo, Direc, PopState
from constants import SKIN_DIRECTORY
import cv2

# This module is designed to work with 512x512px skin files from PPVS2.


def grid2graphics(skin, grid, ghosts=set(), pops=set(), popstate=PopState.PREPOP):
    # Load the skin file.
    skin = cv2.imread(SKIN_DIRECTORY + skin, cv2.IMREAD_UNCHANGED)
    skin = cv2.cvtColor(skin, cv2.COLOR_BGRA2RGBA)

    # Accumulate the various graphics.
    exclude = ghosts | pops if popstate is not PopState.PREPOP else ghosts
    graphics = _grid2regulargfx(skin, grid, exclude)
    graphics += _ghostgfx(skin, ghosts)
    graphics += _popgfx(skin, pops, popstate) if popstate is not PopState.PREPOP else []
    return graphics


def _grid2regulargfx(skin, grid, exclude=set()):
    graphics = []
    for elem in grid:
        if elem.pos in {x.pos for x in exclude}:
            continue

        adj_set = grid.adjacent(elem.pos)
        adj_set = {adj for adj in adj_set if adj.puyo is elem.puyo}

        north, south, east, west = (False, False, False, False)
        if not grid.is_hidden(elem.pos):
            for adj in adj_set:
                if grid.is_hidden(adj.pos):
                    continue
                direc = Direc.adj_direc(elem.pos, adj.pos)
                north = True if direc is Direc.NORTH else north
                south = True if direc is Direc.SOUTH else south
                east = True if direc is Direc.EAST else east
                west = True if direc is Direc.WEST else west

        if elem.puyo is Puyo.NONE:
            px_col = NONE_COL
        elif elem.puyo is Puyo.GARBAGE:
            px_col = GARBAGE_COL
        else:
            px_col = SKIN_COL_MAP[AdjMatch(north, south, east, west)]

        px_row = SKIN_ROW_MAP[elem.puyo]
        image = skin[
            px_row * SKIN_SIZE + 1 : (px_row + 1) * SKIN_SIZE - 1,
            px_col * SKIN_SIZE + 1 : (px_col + 1) * SKIN_SIZE - 1,
        ]

        opacity = 0.5 if grid.is_hidden(elem.pos) else 1
        graphics.append(Graphic(elem.pos, image, opacity))

    return graphics


def _ghostgfx(skin, ghosts):
    graphics = []
    for elem in ghosts:
        px_row, px_col = SKIN_GHOST_MAP[elem.puyo]
        image = skin[
            px_row * GHOST_SIZE + 1 : (px_row + 1) * GHOST_SIZE - 1,
            px_col * GHOST_SIZE + 1 : (px_col + 1) * GHOST_SIZE - 1,
        ]

        padsize = int((SKIN_SIZE - GHOST_SIZE) / 2)
        image = cv2.copyMakeBorder(
            image, padsize, padsize, padsize, padsize, cv2.BORDER_CONSTANT
        )

        graphics.append(Graphic(elem.pos, image, 1))

    return graphics


def _popgfx(skin, pops, popstate):
    graphics = []
    for elem in pops:
        if elem.puyo is Puyo.GARBAGE:
            if popstate is PopState.POPEARLY:
                px_col = GARBAGE_COL
                px_row = SKIN_ROW_MAP[Puyo.GARBAGE]
            else:
                px_col = NONE_COL
                px_row = SKIN_ROW_MAP[Puyo.NONE]
        else:
            px_col = SKIN_POPMAP[elem.puyo]
            px_col = px_col + 1 if popstate is PopState.POPLATER else px_col
            px_row = SKIN_POPMAP_ROW

        image = skin[
            px_row * SKIN_SIZE + 1 : (px_row + 1) * SKIN_SIZE - 1,
            px_col * SKIN_SIZE + 1 : (px_col + 1) * SKIN_SIZE - 1,
        ]
        graphics.append(Graphic(elem.pos, image, 1))

    return graphics


Graphic = namedtuple("Graphic", "pos, image, opacity")
AdjMatch = namedtuple("AdjMatch", "north, south, east, west")

SKIN_SIZE = 32
SKIN_ROW_MAP = defaultdict(int)
SKIN_ROW_MAP[Puyo.RED] = 0
SKIN_ROW_MAP[Puyo.GREEN] = 1
SKIN_ROW_MAP[Puyo.BLUE] = 2
SKIN_ROW_MAP[Puyo.YELLOW] = 3
SKIN_ROW_MAP[Puyo.PURPLE] = 4
SKIN_ROW_MAP[Puyo.GARBAGE] = 12
SKIN_ROW_MAP[Puyo.NONE] = 15

GARBAGE_COL = 6
NONE_COL = 8

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

GHOST_SIZE = int(SKIN_SIZE / 2)
SKIN_GHOST_MAP = defaultdict(int)
SKIN_GHOST_MAP[Puyo.RED] = (14, 29)
SKIN_GHOST_MAP[Puyo.GREEN] = (15, 29)
SKIN_GHOST_MAP[Puyo.BLUE] = (16, 29)
SKIN_GHOST_MAP[Puyo.YELLOW] = (14, 28)
SKIN_GHOST_MAP[Puyo.PURPLE] = (15, 28)

SKIN_POPMAP_ROW = 10

SKIN_POPMAP = defaultdict(int)
SKIN_POPMAP[Puyo.RED] = 6
SKIN_POPMAP[Puyo.GREEN] = 8
SKIN_POPMAP[Puyo.BLUE] = 10
SKIN_POPMAP[Puyo.YELLOW] = 12
SKIN_POPMAP[Puyo.PURPLE] = 14
