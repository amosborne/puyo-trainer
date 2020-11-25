from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from viewcontrols.gamepage.puyo import PuyoGridView
from viewcontrols.qtutils import deleteItemsOfLayout


class GameView(QWidget):
    pressX = pyqtSignal()
    pressZ = pyqtSignal()
    pressUp = pyqtSignal()
    pressDown = pyqtSignal()
    pressRight = pyqtSignal()
    pressLeft = pyqtSignal()
    pressSpace = pyqtSignal()

    def __init__(
        self,
        board_graphics,
        drawpile_graphicslist,
        hover_graphics,
        nremaining,
        parent=None,
    ):
        super().__init__(parent)

        self.board = PuyoGridView(board_graphics, isframed=True)
        self.hover = PuyoGridView(hover_graphics, isframed=True)
        self.drawpile = QVBoxLayout()

        leftlayout = QVBoxLayout()
        leftlayout.addWidget(self.hover)
        leftlayout.addWidget(self.board)

        layout = QHBoxLayout(self)
        layout.addLayout(leftlayout)
        layout.addLayout(self.drawpile)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setGraphics(
            board_graphics, drawpile_graphicslist, hover_graphics, nremaining
        )

    def setGraphics(
        self, board_graphics, drawpile_graphicslist, hover_graphics, nremaining
    ):
        self.board.setGraphics(board_graphics)
        self.hover.setGraphics(hover_graphics)

        deleteItemsOfLayout(self.drawpile)
        for drawpile_gfx in drawpile_graphicslist:
            self.drawpile.addWidget(PuyoGridView(drawpile_gfx, isframed=True))

        self.drawpile.addStretch()
        self.drawpile.addWidget(QLabel(str(nremaining) + " remaining."))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_X:
            self.pressX.emit()
        elif event.key() == Qt.Key_Z:
            self.pressZ.emit()
        elif event.key() == Qt.Key_Up:
            self.pressUp.emit()
        elif event.key() == Qt.Key_Down:
            self.pressDown.emit()
        elif event.key() == Qt.Key_Right:
            self.pressRight.emit()
        elif event.key() == Qt.Key_Left:
            self.pressLeft.emit()
        elif event.key() == Qt.Key_Space:
            self.pressSpace.emit()
