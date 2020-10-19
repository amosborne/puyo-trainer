from PyQt5.QtWidgets import QAbstractButton, QSizePolicy
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QRect
from puyolib.puyo import Puyo, AdjMatch

"""
Creates a single clickable panel that displays a graphic of a puyo.
The panel is aware of its adjacent panels (as applicable) in order
to select the correct graphic.
"""


class PuyoPanel(QAbstractButton):
    def __init__(
        self, skin_pixmap, clickable=False, opaque=False, coloronly=False, parent=None
    ):
        super(PuyoPanel, self).__init__(parent)
        self.skin_pixmap = skin_pixmap
        self.coloronly = coloronly
        self.puyo = Puyo.NONE if not coloronly else Puyo.RED

        self.opaque = opaque
        self.clickable = clickable
        self.clicked.connect(self.onClick)

        self.north = None
        self.south = None
        self.east = None
        self.west = None

        self.updatePixmap(mutual=False)

    def sizeHint(self):
        return self.puyo_pixmap.size()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.opaque:
            painter.setOpacity(0.50)
        painter.drawPixmap(self.rect(), self.puyo_pixmap)

    def updatePixmap(self, mutual=True):

        (north, south, east, west) = (False for _ in range(4))
        if self.north is not None:
            north = True if self.north.puyo is self.puyo else False
            if mutual:
                self.north.updatePixmap(mutual=False)
        if self.south is not None:
            south = True if self.south.puyo is self.puyo else False
            if mutual:
                self.south.updatePixmap(mutual=False)
        if self.east is not None:
            east = True if self.east.puyo is self.puyo else False
            if mutual:
                self.east.updatePixmap(mutual=False)
        if self.west is not None:
            west = True if self.west.puyo is self.puyo else False
            if mutual:
                self.west.updatePixmap(mutual=False)

        adjmatch = AdjMatch(north, south, east, west)
        rect = Puyo.rect(self.puyo, adjmatch)
        area = QRect(*rect)
        self.puyo_pixmap = self.skin_pixmap.copy(area)
        self.update()

    def onClick(self):
        if self.clickable:
            self.puyo = Puyo.cycle(self.puyo)
            while self.coloronly and (
                self.puyo is Puyo.NONE or self.puyo is Puyo.GARBAGE
            ):
                self.puyo = Puyo.cycle(self.puyo)
            self.updatePixmap()

    def setPuyo(self, puyo):
        self.puyo = puyo
        self.updatePixmap()

    def clear(self):
        self.setPuyo(Puyo.NONE)
