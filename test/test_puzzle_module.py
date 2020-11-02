from models.puzzle_module import PuzzleModule
import unittest


class TestPuzzleModule(unittest.TestCase):
    def test_new(self):
        # module_in = PuzzleModule.new(
        #     modulename="test_module",
        #     board_shape=(12, 6),
        #     board_nhide=1,
        #     drawelem_shape=(2, 1),
        #     color_limit=4,
        #     pop_limit=4,
        #     modulereadme="",
        # )

        module = PuzzleModule.load("test_module")
        print(module)
