from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt
from puyoui.puyoview import PuyoGridView


# Creates UI elements for editing a puyo test case.


class DrawpileElementView(QHBoxLayout):
    def __init__(
        self,
        index,
        skin_file,
        click_callback,
        init_rect,
        init_opacity,
        delete_callback,
        insert_callback,
    ):
        """
        index, the position in the drawpile, displayed in a label.
        skin_file, the skin image file name the pixel boxes are drawn from.
        click_callback, the function called during a click event with the position
            (row, col) of the clicked puyo view used as an argument.
        init_rect, the initial pixel box for all puyo views (top, left, height, width).
        init_opacity, the initial opacity for all puyo views.
        delete_callback, the function called when the delete button is pressed.
        insert_callback, the function called when the insert button is pressed.
        """
        super().__init__()

        label = QLabel()
        label.setFixedWidth(25)
        label.setAlignment(Qt.AlignCenter)
        self.addWidget(label)
        self.setIndex(index)

        puyopair = PuyoGridView(
            size=(2, 1),
            skin_file=skin_file,
            click_callback=click_callback,
            init_rect=init_rect,
            init_opacity=init_opacity,
            isframed=True,
        )
        self.addWidget(puyopair)

        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)

        delete_button = QPushButton()
        delete_button.setText("Delete")
        delete_button.clicked.connect(delete_callback)
        delete_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_layout.addWidget(delete_button)

        insert_button = QPushButton()
        insert_button.setText("Insert")
        insert_button.clicked.connect(insert_callback)
        insert_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_layout.addWidget(insert_button)

        self.addLayout(button_layout)

    def setIndex(self, index):
        self.itemAt(0).widget().setText(str(index))

    def setGraphic(self, pos, rect, opacity):
        puyopair = self.itemAt(1).widget()
        puyoview = puyopair.layout().itemAtPosition(*pos).widget()
        puyoview.setGraphic(rect, opacity)
