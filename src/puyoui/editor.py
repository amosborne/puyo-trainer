from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QStackedWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QPushButton,
    QSizePolicy,
    QLabel,
    QScrollArea,
)
from PyQt5.QtCore import Qt
from puyoui.board import PuyoBoard
from puyoui.panel import PuyoPanel
from puyoui.qtutils import deleteItemsOfLayout


def addButton(
    layout,
    text="",
    callback=lambda: None,
    sizepolicy=(QSizePolicy.Minimum, QSizePolicy.Fixed),
    stylesheet="",
):
    """Add button with text to layout with click callback, size policy, and stylesheet."""
    button = QPushButton()
    button.setText(text)
    button.clicked.connect(callback)
    button.setSizePolicy(*sizepolicy)
    button.setStyleSheet(stylesheet)
    layout.addWidget(button)


class DrawpileElement(QHBoxLayout):
    def __init__(self, drawpile, skin, parent=None):
        super(DrawpileElement, self).__init__(parent)

        self.drawpile = drawpile

        # initialize index label
        index_label = QLabel()
        index_label.setFixedWidth(25)
        index_label.setAlignment(Qt.AlignCenter)
        self.addWidget(index_label)
        self.index_label = index_label
        self.setIndex(drawpile.count())

        # initialize puyo pair
        puyopair = QFrame()
        puyopair.setFrameShape(QFrame.Box)
        puyopair.setFrameShadow(QFrame.Plain)
        puyopair.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        puyo1 = PuyoPanel(skin, clickable=True, coloronly=True)
        puyo2 = PuyoPanel(skin, clickable=True, coloronly=True)
        puyo1.south = puyo2
        puyo2.north = puyo1

        layout = QVBoxLayout(puyopair)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(puyo1)
        layout.addWidget(puyo2)

        self.addWidget(puyopair)
        self.puyo1 = puyo1
        self.puyo2 = puyo2

        # initialize button controls
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        addButton(
            layout=layout,
            text="Delete",
            sizepolicy=(QSizePolicy.Expanding, QSizePolicy.Minimum),
        )
        addButton(
            layout=layout,
            text="Insert Below",
            sizepolicy=(QSizePolicy.Expanding, QSizePolicy.Minimum),
        )
        self.addLayout(layout)

    def setIndex(self, index):
        self.index = index
        self.index_label.setText(str(index + 1))

    def getPuyos(self):
        return (self.puyo1.puyo, self.puyo2.puyo)


class Drawpile(QScrollArea):
    def __init__(self, skin, parent=None):
        super(Drawpile, self).__init__(parent)

        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addLayout(DrawpileElement(layout, skin))
        layout.addLayout(DrawpileElement(layout, skin))
        layout.addStretch()

        self.layout = layout
        self.skin = skin

        self.setMinimumWidth(
            layout.sizeHint().width()
            + 2 * self.frameWidth()
            + self.verticalScrollBar().sizeHint().width()
        )
        self.setWidget(widget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def reset(self):
        deleteItemsOfLayout(self.layout)
        self.layout.addLayout(DrawpileElement(self.layout, self.skin))
        self.layout.addLayout(DrawpileElement(self.layout, self.skin))
        self.layout.addStretch()


class DefineWindow(QWidget):
    def __init__(self, skin, parent=None):
        super(DefineWindow, self).__init__(parent)

        # initialize right side - puyo drawpile
        drawpile = Drawpile(skin)  # widget

        # initialize left side - initial board editor and button controls
        board = PuyoBoard(skin, clickable=True)  # vbox

        addButton(
            layout=board,
            text="Reset Board",
            callback=board.clear,
            sizepolicy=(QSizePolicy.Minimum, QSizePolicy.Expanding),
        )
        addButton(
            layout=board,
            text="Reset Drawpile",
            callback=drawpile.reset,
            sizepolicy=(QSizePolicy.Minimum, QSizePolicy.Expanding),
        )
        addButton(
            layout=board,
            text="Start Solution",
            sizepolicy=(QSizePolicy.Minimum, QSizePolicy.Expanding),
            stylesheet="background-color: green",
        )

        # construct layout
        layout = QHBoxLayout(self)
        layout.addLayout(board)
        layout.addWidget(drawpile)


class Editor(QMainWindow):
    def __init__(self, skin, parent=None):
        super(Editor, self).__init__(parent)

        self.setCentralWidget(QStackedWidget())
        self.centralWidget().addWidget(DefineWindow(skin))

        self.show()
