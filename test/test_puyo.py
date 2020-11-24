from models import Puyo, Direc
import unittest


class TestEnums(unittest.TestCase):
    def test_puyo_enum(self):
        # first enum wrap-around
        self.assertEqual(Puyo.YELLOW, Puyo.NONE.next_(k=-3))
        self.assertEqual(Puyo.RED, Puyo.NONE.next_())
        self.assertEqual(Puyo.BLUE, Puyo.NONE.next_(k=3))

        # last enum wrap-around
        self.assertEqual(Puyo.YELLOW, Puyo.GARBAGE.next_(k=-2))
        self.assertEqual(Puyo.NONE, Puyo.GARBAGE.next_())
        self.assertEqual(Puyo.RED, Puyo.GARBAGE.next_(k=2))

        # conditional functions
        self.assertEqual(Puyo.RED, Puyo.PURPLE.next_(cond=Puyo.is_color))
        self.assertEqual(Puyo.GREEN, Puyo.PURPLE.next_(cond=Puyo.is_color, k=2))
        self.assertEqual(Puyo.BLUE, Puyo.PURPLE.next_(cond=Puyo.is_color, k=-2))

    def test_direc_enum(self):
        # enum ordering and wrap-around
        self.assertEqual(Direc.rotate_cw(Direc.NORTH), Direc.EAST)
        self.assertEqual(Direc.rotate_cw(Direc.EAST), Direc.SOUTH)
        self.assertEqual(Direc.rotate_cw(Direc.SOUTH), Direc.WEST)
        self.assertEqual(Direc.rotate_cw(Direc.WEST), Direc.NORTH)
        self.assertEqual(Direc.rotate_ccw(Direc.NORTH), Direc.WEST)

        # adjacent direction
        self.assertEqual(Direc.NORTH, Direc.adj_direc((1, 1), (2, 1)))
        self.assertEqual(Direc.EAST, Direc.adj_direc((1, 1), (1, 2)))
        self.assertEqual(Direc.SOUTH, Direc.adj_direc((1, 1), (0, 1)))
        self.assertEqual(Direc.WEST, Direc.adj_direc((1, 1), (1, 0)))
        self.assertEqual(None, Direc.adj_direc((1, 1), (2, 2)))
