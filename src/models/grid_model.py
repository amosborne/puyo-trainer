import numpy as np
from collections import namedtuple
from pandas import DataFrame
from models.puyo_model import Puyo, Direc


class AbstractGrid:
    """
    An abstract grid of puyo enumeration elements (including hidden rows).
    Supports set by slice, get by single key, iteration over elements,
    equality, and the difference operator. Use classmethod constructors.
    """

    GridElem = namedtuple("GridElem", "pos, puyo")

    def __init__(self, board, nhide):
        self._board = board
        self._nhide = nhide

    @classmethod
    def new(cls, shape, nhide):
        """
        Args:
            shape (int, int): Shape of the visible grid.
            nhide (int): Number of hidden rows above the visible grid.
        """
        fullsize = (shape[0] + nhide, shape[1])
        board = np.empty(fullsize).astype(Puyo)
        return cls(board, nhide).reset()

    @property
    def shape(self):
        """(int, int): Shape of the grid (including hidden rows). Read-only."""
        return self._board.shape

    @staticmethod
    def _tighten(board):
        """
        Reduce the given board to the minimum non-empty sub-board. Implemented
        as a private static method to decouple sub-grids and hidden rows.

        Returns:
            (board, int, int): The tightened board and row and column integer
            offsets of the bottom-left corner of the resulting sub-board.
        """

        rstart, cstart, rend, cend = (board.shape[0], board.shape[1], 0, 0)

        for r, row in enumerate(board):
            for puyo in row:
                rstart = r if puyo is not Puyo.NONE and r < rstart else rstart
                rend = r + 1 if puyo is not Puyo.NONE and r >= rend else rend
        for c, col in enumerate(board.T):
            for puyo in col:
                cstart = c if puyo is not Puyo.NONE and c < cstart else cstart
                cend = c + 1 if puyo is not Puyo.NONE and c >= cend else cend

        return board[rstart:rend, cstart:cend], rstart, cstart

    def __setitem__(self, subscript, value):
        self._board[subscript] = value

    def __iter__(self):
        return (self.GridElem(pos, puyo) for (pos, puyo) in np.ndenumerate(self._board))

    def __getitem__(self, subscript):
        has_slice = any([isinstance(ax_sub, slice) for ax_sub in subscript])
        if has_slice:
            raise RuntimeError("AbstractGrid does not support slice access.")
        else:
            return self._board[subscript]

    def __str__(self):
        board_flipped = np.flipud(self._board)
        height, width = board_flipped.shape

        col_names = ["c" + str(i + 1) for i in range(width)]
        row_names1 = ["r" + str(i + 1) for i in reversed(range(height - self._nhide))]
        row_names2 = ["h" + str(i + 1) for i in reversed(range(self._nhide))]

        dataframe = DataFrame(board_flipped)
        dataframe.columns = col_names
        dataframe.index = row_names2 + row_names1

        return dataframe.__str__()

    def __sub__(self, other):
        """Return the set of grid elements in self that are different from other."""
        return set([elem for elem in self if elem.puyo is not other[elem.pos]])

    def __eq__(self, other):
        return len(self - other) == 0

    def __ne__(self, other):
        return not self == other

    def reset(self):
        """Set all elements to empty. Return **self**."""
        self[:] = Puyo.NONE
        return self

    def gravitize(self):
        """Apply gravity to cause floating elements to fall. Return **self**."""
        for c, col in enumerate(self._board.T):
            h = 0
            for puyo in col:
                if puyo is not Puyo.NONE:
                    self[h, c] = puyo
                    h += 1
            self[h:, c] = Puyo.NONE

        return self

    def is_hidden(self, subscript):
        """Return **True** if the element position is in a hidden row."""
        return subscript[0] >= self._board.shape[0] - self._nhide

    def adjacent(self, subscript):
        """Return the set of adjacent elements to the element position."""
        return set([elem for elem in self if Direc.adj_direc(subscript, elem.pos)])


class DrawElemGrid(AbstractGrid):
    """
    A grid representing the puyos to be drawn from the drawpile. Setting elements
    is additionally restricted: the size must be at least (2,1), no puyos may be
    garbage, and the two bottom-left puyos must be a color. Attempting to set an
    invalid puyo will do nothing (during initialization a valid puyo is assumed).
    """

    @classmethod
    def new(cls, shape):
        """Calls super constructor with zero hidden rows."""
        assert shape > (2, 1)
        return super().new(shape, nhide=0)

    def __setitem__(self, subscript, value):
        old_board = self._board.copy()
        super().__setitem__(subscript, value)

        for elem in self:
            cond = self.cond(elem.pos)
            if not cond(elem.puyo):
                old_elem = old_board[elem.pos]
                if isinstance(old_elem, Puyo):
                    self._board[elem.pos] = old_elem
                else:
                    self._board[elem.pos] = elem.puyo.next_(cond=cond)

    def cond(self, pos):
        """For the given position, return the conditional function for a valid puyo."""
        if pos in {(0, 0), (1, 0)}:
            return lambda puyo: puyo is not Puyo.NONE and puyo is not Puyo.GARBAGE
        else:
            return lambda puyo: puyo is not Puyo.GARBAGE

    def finalize(self, direc):
        """
        Assuming **self** is north-oriented, reorient the grid to the given
        direction, gravitize, and tighten to the smallest sub-grid containing
        grid elements.

        Returns:
            (AbstractGrid, int): The finalized grid and resulting column
            offset relative to the bottom-left grid element.
        """
        reorient_grid, _, coff = self.reorient(direc)
        reorient_grid.gravitize()
        final_board, _, _ = AbstractGrid._tighten(reorient_grid._board)
        return AbstractGrid(final_board, nhide=0), coff

    def reorient(self, direc):
        """
        Assuming **self** is north-oriented, reorient the grid to the given 
        direction and tighten to the smallest sub-grid containing non-empty elements.

        Returns:
            (AbstractGrid, int, int): The finalized grid and resulting row
            and column offsets relative to the bottom-left grid element.
        """
        board = self._board.copy()

        if direc is Direc.EAST:
            new_board, roff, coff = AbstractGrid._tighten(np.rot90(board))
            roff, coff = roff - board.shape[1] + 1, coff
        elif direc is Direc.SOUTH:
            new_board, roff, coff = AbstractGrid._tighten(np.rot90(board, k=2))
            roff, coff = roff - board.shape[0] + 1, coff - board.shape[1] + 1
        elif direc is Direc.WEST:
            new_board, roff, coff = AbstractGrid._tighten(np.rot90(board, k=-1))
            roff, coff = roff, coff - board.shape[0] + 1
        elif direc is Direc.NORTH:
            new_board, roff, coff = AbstractGrid._tighten(board)
        else:
            return None

        return AbstractGrid(new_board, nhide=0), roff, coff


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


class Move:
    """
    A move is the position and orientation of the puyos about to be dropped.
    Supports equality, including rotationally equivalent moves.
    
    Args:
        puyos (DrawElemGrid): The puyo grid in its north orientation.
        col (int): The column the bottom-left puyo will be dropped
            in to.
        direc (Direc): The orientation of the puyo grid.
    """

    def __init__(self, puyos, col, direc):
        self.puyos = puyos
        self.col = col
        self.direc = direc

    def __eq__(self, move):
        this_grid, _, this_coff = self.grid_with_offsets()
        that_grid, _, that_coff = move.grid_with_offsets()
        # print(this_grid)
        # print(that_grid)
        if (this_coff + self.col) == (that_coff + move.col):
            return this_grid.gravitize() == that_grid.gravitize()
        else:
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
        grid = self.puyos.reorient(self.direc)
        if self.direc is Direc.NORTH:
            roff, coff = 0, 0
        elif self.direc is Direc.EAST:
            roff, coff = 1 - grid.tight_shape[1], 0
        elif self.direc is Direc.SOUTH:
            roff, coff = 1 - grid.tight_shape[0], 1 - grid.tight_shape[1]
        elif self.direc is Direc.WEST:
            roff, coff = 0, 1 - grid.tight_shape[0]
        else:
            return None

        return grid, roff, coff
