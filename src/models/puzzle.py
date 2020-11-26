from models.grid import BoardGrid, HoverGrid, Move
from models.puyo import Direc, Puyo
from constants import PUZZLE_FILE_ROOT, PUZZLE_FILE_EXT, MODULE_DIRECTORY
import os
import yaml
from copy import deepcopy
import numpy as np
import random


class Puzzle:
    @staticmethod
    def new(module, path):
        puzzle = Puzzle()
        puzzle.board = BoardGrid.new(shape=module.board_shape, nhide=module.board_nhide)
        puzzle.moves = []
        puzzle.hover = HoverGrid.new(module.board_shape, module.move_shape)
        puzzle.module = module
        puzzle.path = path

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
        puzzle.path = path

        return puzzle

    def save(self):
        def grid2list(grid):
            grid = grid._board.tolist()
            grid = [" ".join([puyo.name for puyo in row]) for row in grid]
            return list(reversed(grid))

        puzzle_to_save = deepcopy(self)
        puzzle_to_save.board.revert()

        filename = next_puzzle_name(MODULE_DIRECTORY + puzzle_to_save.path)
        filepath = MODULE_DIRECTORY + puzzle_to_save.path + "/" + filename

        data = dict()
        data["board"] = grid2list(puzzle_to_save.board)
        data["moves"] = [
            {"grid": grid2list(move.grid), "col": move.col, "direc": move.direc.name}
            for move in puzzle_to_save.moves
        ]

        with open(filepath, "w") as outfile:
            yaml.dump(data, outfile)

        self.module.puzzles[filename.rstrip(PUZZLE_FILE_EXT)] = puzzle_to_save

    def apply_rules(self, force=False):
        return all([rule(self, force) for rule in self.module.rules])

    def new_move(self, index=0):
        new_move = Move(shape=self.module.move_shape, col=2, direc=Direc.NORTH)
        self.moves.insert(index, new_move)
        return new_move

    def randomize_color(self):
        cmap = random.sample(Puyo.color_maps(), 1)[0]
        self.apply_color_map(cmap)

    def apply_color_map(self, cmap):
        self.board.apply_color_map(cmap)
        for move in self.moves:
            move.grid.apply_color_map(cmap)

    @staticmethod
    def compatible_over_colors(x):
        this, thisname, other, othername = x
        cmaps = Puyo.color_maps()
        for this_cmap in cmaps:
            this_puzzle = deepcopy(this)
            this_puzzle.apply_color_map(this_cmap)

            for that_cmap in cmaps:
                that_puzzle = deepcopy(other)
                that_puzzle.apply_color_map(that_cmap)

                if not this_puzzle.compatible(that_puzzle):
                    return (False, thisname, othername)

        return (True, thisname, othername)

    def compatible(self, other):
        def compare_moves(puz1, puz2, n):
            try:
                move1 = puz1.moves[n]
            except IndexError:
                return True
            try:
                move2 = puz2.moves[n]
            except IndexError:
                return True

            return move1.grid == move2.grid

        while True:
            other_copy = deepcopy(other)
            while True:
                if self.board == other_copy.board:
                    move_match = compare_moves(self, other_copy, 0)
                    move_match &= compare_moves(self, other_copy, 1)
                    move_match &= compare_moves(self, other_copy, 2)

                    if move_match:
                        this_move = self.moves[0]
                        that_move = other_copy.moves[0]
                        if not this_move == that_move:
                            return False

                if len(other_copy.moves) == 1:
                    break
                else:
                    other_copy.board.apply_move(other_copy.moves.pop(0))

            if len(self.moves) == 1:
                break
            else:
                self.board.apply_move(self.moves.pop(0))

        return True

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
