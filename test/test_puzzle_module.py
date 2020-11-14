from models.puzzle_module import PuzzleModule
import unittest
import shutil


class TestPuzzleModule(unittest.TestCase):
    def test_new_module(self):
        name = "test"
        buildup(name)
        PuzzleModule.load(name)
        teardown(name)

    def test_new_puzzle(self):
        name = "test"
        module = buildup(name)
        puzzle = module.new_puzzle()
        print(puzzle)
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
