from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from puyoui.puyoview import PuyoGridView
from puyoui.qtutils import deleteItemOfLayout


class GameplayView(QWidget):
    keypressed = pyqtSignal(int)

    def __init__(self, board, drawpile, hoverarea, draw_index, parent=None):
        super().__init__(parent)

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
        self.keypressed.emit(event.key())
