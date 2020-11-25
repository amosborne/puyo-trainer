from PyQt5.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QScrollArea,
    QWidget,
    QMainWindow,
    QStackedWidget,
)
from PyQt5.QtCore import Qt, pyqtSignal
from viewcontrols.gamepage.puyo import PuyoGridView
from viewcontrols.gamepage.game import GameView
from viewcontrols.qtutils import deleteItemsOfLayout


# A view of a single drawpile element, including drawpile control buttons.
class DrawpileElementView(QHBoxLayout):
    insert = pyqtSignal(int)
    delete = pyqtSignal(int)
    rightclick = pyqtSignal(int, tuple)
    leftclick = pyqtSignal(int, tuple)

    def __init__(self, graphics, index, parent=None):
        super().__init__(parent)

        indexlabel = QLabel(str(index + 1))
        indexlabel.setFixedWidth(25)
        indexlabel.setAlignment(Qt.AlignCenter)

        puyos = PuyoGridView(graphics, isframed=True)
        puyos.rightclick.connect(lambda pos: self.rightclick.emit(index, pos))
        puyos.leftclick.connect(lambda pos: self.leftclick.emit(index, pos))

        delete_button = QPushButton()
        delete_button.setText("Delete")
        delete_button.clicked.connect(lambda: self.delete.emit(index))
        delete_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        insert_button = QPushButton()
        insert_button.setText("Insert")
        insert_button.clicked.connect(lambda: self.insert.emit(index))
        insert_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.addWidget(indexlabel)
        self.addWidget(puyos)
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(insert_button)
        self.addLayout(button_layout)


# A scrollable list of drawpile elements. Elements are destroyed and rebuilt.
class DrawpileView(QScrollArea):
    insert = pyqtSignal(int)
    delete = pyqtSignal(int)
    rightclick = pyqtSignal(int, tuple)
    leftclick = pyqtSignal(int, tuple)

    def __init__(self, graphicslist, parent=None):
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)

        widget = QWidget(parent=self)
        layout = QVBoxLayout(widget)
        self.setWidget(widget)

        self.setGraphics(graphicslist)

        self.setMinimumWidth(
            layout.sizeHint().width()
            + 2 * self.frameWidth()
            + self.verticalScrollBar().sizeHint().width()
        )

    def setGraphics(self, graphicslist):
        layout = self.widget().layout()
        deleteItemsOfLayout(layout)

        for index, graphics in enumerate(graphicslist):
            elem = DrawpileElementView(graphics, index)
            elem.insert.connect(self.insert)
            elem.delete.connect(self.delete)
            elem.rightclick.connect(self.rightclick)
            elem.leftclick.connect(self.leftclick)
            layout.addLayout(elem)

        layout.addStretch()


# The first of two stacked widgets in the editor - used for puzzle definition.
class PuzzleDefineView(QWidget):
    insert = pyqtSignal(int)
    delete = pyqtSignal(int)
    clear = pyqtSignal()
    reset = pyqtSignal()
    start = pyqtSignal()
    rightclick_drawpile = pyqtSignal(int, tuple)
    leftclick_drawpile = pyqtSignal(int, tuple)
    rightclick_board = pyqtSignal(tuple)
    leftclick_board = pyqtSignal(tuple)

    def __init__(self, board_graphics, drawpile_graphicslist, parent=None):
        super().__init__(parent)

        drawpile_view = DrawpileView(drawpile_graphicslist)
        drawpile_view.insert.connect(self.insert)
        drawpile_view.delete.connect(self.delete)
        drawpile_view.rightclick.connect(self.rightclick_drawpile)
        drawpile_view.leftclick.connect(self.leftclick_drawpile)

        board_view = PuyoGridView(board_graphics, isframed=True)
        board_view.rightclick.connect(self.rightclick_board)
        board_view.leftclick.connect(self.leftclick_board)

        clear_button = QPushButton("Clear Board")
        clear_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        clear_button.clicked.connect(self.clear)

        reset_button = QPushButton("Reset Drawpile")
        reset_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        reset_button.clicked.connect(self.reset)

        start_button = QPushButton("Start")
        start_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        start_button.setStyleSheet("background-color: green")
        start_button.clicked.connect(self.start)

        layout = QHBoxLayout(self)
        sublayout = QVBoxLayout()
        sublayout.addWidget(board_view)
        sublayout.addWidget(clear_button)
        sublayout.addWidget(reset_button)
        sublayout.addWidget(start_button)
        layout.addLayout(sublayout)
        layout.addWidget(drawpile_view)

        self.drawpile = drawpile_view
        self.board = board_view

    def setGraphics(self, board_graphics, drawpile_graphicslist):
        self.board.setGraphics(board_graphics)
        self.drawpile.setGraphics(drawpile_graphicslist)


class PuzzleSolveView(QWidget):
    back = pyqtSignal()
    save = pyqtSignal()

    def __init__(
        self, board_graphics, drawpile_graphicslist, hover_graphics, parent=None
    ):
        super().__init__(parent)

        self.gameview = GameView(
            board_graphics, drawpile_graphicslist, hover_graphics, nremaining=0
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.gameview)

        back_button = QPushButton("Go Back")
        back_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        back_button.clicked.connect(self.back)
        layout.addWidget(back_button)

        save_button = QPushButton("Save and Exit")
        save_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        save_button.setStyleSheet("background-color: green")
        save_button.clicked.connect(self.save)
        layout.addWidget(save_button)


class EditorView(QMainWindow):
    close = pyqtSignal()

    def __init__(
        self, board_graphics, drawpile_graphicslist, hover_graphics, parent=None
    ):
        super().__init__(parent)

        self.defineview = PuzzleDefineView(board_graphics, drawpile_graphicslist)
        self.solverview = PuzzleSolveView(
            board_graphics, drawpile_graphicslist, hover_graphics
        )

        self.setCentralWidget(QStackedWidget())
        self.centralWidget().addWidget(self.defineview)
        self.centralWidget().addWidget(self.solverview)

    def closeEvent(self, event):
        self.close.emit()
        super().closeEvent(event)
