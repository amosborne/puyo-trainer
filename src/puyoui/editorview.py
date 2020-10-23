from PyQt5.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QScrollArea,
    QWidget,
)
from PyQt5.QtCore import Qt, pyqtSignal
from puyoui.puyoview import PuyoGridView
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

        label = QLabel()
        label.setFixedWidth(25)
        label.setAlignment(Qt.AlignCenter)
        label.setText(str(index))
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

    def count(self):
        return self.widget().layout().count() - 1  # minus 1 for stretch element
