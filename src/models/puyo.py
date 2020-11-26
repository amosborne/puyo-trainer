from enum import Enum, auto
from itertools import permutations


class EnumCycle(Enum):
    """Abstract enum which can cycle amongst its members."""

    def _next(self, fwd=True):
        cls = self.__class__
        members = list(cls)
        index = members.index(self)
        index = index + 1 if fwd else index - 1
        if index >= len(members):
            index = 0
        elif index < 0:
            index = len(members) - 1
        return members[index]

    def next_(self, cond=None, k=1):
        """
        Return the next enum subject to the given condition.

        Args:
            cond (func, optional): Conditional function returns **True** when
                the enum has cycled to the next valid member.
            k (int, optional): Cycle forward **k** times (negative **k** is
                backwards). Each cycle is subject to the conditional function.
        """
        if k == 0:
            return self

        enum = self
        for _ in range(abs(k)):
            enum = enum._next(fwd=k > 0)
            if cond is not None:
                while not cond(enum):
                    enum = enum._next(fwd=k > 0)

        return enum


class PopState(EnumCycle):
    PREPOP = auto()
    POPEARLY = auto()
    POPLATER = auto()


class Puyo(EnumCycle):
    """A single puyo (order: red, yellow, green, blue, purple, garbage, and none)."""

    NONE = auto()
    RED = auto()
    GREEN = auto()
    BLUE = auto()
    YELLOW = auto()
    PURPLE = auto()
    GARBAGE = auto()

    @staticmethod
    def is_color(puyo):
        """Return **True** if the given **Puyo** is colored."""
        return puyo is not Puyo.NONE and puyo is not Puyo.GARBAGE

    @staticmethod
    def isnot_garbage(puyo):
        """Return **True** if the given **Puyo** is not garbage."""
        return puyo is not Puyo.GARBAGE

    def __str__(self):
        if self is Puyo.NONE:
            return "  "
        return self.name[0] + self.name[1].lower()

    @staticmethod
    def color_maps():
        colors = [puyo for puyo in Puyo if Puyo.is_color(puyo)]
        cpermute = permutations(colors)
        cmaps = set()
        for c1 in cpermute:
            for c2 in cpermute:
                cmap = zip(c1, c2)
                cmaps.add(frozenset(cmap))

        return cmaps


class Direc(EnumCycle):
    """A cardinal direction (north, south, east, and west)."""

    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()

    @staticmethod
    def rotate_cw(direc):
        """Return the **Direc** that is 90 degrees clockwise."""
        return direc.next_()

    @staticmethod
    def rotate_ccw(direc):
        """Return the **Direc** that is 90 degrees counter-clockwise."""
        return direc.next_(k=-1)

    @staticmethod
    def adj_direc(pos1, pos2):
        """Return the **Direc** which points from **pos1** to **pos2** (if adjacent)."""
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
