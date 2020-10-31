from models.grid_model import AbstractPuyoGridModel
from models.puyo_model import Puyo
import unittest


class TestAbstractPuyoGridModel(unittest.TestCase):
    def test_construct_setslice(self):
        return

        # Abstract puyo grid with no hidden rows.
        rsize, csize, hsize = (3, 2, 0)
        grid = AbstractPuyoGridModel(size=(rsize, csize), nhide=hsize)
        for r in range(rsize + hsize):
            for c in range(csize):
                self.assertEqual(grid[r, c], Puyo.NONE)

        # Abstract puyo grid with hidden rows.
        rsize, csize, hsize = (3, 2, 1)
        grid = AbstractPuyoGridModel(size=(rsize, csize), nhide=hsize)
        for r in range(rsize + hsize):
            for c in range(csize):
                self.assertEqual(grid[r, c], Puyo.NONE)

        # Abstract puyo grid with slice assignment.
        rsize, csize, hsize = (3, 2, 1)
        red_col = 0
        grid = AbstractPuyoGridModel(size=(rsize, csize), nhide=hsize)
        grid[:, red_col] = Puyo.RED
        for r in range(rsize + hsize):
            for c in range(csize):
                if c == red_col:
                    self.assertEqual(grid[r, c], Puyo.RED)
                else:
                    self.assertEqual(grid[r, c], Puyo.NONE)

    def test_getslice_equality(self):
        rsize, csize, hsize = (4, 4, 4)
        grid = AbstractPuyoGridModel(size=(rsize, csize), nhide=hsize)
        # print("/n")
        # print(grid)
        # print(grid[2:6, 2:6])
