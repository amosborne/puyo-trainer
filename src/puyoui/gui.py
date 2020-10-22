from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout

# from PyQt5.QtGui import QPixmap
# from puyoui.editor import Editor
from puyoui.puyoview import PuyoView, PuyoGridView
from puyoui.editorview import DrawpileElementView
from puyolib.puyomodel import PuyoPuzzleModel


def runApp():

    app = QApplication([])
    win = QMainWindow()
    widget = QWidget()
    win.setCentralWidget(widget)

    puyogrid = PuyoGridView(
        skin="../ppvs2_skins/gummy.png",
        rects=[[(0, 0, 32, 32) for _ in range(6)] for _ in range(13)],
        opacities=[[1 for _ in range(6)] for _ in range(13)],
        isframed=True,
    )

    puyogrid.clicked.connect(lambda x: print(x))

    layout = QVBoxLayout(widget)
    layout.addWidget(puyogrid)

    win.show()

    pz = PuyoPuzzleModel.new(13, 6)
    puyogrid.setGraphics(*pz.getBoardGraphics())

    return app.exec_()
