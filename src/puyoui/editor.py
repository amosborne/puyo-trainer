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
from puyoui.qtutils import deleteItemsOfLayout, deleteItemOfLayout


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

        # initialize index label
        index_label = QLabel()
        index_label.setFixedWidth(25)
        index_label.setAlignment(Qt.AlignCenter)
        self.addWidget(index_label)
        self.index_label = index_label
        self.setIndex(drawpile.layout().count())

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
            callback=lambda: drawpile.deleteItem(self.index),
            sizepolicy=(QSizePolicy.Expanding, QSizePolicy.Minimum),
        )
        addButton(
            layout=layout,
            text="Insert Below",
            callback=lambda: drawpile.insertItem(self.index + 1),
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

        self.skin = skin

        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.setWidget(widget)

        self.reset()

        self.setMinimumWidth(
            layout.sizeHint().width()
            + 2 * self.frameWidth()
            + self.verticalScrollBar().sizeHint().width()
        )

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def layout(self):
        return self.widget().layout()

    def reset(self):
        deleteItemsOfLayout(self.layout())
        self.layout().addLayout(DrawpileElement(self, self.skin))
        self.layout().addLayout(DrawpileElement(self, self.skin))
        self.layout().addStretch()

    def renumber(self):
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            layout = item.layout()
            if layout is not None:
                layout.setIndex(i)

    def insertItem(self, index):
        self.layout().insertLayout(index, DrawpileElement(self, self.skin))
        self.renumber()

    def deleteItem(self, index):
        if self.layout().count() <= 3:  # one extra for the vertical spacer
            return

        deleteItemOfLayout(self.layout(), index)
        self.renumber()

    def toList(self):
        result = []
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            layout = item.layout()
            if layout is not None:
                result.append(layout.getPuyos())

        return result


class DefineWindow(QWidget):
    def __init__(self, editor, parent=None):
        super(DefineWindow, self).__init__(parent)

        # initialize right side - puyo drawpile
        drawpile = Drawpile(editor.skin)  # widget

        # initialize left side - initial board editor and button controls
        board = PuyoBoard(editor.skin, clickable=True)  # vbox

        addButton(
            layout=board,
            text="Clear Board",
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
            callback=editor.solve,
            sizepolicy=(QSizePolicy.Minimum, QSizePolicy.Expanding),
            stylesheet="background-color: green",
        )

        # construct layout
        layout = QHBoxLayout(self)
        layout.addLayout(board)
        layout.addWidget(drawpile)

        self.drawpile = drawpile
        self.board = board

    def drawpileList(self):
        return self.drawpile.toList()


class Editor(QMainWindow):
    def __init__(self, skin, parent=None):
        super(Editor, self).__init__(parent)

        self.skin = skin
        self.define_window = DefineWindow(self)  # widget

        self.setCentralWidget(QStackedWidget())
        self.centralWidget().addWidget(self.define_window)

        self.show()

    def solve(self):
        print("Drawpile:")
        print(self.define_window.drawpileList())
