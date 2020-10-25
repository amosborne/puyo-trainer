from puyolib.puyogridmodel import PuyoBoardModel, PuyoDrawpileElemModel


class PuzzleModel:
    def __init__(self, board_size, board_nhide, drawpile_elem_size):
        self.board = PuyoBoardModel(size=board_size, nhide=board_nhide)
        self.drawpile = []
        self.drawpile_elem_size = drawpile_elem_size

    def newDrawpileElem(self, index=0):
        elem = PuyoDrawpileElemModel(self.drawpile_elem_size)
        self.drawpile.insert(index, elem)
        return elem
