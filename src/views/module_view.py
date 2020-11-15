from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QHBoxLayout,
    QComboBox,
    QFormLayout,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QPlainTextEdit,
)
from PyQt5.QtCore import Qt
import os


class NewModuleDialog(QDialog):
    def __init__(self, modulepath, moduleparams, parent=None):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModal)
        self.modulepath = modulepath

        layout = QVBoxLayout(self)
        form = CreateModuleFormLayout(moduleparams)
        quit_button = QPushButton("Cancel")
        ok_button = QPushButton("Apply")

        quit_button.clicked.connect(self.reject)
        ok_button.clicked.connect(self._validateModule)

        layout.addLayout(form)
        layout.addWidget(quit_button)
        layout.addWidget(ok_button)
        self.form = form

    @property
    def new_module_kwargs(self):
        return self.form.new_module_kwargs

    def _validateModule(self):
        name = self.form.new_module_kwargs["modulename"]
        if os.path.isdir(self.modulepath + name):
            pass  # TODO: catch duplicate names
        else:
            self.accept()


class CreateModuleFormLayout(QFormLayout):
    def __init__(self, moduleparams, parent=None):
        super().__init__(parent)

        self.moduleparams = moduleparams
        self.callbacks = []

        line_edit = QLineEdit()
        self.addRow("Module Name:", line_edit)
        self.callbacks.append(lambda: ("modulename", line_edit.text()))

        self._addComboRow(
            key="board_shape",
            formlabel="Board Shape:",
            fieldlabel=("rows", "columns"),
            default=(12, 6),
        )
        self._addComboRow(
            key="board_nhide", formlabel="Hidden Rows:", fieldlabel="rows", default=1,
        )
        self._addComboRow(
            key="move_shape",
            formlabel="Move Shape:",
            fieldlabel=("rows", "columns"),
            default=(2, 1),
        )
        self._addComboRow(
            key="color_limit", formlabel="Color Limit:", fieldlabel="colors", default=4
        )
        self._addComboRow(
            key="pop_limit", formlabel="Pop Limit:", fieldlabel="puyos", default=4
        )

        text_edit = QPlainTextEdit()
        self.addRow("Description:", text_edit)
        self.callbacks.append(lambda: ("modulereadme", text_edit.toPlainText()))

    @property
    def new_module_kwargs(self):
        return {k: v for (k, v) in [f() for f in self.callbacks]}

    def _addComboRow(self, key, formlabel, fieldlabel, default):
        hbox = QHBoxLayout()

        def constructField(valuerange, fieldname, dft):
            combo = QComboBox()
            label = QLabel(fieldname)
            dft_idx = 0
            for idx, x in enumerate(valuerange):
                combo.addItem(str(x), userData=x)
                dft_idx = idx if x == dft else dft_idx

            combo.setCurrentIndex(dft_idx)
            hbox.addWidget(combo)
            hbox.addWidget(label)
            return combo.currentData

        if not isinstance(fieldlabel, tuple):
            field_callback = constructField(self.moduleparams[key], fieldlabel, default)
            self.callbacks.append(lambda: (key, field_callback()))
        else:
            sub_callbacks = []
            for sub_vr, sub_fn, sub_dft in zip(
                self.moduleparams[key], fieldlabel, default
            ):
                sub_callbacks.append(constructField(sub_vr, sub_fn, sub_dft))

            self.callbacks.append(lambda: (key, tuple([f() for f in sub_callbacks])))

        hbox.addStretch()
        self.addRow(QLabel(formlabel), hbox)
