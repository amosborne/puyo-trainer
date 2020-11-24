from models.puyo import Puyo
from models.puzzle import Puzzle
from copy import deepcopy
import os
import yaml

from constants import (
    MODULE_DIRECTORY,
    MODULE_PARAMETERS,
    METADATA_FILE,
    PUZZLE_FILE_EXT,
    PUZZLE_FILE_ROOT,
)


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

    def __init__(
        self,
        board_shape,
        board_nhide,
        move_shape,
        color_limit,
        pop_limit,
        modulereadme,
    ):
        self.board_shape = board_shape
        self.board_nhide = board_nhide
        self.move_shape = move_shape
        self.color_limit = color_limit
        self.pop_limit = pop_limit
        self.modulereadme = modulereadme

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
        module = PuzzleModule(
            board_shape, board_nhide, move_shape, color_limit, pop_limit, modulereadme
        )

        # Write the metadata file.
        os.mkdir(MODULE_DIRECTORY + modulename)
        with open(MODULE_DIRECTORY + modulename + METADATA_FILE, "w") as outfile:
            yaml.dump(module._toyaml(), outfile)

        module._specify_rules()
        module.puzzles = {}

        return module

    @staticmethod
    def load(modulename):
        """
        Args:
            modulename (str): Must be on file (with metadata).
        """

        # Load metadata attributes.
        with open(MODULE_DIRECTORY + modulename + METADATA_FILE, "r") as infile:
            safe_data = yaml.safe_load(infile)
            kwargs = PuzzleModule._fromyaml(safe_data)
            module = PuzzleModule(**kwargs)
            module._validate_metadata()
            module._specify_rules()

        module.puzzles = {}
        _, _, filenames = next(os.walk(MODULE_DIRECTORY + modulename))
        for filename in filenames:
            if not filename.startswith(PUZZLE_FILE_ROOT):
                continue
            elif not filename.endswith(PUZZLE_FILE_EXT):
                continue

            puzzle = Puzzle.load(filename, modulename, module)
            module.puzzles[filename] = puzzle

        return module

    def _validate_metadata(self):
        assert self.board_shape[0] in MODULE_PARAMETERS["board_shape"][0]
        assert self.board_shape[1] in MODULE_PARAMETERS["board_shape"][1]
        assert self.board_nhide in MODULE_PARAMETERS["board_nhide"]
        assert self.move_shape[0] in MODULE_PARAMETERS["move_shape"][0]
        assert self.move_shape[1] in MODULE_PARAMETERS["move_shape"][1]
        assert self.color_limit in MODULE_PARAMETERS["color_limit"]
        assert self.pop_limit in MODULE_PARAMETERS["pop_limit"]

    def _specify_rules(self):
        """
        Each rule has the signature rule(puzzle, force). If force is True,
        then the rule may take corrective action. Each rule returns whether
        the puzzle is compliant to the rule.
        """
        rules = []
        rules.append(self._rule_metadata_matches_board_shape)
        rules.append(self._rule_metadata_matches_move_shape)
        rules.append(self._rule_atleast_one_move)  # has force
        rules.append(self._rule_move_lacks_garbage)  # has force
        rules.append(self._rule_minimum_move_size)  # has force
        rules.append(self._rule_color_limit)
        rules.append(self._rule_move_fits_horizontally)  # has force
        # TODO: Add rule -- no floating puyos (no corrective action)
        # TODO: Add rule -- no pop groups (no corrective action)
        self.rules = rules

    def _rule_metadata_matches_board_shape(self, puzzle, force):
        visr, visc = self.board_shape
        shape = (visr + puzzle.board.nhide, visc) == puzzle.board.shape
        nhide = self.board_nhide == puzzle.board.nhide
        return shape and nhide

    def _rule_metadata_matches_move_shape(self, puzzle, force):
        return all([self.move_shape == move.shape for move in puzzle.moves])

    def _rule_atleast_one_move(self, puzzle, force):
        if not puzzle.moves and not force:
            return False
        elif not puzzle.moves:
            puzzle.new_move()
            puzzle.apply_rules(force=True)

        return True

    def _rule_move_lacks_garbage(self, puzzle, force):
        for move in puzzle.moves:
            for elem in move.grid:
                if elem.puyo is Puyo.GARBAGE and not force:
                    return False
                elif elem.puyo is Puyo.GARBAGE:
                    puyo = elem.puyo.next_(cond=Puyo.isnot_garbage)
                    move.grid[elem.pos] = puyo

        return True

    def _rule_minimum_move_size(self, puzzle, force):
        required = {(0, 0), (1, 0)}
        for move in puzzle.moves:
            for elem in move.grid:
                violates = elem.pos in required and not Puyo.is_color(elem.puyo)
                if violates and not force:
                    return False
                elif violates:
                    puyo = elem.puyo.next_(cond=Puyo.is_color)
                    move.grid[elem.pos] = puyo

        return True

    def _rule_color_limit(self, puzzle, force):
        colors = set.union(*tuple([move.grid.colors for move in puzzle.moves]))
        colors |= puzzle.board.colors
        colors -= {Puyo.NONE, Puyo.GARBAGE}
        return len(colors) <= self.color_limit

    def _rule_move_fits_horizontally(self, puzzle, force):
        for idx, move in enumerate(puzzle.moves):
            new_move = puzzle.hover.fit_move(move)
            if not new_move == move and not force:
                return False
            elif not new_move == move:
                puzzle.moves[idx] = new_move

        return True

    def _toyaml(self):
        dump = self.__dict__
        for (k, v) in dump.items():
            if isinstance(v, tuple):
                dump[k] = list(v)
        return dump

    @staticmethod
    def _fromyaml(load):
        for (k, v) in load.items():
            if isinstance(v, list):
                load[k] = tuple(v)
        return load
