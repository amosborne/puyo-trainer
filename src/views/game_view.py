from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from views.puyo_view import PuyoGridView
from views.qtutils import deleteItemOfLayout


class GameView(QWidget):
    pressX = pyqtSignal()
    pressZ = pyqtSignal()
    pressUp = pyqtSignal()
    pressDown = pyqtSignal()
    pressRight = pyqtSignal()
    pressLeft = pyqtSignal()

    def __init__(self, board, drawpile, hoverarea, draw_index, parent=None):
        super().__init__(parent)

        self.board = board
        self.board_view = PuyoGridView(board, isframed=True)
        self.hover_view = PuyoGridView(hoverarea, isframed=False)

        self.drawpile = drawpile

        leftlayout = QVBoxLayout()
        leftlayout.addWidget(self.hover_view)
        leftlayout.addWidget(self.board_view)

        layout = QHBoxLayout(self)
        layout.addLayout(leftlayout)
        layout.addLayout(QVBoxLayout())  # placeholder
        layout.addStretch()
        layout.setContentsMargins(0, 0, 0, 0)

        self.setFocusPolicy(Qt.StrongFocus)
        self.layout = layout
        self.updateView(draw_index)

    def updateView(self, draw_index):
        self.board_view.updateView()
        self.hover_view.updateView()

        layout = QVBoxLayout()
        for idx in range(2):  # hardcoded two previews
            try:
                elem = PuyoGridView(self.drawpile[draw_index + idx], isframed=False)
                layout.addWidget(elem)
            except IndexError:
                pass

        layout.addStretch()
        label = QLabel(str(len(self.drawpile) - draw_index + 1) + " remaining.")
        layout.addWidget(label)

        deleteItemOfLayout(self.layout, 1)
        self.layout.insertLayout(1, layout)
        self.setFocus()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
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
