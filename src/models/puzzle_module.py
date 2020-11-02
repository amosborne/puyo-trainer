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
    - Each move shall have a minimum non-empty shape of (2,1).
    - Each move shall not contain any garbage.
    - Each move shall fit the board horizontally.
    """

    rules = []

    @staticmethod
    def new(
        modulename,
        board_shape,
        board_nhide,
        drawelem_shape,
        color_limit,
        pop_limit,
        modulereadme,
    ):
        """
        Args:
            modulename (str): Must be unique.
            board_shape (int, int): Within (12,6) and (26,16).
            board_nhide (int): Within 1 and 2.
            drawelem_shape (int, int): Within (2,1) and (2,2).
            color_limit (int): Within 3 and 5.
            pop_limit (int): Within 2 and 6.
            modulereadme (str): Documentation.
        """

        # Validate function arguments.
        assert (12 <= board_shape[0] <= 26) and (6 <= board_shape[1] <= 16)
        assert 1 <= board_nhide <= 2
        assert (2 == drawelem_shape[0]) and (1 <= drawelem_shape[1] <= 2)
        assert 3 <= color_limit <= 5
        assert 2 <= pop_limit <= 6
        assert not os.path.isdir(MODULE_ROOT + modulename)

        # Assign attributes and return.
        module = PuzzleModule()
        module.board_shape = board_shape
        module.board_nhide = board_nhide
        module.drawelem_shape = drawelem_shape
        module.color_limit = color_limit
        module.pop_limit = pop_limit

        # Write the metadata file.
        os.mkdir(MODULE_ROOT + modulename)
        with open(MODULE_ROOT + modulename + METADATA_FILE, "w") as outfile:
            yaml.dump(module, outfile)

        return module

    @staticmethod
    def load(modulename):
        """
        Args:
            modulename (str): Must be on file (with metadata).
        """

        with open(MODULE_ROOT + modulename + METADATA_FILE, "r") as infile:
            module = yaml.load(infile, Loader=yaml.Loader)

        return module
