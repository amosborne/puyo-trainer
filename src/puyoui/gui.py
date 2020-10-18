from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap
from puyoui.editor import Editor


def runApp():

    app = QApplication([])

    skin = QPixmap("../ppvs2_skins/gummy.png")

    editor = Editor(skin)

    return app.exec_()
