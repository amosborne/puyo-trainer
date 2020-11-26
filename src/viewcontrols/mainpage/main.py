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
from viewcontrols.gamepage.player import ReviewVC, TesterVC
from models import PuzzleModule, Puzzle
from constants import (
    SKIN_DIRECTORY,
    MODULE_DIRECTORY,
    PUZZLE_FILE_ROOT,
    PUZZLE_FILE_EXT,
)
from copy import deepcopy
import threading


def check_module(func):
    def wrapper(*args, **kwargs):
        if args[0].module is None:
            ErrorPopup("No module is loaded.")
        else:
            return func(*args, **kwargs)

    return wrapper


class CompatThread(threading.Thread):
    def __init__(self, module, callback):
        super().__init__()
        self.killme = threading.Event()
        self.module = module
        self.callback = callback

    def run(self):
        self.module.self_compatible(self)
        if not self.killme.is_set():
            self.callback()


class MainControl:
    def __init__(self):
        view = MainView()
        view.select_module.connect(self._load_module)
        view.new_module.connect(self._new_module)
        view.test_module.connect(self._test_module)
        view.review_puzzle.connect(self._review_puzzle)
        view.new_puzzle.connect(self._new_puzzle)
        view.self_compat.connect(self._run_selfcompat)
        view.setCompatStatus(isactive=False)

        self.selfcompat_thread = CompatThread(None, lambda: None)
        view.closed.connect(lambda: self.selfcompat_thread.killme.set())

        # New windows aren't garbage collected.
        # So don't make thousands of windows?
        self._garbage_pit = []

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
    def _run_selfcompat(self):
        if self.selfcompat_thread.is_alive():
            ErrorPopup("Module self-compatibility check in progress.")
            return
        elif len(self.module.puzzles.keys()) <= 1:
            ErrorPopup("Module has less than 2 puzzles.")
            return

        self.view.setCompatStatus(isactive=True)
        module = deepcopy(self.module)
        self.selfcompat_thread = CompatThread(
            module, lambda: self.view.setCompatStatus(isactive=False)
        )
        self.selfcompat_thread.start()

    @check_module
    def _test_module(self, skin, movelen, fbdelay):
        if len(self.module.puzzles.keys()) == 0:
            ErrorPopup("Loaded module has no puzzles.")
            return
        if not skin:
            ErrorPopup("No skin is loaded.")
            return

        tester = TesterVC(skin, deepcopy(self.module), movelen, fbdelay, self.view)
        tester.win.setWindowTitle("Test (" + self.view.module() + ")")
        self._garbage_pit.append(tester)
        self._garbage_pit.append(tester.win)

    @check_module
    def _new_puzzle(self, skin):
        if not skin:
            ErrorPopup("No skin is loaded.")
            return

        puzzle = Puzzle.new(self.module, self.view.module())
        editor = EditorVC(puzzle, skin, self.view)

        # The connection seems to prevent garbage collection also.
        editor.view.winclose.connect(self.view._updatePuzzleSelector)

    @check_module
    def _review_puzzle(self, skin, puzzle):
        if not puzzle:
            ErrorPopup("No puzzle is loaded.")
            return
        if not skin:
            ErrorPopup("No skin is loaded.")
            return

        puz = self.module.puzzles[puzzle]
        text = puz.path + "/" + puzzle

        reviewer = ReviewVC(skin, deepcopy(puz), text, self.view)
        self._garbage_pit.append(reviewer)
        self._garbage_pit.append(reviewer.win)

        reviewer.win.setWindowTitle("Review Puzzle")


class MainView(QMainWindow):
    select_module = pyqtSignal(str)
    new_module = pyqtSignal()
    test_module = pyqtSignal(str, int, int)
    new_puzzle = pyqtSignal(str)
    review_puzzle = pyqtSignal(str, str)
    self_compat = pyqtSignal()
    closed = pyqtSignal()

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

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

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
        addLink(link="https://github.com/amosborne/puyo-trainer", text="github.")

        status_bar.addWidget(QLabel("(keyboard usage: arrow keys, x, z, spacebar)"))

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

        self.selfcompat_button = QPushButton("Self-Compat")
        self.selfcompat_button.clicked.connect(self.self_compat)

        puzzle_select_layout = QHBoxLayout()
        puzzle_select_layout.addWidget(modlabel)
        puzzle_select_layout.addWidget(modcombo)
        puzzle_select_layout.addWidget(puzlabel)
        puzzle_select_layout.addWidget(puzcombo)
        puzzle_select_layout.addWidget(self.selfcompat_button)
        self.layout.addLayout(puzzle_select_layout)

    def setCompatStatus(self, isactive):
        if isactive:
            self.selfcompat_button.setStyleSheet("font: bold; color: red")
        else:
            self.selfcompat_button.setStyleSheet("font: bold; color: blue")

    def _updatePuzzleSelector(self, empty=False):
        self.puzzle_selector.clear()
        if empty or self.module() is None:
            return

        _, _, filenames = next(os.walk(MODULE_DIRECTORY + self.module()))
        puzzle_files = [
            filename
            for filename in filenames
            if filename.startswith(PUZZLE_FILE_ROOT)
            and filename.endswith(PUZZLE_FILE_EXT)
        ]
        for filename in sorted(puzzle_files):
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
