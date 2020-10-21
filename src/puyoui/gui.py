from PyQt5.QtWidgets import QApplication, QMainWindow

# from PyQt5.QtGui import QPixmap
# from puyoui.editor import Editor
from puyoui.puyoview import PuyoView, PuyoGridView
from functools import partial


def runApp():

    app = QApplication([])
    win = QMainWindow()

    pgv = PuyoGridView(
        size=(2, 2),
        skin_file="../ppvs2_skins/gummy.png",
        click_callback=lambda x: print(x),
        init_rect=(0, 0, 32, 32),
        init_opacity=1,
        isframed=True,
    )

    win.setCentralWidget(pgv)
    win.show()

    return app.exec_()
