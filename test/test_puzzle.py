from models import PuzzleModule, Puzzle, Puyo, Direc
import unittest
import shutil


def buildup_teardown():
    def buildup_teardown_decorator(func):
        def buildup_teardown_wrapper(*args, **kwargs):
            name = "unittest"
            module = PuzzleModule.new(
                modulename=name,
                board_shape=(12, 6),
                board_nhide=1,
                move_shape=(2, 1),
                color_limit=4,
                pop_limit=4,
                modulereadme="",
            )
            puzzle = Puzzle.new(module)
            func(*args, module, puzzle, **kwargs)
            shutil.rmtree("./modules/" + name + "/")

        return buildup_teardown_wrapper

    return buildup_teardown_decorator


class TestPuzzleModuleRules(unittest.TestCase):
    @buildup_teardown()
    def test_rule_atleast_one_move(self, module, puzzle):
        puzzle.moves = []
        self.assertFalse(module._rule_atleast_one_move(puzzle, force=False))
        self.assertTrue(module._rule_atleast_one_move(puzzle, force=True))
        self.assertTrue(module._rule_atleast_one_move(puzzle, force=False))

    @buildup_teardown()
    def test_rule_move_lacks_garbage(self, module, puzzle):
        puzzle.moves[0].grid[:] = Puyo.GARBAGE
        self.assertFalse(module._rule_move_lacks_garbage(puzzle, force=False))
        self.assertTrue(module._rule_move_lacks_garbage(puzzle, force=True))
        self.assertTrue(module._rule_move_lacks_garbage(puzzle, force=False))

    @buildup_teardown()
    def test_rule_minimum_move_size(self, module, puzzle):
        puzzle.moves[0].grid[:] = Puyo.NONE
        self.assertFalse(module._rule_minimum_move_size(puzzle, force=False))
        self.assertTrue(module._rule_minimum_move_size(puzzle, force=True))
        self.assertTrue(module._rule_minimum_move_size(puzzle, force=False))

    @buildup_teardown()
    def test_rule_color_limit(self, module, puzzle):
        puzzle.board[0, 1] = Puyo.GARBAGE
        puzzle.board[0, 0] = Puyo.GREEN
        puzzle.board[1, 0] = Puyo.BLUE
        puzzle.board[2, 0] = Puyo.YELLOW

        puzzle.moves[0].grid[0, 0] = Puyo.PURPLE
        self.assertFalse(module._rule_color_limit(puzzle, force=False))

        puzzle.moves[0].grid[0, 0] = Puyo.NONE
        self.assertTrue(module._rule_color_limit(puzzle, force=False))

    @buildup_teardown()
    def test_rule_move_fits_horizontally(self, module, puzzle):
        puzzle.moves[0].col = 6
        puzzle.moves[0].direc = Direc.EAST
        self.assertFalse(module._rule_move_fits_horizontally(puzzle, force=False))
        self.assertTrue(module._rule_move_fits_horizontally(puzzle, force=True))
        self.assertTrue(module._rule_move_fits_horizontally(puzzle, force=False))
