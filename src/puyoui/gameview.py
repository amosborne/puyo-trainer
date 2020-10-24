from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from puyoui.puyoview import PuyoGridView
from puyolib.puyomodel import move2hovergrid


class GameplayView(QWidget):
    def __init__(self, graphicsmodel, board, nhide, drawpile, npreview, parent=None):
        super().__init__(parent)

        board_view = PuyoGridView(graphicsmodel, board, nhide, isframed=True)
        hover_area = PuyoGridView(
            graphicsmodel,
            board=move2hovergrid(size=(max(drawpile[0].shape), board.shape[1])),
            nhide=0,
            isframed=False,
        )

        layout = QVBoxLayout(self)
        layout.addWidget(hover_area)
        layout.addWidget(board_view)
