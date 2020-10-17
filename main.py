import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QAbstractButton,
    QPushButton,
    QLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
)
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import QRect, Qt
from enum import IntEnum, auto
from collections import namedtuple


class Puyo(IntEnum):
    RED = 0
    GREEN = 1
    BLUE = 2
    YELLOW = 3
    PURPLE = 4
    GARBAGE = 5
    NONE = 6


def puyoPixmap(puyo, skin_pixmap, adj_match):
    if puyo is Puyo.NONE:
        area = QRect(0, 9 * 32, 32, 32)
    elif puyo is Puyo.GARBAGE:
        area = QRect(6 * 32, 12 * 32, 32, 32)
    else:  # Only adjacencies of up to 3 puyos are supported.
        if adj_match == [True, False, False, False]:
            offset = 2
        elif adj_match == [False, True, False, False]:
            offset = 1
        elif adj_match == [True, True, False, False]:
            offset = 3
        elif adj_match == [False, False, True, False]:
            offset = 8
        elif adj_match == [False, False, False, True]:
            offset = 4
        elif adj_match == [False, False, True, True]:
            offset = 12
        elif adj_match == [True, False, True, False]:
            offset = 10
        elif adj_match == [True, False, False, True]:
            offset = 6
        elif adj_match == [False, True, True, False]:
            offset = 9
        elif adj_match == [False, True, False, True]:
            offset = 5
        else:
            offset = 0
        area = QRect(offset * 32, puyo * 32, 32, 32)
    return skin_pixmap.copy(area)


class PuyoPanel(QAbstractButton):
    def __init__(self, skin_pixmap, clickable=False, opaque=False, parent=None):
        super(PuyoPanel, self).__init__(parent)
        self.skin_pixmap = skin_pixmap
        self.puyo = Puyo.NONE
        self.puyo_pixmap = puyoPixmap(
            self.puyo, self.skin_pixmap, [False for _ in range(4)]
        )

        self.opaque = opaque
        self.clickable = clickable
        self.clicked.connect(self.onClick)

        self.top = None
        self.bottom = None
        self.left = None
        self.right = None

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.opaque:
            painter.setOpacity(0.50)
        painter.drawPixmap(event.rect(), self.puyo_pixmap)

    def sizeHint(self):
        return self.puyo_pixmap.size()

    def updatePixmap(self, recurse=False):

        adjacent_panels = [self.top, self.bottom, self.left, self.right]
        adjacent_match = [False for _ in range(4)]
        for idx, panel in enumerate(adjacent_panels):
            if panel is not None:
                if recurse:
                    panel.updatePixmap()
                if panel.puyo is self.puyo:
                    adjacent_match[idx] = True

        self.puyo_pixmap = puyoPixmap(self.puyo, self.skin_pixmap, adjacent_match)
        self.update()

    def onClick(self):
        if self.clickable:
            self.puyo = Puyo((self.puyo + 1) % len(Puyo))
            self.updatePixmap(recurse=True)


class PuyoBoard:
    def __init__(self, skin_pixmap):
        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(0)
        self.layout.setVerticalSpacing(0)

        # Populate the grid layout with the puyo panels.
        for row in range(15):
            for col in range(6):
                if row > 1:  # First two rows hold the piece about to be placed.
                    if row == 2:  # Third row is the hidden row.
                        panel = PuyoPanel(skin_pixmap, clickable=True, opaque=True)
                    else:
                        panel = PuyoPanel(skin_pixmap, clickable=True, opaque=False)
                else:
                    panel = PuyoPanel(skin_pixmap, clickable=False, opaque=False)
                self.layout.addWidget(panel, row, col)

        # Assign panel adjacencies.
        self.assignAdjacencies(3, 15)
        self.assignAdjacencies(0, 2)

    def assignAdjacencies(self, rowmin, rowmax):
        for row in range(rowmin, rowmax):
            for col in range(6):
                this_panel = self.layout.itemAtPosition(row, col).widget()
                if row < rowmax - 1:
                    this_panel.bottom = self.layout.itemAtPosition(
                        row + 1, col
                    ).widget()
                if row > rowmin:
                    this_panel.top = self.layout.itemAtPosition(row - 1, col).widget()
                if col < 5:
                    this_panel.right = self.layout.itemAtPosition(row, col + 1).widget()
                if col > 0:
                    this_panel.left = self.layout.itemAtPosition(row, col - 1).widget()


def main():
    app = QApplication(sys.argv)
    window = QWidget()

    window_layout = QHBoxLayout(window)
    skin_pixmap = QPixmap("ppvs2_skins/gummy.png")
    board = PuyoBoard(skin_pixmap)
    window_layout.addLayout(board.layout)

    spacer = QFrame()
    spacer.setFrameShape(QFrame.VLine)
    window_layout.addWidget(spacer)

    button = QPushButton()
    button.setText("test button")
    window_layout.addWidget(button)

    window_layout.setSizeConstraint(QLayout.SetFixedSize)

    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
