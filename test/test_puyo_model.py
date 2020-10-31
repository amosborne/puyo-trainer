from models.puyo_model import Puyo, Direc
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
        def iscolor(puyo):
            return puyo is not Puyo.NONE and puyo is not Puyo.GARBAGE

        self.assertEqual(Puyo.RED, Puyo.PURPLE.next_(cond=iscolor))
        self.assertEqual(Puyo.GREEN, Puyo.PURPLE.next_(cond=iscolor, k=2))
        self.assertEqual(Puyo.BLUE, Puyo.PURPLE.next_(cond=iscolor, k=-2))

    def test_direc_enum(self):
        # enum ordering and wrap-around
        self.assertEqual(Direc.NORTH.rotate_cw(), Direc.EAST)
        self.assertEqual(Direc.EAST.rotate_cw(), Direc.SOUTH)
        self.assertEqual(Direc.SOUTH.rotate_cw(), Direc.WEST)
        self.assertEqual(Direc.WEST.rotate_cw(), Direc.NORTH)
        self.assertEqual(Direc.NORTH.rotate_ccw(), Direc.WEST)
