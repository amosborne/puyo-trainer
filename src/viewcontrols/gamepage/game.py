from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSizePolicy,
    QStackedWidget,
)
from PyQt5.QtCore import pyqtSignal, Qt
from viewcontrols.gamepage.puyo import PuyoGridView
from viewcontrols.qtutils import deleteItemsOfLayout


class GameView(QWidget):
    pressX = pyqtSignal()
    pressZ = pyqtSignal()
    pressUp = pyqtSignal()
    pressDown = pyqtSignal()
    pressRight = pyqtSignal()
    pressLeft = pyqtSignal()
    pressSpace = pyqtSignal()

    def __init__(
        self,
        board_graphics,
        drawpile_graphicslist,
        hover_graphics,
        nremaining,
        parent=None,
    ):
        super().__init__(parent)

        self.board = PuyoGridView(board_graphics, isframed=True, parent=self)
        self.hover = PuyoGridView(hover_graphics, isframed=False, parent=self)
        self.drawpile = QVBoxLayout()

        leftlayout = QVBoxLayout()
        leftlayout.addWidget(self.hover)
        leftlayout.addWidget(self.board)

        layout = QHBoxLayout(self)
        layout.addLayout(leftlayout)
        layout.addLayout(self.drawpile)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setGraphics(
            board_graphics, drawpile_graphicslist, hover_graphics, nremaining
        )

        self.setFocusPolicy(Qt.StrongFocus)

    def setGraphics(
        self, board_graphics, drawpile_graphicslist, hover_graphics, nremaining
    ):
        self.board.setGraphics(board_graphics)
        self.hover.setGraphics(hover_graphics)

        deleteItemsOfLayout(self.drawpile)
        for drawpile_gfx in drawpile_graphicslist:
            self.drawpile.addWidget(PuyoGridView(drawpile_gfx, isframed=False))

        self.drawpile.addStretch()
        self.drawpile.addWidget(QLabel(str(nremaining) + " remaining."))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_X:
            self.pressX.emit()
        elif event.key() == Qt.Key_Z:
            self.pressZ.emit()
        elif event.key() == Qt.Key_Up:
            self.pressUp.emit()
        elif event.key() == Qt.Key_Down:
            self.pressDown.emit()
        elif event.key() == Qt.Key_Right:
            self.pressRight.emit()
        elif event.key() == Qt.Key_Left:
            self.pressLeft.emit()
        elif event.key() == Qt.Key_Space:
            self.pressSpace.emit()

        super().keyPressEvent(event)


class SoloGameView(QMainWindow):
    def __init__(
        self,
        board_graphics,
        drawpile_graphicslist,
        hover_graphics,
        nremaining,
        text,
        parent=None,
    ):
        super().__init__(parent)
        self.gameview = GameView(
            board_graphics,
            drawpile_graphicslist,
            hover_graphics,
            nremaining,
            parent=parent,
        )

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self.gameview)

        label = QLabel("Reviewing: " + text)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(label)

        self.setCentralWidget(widget)


class PairedGameView(QWidget):
    def __init__(
        self,
        board1,
        drawpile1,
        hover1,
        nremain1,
        board2,
        drawpile2,
        hover2,
        nremain2,
        parent=None,
    ):
        super().__init__(parent)

        self.gameview1 = GameView(board1, drawpile1, hover1, nremain1, parent=self)
        self.label1 = QLabel("Response")
        self.gameview2 = GameView(board2, drawpile2, hover2, nremain2, parent=self)
        self.label2 = QLabel("Solution")

        self.label1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        top_layout = QHBoxLayout(self)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.gameview1)
        left_layout.addWidget(self.label1)
        top_layout.addLayout(left_layout)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.gameview2)
        right_layout.addWidget(self.label2)
        top_layout.addLayout(right_layout)

    def setCorrect(iscorrect):
        if iscorrect:
            pass
        else:
            pass


class TestGameView(QWidget):
    def __init__(
        self,
        board_graphics,
        drawpile_graphicslist,
        hover_graphics,
        nremaining,
        parent=None,
    ):
        super().__init__(parent)
        self.gameview = GameView(
            board_graphics,
            drawpile_graphicslist,
            hover_graphics,
            nremaining,
            parent=self,
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.gameview)

        label = QLabel("Test")
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(label)


class TestWindow(QMainWindow):
    def __init__(
        self,
        board1,
        drawpile1,
        hover1,
        nremain1,
        board2,
        drawpile2,
        hover2,
        nremain2,
        parent=None,
    ):
        super().__init__(parent)

        self.review = PairedGameView(
            board1,
            drawpile1,
            hover1,
            nremain1,
            board2,
            drawpile2,
            hover2,
            nremain2,
            parent=self,
        )
        self.test = TestGameView(board1, drawpile1, hover1, nremain1, parent=self)

        self.setCentralWidget(QStackedWidget())
        self.centralWidget().addWidget(self.test)
        self.centralWidget().addWidget(self.review)
