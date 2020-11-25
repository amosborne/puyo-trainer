from PyQt5.QtWidgets import QAbstractButton, QFrame, QGridLayout, QSizePolicy
from PyQt5.QtGui import QPixmap, QPainter, QImage
from PyQt5.QtCore import Qt, pyqtSignal
from functools import partial


# A view of a single, clickable puyo. Displays an image with opacity.
class PuyoView(QAbstractButton):
    rightclick = pyqtSignal()
    leftclick = pyqtSignal()

    def __init__(self, image, opacity, parent=None):
        super().__init__(parent)
        self.setGraphic(image, opacity)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.leftclick.emit()
        if event.button() == Qt.RightButton:
            self.rightclick.emit()

    def setGraphic(self, image, opacity):
        height, width, channel = image.shape
        qimg = QImage(
            image.tobytes(), width, height, channel * width, QImage.Format_RGBA8888,
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
class PuyoGridView(QFrame):
    rightclick = pyqtSignal(tuple)
    leftclick = pyqtSignal(tuple)

    def __init__(self, graphics, isframed, parent=None):
        super().__init__(parent)

        if isframed:
            self.setFrameShape(QFrame.Box)
            self.setFrameShadow(QFrame.Plain)
            self.setLineWidth(2)

        layout = QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setOriginCorner(Qt.BottomLeftCorner)

        for gfx in graphics:
            puyo = PuyoView(gfx.image, gfx.opacity, parent=self)
            puyo.rightclick.connect(partial(self.rightclick.emit, gfx.pos))
            puyo.leftclick.connect(partial(self.leftclick.emit, gfx.pos))
            layout.addWidget(puyo, *gfx.pos)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def setGraphics(self, graphics):
        for gfx in graphics:
            puyo = self.layout().itemAtPosition(*gfx.pos).widget()
            puyo.setGraphic(gfx.image, gfx.opacity)
