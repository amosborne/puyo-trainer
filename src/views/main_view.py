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
from views.module_view import NewModuleDialog
from models.puzzle_module import PuzzleModule  # model
import os


class MainControl:
    def __init__(self, view):
        self.view = view

        view.skin_select.connect(lambda x: print(x))
        view.module_select.connect(self._load_module)
        view.new_module_click.connect(self._define_new_module)
        view.test_module_click.connect(lambda: print("testing module"))

        view.emitInitialState()
        view.show()

    def _load_module(self, module):
        if module is not None:
            self.module = PuzzleModule.load(module, self.view.moduleparams)
        else:
            self.module = None

    def _define_new_module(self):
        dialog = NewModuleDialog(
            modulepath=self.view.modulepath,
            moduleparams=self.view.moduleparams,
            parent=self.view,
        )
        dialog.show()

        dialog.accepted.connect(lambda: PuzzleModule.new(**dialog.new_module_kwargs))


class MainView(QMainWindow):
    skin_select = pyqtSignal(str)
    module_select = pyqtSignal(str)
    new_module_click = pyqtSignal()
    test_module_click = pyqtSignal()

    def __init__(self, skinpath, modulepath, moduleparams, parent=None):
        super().__init__(parent)

        self.skinpath = skinpath
        self.modulepath = modulepath
        self.moduleparams = moduleparams
        self.setWindowTitle("PuyoTrainer v1.0.0")

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)

        self._createStatusBar()
        self._createSkinSelector()
        self._createModuleHandler()
        self._createPuzzleHandler()

    def _createStatusBar(self):
        status_bar = QStatusBar()

        def addLink(link, text):
            label = QLabel('<a href="' + link + '">' + text + "</a>")
            label.setOpenExternalLinks(True)
            status_bar.addWidget(label)

        addLink(link="https://twitter.com/terramyst1", text="by terramyst, ")
        addLink(link="https://github.com/amosborne/puyo-trainer", text="github")
        self.setStatusBar(status_bar)

    def _createSkinSelector(self):
        skins = [f for f in os.listdir(self.skinpath) if f.endswith(".png")]

        sublayout = QHBoxLayout()
        label = QLabel("Select Puyo Skin:")
        label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        combo_box = QComboBox()
        combo_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        for skin in skins:
            root, _ = os.path.splitext(skin)
            combo_box.addItem(root, userData=self.skinpath + skin)

        combo_box.currentIndexChanged.connect(
            lambda _: self.skin_select.emit(combo_box.currentData())
        )

        sublayout.addWidget(label)
        sublayout.addWidget(combo_box)
        self.layout.addLayout(sublayout)
        self.skin_combo_box = combo_box

        hline = QFrame()
        hline.setFrameShape(QFrame.HLine)
        self.layout.addWidget(hline)

    def _createModuleHandler(self):
        module_select_layout = QHBoxLayout()

        label = QLabel("Select Puzzle Module:")
        label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        modules = [
            d
            for d in os.listdir(self.modulepath)
            if os.path.isdir(os.path.join(self.modulepath, d))
        ]
        combo_box = QComboBox()
        combo_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        for module in modules:
            combo_box.addItem(module, userData=self.modulepath + module + "/")

        combo_box.currentIndexChanged.connect(
            lambda _: self.module_select.emit(combo_box.currentData())
        )

        module_select_layout.addWidget(label)
        module_select_layout.addWidget(combo_box)
        self.module_combo_box = combo_box

        module_metadata_layout = QHBoxLayout()

        module_control_layout = QHBoxLayout()

        new_module_button = QPushButton("New Module")
        new_module_button.clicked.connect(self.new_module_click)
        module_control_layout.addWidget(new_module_button)

        test_module_button = QPushButton("Test Module")
        test_module_button.clicked.connect(self.test_module_click)
        module_control_layout.addWidget(test_module_button)

        module_handler_layout = QVBoxLayout()
        module_handler_layout.addLayout(module_select_layout)
        module_handler_layout.addLayout(module_metadata_layout)
        module_handler_layout.addLayout(module_control_layout)
        self.layout.addLayout(module_handler_layout)

        hline = QFrame()
        hline.setFrameShape(QFrame.HLine)
        self.layout.addWidget(hline)

    def _createPuzzleHandler(self):
        label = QLabel("puzzle handler")
        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.layout.addWidget(label)

    def emitInitialState(self):
        self.skin_select.emit(self.skin_combo_box.currentData())
        self.module_select.emit(self.module_combo_box.currentData())
