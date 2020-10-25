from puyolib.puyogridmodel import PuyoBoardModel, PuyoDrawpileElemModel


class PuzzleModel:
    def __init__(self, board_size, board_nhide, drawpile_elem_size):
        self.board = PuyoBoardModel(size=board_size, nhide=board_nhide)
        self.drawpile = [PuyoDrawpileElemModel(drawpile_elem_size) for _ in range(2)]
