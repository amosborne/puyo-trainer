from models.grid_model import AbstractGrid, DrawElemGrid
from models.puyo_model import Puyo
import unittest


class TestAbstractGrid(unittest.TestCase):
    def test_new(self):
        # abstract grid with no hidden rows
        rsize, csize, hsize = (3, 2, 0)
        grid = AbstractGrid.new(size=(rsize, csize), nhide=hsize)
        self.assertEqual(grid.shape, (3, 2))

        for r in range(rsize + hsize):
            for c in range(csize):
                self.assertEqual(grid[r, c], Puyo.NONE)

        # abstract grid with hidden rows, slice assignment
        rsize, csize, hsize, red_col = (3, 2, 1, 0)
        grid = AbstractGrid.new(size=(rsize, csize), nhide=hsize)
        self.assertEqual(grid.shape, (4, 2))

        for r in range(rsize + hsize):
            for c in range(csize):
                self.assertEqual(grid[r, c], Puyo.NONE)

        grid[:, red_col] = Puyo.RED
        for r in range(rsize + hsize):
            for c in range(csize):
                if c == red_col:
                    self.assertEqual(grid[r, c], Puyo.RED)
                else:
                    self.assertEqual(grid[r, c], Puyo.NONE)

        self.assertFalse(grid.is_hidden((0, 0)))
        self.assertFalse(grid.is_hidden((2, 0)))
        self.assertTrue(grid.is_hidden((3, 0)))

    def test_equality(self):
        # construct three identical grids and alter the first two
        rsize, csize, hsize = (2, 2, 0)
        grid1 = AbstractGrid.new(size=(rsize, csize), nhide=hsize)
        grid2 = AbstractGrid.new(size=(rsize, csize), nhide=hsize)
        grid3 = AbstractGrid.new(size=(rsize, csize), nhide=hsize)
        grid1[0, 0] = Puyo.RED
        grid2[0, 0] = Puyo.RED
        grid3[0, 0] = Puyo.GREEN

        # assess difference, equality, and reset
        self.assertEqual(grid1 - grid3, {((0, 0), Puyo.RED)})
        self.assertEqual(grid3 - grid1, {((0, 0), Puyo.GREEN)})
        self.assertTrue(grid1 == grid2)
        self.assertFalse(grid1 == grid3)
        self.assertTrue(grid1.reset() == grid3.reset())

    def test_adjacent(self):
        rsize, csize, hsize = (2, 3, 1)
        grid = AbstractGrid.new(size=(rsize, csize), nhide=hsize)
        grid[1, 0] = Puyo.RED
        grid[0, 1] = Puyo.GREEN

        predict_adj = {
            ((1, 0), Puyo.RED),
            ((0, 1), Puyo.GREEN),
            ((2, 1), Puyo.NONE),
            ((1, 2), Puyo.NONE),
        }
        self.assertEqual(predict_adj, grid.adjacent((1, 1)))

        predict_adj = {((1, 0), Puyo.RED), ((0, 1), Puyo.GREEN)}
        self.assertEqual(predict_adj, grid.adjacent((0, 0)))


class TestDrawElemGrid(unittest.TestCase):
    def test_new(self):
        rsize, csize = (2, 2)
        grid1 = DrawElemGrid.new(size=(rsize, csize))
        grid2 = DrawElemGrid.new(size=(rsize, csize))

        grid2[0, 0] = Puyo.NONE
        grid2[1, 0] = Puyo.GARBAGE
        grid2[0, 1] = Puyo.GARBAGE
        self.assertTrue(grid1 == grid2)

        grid2[0, :] = Puyo.BLUE
        predict_diff = {((0, 0), Puyo.BLUE), ((0, 1), Puyo.BLUE)}
        self.assertEqual(predict_diff, grid2 - grid1)

        grid2.reset()
        self.assertEqual({((0, 0), Puyo.BLUE)}, grid2 - grid1)
