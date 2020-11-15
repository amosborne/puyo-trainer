from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFrame,
    QLabel,
    QStatusBar,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QSizePolicy,
)
from PyQt5.QtCore import pyqtSignal
from models.puzzle_module import PuzzleModule  # model
from controls.edit_control import EditorVC  # view-controller
import shutil
import os
from functools import partial

SKIN_DIRECTORY = "./ppvs2_skins/"


def run_app():

    app = QApplication([])

    # skin = "./ppvs2_skins/gummy.png"

    # name = "dryrun"
    # module = PuzzleModule.new(
    #     modulename=name,
    #     board_shape=(12, 6),
    #     board_nhide=1,
    #     move_shape=(2, 1),
    #     color_limit=4,
    #     pop_limit=4,
    #     modulereadme="",
    # )
    # puzzle = module.new_puzzle()
    # shutil.rmtree("./modules/" + name + "/")

    # editor = EditorVC(puzzle, skin)

    # editor.view.show()

    view = MainView()
    control = MainControl(view)

    return app.exec_()


class MainControl:
    def __init__(self, view):
        view.skin_select.connect(lambda x: print(x))

        view.show()
        view.emitInitialState()


class MainView(QMainWindow):
    skin_select = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("PuyoTrainer v1.0.0")

        main_widget = QWidget()
        self.layout = QVBoxLayout(main_widget)

        self.setCentralWidget(main_widget)

        self._createStatusBar()
        self._createSkinSelector()
        self._createModuleHandler()
        self._createPuzzleHandler()

    def _createStatusBar(self):
        status_bar = QStatusBar()
        author_label = QLabel(
            '<a href="https://twitter.com/terramyst1"> by terramyst, </a>'
        )
        author_label.setOpenExternalLinks(True)
        doc_label = QLabel(
            ' <a href="https://github.com/amosborne/puyo-trainer"> github src and docs. </a>'
        )
        doc_label.setOpenExternalLinks(True)
        status_bar.insertWidget(0, author_label)
        status_bar.insertWidget(1, doc_label)
        self.setStatusBar(status_bar)

    def _createSkinSelector(self):
        skins = [f for f in os.listdir(SKIN_DIRECTORY) if f.endswith(".png")]

        sublayout = QHBoxLayout()
        label = QLabel("Select Puyo Skin:")
        label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        combo_box = QComboBox()
        combo_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        for skin in skins:
            root, _ = os.path.splitext(skin)
            combo_box.addItem(root.capitalize(), userData=SKIN_DIRECTORY + skin)

        combo_box.currentIndexChanged.connect(
            lambda _: self.skin_select.emit(combo_box.currentData())
        )

        sublayout.addWidget(label)
        sublayout.addWidget(combo_box)
        self.layout.addLayout(sublayout)
        self.combo_box = combo_box

        hline = QFrame()
        hline.setFrameShape(QFrame.HLine)
        self.layout.addWidget(hline)

    def _createModuleHandler(self):
        self.layout.addWidget(QLabel("module handler"))

        hline = QFrame()
        hline.setFrameShape(QFrame.HLine)
        self.layout.addWidget(hline)

    def _createPuzzleHandler(self):
        label = QLabel("puzzle handler")
        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.layout.addWidget(label)

    def emitInitialState(self):
        self.skin_select.emit(self.combo_box.currentData())
