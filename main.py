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
from enum import IntEnum
from collections import namedtuple


class Puyo(IntEnum):
    NONE = 0
    GARBAGE = 1
    RED = 2
    GREEN = 3
    BLUE = 4
    YELLOW = 5
    PURPLE = 6


def puyoPixmap(puyo, skin_pixmap):
    if puyo is Puyo.NONE:
        area = QRect(0, 9 * 32, 32, 32)
    elif puyo is Puyo.GARBAGE:
        area = QRect(6 * 32, 12 * 32, 32, 32)
    else:
        area = QRect(15 * 32, (puyo - 2) * 32, 32, 32)
    return skin_pixmap.copy(area)


class PuyoPanel(QAbstractButton):
    def __init__(self, skin_pixmap, clickable=False, opaque=False, parent=None):
        super(PuyoPanel, self).__init__(parent)
        self.skin_pixmap = skin_pixmap
        self.puyo = Puyo.NONE
        self.puyo_pixmap = puyoPixmap(self.puyo, self.skin_pixmap)

        self.opaque = opaque
        self.clickable = clickable
        self.clicked.connect(self.onClick)

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.opaque:
            painter.setOpacity(0.50)
        painter.drawPixmap(event.rect(), self.puyo_pixmap)

    def sizeHint(self):
        return self.puyo_pixmap.size()

    def onClick(self):
        if self.clickable:
            self.puyo = Puyo((self.puyo + 1) % 7)
            self.puyo_pixmap = puyoPixmap(self.puyo, self.skin_pixmap)
            self.update()


class PuyoBoard:
    def __init__(self, skin_pixmap):
        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(0)
        self.layout.setVerticalSpacing(0)
        for row in range(15):
            for col in range(6):
                if row > 1:  # first two rows hold the piece about to be placed
                    if row == 2:  # third row is the hidden row
                        panel = PuyoPanel(skin_pixmap, clickable=True, opaque=True)
                    else:
                        panel = PuyoPanel(skin_pixmap, clickable=True, opaque=False)
                else:
                    panel = PuyoPanel(skin_pixmap, clickable=False, opaque=False)
                self.layout.addWidget(panel, row, col)


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
