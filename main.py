import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QAbstractButton,
    QHBoxLayout,
)
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import QRect
from enum import IntEnum


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
        area = QRect(0, 9 * 32, 64, 64)
    else:
        area = QRect((puyo - 1) * 64, 7 * 32, 64, 64)
    return skin_pixmap.copy(area)


class PuyoPanel(QAbstractButton):
    def __init__(self, skin_pixmap, parent=None):
        super(PuyoPanel, self).__init__(parent)
        self.skin_pixmap = skin_pixmap
        self.puyo = Puyo.NONE
        self.puyo_pixmap = puyoPixmap(self.puyo, self.skin_pixmap)

        self.clicked.connect(self.onClick)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), puyoPixmap(self.puyo, self.skin_pixmap))

    def sizeHint(self):
        return self.puyo_pixmap.size()

    def onClick(self):
        self.puyo = Puyo((self.puyo + 1) % 7)
        self.update()


def main():

    app = QApplication(sys.argv)
    window = QWidget()
    layout = QHBoxLayout(window)

    skin_pixmap = QPixmap("ppvs2_skins/gummy.png")
    button = PuyoPanel(skin_pixmap)
    layout.addWidget(button)

    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
