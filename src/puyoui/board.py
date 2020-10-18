from PyQt5.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QVBoxLayout,
    QGridLayout,
    QSizePolicy,
)
from PyQt5.QtCore import QSize, Qt
from puyoui.panel import PuyoPanel

"""
Creates a grid of puyo panels to represent the board,
hidden row, and the incoming puyo to be dropped.
"""

NROWS = 13
NCOLS = 6


def assignAdjacencies(layout, rowmin, rowmax):
    for row in range(rowmin, rowmax):
        for col in range(NCOLS):
            this_panel = layout.itemAtPosition(row, col).widget()
            if row < rowmax - 1:
                this_panel.south = layout.itemAtPosition(row + 1, col).widget()
            if row > rowmin:
                this_panel.north = layout.itemAtPosition(row - 1, col).widget()
            if col < 5:
                this_panel.east = layout.itemAtPosition(row, col + 1).widget()
            if col > 0:
                this_panel.west = layout.itemAtPosition(row, col - 1).widget()


class HoverArea(QWidget):
    def __init__(self, skin_pixmap, parent=None):
        super(HoverArea, self).__init__(parent)

        layout = QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        for row in range(2):
            for col in range(NCOLS):
                layout.addWidget(PuyoPanel(skin_pixmap, clickable=False), row, col)

        assignAdjacencies(layout, 0, 2)


class BoardArea(QFrame):
    def __init__(self, skin_pixmap, clickable=False, parent=None):
        super(BoardArea, self).__init__(parent)

        border_width = 2

        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(border_width)

        layout = QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        for row in range(NROWS):
            for col in range(NCOLS):
                if row == 0:
                    panel = PuyoPanel(skin_pixmap, clickable=clickable, opaque=True)
                else:
                    panel = PuyoPanel(skin_pixmap, clickable=clickable, opaque=False)
                layout.addWidget(panel, row, col)

        assignAdjacencies(layout, 1, NROWS)

    def clear(self):
        layout = self.layout()
        panels = (layout.itemAt(i).widget() for i in range(layout.count()))
        for panel in panels:
            panel.clear()


class PuyoBoard(QVBoxLayout):
    def __init__(self, skin_pixmap, clickable=False, parent=None):
        super(PuyoBoard, self).__init__(parent)

        label = QLabel()
        label.setText("Initial Board")
        label.setAlignment(Qt.AlignCenter)
        self.addWidget(label)

        self.hover_area = HoverArea(skin_pixmap)
        self.addWidget(self.hover_area)

        self.board_area = BoardArea(skin_pixmap, clickable=clickable)
        self.addWidget(self.board_area)

    def clear(self):
        self.board_area.clear()
