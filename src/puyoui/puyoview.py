from PyQt5.QtWidgets import QAbstractButton, QFrame, QGridLayout, QSizePolicy
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import QRect, Qt, pyqtSignal
from functools import partial

"""
This module creates UI elements for viewing puyo graphics on a grid.
The view controller is responsible for specifying the graphics displayed.
The view controller may connect to the view to detect click events.
"""

# A view of a single, clickable puyo.
# Specify the graphic by skin file, pixel rectangle, and opacity.
class PuyoView(QAbstractButton):
    def __init__(self, skin, rect, opacity, parent=None):
        super().__init__(parent)

        self.skin = QPixmap(skin)
        self.setGraphic(rect, opacity)

    def setGraphic(self, rect, opacity):
        self.image = self.skin.copy(QRect(*rect))
        self.opacity = opacity
        self.update()

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setOpacity(self.opacity)
        painter.drawPixmap(self.rect(), self.image)

    def sizeHint(self):
        return self.image.size()


# A view of a grid of clickable puyos. May or may not be framed.
# Specify the graphics by skin file, pixel rectangles, and opacities.
class PuyoGridView(QFrame):
    clicked = pyqtSignal(tuple)

    def __init__(self, skin, rects, opacities, isframed, parent=None):
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

        for row_idx, row in enumerate(rects):
            for col_idx, rect in enumerate(row):
                pos = (row_idx, col_idx)
                opacity = opacities[row_idx][col_idx]
                puyoview = PuyoView(skin, rect, opacity, parent=self)
                puyoview.clicked.connect(partial(self.clicked.emit, pos))
                layout.addWidget(puyoview, *pos)

    def setGraphic(self, pos, rect, opacity):
        puyoview = self.layout().itemAtPosition(*pos).widget()
        puyoview.setGraphic(rect, opacity)

    def setGraphics(self, rects, opacities):
        for row_idx, row in enumerate(rects):
            for col_idx, rect in enumerate(row):
                pos = (row_idx, col_idx)
                opacity = opacities[row_idx][col_idx]
                self.setGraphic(pos, rect, opacity)
