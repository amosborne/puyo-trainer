from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QFrame,
    QLabel,
    QStatusBar,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QSizePolicy,
    QPushButton,
)
from PyQt5.QtCore import pyqtSignal
import os
from viewcontrols.qtutils import ErrorPopup, deleteItemOfLayout
from viewcontrols.mainpage.module import NewModuleDialog, ViewModuleFormLayout
from viewcontrols.gamepage.editor import EditorVC
from models import PuzzleModule, Puzzle
from constants import (
    SKIN_DIRECTORY,
    MODULE_DIRECTORY,
    PUZZLE_FILE_ROOT,
    PUZZLE_FILE_EXT,
)


def check_module(func):
    def wrapper(*args, **kwargs):
        if args[0].module is None:
            ErrorPopup("No module is loaded.")
        else:
            return func(*args, **kwargs)

    return wrapper


class MainControl:
    def __init__(self):
        view = MainView()
        view.select_module.connect(self._load_module)
        view.new_module.connect(self._new_module)
        view.test_module.connect(self._test_module)
        view.review_puzzle.connect(self._review_puzzle)
        view.new_puzzle.connect(self._new_puzzle)

        self.view = view
        self.view.show()

    def _load_module(self, module):
        if not module:
            self.module = None
        else:
            try:
                self.module = PuzzleModule.load(module)
            except AssertionError:
                ErrorPopup("Selected module could not be loaded.")
                self.module = None

        self.view.setModuleMetadata(self.module)

    def _new_module(self):
        dialog = NewModuleDialog(parent=self.view,)
        dialog.show()

        def create_module():
            PuzzleModule.new(**dialog.module_kwargs)
            self.view.addModuleSelector(dialog.module_kwargs["modulename"])

        dialog.accepted.connect(create_module)

    @check_module
    def _test_module(self, skin, movelen, fbdelay):
        print(
            "TESTING MODULE (skin: "
            + skin
            + ", moves: "
            + str(movelen)
            + ", period: "
            + str(fbdelay)
            + ")"
        )

    @check_module
    def _new_puzzle(self, skin):
        print("NEW PUZZLE (skin: " + skin + ")")
        puzzle = Puzzle.new(self.module)

    @check_module
    def _review_puzzle(self, skin, puzzle):
        print("REVIEWING PUZZLE (skin: " + skin + ", puzzle: " + puzzle + ")")


class MainView(QMainWindow):
    select_module = pyqtSignal(str)
    new_module = pyqtSignal()
    test_module = pyqtSignal(str, int, int)
    new_puzzle = pyqtSignal(str)
    review_puzzle = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PuyoTrainer v1.0.0")

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)

        self._createStatusBar()
        self._createPuzzleSelector()
        self._hlineSeparator()
        self._createModuleControls()
        self._hlineSeparator()
        self._createSettingSelector()

    def show(self):
        self.select_module.emit(self.module())
        return super().show()

    def setModuleMetadata(self, module):
        new_module_layout = ViewModuleFormLayout(module)

        def transfer_widget(row, col):
            widget = self.module_layout.itemAtPosition(row, col).widget()
            new_module_layout.addWidget(widget)

        transfer_widget(1, 0)
        transfer_widget(1, 1)
        transfer_widget(2, 0)
        transfer_widget(2, 1)

        deleteItemOfLayout(self.layout, 2)
        self.layout.insertLayout(2, new_module_layout)
        self.module_layout = new_module_layout

        if module is None:
            self._updatePuzzleSelector(empty=True)

    def addModuleSelector(self, modulename):
        self.module_selector.addItem(modulename, userData=modulename)

    def _createStatusBar(self):
        status_bar = QStatusBar()

        def addLink(link, text):
            label = QLabel('<a href="' + link + '">' + text + "</a>")
            label.setOpenExternalLinks(True)
            status_bar.addWidget(label)

        addLink(link="https://twitter.com/terramyst1", text="by terramyst, ")
        addLink(link="https://github.com/amosborne/puyo-trainer", text="github")
        self.setStatusBar(status_bar)

    def _hlineSeparator(self):
        hline = QFrame()
        hline.setFrameShape(QFrame.HLine)
        self.layout.addWidget(hline)

    def _createSettingSelector(self):
        sublayout = QHBoxLayout()

        skins = [f for f in os.listdir(SKIN_DIRECTORY) if f.endswith(".png")]

        label = QLabel("Puyo Skin:")
        label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        label.setStyleSheet("font-weight: bold")

        combo_box = QComboBox()
        combo_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        for skin in skins:
            root, _ = os.path.splitext(skin)
            combo_box.addItem(root, userData=skin)

        sublayout.addWidget(label)
        sublayout.addWidget(combo_box)
        self.skin = combo_box.currentData

        label = QLabel("Test Moves:")
        label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        label.setStyleSheet("font-weight: bold")

        combo_box = QComboBox()
        combo_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        for val in range(1, 11):
            combo_box.addItem(str(val), userData=val)

        sublayout.addWidget(label)
        sublayout.addWidget(combo_box)
        self.movelen = combo_box.currentData

        label = QLabel("Test Period:")
        label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        label.setStyleSheet("font-weight: bold")

        combo_box = QComboBox()
        combo_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        for val in range(1, 11):
            combo_box.addItem(str(val), userData=val)

        sublayout.addWidget(label)
        sublayout.addWidget(combo_box)
        self.fbdelay = combo_box.currentData

        self.layout.addLayout(sublayout)

    def _createPuzzleSelector(self):

        modlabel = QLabel("Module:")
        modlabel.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        modlabel.setStyleSheet("font-weight: bold")

        modcombo = QComboBox()
        modcombo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        modules = [
            d
            for d in os.listdir(MODULE_DIRECTORY)
            if os.path.isdir(os.path.join(MODULE_DIRECTORY, d))
        ]
        for module in modules:
            modcombo.addItem(module, userData=module)

        self.module = modcombo.currentData

        def module_select():
            self._updatePuzzleSelector()
            self.select_module.emit(self.module())

        modcombo.currentIndexChanged.connect(module_select)
        self.module_selector = modcombo

        puzlabel = QLabel("Puzzle:")
        puzlabel.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        puzlabel.setStyleSheet("font-weight: bold")

        puzcombo = QComboBox()
        puzcombo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.puzzle = puzcombo.currentData
        self.puzzle_selector = puzcombo

        self._updatePuzzleSelector()

        puzzle_select_layout = QHBoxLayout()
        puzzle_select_layout.addWidget(modlabel)
        puzzle_select_layout.addWidget(modcombo)
        puzzle_select_layout.addWidget(puzlabel)
        puzzle_select_layout.addWidget(puzcombo)
        self.layout.addLayout(puzzle_select_layout)

    def _updatePuzzleSelector(self, empty=False):
        for idx in range(self.puzzle_selector.count()):
            self.puzzle_selector.removeItem(idx)
            if empty:
                return

        _, _, filenames = next(os.walk(MODULE_DIRECTORY + self.module()))
        puzzle_files = [
            filename
            for filename in filenames
            if filename.startswith(PUZZLE_FILE_ROOT)
            and filename.endswith(PUZZLE_FILE_EXT)
        ]
        for filename in puzzle_files:
            root, _ = os.path.splitext(filename)
            self.puzzle_selector.addItem(root, userData=root)

    def _createModuleControls(self):
        new_module_button = QPushButton("New Module")
        new_module_button.clicked.connect(lambda: self.new_module.emit())
        new_module_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        test_module_button = QPushButton("Test Module")
        test_module_button.clicked.connect(
            lambda: self.test_module.emit(self.skin(), self.movelen(), self.fbdelay())
        )
        test_module_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        new_puzzle_button = QPushButton("New Puzzle")
        new_puzzle_button.clicked.connect(lambda: self.new_puzzle.emit(self.skin()))
        new_puzzle_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        review_puzzle_button = QPushButton("Review Puzzle")
        review_puzzle_button.clicked.connect(
            lambda: self.review_puzzle.emit(self.skin(), self.puzzle())
        )
        review_puzzle_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        module_control_layout = ViewModuleFormLayout()
        module_control_layout.addWidget(new_module_button, 1, 0)
        module_control_layout.addWidget(test_module_button, 1, 1)
        module_control_layout.addWidget(new_puzzle_button, 2, 0)
        module_control_layout.addWidget(review_puzzle_button, 2, 1)
        self.layout.addLayout(module_control_layout)

        self.module_layout = module_control_layout
