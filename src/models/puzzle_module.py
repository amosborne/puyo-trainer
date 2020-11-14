from models.puyo_model import Puyo
from models.puzzle_model import Puzzle
from copy import deepcopy
import os
import yaml

MODULE_ROOT = "./modules/"
METADATA_FILE = "/metadata.yml"


class PuzzleModule:
    """
    A puzzle module collectively manages a set of individual puyo puzzles.
    Every puzzle within a module must adhere to the same set of rules. These
    rules are used to determine if puzzle files are compliant when loaded and
    also define corrective actions when being edited within the GUI.

    The following rules are applied to each individual puzzle:

    - The initial board and hidden rows shall be of the specified shape.
    - The initial board shall not contain floating puyos or pop groups.
    - The initial board and all moves shall not collectively exceed the
      specified color limit.
    - Each move shall be of the specified shape.
    - Each move shall have a minimum non-empty shape of (2, 1).
    - Each move shall not contain any garbage.
    - Each move shall fit the board horizontally.
    - A puzzle shall have atleast one move.
    """

    @staticmethod
    def new(
        modulename,
        board_shape,
        board_nhide,
        move_shape,
        color_limit,
        pop_limit,
        modulereadme,
    ):
        """
        Args:
            modulename (str): Must be unique.
            board_shape (int, int): Within (12, 6) and (26, 16).
            board_nhide (int): Within 1 and 2.
            move_shape (int, int): Within (2, 1) and (2, 2).
            color_limit (int): Within 3 and 5.
            pop_limit (int): Within 2 and 6.
            modulereadme (str): Documentation.
        """

        # Assign metadata attributes.
        module = PuzzleModule()
        module.board_shape = board_shape
        module.board_nhide = board_nhide
        module.move_shape = move_shape
        module.color_limit = color_limit
        module.pop_limit = pop_limit
        module.modulereadme = modulereadme

        module._validate_metadata()

        # Write the metadata file.
        assert not os.path.isdir(MODULE_ROOT + modulename)
        os.mkdir(MODULE_ROOT + modulename)
        with open(MODULE_ROOT + modulename + METADATA_FILE, "w") as outfile:
            yaml.dump(module, outfile)

        module._specify_rules()
        module.puzzles = []

        return module

    @staticmethod
    def load(modulename):
        """
        Args:
            modulename (str): Must be on file (with metadata).
        """

        # Load metadata attributes.
        with open(MODULE_ROOT + modulename + METADATA_FILE, "r") as infile:
            module = yaml.load(infile, Loader=yaml.Loader)
            module._validate_metadata()
            module._specify_rules()

        # TODO: load all puzzles in module, check all rules and compatability

        return module

    def new_puzzle(self, puzzle_copy=None):
        if puzzle_copy is not None:
            return deepcopy(puzzle_copy)
        else:
            return Puzzle.new(self)

    def save_puzzle(self, puzzle):
        # TODO: check compatability
        self.puzzles.append(puzzle)

    def _validate_metadata(self):
        def between(x, xmin, xmax):
            return xmin <= x <= xmax

        assert between(self.board_shape[0], 12, 26)  # board height
        assert between(self.board_shape[1], 6, 16)  # board width
        assert between(self.board_nhide, 1, 2)  # hidden rows
        assert between(self.move_shape[0], 2, 2)  # move height
        assert between(self.move_shape[1], 1, 2)  # move width
        assert between(self.color_limit, 3, 5)  # colors
        assert between(self.pop_limit, 2, 6)  # pops

    def _specify_rules(self):
        """
        Rules are a list of functions with the signature rule(puzzle, force).
        If force is True, then the rule will may take corrective action.
        The return value is whether the puzzle is compliant upon function return.
        """
        rules = []
        rules.append(self._rule_board_shape)
        rules.append(self._rule_move_shape)
        rules.append(self._rule_move_quantity)  # has force
        rules.append(self._rule_move_minsize_nogarbage)  # has force
        rules.append(self._rule_color_count)
        # TODO: add rule no floating puyos or pop groups (no correction)
        self.rules = rules

    def _rule_board_shape(self, puzzle, force):  # no force action
        visr, visc = self.board_shape
        shape = (visr + puzzle.board.nhide, visc) == puzzle.board.shape
        nhide = self.board_nhide == puzzle.board.nhide
        return shape and nhide

    def _rule_move_shape(self, puzzle, force):  # no force action
        return all([self.move_shape == move.shape for move in puzzle.moves])

    def _rule_move_quantity(self, puzzle, force):
        if not puzzle.moves and not force:
            return False
        elif not puzzle.moves:
            puzzle.new_move()
            puzzle.apply_rules(force=True)

        return True

    def _rule_floaters_or_poppers(self, puzzle, force):  # no force action
        pass

    def _rule_color_count(self, puzzle, force):  # no force action
        colors = puzzle.board.colors
        for move in puzzle.moves:
            colors |= move.grid.colors
        colors -= {Puyo.NONE, Puyo.GARBAGE}
        return len(colors) <= self.color_limit

    def _rule_move_fit(self, puzzle, force):
        pass

    @staticmethod
    def _rule_move_minsize_nogarbage(puzzle, force):
        mv_elems = [(mv.grid, elem) for mv in puzzle.moves for elem in mv.grid]

        for grid, elem in mv_elems:

            # no garbage rule
            if elem.puyo is Puyo.GARBAGE:
                if not force:
                    return False
                else:
                    puyo = elem.puyo.next_(cond=lambda p: p is not Puyo.GARBAGE)
                    grid[elem.pos] = puyo

            # minimum size rule
            if elem.pos in {(0, 0), (1, 0)} and not elem.puyo.is_color():
                if not force:
                    return False
                else:
                    puyo = elem.puyo.next_(cond=lambda p: p.is_color())
                    grid[elem.pos] = puyo

        return True
