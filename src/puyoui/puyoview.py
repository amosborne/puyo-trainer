from PyQt5.QtWidgets import QAbstractButton, QFrame, QGridLayout, QSizePolicy
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import QRect, Qt
from functools import partial


# Creates UI elements for viewing and clicking a single puyo or a grid of puyos.


class PuyoView(QAbstractButton):
    def __init__(self, skin_file, click_callback, init_rect, init_opacity):
        """
        skin_file, the skin image file name the pixel box is drawn from.
        click_callback, the function called during a click event.
        init_rect, the initial pixel box (top, left, heigh, width).
        init_opacity, the initial opacity.
        """
        super().__init__()

        self.skin_pixmap = QPixmap(skin_file)
        self.clicked.connect(click_callback)
        self.setGraphic(init_rect, init_opacity)

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setOpacity(self.opacity)
        painter.drawPixmap(self.rect(), self.puyo_pixmap)

    def sizeHint(self):
        return self.puyo_pixmap.size()

    def setGraphic(self, rect, opacity):
        self.puyo_pixmap = self.skin_pixmap.copy(QRect(*rect))
        self.opacity = opacity
        self.update()


class PuyoGridView(QFrame):
    def __init__(
        self, size, skin_file, click_callback, init_rect, init_opacity, isframed
    ):
        """
        size, the size of the puyo view grid (rows, cols).
        skin_file, the skin image file name the pixel boxes are drawn from.
        click_callback, the function called during a click event with the position
            (row, col) of the clicked puyo view used as an argument.
        init_rect, the initial pixel box for all puyo views (top, left, heigh, width).
        init_opacity, the initial opacity for all puyo views.
        isframed, boolean of whether the grid is framed in a box.
        """
        super().__init__()

        if isframed:
            self.setFrameShape(QFrame.Box)
            self.setFrameShadow(QFrame.Plain)
            self.setLineWidth(2)

        layout = QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setOriginCorner(Qt.BottomLeftCorner)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        for row in range(size[0]):
            for col in range(size[1]):
                puyoview = PuyoView(
                    skin_file,
                    partial(click_callback, (row, col)),
                    init_rect,
                    init_opacity,
                )
                layout.addWidget(puyoview, row, col)

    def setGraphic(self, pos, rect, opacity):
        puyoview = self.layout().itemAtPosition(*pos).widget()
        puyoview.setGraphic(rect, opacity)
