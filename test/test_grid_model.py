from models.grid_model import AbstractGrid, DrawElemGrid, Move
from models.puyo_model import Puyo, Direc
import unittest


class TestAbstractGrid(unittest.TestCase):
    def test_new(self):
        # abstract grid with no hidden rows
        rsize, csize, hsize = (3, 2, 0)
        grid = AbstractGrid.new(shape=(rsize, csize), nhide=hsize)
        self.assertEqual(grid.shape, (3, 2))

        for r in range(rsize + hsize):
            for c in range(csize):
                self.assertEqual(grid[r, c], Puyo.NONE)

        # abstract grid with hidden rows, slice assignment
        rsize, csize, hsize, red_col = (3, 2, 1, 0)
        grid = AbstractGrid.new(shape=(rsize, csize), nhide=hsize)
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
        grid1 = AbstractGrid.new(shape=(rsize, csize), nhide=hsize)
        grid2 = AbstractGrid.new(shape=(rsize, csize), nhide=hsize)
        grid3 = AbstractGrid.new(shape=(rsize, csize), nhide=hsize)
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
        grid = AbstractGrid.new(shape=(rsize, csize), nhide=hsize)
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

    def test_gravitize(self):
        rsize, csize, hsize = (2, 3, 1)
        grid1 = AbstractGrid.new(shape=(rsize, csize), nhide=hsize)
        grid1[1, 0] = Puyo.RED
        grid1[0, 1:] = Puyo.RED
        grid1[2, 2] = Puyo.BLUE

        grid2 = AbstractGrid.new(shape=(rsize, csize), nhide=hsize)
        grid2[0, :] = Puyo.RED
        grid2[1, 2] = Puyo.BLUE
        self.assertTrue(grid1.gravitize(), grid2)

    def test_tighten(self):
        # a single puyo
        loose_grid = AbstractGrid.new(shape=(2, 3), nhide=1)
        loose_grid[1, 1] = Puyo.RED
        tight_grid = AbstractGrid.new(shape=(1, 1), nhide=0)
        tight_grid[0, 0] = Puyo.RED

        actual = AbstractGrid._tighten(loose_grid._board)
        predict = (tight_grid._board, 1, 1)
        self.assertTrue((actual[0] == predict[0]).all())
        self.assertEqual(actual[1:], predict[1:])

        # multiple puyos
        loose_grid = AbstractGrid.new(shape=(2, 3), nhide=1)
        loose_grid[2, 1] = Puyo.RED
        loose_grid[2, 2] = Puyo.BLUE
        tight_grid = AbstractGrid.new(shape=(1, 2), nhide=0)
        tight_grid[0, 0] = Puyo.RED
        tight_grid[0, 1] = Puyo.BLUE

        actual = AbstractGrid._tighten(loose_grid._board)
        predict = (tight_grid._board, 2, 1)
        self.assertTrue((actual[0] == predict[0]).all())
        self.assertEqual(actual[1:], predict[1:])


class TestDrawElemGrid(unittest.TestCase):
    def test_new(self):
        rsize, csize = (2, 2)
        grid1 = DrawElemGrid.new(shape=(rsize, csize))
        grid2 = DrawElemGrid.new(shape=(rsize, csize))

        grid2[0, 0] = Puyo.NONE
        grid2[1, 0] = Puyo.GARBAGE
        grid2[0, 1] = Puyo.GARBAGE
        self.assertTrue(grid1 == grid2)

        grid2[0, :] = Puyo.BLUE
        predict_diff = {((0, 0), Puyo.BLUE), ((0, 1), Puyo.BLUE)}
        self.assertEqual(predict_diff, grid2 - grid1)

        grid2.reset()
        self.assertEqual({((0, 0), Puyo.BLUE)}, grid2 - grid1)

    def test_reorient(self):
        # create a non-typical draw element that bypasses set restrictions
        grid1 = DrawElemGrid.new(shape=(4, 5))
        grid1._board[:] = Puyo.NONE
        grid1[1:3, 1] = [Puyo.RED, Puyo.BLUE]

        grid2 = AbstractGrid.new(shape=(2, 1), nhide=0)
        grid2[:, 0] = [Puyo.RED, Puyo.BLUE]
        predict = (grid2, 1, 1)
        result = grid1.reorient(Direc.NORTH)
        self.assertTrue(result == predict)

        grid2 = AbstractGrid.new(shape=(1, 2), nhide=0)
        grid2[0, :] = [Puyo.RED, Puyo.BLUE]
        predict = (grid2, -1, 1)
        result = grid1.reorient(Direc.EAST)
        self.assertTrue(result == predict)

        grid2 = AbstractGrid.new(shape=(2, 1), nhide=0)
        grid2[:, 0] = [Puyo.BLUE, Puyo.RED]
        predict = (grid2, -2, -1)
        result = grid1.reorient(Direc.SOUTH)
        self.assertTrue(result == predict)

        grid2 = AbstractGrid.new(shape=(1, 2), nhide=0)
        grid2[0, :] = [Puyo.BLUE, Puyo.RED]
        predict = (grid2, 1, -2)
        result = grid1.reorient(Direc.WEST)
        self.assertTrue(result == predict)


# class TestMove(unittest.TestCase):
#     def test_equality(self):
#         return
#         # only gravity
#         grid1 = DrawElemGrid.new(size=(3, 3))
#         grid1[0, 0:2] = Puyo.PURPLE
#         grid1[1, 0] = Puyo.GREEN
#         grid1[2, 1] = Puyo.BLUE
#         move1 = Move(puyos=grid1, col=2, direc=Direc.NORTH)

#         grid2 = DrawElemGrid.new(size=(3, 3))
#         grid2[0, 0:2] = Puyo.PURPLE
#         grid2[1, 0] = Puyo.GREEN
#         grid2[1, 1] = Puyo.BLUE
#         move2 = Move(puyos=grid2, col=2, direc=Direc.NORTH)

#         self.assertTrue(move1 == move2)

#         # with rotation and offset
#         grid2 = DrawElemGrid.new(size=(3, 3))
#         grid2[1, 0:2] = Puyo.PURPLE
#         grid2[0, 1] = Puyo.GREEN
#         grid2[0, 0] = Puyo.BLUE
#         move2 = Move(puyos=grid2, col=3, direc=Direc.SOUTH)

#         self.assertTrue(move1 == move2)
