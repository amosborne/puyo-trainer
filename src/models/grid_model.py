import numpy as np
from collections import namedtuple
from pandas import DataFrame
from models.puyo_model import Puyo, Direc


class AbstractGrid:
    """
    An abstract grid holds a grid of puyos, potentially with hidden rows.
    Supports setting by slicing, getting by individual subscripts, iteration,
    equality, and the difference operator.
    """

    GridElem = namedtuple("GridElem", "pos, puyo")

    def __init__(self, board, nhide):
        self.board = board
        self.nhide = nhide

    @classmethod
    def new(cls, size, nhide):
        """
        Create a new abstract grid.

        Args:
            size (tuple(int,int)): Size of the visible board.
            nhide (int): Number of hidden rows above the visible board.
        """
        fullsize = (size[0] + nhide, size[1])
        board = np.empty(fullsize).astype(Puyo)
        return cls(board, nhide).reset()

    def __setitem__(self, subscript, value):
        self.board[subscript] = value

    def __iter__(self):
        return (self.GridElem(pos, puyo) for (pos, puyo) in np.ndenumerate(self.board))

    def __getitem__(self, subscript):
        has_slice = any([isinstance(ax_sub, slice) for ax_sub in subscript])
        if has_slice:
            raise RuntimeError("AbstractGrid does not support slice access.")
        else:
            return self.board[subscript]

    def __str__(self):
        board_flipped = np.flipud(self.board)
        height, width = board_flipped.shape

        col_names = ["c" + str(i + 1) for i in range(width)]
        row_names1 = ["r" + str(i + 1) for i in reversed(range(height - self.nhide))]
        row_names2 = ["h" + str(i + 1) for i in reversed(range(self.nhide))]

        dataframe = DataFrame(board_flipped)
        dataframe.columns = col_names
        dataframe.index = row_names2 + row_names1

        return dataframe.__str__()

    def __sub__(self, other):
        """Return the grid elements in self that are different from other."""
        return set([elem for elem in self if elem.puyo is not other[elem.pos]])

    def __eq__(self, other):
        return len(self - other) == 0

    def __ne__(self, other):
        return not self == other

    def reset(self):
        """Return self will all grid elements set to none."""
        self[:] = Puyo.NONE
        return self

    @property
    def shape(self):
        """Return the shape of the entire grid, including hidden rows."""
        return self.board.shape

    def is_hidden(self, subscript):
        """Return True if the element position is in a hidden row."""
        return subscript[0] >= self.board.shape[0] - self.nhide

    def adjacent(self, subscript):
        """Return the set of adjacent grid elements to the element position."""
        return set([elem for elem in self if Direc.adj_direc(subscript, elem.pos)])


class DrawElemGrid(AbstractGrid):
    """
    A grid representing the puyos to be drawn from the drawpile. Setting elements
    is additionally restricted: the size must be at least (2,1), no puyos may be
    garbage, and the two bottom-left puyos must be a color. Attempting to set an
    invalid puyo will do nothing (during initialization a valid puyo is assumed).
    """

    @classmethod
    def new(cls, size):
        """Calls super constructor with zero hidden rows."""
        assert size > (2, 1)
        return super().new(size, nhide=0)

    def __setitem__(self, subscript, value):
        old_board = self.board.copy()
        super().__setitem__(subscript, value)

        for elem in self:
            cond = self.cond(elem.pos)
            if not cond(elem.puyo):
                old_elem = old_board[elem.pos]
                if isinstance(old_elem, Puyo):
                    self.board[elem.pos] = old_elem
                else:
                    self.board[elem.pos] = elem.puyo.next_(cond=cond)

    def cond(self, pos):
        """For the given position, return the conditional function for a valid puyo."""
        if pos in {(0, 0), (1, 0)}:
            return lambda puyo: puyo is not Puyo.NONE and puyo is not Puyo.GARBAGE
        else:
            return lambda puyo: puyo is not Puyo.GARBAGE

    def shape(self):
        row_sz, col_sz = (0, 0)
        for elem in self:
            if elem.puyo is not Puyo.NONE:
                row_sz = elem.pos[0] if elem.pos[0] > row_sz else row_sz
                col_sz = elem.pos[1] if elem.pos[1] > col_sz else col_sz

        return (row_sz + 1, col_sz + 1)

    def grid(self):
        return self[0 : self.shape()[0], 0 : self.shape()[1]]

    def reorient(self, direc):
        """
        Assuming self is north oriented, return a new abstract grid that is
        reoriented to the given direction (by rotation).
        """
        grid = DrawElemGrid(board=self.board.copy(), nhide=0)

        if direc is Direc.EAST:
            grid.board = np.rot90(grid.board)
        elif direc is Direc.SOUTH:
            grid.board = np.rot90(grid.board, k=2)
        elif direc is Direc.WEST:
            grid.board = np.rot90(grid.board, k=-1)
        elif direc is Direc.NORTH:
            pass
        else:
            return None

        return grid


# Whenever a move is applied to the puyo board model, the move is recorded
# alongside the board pre-application.
class PuyoBoardModel(AbstractGrid):
    def __init__(self, size, nhide):
        super().__init__(size, nhide)
        self.movelist = []

    def _colHeight(self, idx):
        if all(self[:, idx] != Puyo.NONE):
            return self.shape()[0]
        else:
            return np.argmin(self[:, idx] != Puyo.NONE)

    def applyMove(self, move):

        # First record the move and the pre-application board.
        self.movelist.append((move, self.board.copy()))

        def applybyColumn(puyos, leftcol):
            for cidx, puyocol in enumerate(puyos.T):
                puyocol = [puyo for puyo in puyocol if puyo is not Puyo.NONE]
                rstart = self._colHeight(cidx + leftcol)
                for ridx, puyo in enumerate(puyocol):
                    rend = rstart + ridx
                    if rend < self.shape()[0]:
                        self[rend, cidx + leftcol] = puyo
                    else:
                        break

        if move.direc is Direc.NORTH:
            puyos = move.puyos.grid()
            applybyColumn(puyos, move.col)

        elif move.direc is Direc.SOUTH:
            puyos = np.rot90(move.puyos.grid(), k=2)
            applybyColumn(puyos, move.col - move.puyos.shape()[1] + 1)

        elif move.direc is Direc.EAST:
            puyos = np.rot90(move.puyos.grid(), k=1)
            applybyColumn(puyos, move.col)

        elif move.direc is Direc.WEST:
            puyos = np.rot90(move.puyos.grid(), k=-1)
            applybyColumn(puyos, move.col - move.puyos.shape()[0] + 1)

    def revertMove(self):
        if self.movelist:
            move, board = self.movelist.pop()
            self.board = board
            return move

    def revert(self):
        if self.movelist:
            self.board = self.movelist[0][1]
            self.movelist = []


# Note: this class does not check that the drawpile elements can fit the board.
class PuyoHoverAreaModel(AbstractGrid):
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
            elif move.col > self.shape()[0]:
                return self.assignMove(move._replace(col=move.col - 1))

        # Apply the move to the hover area grid by slicing.
        if move.direc is Direc.NORTH:
            puyos = move.puyos.grid()
            rslice = slice(self.crow, self.crow + move.puyos.shape()[0])
            cslice = slice(move.col, move.col + move.puyos.shape()[1])

        elif move.direc is Direc.SOUTH:
            puyos = np.rot90(move.puyos.grid(), k=2)
            rslice = slice(self.crow - move.puyos.shape()[0] + 1, self.crow + 1)
            cslice = slice(move.col - move.puyos.shape()[1] + 1, move.col + 1)

        elif move.direc is Direc.EAST:
            puyos = np.rot90(move.puyos.grid(), k=1)
            rslice = slice(self.crow - move.puyos.shape()[1] + 1, self.crow + 1)
            cslice = slice(move.col, move.col + move.puyos.shape()[0])

        elif move.direc is Direc.WEST:
            puyos = np.rot90(move.puyos.grid(), k=-1)
            rslice = slice(self.crow, self.crow + move.puyos.shape()[1])
            cslice = slice(move.col - move.puyos.shape()[0] + 1, move.col + 1)

        self[rslice, cslice] = puyos
        return move
