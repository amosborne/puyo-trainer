from models.grid import BoardGrid, HoverGrid, Move
from models.puyo import Direc, Puyo
from constants import PUZZLE_FILE_ROOT, PUZZLE_FILE_EXT, MODULE_DIRECTORY
import os
import yaml
from copy import deepcopy
import numpy as np


class Puzzle:
    @staticmethod
    def new(module, path):
        puzzle = Puzzle()
        puzzle.board = BoardGrid.new(shape=module.board_shape, nhide=module.board_nhide)
        puzzle.moves = []
        puzzle.hover = HoverGrid.new(module.board_shape, module.move_shape)
        puzzle.module = module
        puzzle.path = MODULE_DIRECTORY + path

        puzzle.apply_rules(force=True)

        return puzzle

    @staticmethod
    def load(puzzlename, path, module):
        def yaml2board(yml):
            board = BoardGrid.new(shape=module.board_shape, nhide=module.board_nhide)
            str_board = list(reversed([s.split(" ") for s in yml]))
            for (row, col), puyo_str in np.ndenumerate(str_board):
                board[row, col] = Puyo[puyo_str]

            return board

        def yaml2move(yml):
            move = Move(
                shape=module.move_shape, col=yml["col"], direc=Direc[yml["direc"]]
            )
            str_grid = list(reversed([s.split(" ") for s in yml["grid"]]))
            for (row, col), puyo_str in np.ndenumerate(str_grid):
                move.grid[row, col] = Puyo[puyo_str]
            return move

        with open(MODULE_DIRECTORY + path + "/" + puzzlename, "r") as infile:
            safe_data = yaml.safe_load(infile)

        puzzle = Puzzle()
        puzzle.board = yaml2board(safe_data["board"])
        puzzle.moves = [yaml2move(move) for move in safe_data["moves"]]
        puzzle.module = module
        puzzle.hover = HoverGrid.new(module.board_shape, module.move_shape)
        puzzle.path = MODULE_DIRECTORY + path

        return puzzle

    def save(self):
        def grid2list(grid):
            grid = grid._board.tolist()
            grid = [" ".join([puyo.name for puyo in row]) for row in grid]
            return list(reversed(grid))

        puzzle_to_save = deepcopy(self)
        puzzle_to_save.board.revert()

        filename = next_puzzle_name(puzzle_to_save.path)
        filepath = puzzle_to_save.path + "/" + filename

        data = dict()
        data["board"] = grid2list(puzzle_to_save.board)
        data["moves"] = [
            {"grid": grid2list(move.grid), "col": move.col, "direc": move.direc.name}
            for move in puzzle_to_save.moves
        ]

        with open(filepath, "w") as outfile:
            yaml.dump(data, outfile)

        self.module.puzzles[filename] = puzzle_to_save

    def apply_rules(self, force=False):
        return all([rule(self, force) for rule in self.module.rules])

    def new_move(self, index=0):
        new_move = Move(shape=self.module.move_shape, col=2, direc=Direc.NORTH)
        self.moves.insert(index, new_move)
        return new_move

    def __str__(self):
        def sdivider(slen, score):
            score = " " + score + " "
            scorelen = len(score)
            ldash = "-" * int((slen - scorelen) / 2)
            rdash = "-" * (slen - len(ldash) - scorelen)
            return "\n" + ldash + score + rdash + "\n"

        bstring = self.board.__str__()
        slen = bstring.find("\n")
        pstring = sdivider(slen, "BOARD") + bstring

        for idx, move in enumerate(self.moves):
            pstring += sdivider(slen, "MOVE " + str(idx))
            pstring += self.hover.assign_move(move).__str__()

        return pstring


def next_puzzle_name(path):
    def ind2name(idx):
        return PUZZLE_FILE_ROOT + str(idx + 1) + PUZZLE_FILE_EXT

    _, _, filenames = next(os.walk(path))
    idx = 0
    while ind2name(idx) in filenames:
        idx += 1

    return ind2name(idx)
