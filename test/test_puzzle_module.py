from models.puzzle_module import PuzzleModule
from models.puyo_model import Puyo
import unittest
import shutil


class TestPuzzleModule(unittest.TestCase):
    def test_new_module(self):
        name = "test"
        buildup(name)
        PuzzleModule.load(name)
        teardown(name)

    def test_puzzle_color_limit(self):
        name = "test"
        module = buildup(name)
        puzzle = module.new_puzzle()

        # test color limit
        puzzle.board[1, 0] = Puyo.GARBAGE
        puzzle.board[0, 0] = Puyo.GREEN
        puzzle.board[1, 0] = Puyo.BLUE
        puzzle.board[2, 0] = Puyo.YELLOW
        puzzle.moves[0].grid[0, 0] = Puyo.PURPLE
        self.assertFalse(puzzle.apply_rules())
        puzzle.moves[0].grid[0, 0] = Puyo.RED
        print(puzzle)
        self.assertTrue(puzzle.apply_rules())

        teardown(name)


def buildup(name):  # a standard puzzle module
    return PuzzleModule.new(
        modulename=name,
        board_shape=(12, 6),
        board_nhide=1,
        move_shape=(2, 1),
        color_limit=4,
        pop_limit=4,
        modulereadme="",
    )


def teardown(name):
    shutil.rmtree("./modules/" + name + "/")
