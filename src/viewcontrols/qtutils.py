from PyQt5.QtWidgets import QMessageBox


def ErrorPopup(msg, parent=None):
    error_dialog = QMessageBox(parent)
    error_dialog.setText(msg)
    error_dialog.exec_()


def deleteItemsOfLayout(layout):
    if layout is not None:
        while layout.count():
            deleteItemOfLayout(layout, 0)


def deleteItemOfLayout(layout, index):
    item = layout.takeAt(index)
    widget = item.widget()
    if widget is not None:
        widget.deleteLater()
    else:
        deleteItemsOfLayout(item.layout())
