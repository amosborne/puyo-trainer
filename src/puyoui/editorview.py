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
from puyoui.puyoview import PuyoGridView
from puyoui.gameview import GameplayView
from puyoui.qtutils import deleteItemsOfLayout
from functools import partial


"""
The module creates UI elements for editing a puyo puzzle definition.
The view controller is responsible for connecting to click events and
modifying the displayed information as appropriate.
"""


# A view of a single drawpile element, including drawpile control buttons.
# Specify the graphics model, the puyo grid displayed, and its index.
class DrawpileElementView(QHBoxLayout):
    click_insert = pyqtSignal()
    click_delete = pyqtSignal()
    click_puyos = pyqtSignal(tuple)

    def __init__(self, graphicsmodel, puyogrid, index):
        super().__init__()

        label = QLabel(str(index))
        label.setFixedWidth(25)
        label.setAlignment(Qt.AlignCenter)
        self.addWidget(label)

        puyos = PuyoGridView(graphicsmodel, puyogrid, nhide=0, isframed=True)
        puyos.clicked.connect(lambda pos: self.click_puyos.emit(pos))
        self.addWidget(puyos)

        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)

        delete_button = QPushButton()
        delete_button.setText("Delete")
        delete_button.clicked.connect(self.click_delete)
        delete_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_layout.addWidget(delete_button)

        insert_button = QPushButton()
        insert_button.setText("Insert")
        insert_button.clicked.connect(self.click_insert)
        insert_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_layout.addWidget(insert_button)

        self.addLayout(button_layout)


# A scrollable list of drawpile elements.
# When the controller sets the drawpile graphics, all widgets are reconstructed.
class DrawpileView(QScrollArea):
    click_insert = pyqtSignal(int)
    click_delete = pyqtSignal(int)
    click_puyos = pyqtSignal(tuple)

    def __init__(self, graphicsmodel, drawpile, parent=None):
        super().__init__(parent)

        self.graphicsmodel = graphicsmodel

        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.setWidget(widget)

        self.setGraphics(drawpile)

        self.setMinimumWidth(
            layout.sizeHint().width()
            + 2 * self.frameWidth()
            + self.verticalScrollBar().sizeHint().width()
        )

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def setGraphics(self, drawpile):
        layout = self.widget().layout()
        deleteItemsOfLayout(layout)

        for index, puyos in enumerate(drawpile):
            drawpile_elem = DrawpileElementView(self.graphicsmodel, puyos, index + 1)
            drawpile_elem.click_insert.connect(partial(self.click_insert.emit, index))
            drawpile_elem.click_delete.connect(partial(self.click_delete.emit, index))
            drawpile_elem.click_puyos.connect(
                lambda pos, index=index: self.click_puyos.emit((index, *pos))
            )
            layout.addLayout(drawpile_elem)

        layout.addStretch()


# The first of two stacked widgets in the editor, this window defines the puzzle.
class PuzzleDefineView(QWidget):
    click_drawpile_insert = pyqtSignal(int)
    click_drawpile_delete = pyqtSignal(int)
    click_drawpile_puyos = pyqtSignal(tuple)
    click_board_puyos = pyqtSignal(tuple)
    click_clear_board = pyqtSignal()
    click_reset_drawpile = pyqtSignal()
    click_start = pyqtSignal()

    def __init__(self, graphicsmodel, board, nhide, drawpile, parent=None):
        super().__init__(parent)

        drawpile_view = DrawpileView(graphicsmodel, drawpile)
        drawpile_view.click_insert.connect(self.click_drawpile_insert)
        drawpile_view.click_delete.connect(self.click_drawpile_delete)
        drawpile_view.click_puyos.connect(self.click_drawpile_puyos)

        board_view = PuyoGridView(graphicsmodel, board, nhide, isframed=True)
        board_view.clicked.connect(self.click_board_puyos)

        sublayout = QVBoxLayout()
        sublayout.addWidget(board_view)

        clear_button = QPushButton("Clear Board")
        clear_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        clear_button.clicked.connect(self.click_clear_board)
        sublayout.addWidget(clear_button)

        reset_button = QPushButton("Reset Drawpile")
        reset_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        reset_button.clicked.connect(self.click_reset_drawpile)
        sublayout.addWidget(reset_button)

        start_button = QPushButton("Start")
        start_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        start_button.setStyleSheet("background-color: green")
        start_button.clicked.connect(self.click_start)
        sublayout.addWidget(start_button)

        layout = QHBoxLayout(self)
        layout.addLayout(sublayout)
        layout.addWidget(drawpile_view)

        self.drawpile_view = drawpile_view
        self.board_view = board_view

    def setBoardGraphics(self, board):
        self.board_view.setGraphics(board)

    def setDrawpileGraphics(self, drawpile):
        self.drawpile_view.setGraphics(drawpile)


class PuzzleSolveView(QWidget):
    def __init__(self, graphicsmodel, board, nhide, drawpile, parent=None):
        super().__init__(parent)

        self.gameplayview = GameplayView(graphicsmodel, board, nhide, drawpile)

        layout = QVBoxLayout(self)
        layout.addWidget(self.gameplayview)

        self.back_button = QPushButton("Go Back")
        self.back_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addWidget(self.back_button)

        self.save_button = QPushButton("Save and Exit")
        self.save_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.save_button.setStyleSheet("background-color: green")
        layout.addWidget(self.save_button)


class EditorView(QMainWindow):
    def __init__(self, graphicsmodel, board, nhide, drawpile, parent=None):
        super().__init__(parent)

        self.defineview = PuzzleDefineView(graphicsmodel, board, nhide, drawpile)
        self.solverview = PuzzleSolveView(graphicsmodel, board, nhide, drawpile)

        self.setCentralWidget(QStackedWidget())
        self.centralWidget().addWidget(self.defineview)
        self.centralWidget().addWidget(self.solverview)
