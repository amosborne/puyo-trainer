from puyolib.puyogridmodel import PuyoBoardModel, PuyoDrawpileElemModel


class PuzzleModel:
    def __init__(self, board_size, board_nhide, drawpile_elem_size):
        self.board = PuyoBoardModel(size=board_size, nhide=board_nhide)
        self.drawpile = []
        self.drawpile_elem_size = drawpile_elem_size

        self.insertDrawpileElem(0)
        self.insertDrawpileElem(0)

    def insertDrawpileElem(self, index):
        self.drawpile.insert(index, PuyoDrawpileElemModel(self.drawpile_elem_size))
