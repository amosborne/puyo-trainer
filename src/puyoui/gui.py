from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout

# from PyQt5.QtGui import QPixmap
# from puyoui.editor import Editor
from puyoui.puyoview import PuyoView, PuyoGridView
from puyoui.editorview import DrawpileElementView
from puyolib.puyomodel import PuyoPuzzleModel, PuyoGridGraphicsModel


def runApp():

    app = QApplication([])
    win = QMainWindow()
    widget = QWidget()
    win.setCentralWidget(widget)

    puzzlemodel = PuyoPuzzleModel.new((12, 6), 1)
    graphicsmodel = PuyoGridGraphicsModel("../ppvs2_skins/gummy.png")

    puyogrid = PuyoGridView(
        graphicsmodel, puzzlemodel.board, puzzlemodel.nhide, isframed=True
    )

    puyogrid.clicked.connect(lambda pos: processClick(puzzlemodel, puyogrid, pos))

    layout = QVBoxLayout(widget)
    layout.addWidget(puyogrid)

    win.show()

    return app.exec_()


def processClick(model, view, pos):
    puyo = model.board[pos]
    model.board[pos] = puyo.next()
    view.setGraphics(model.board)
