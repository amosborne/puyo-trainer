from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QFrame,
    QPushButton,
)
from puyoui.board import PuyoBoard

"""
The editor opens two windows:
   1. A window to assign the initial board state.
   2. A window to assign the sequence of puyos to draw.

If one of the above windows is closed, the other is
automatically closed and the editor concludes without
taking any further action.

Both windows have the same set of buttons for start and
cancel. Cancel closes the editor; start closes the two
windows and opens a new window where the user will play
the defined problem. Once complete, the save button will
become available. The user may otherwise cancel or close
the editor or press the back button to reopen the initial
two windows for further editing.

A problem may not be started unless there are atleast two
puyo pairs to be drawn. There are no other guard rails
implemented while a problem is being solved. Puyo pops are
not detected nor is the ability to utilize the vanish row.

Upon saving, the problem solution will be compared to other
problems in the same module. A warning will be displayed if
there is a logical conflict; the user has the option to
return to the editor or to save the solution anyways.
"""


class PairedWindow(QMainWindow):
    def __init__(self, parent=None):
        super(PairedWindow, self).__init__(parent)
        self.linked_windows = []

    def link(self, window, mutual=True):
        self.linked_windows.append(window)
        if mutual:
            window.link(self, mutual=False)

    def closeEvent(self, event):
        for window in self.linked_windows:
            window.close()
        event.accept()


class Editor:
    def __init__(self, skin, src=None, ascopy=False):
        # Initialize the initial board window.
        ib_window = PairedWindow()
        c_widget = QWidget()
        ib_window.setCentralWidget(c_widget)

        board = PuyoBoard(skin)
        layout = QHBoxLayout(c_widget)
        layout.addLayout(board.layout)

        spacer = QFrame()
        spacer.setFrameShape(QFrame.VLine)
        layout.addWidget(spacer)

        button = QPushButton()
        button.setText("Clear Board")
        button.clicked.connect(board.clear)
        layout.addWidget(button)

        ib_window.show()
        ib_window.setFixedSize(ib_window.size())
        self.initial_board_window = ib_window
        self.initial_board = board

        # Initialize the puyo sequence window.
        ps_window = PairedWindow()
        c_widget = QWidget()
        ps_window.setCentralWidget(c_widget)

        ps_window.show()
        self.puyo_sequence_window = ps_window

        ib_window.link(ps_window)
