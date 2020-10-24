from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from puyoui.puyoview import PuyoGridView
from puyolib.puyomodel import move2hovergrid, Puyo


class GameplayView(QWidget):
    def __init__(self, graphicsmodel, board, nhide, drawpile, parent=None):
        super().__init__(parent)

        self.board_view = PuyoGridView(graphicsmodel, board, nhide, isframed=True)
        self.hover_area = PuyoGridView(
            graphicsmodel,
            board=move2hovergrid(size=(max(drawpile[0].shape), board.shape[1])),
            nhide=0,
            isframed=False,
        )

        leftlayout = QVBoxLayout()
        leftlayout.addWidget(self.hover_area)
        leftlayout.addWidget(self.board_view)

        rightlayout = QVBoxLayout()
        for idx in range(2):  # hardcoded two previews
            rightlayout.addWidget(
                PuyoGridView(graphicsmodel, drawpile[idx], nhide=0, isframed=False)
            )
        rightlayout.addWidget(QLabel(str(drawpile.shape[0]) + " remaining."))
        rightlayout.addStretch()
        self.drawpile_layout = rightlayout

        layout = QHBoxLayout(self)
        layout.addLayout(leftlayout)
        layout.addLayout(rightlayout)
        layout.addStretch()
        layout.setContentsMargins(0, 0, 0, 0)

    def setBoardGraphics(self, board):
        self.board_view.setGraphics(board)

    def setDrawpileGraphics(self, drawpile, index):
        for i in range(2):
            puyo_widget = self.drawpile_layout.itemAt(i).widget()
            if (index + 1 + i) < drawpile.shape[0]:
                puyo_widget.setGraphics(drawpile[index + 1 + i])
            else:
                puyos = drawpile[0].copy()
                puyos.fill(Puyo.NONE)
                puyo_widget.setGraphics(puyos)

        label = self.drawpile_layout.itemAt(2).widget()
        label.setText(str(drawpile.shape[0] - index) + " remaining.")
