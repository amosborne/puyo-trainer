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
    QSizePolicy,
)
from PyQt5.QtCore import Qt
import os
from viewcontrols.qtutils import ErrorPopup
from constants import MODULE_DIRECTORY, MODULE_PARAMETERS, MODULE_DEFAULTS


class NewModuleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModal)

        layout = QVBoxLayout(self)
        form = EditModuleFormLayout()
        quit_button = QPushButton("Cancel")
        ok_button = QPushButton("Apply")

        quit_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        ok_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        quit_button.clicked.connect(self.reject)
        ok_button.clicked.connect(self._validateModule)

        layout.addLayout(form)
        button_layout = QHBoxLayout()
        button_layout.addWidget(quit_button)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)

        self.form = form

    @property
    def module_kwargs(self):
        return self.form.module_kwargs

    def _validateModule(self):
        name = self.module_kwargs["modulename"]
        if os.path.isdir(MODULE_DIRECTORY + name):
            ErrorPopup("Module name already exists.")
        else:
            self.accept()


class AbstractModuleFormLayout(QHBoxLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._buildForm()

        readme = QPlainTextEdit()
        readme.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        self.addWidget(readme)
        self.readme = readme

    def _buildForm(self):
        form = QFormLayout()
        self.addLayout(form)
        self.form = form

        self._addFormRow(
            fieldname="board_shape",
            formname="Board Shape:",
            formlabels=("rows,", "columns"),
        )
        self._addFormRow(
            fieldname="board_nhide", formname="Hidden Rows:", formlabels="rows",
        )

        self._addFormRow(
            fieldname="move_shape",
            formname="Move Shape:",
            formlabels=("rows,", "columns"),
        )
        self._addFormRow(
            fieldname="color_limit", formname="Color Limit:", formlabels="colors"
        )
        self._addFormRow(
            fieldname="pop_limit", formname="Pop Limit:", formlabels="puyos"
        )

    def _addFormRow(self, formname, layout):
        label = QLabel(formname)
        label.setStyleSheet("font-weight: bold")
        self.form.addRow(label, layout)


class EditModuleFormLayout(AbstractModuleFormLayout):
    def __init__(self, parent=None):
        self.callbacks = []
        super().__init__(parent)

        self.readme.insertPlainText("README: ")
        self.callbacks.append(lambda: ("modulereadme", self.readme.toPlainText()))

        name = QLineEdit()
        label = QLabel("Module Name:")
        label.setStyleSheet("font-weight: bold")
        self.form.addRow(label, name)
        self.callbacks.append(lambda: ("modulename", name.text()))

    def _addFormRow(self, fieldname, formname, formlabels):
        layout = QHBoxLayout()

        formlabels = formlabels if isinstance(formlabels, tuple) else [formlabels]

        value_range = MODULE_PARAMETERS[fieldname]
        value_range = value_range if isinstance(value_range, tuple) else [value_range]

        value_def = MODULE_DEFAULTS[fieldname]
        value_def = value_def if isinstance(value_def, tuple) else [value_def]

        sub_callbacks = []

        for label, vrange, vdef in zip(formlabels, value_range, value_def):
            combo = QComboBox()
            label = QLabel(label)
            default_idx = 0
            for idx, value in enumerate(vrange):
                combo.addItem(str(value), userData=value)
                default_idx = idx if value == vdef else default_idx

            combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            combo.setCurrentIndex(default_idx)
            layout.addWidget(combo)
            layout.addWidget(label)
            sub_callbacks.append(combo.currentData)

        def reduce_callbacks(callbacks):
            result = [f() for f in callbacks]
            return tuple(result) if len(result) > 1 else result[0]

        self.callbacks.append(lambda: (fieldname, reduce_callbacks(sub_callbacks)))

        layout.addStretch()
        super()._addFormRow(formname, layout)

    @property
    def module_kwargs(self):
        return {k: v for (k, v) in [f() for f in self.callbacks]}


class ViewModuleFormLayout(AbstractModuleFormLayout):
    def __init__(self, module=None, parent=None):
        self.module = module
        super().__init__(parent)

        self.readme.setReadOnly(True)
        if module is not None:
            self.readme.insertPlainText(module.modulereadme)

    def _addFormRow(self, fieldname, formname, formlabels):
        layout = QHBoxLayout()

        if self.module is None:
            values = [""] * len(formlabels)
        else:
            values = getattr(self.module, fieldname)
            values = values if isinstance(values, tuple) else [values]

        formlabels = formlabels if isinstance(formlabels, tuple) else [formlabels]

        combined = ""
        for value, label in zip(values, formlabels):
            combined += " " + str(value) + " " + str(label)

        layout.addWidget(QLabel(combined))
        super()._addFormRow(formname, layout)
