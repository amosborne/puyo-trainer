from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QStackedWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QPushButton,
    QLayout,
    QSizePolicy,
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


class DefineWindow(QWidget):
    def __init__(self, skin, board=None, drawpile=None, parent=None):
        super(DefineWindow, self).__init__(parent)

        layout = QHBoxLayout(self)  # hbox

        # left side - initial board editor and button controls
        board = PuyoBoard(skin, clickable=True)  # vbox
        layout.addLayout(board)

        clear_button = QPushButton()
        clear_button.setText("Clear Board")
        clear_button.clicked.connect(board.clear)
        board.addWidget(clear_button)
        clear_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        empty_button = QPushButton()
        empty_button.setText("Empty Drawpile")
        board.addWidget(empty_button)
        empty_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        moreless = QWidget()
        moreless_layout = QHBoxLayout(moreless)  # hbox
        # moreless_layout.setSpacing(0)
        moreless_layout.setContentsMargins(0, 0, 0, 0)
        moreless.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        less_button = QPushButton()
        less_button.setText("Drawpile Less")
        moreless_layout.addWidget(less_button)
        less_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        more_button = QPushButton()
        more_button.setText("Drawpile More")
        more_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        moreless_layout.addWidget(more_button)
        board.addWidget(moreless)

        start_button = QPushButton()
        start_button.setText("Start Solution")
        start_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        board.addWidget(start_button)

        cancel_button = QPushButton()
        cancel_button.setText("Close Editor (No Save)")
        cancel_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        board.addWidget(cancel_button)

        # right side - puyo drawpile
        drawpile = QVBoxLayout()
        layout.addLayout(drawpile)
        test = QPushButton()
        test.setText("test")
        drawpile.addWidget(test)
        test.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)


class Editor(QMainWindow):
    def __init__(self, skin, src=None, ascopy=False, parent=None):
        super(Editor, self).__init__(parent)

        editor = QStackedWidget()
        self.setCentralWidget(editor)

        define_window = DefineWindow(skin)
        editor.addWidget(define_window)
        self.define_window = define_window

        self.show()
