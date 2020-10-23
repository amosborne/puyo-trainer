from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from puyoui.puyoview import PuyoGridView


"""
The module creates UI elements for editing a puyo puzzle definition.
The view controller is responsible for connecting to click events and
modifying the displayed information as appropriate.
"""


# A view of a single drawpile element, including drawpile control buttons.
# The parent drawpile is responsible for maintaining the correct index.
# Specify the graphics model and the puyo grid displayed.
class DrawpileElementView(QHBoxLayout):
    click_insert = pyqtSignal()
    click_delete = pyqtSignal()
    click_puyos = pyqtSignal(tuple)

    def __init__(self, graphicsmodel, puyogrid, parent=None):
        super().__init__(parent)

        label = QLabel()
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

    def setIndex(self, index):
        self.itemAt(0).widget().setText(str(index))

    def setGraphics(self, puyogrid):
        puyos = self.itemAt(1).widget()
        puyos.setGraphics(puyogrid)
