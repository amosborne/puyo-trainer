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
from models import PuzzleModule
from constants import SKIN_DIRECTORY, MODULE_DIRECTORY


class MainControl:
    def __init__(self):
        view = MainView()
        view.select_module.connect(self._load_module)
        view.new_module.connect(self._new_module)
        view.test_module.connect(self._test_module)

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

    def _test_module(self, skin):
        if self.module is None:
            ErrorPopup("No module is loaded.")


class MainView(QMainWindow):
    select_module = pyqtSignal(str)
    new_module = pyqtSignal()
    test_module = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PuyoTrainer v1.0.0")

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)

        self._createStatusBar()
        self._createSkinSelector()
        self._hlineSeparator()
        self._createModuleHandler()
        self._hlineSeparator()
        self._createPuzzleHandler()

    def show(self):
        self.select_module.emit(self.module())
        return super().show()

    def setModuleMetadata(self, module):
        deleteItemOfLayout(self.layout, 4)
        self.layout.insertLayout(4, ViewModuleFormLayout(module))

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

    def _createSkinSelector(self):
        skins = [f for f in os.listdir(SKIN_DIRECTORY) if f.endswith(".png")]

        label = QLabel("Select Puyo Skin:")
        label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        label.setStyleSheet("font-weight: bold")

        combo_box = QComboBox()
        combo_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        for skin in skins:
            root, _ = os.path.splitext(skin)
            combo_box.addItem(root, userData=skin)

        sublayout = QHBoxLayout()
        sublayout.addWidget(label)
        sublayout.addWidget(combo_box)
        self.layout.addLayout(sublayout)

        self.skin = combo_box.currentData

    def _createModuleHandler(self):
        label = QLabel("Select Puzzle Module:")
        label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        label.setStyleSheet("font-weight: bold")

        combo_box = QComboBox()
        combo_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        modules = [
            d
            for d in os.listdir(MODULE_DIRECTORY)
            if os.path.isdir(os.path.join(MODULE_DIRECTORY, d))
        ]
        for module in modules:
            combo_box.addItem(module, userData=module)

        self.module = combo_box.currentData
        combo_box.currentIndexChanged.connect(
            lambda: self.select_module.emit(self.module())
        )

        new_module_button = QPushButton("New Module")
        new_module_button.clicked.connect(lambda: self.new_module.emit())
        new_module_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        test_module_button = QPushButton("Test Module")
        test_module_button.clicked.connect(lambda: self.test_module.emit(self.skin()))
        test_module_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        module_select_layout = QHBoxLayout()
        module_select_layout.addWidget(label)
        module_select_layout.addWidget(combo_box)
        self.layout.addLayout(module_select_layout)
        self._hlineSeparator()

        self.layout.addLayout(ViewModuleFormLayout())
        self._hlineSeparator()

        module_control_layout = QHBoxLayout()
        module_control_layout.addWidget(new_module_button)
        module_control_layout.addWidget(test_module_button)
        self.layout.addLayout(module_control_layout)

        self.module_selector = combo_box

    def _createPuzzleHandler(self):
        label = QLabel("puzzle handler")
        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        label.setStyleSheet("font-weight: bold")
        self.layout.addWidget(label)
