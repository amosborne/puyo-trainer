from models.grid_model import BoardGrid, HoverGrid, Move
from models.puyo_model import Direc


class Puzzle:
    @staticmethod
    def new(module):
        puzzle = Puzzle()
        puzzle.board = BoardGrid.new(shape=module.board_shape, nhide=module.board_nhide)
        puzzle.moves = []
        puzzle.hover = HoverGrid.new(module.board_shape, module.move_shape)
        puzzle.module = module

        puzzle.apply_rules(force=True)

        return puzzle

    @staticmethod
    def load(puzzlename, rules):
        pass

    def apply_rules(self, force=False):
        return all([rule(self, force) for rule in self.module.rules])

    def new_move(self, index=0):
        new_move = Move(shape=self.module.move_shape, col=2, direc=Direc.NORTH)
        self.moves.insert(index, new_move)
        self.apply_rules(force=True)

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
