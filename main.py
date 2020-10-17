import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect
from enum import IntEnum


class Puyo(IntEnum):
    GARBAGE = 0
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4
    PURPLE = 5


def puyoPixmap(puyo, skin_pixmap):
    area = QRect(puyo * 64, 7 * 32, 64, 64)
    return skin_pixmap.copy(area)


def main():

    app = QApplication(sys.argv)

    w = QMainWindow()
    w.setWindowTitle("Puyo Trainer")

    skin_pixmap = QPixmap("ppvs2_skins/gummy.png")
    label = QLabel(w)
    puyo_pixmap = puyoPixmap(Puyo.YELLOW, skin_pixmap)
    label.setPixmap(puyo_pixmap)
    w.setCentralWidget(label)

    w.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
