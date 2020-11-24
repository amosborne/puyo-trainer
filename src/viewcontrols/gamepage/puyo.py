from PyQt5.QtWidgets import QAbstractButton, QFrame, QGridLayout, QSizePolicy
from PyQt5.QtGui import QPixmap, QPainter, QImage
from PyQt5.QtCore import QRect, Qt, pyqtSignal
from functools import partial


"""
This module creates UI elements for viewing puyo graphics on a grid.
The view controller is responsible for connecting to click events and
modifying the displayed information as appropriate.
"""


# A view of a single, clickable puyo.
# Specify the graphic by skin file, pixel rectangle, and opacity.
class PuyoView(QAbstractButton):
    def __init__(self, image, opacity, parent=None):
        super().__init__(parent)
        self.setGraphic(image, opacity)

    def setGraphic(self, image, opacity):
        height, width, channel = image.shape
        bytes_per_line = channel * width
        qimg = QImage(
            image.tobytes(), width, height, bytes_per_line, QImage.Format_RGBA8888
        )

        self.image = QPixmap(qimg)
        self.opacity = opacity
        self.update()

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setOpacity(self.opacity)
        painter.drawPixmap(self.rect(), self.image)

    def sizeHint(self):
        return self.image.size()


# A view of a grid of clickable puyos. May or may not be framed.
# Specify the graphic model to be interrogated on update.
class PuyoGridView(QFrame):
    clicked = pyqtSignal(tuple)

    def __init__(self, graphicmodel, isframed, parent=None):
        super().__init__(parent)

        if isframed:
            self.setFrameShape(QFrame.Box)
            self.setFrameShadow(QFrame.Plain)
            self.setLineWidth(2)

        layout = QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setOriginCorner(Qt.BottomLeftCorner)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        for graphic in graphicmodel:
            puyoview = PuyoView(graphic.image, graphic.opacity)
            puyoview.clicked.connect(partial(self.clicked.emit, graphic.pos))
            layout.addWidget(puyoview, *graphic.pos)

        self.graphicmodel = graphicmodel

    def updateView(self):
        for graphic in self.graphicmodel:
            puyoview = self.layout().itemAtPosition(*graphic.pos).widget()
            puyoview.setGraphic(graphic.image, graphic.opacity)
