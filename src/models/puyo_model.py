from enum import Enum, auto


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


class Puyo(EnumCycle):
    """A single puyo (order: red, yellow, green, blue, purple, garbage, and none)."""

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


class Direc(EnumCycle):
    """A cardinal direction (north, south, east, and west)."""

    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()

    def rotate_cw(self):
        """Rotate clockwise (once)."""
        return self.next_()

    def rotate_ccw(self):
        """Rotate counter-clockwise (once)."""
        return self.next_(k=-1)

    @classmethod
    def adj_direc(cls, pos1, pos2):
        """Return the enum which points from **pos1** to **pos2** (or none)."""
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


class Move:
    """
    A move is the position and orientation of the puyos about to be dropped.
    Supports equality, including rotationally equivalent moves.
    
    Args:
        puyos (AbstractGrid): The puyo grid in its north orientation.
        col (int, optional): The column the bottom-left puyo will be dropped
            in to.
        direc (Direc, optional): The orientation of the puyo grid.
    """

    def __init__(self, puyos, col=2, direc=Direc.NORTH):
        self.puyos = puyos
        self.col = col
        self.direc = direc

    def __eq__(self, move):
        return False

    def __ne__(self, move):
        return not self.__eq__(move)

    def grid_with_offsets(self):
        """
        Rotate the puyo grid by pivoting about the bottom-left puyo.

        Returns:
            (AbstractGrid, int, int): The puyo grid in its true
            orientation and the row and columns offsets of the 
            bottom-left puyo.
        """
        pass
