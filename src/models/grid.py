import numpy as np
from collections import namedtuple
from pandas import DataFrame
from models.puyo import Puyo, Direc
from copy import deepcopy


class AbstractGrid:
    """
    An abstract grid of puyo enumeration elements (including hidden rows).
    Supports set by slice, get by single key, iteration over elements,
    equality, and the difference operator. Use classmethod constructors.
    """

    GridElem = namedtuple("GridElem", "pos, puyo")

    def __init__(self, board, nhide):
        self._board = board
        self.nhide = nhide

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
        """(int, int): Shape of the grid (including hidden rows)."""
        return self._board.shape

    @property
    def colors(self):
        """set(Puyo): Set of unique puyo enumerations contained in the grid."""
        return set(self._board.flatten())

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
        row_names1 = ["r" + str(i + 1) for i in reversed(range(height - self.nhide))]
        row_names2 = ["h" + str(i + 1) for i in reversed(range(self.nhide))]

        dataframe = DataFrame(board_flipped)
        dataframe.columns = col_names
        dataframe.index = row_names2 + row_names1

        return dataframe.__str__()

    def __sub__(self, other):
        """Return the set of grid elements in self that are different from other."""
        return set([elem for elem in self if elem.puyo is not other[elem.pos]])

    def __eq__(self, other):
        if not self.shape == other.shape:
            return False
        return len(self - other) == 0 and self.nhide == other.nhide

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
        return subscript[0] >= self._board.shape[0] - self.nhide

    def adjacent(self, subscript):
        """Return the set of adjacent elements to the element position."""
        return set([elem for elem in self if Direc.adj_direc(subscript, elem.pos)])

    def apply_color_map(self, cmap):
        new_board = deepcopy(self._board)
        for cbefore, cafter in cmap:
            new_board[self._board == cbefore] = cafter

        self._board = new_board

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


class MoveGrid(AbstractGrid):
    """A grid representing the puyos to be drawn from the drawpile."""

    @classmethod
    def new(cls, shape):
        """Calls super constructor with zero hidden rows."""
        return super().new(shape, nhide=0)

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

        return AbstractGrid(new_board, nhide=0), roff, coff

    def __eq__(self, other):
        for direc in Direc:
            if self.reorient(Direc.NORTH)[0] == other.reorient(direc)[0]:
                return True

        return False


class BoardGrid(AbstractGrid):
    """
    A grid representing the puyos on the game board. Moves may be applied to
    the board grid. A history of moves is recorded and the board may be reverted.
    """

    def __init__(self, shape, nhide):
        super().__init__(shape, nhide)
        self._boardlist = []

    def _col_height(self, idx):
        if all(self._board[:, idx] != Puyo.NONE):
            return self.shape[0]
        else:
            return np.argmin(self._board[:, idx] != Puyo.NONE)

    def pop_set(self, poplimit):
        popset = set()
        for elem in self:
            if not Puyo.is_color(elem.puyo):
                continue

            popgroup = set({elem})
            while True:
                last_popgroup = popgroup.copy()
                for elem in last_popgroup:
                    if not Puyo.is_color(elem.puyo):
                        continue
                    elif self.is_hidden(elem.pos):
                        continue

                    adjelems = self.adjacent(elem.pos)
                    adjelems = {adj for adj in adjelems if not self.is_hidden(adj.pos)}
                    popgroup |= {adj for adj in adjelems if adj.puyo is Puyo.GARBAGE}
                    popgroup |= {adj for adj in adjelems if adj.puyo is elem.puyo}

                if last_popgroup == popgroup:
                    break

            if len({elem for elem in popgroup if Puyo.is_color(elem.puyo)}) >= poplimit:
                popset |= popgroup

        return popset

    def execute_pop(self, poplimit):
        popset = self.pop_set(poplimit)
        for elem in popset:
            self[elem.pos] = Puyo.NONE

        return self.gravitize()

    def apply_move(self, move):
        """Apply the given move to the board and return **self**."""

        # First record the move and the pre-application board.
        self._boardlist.append(self._board.copy())

        def apply_by_column(puyos, leftcol):
            for cidx, puyocol in enumerate(puyos._board.T):
                col_idx = cidx + leftcol
                if col_idx < 0 or col_idx >= self.shape[1]:
                    continue
                puyocol = [puyo for puyo in puyocol if puyo is not Puyo.NONE]
                rstart = self._col_height(col_idx)
                for ridx, puyo in enumerate(puyocol):
                    rend = rstart + ridx
                    if rend < self.shape[0]:
                        self[rend, col_idx] = puyo
                    else:
                        break

        puyos, _, coff = move.grid.reorient(move.direc)
        apply_by_column(puyos, coff + move.col)
        return self

    def revert_move(self):
        """Revert the board by one move and return **self**."""
        self._board = self._boardlist.pop() if self._boardlist else self._board
        return self

    def revert(self):
        """Revert the board to its initial state and return **self**."""
        self._board = self._boardlist[0] if self._boardlist else self._board
        self._boardlist = []
        return self


class HoverGrid(AbstractGrid):
    """
    A grid representing the puyos hovering above the game board, foreshadowing
    a move application to the board grid. A single move may be assigned.
    """

    @classmethod
    def new(cls, board_shape, move_shape):
        """Calls super constructor with zero hidden rows."""
        shape = (2 * max(move_shape) - 1, board_shape[1])
        return super().new(shape, nhide=0)

    def fit_move(self, move):
        """Return the same **Move**, but adjusted horizontally as necessary to fit."""
        grid, _, coffset = move.grid.reorient(move.direc)
        lcol = move.col + coffset
        rcol = move.col + coffset + grid.shape[1] - 1
        new_move = deepcopy(move)
        if lcol < 0:
            new_move.col -= lcol
            return new_move
        elif rcol >= self.shape[1]:
            new_move.col -= rcol - self.shape[1] + 1
            return new_move

        return move

    def assign_move(self, move=None):
        """Displays the given move in the hover area. Return **self**."""
        self.reset()
        if move is None:
            return

        crow = int(self.shape[0] / 2)

        grid, roffset, coffset = move.grid.reorient(move.direc)
        rslice = slice(crow + roffset, crow + roffset + grid.shape[0])
        cslice = slice(move.col + coffset, move.col + coffset + grid.shape[1])
        self[rslice, cslice] = grid._board[:]

        return self


class Move:
    """
    A move is the position and orientation of the puyos about to be dropped.
    Supports equality, including rotationally equivalent moves.
    
    Args:
        shape (int, int): The shape of the grid in its north orientation.
        col (int): The column the bottom-left puyo will be dropped
            in to.
        direc (Direc): The orientation of the puyo grid.
    """

    def __init__(self, shape, col, direc):
        self.grid = MoveGrid.new(shape)
        self.col = col
        self.direc = direc

    def __eq__(self, move):
        grid1, coff1 = self.grid.finalize(self.direc)
        grid2, coff2 = move.grid.finalize(move.direc)
        return (grid1 == grid2) and (coff1 + self.col == coff2 + move.col)

    def __ne__(self, move):
        return not self.__eq__(move)

    @property
    def shape(self):
        return self.grid.shape
