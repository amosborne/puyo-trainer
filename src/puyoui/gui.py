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

    # puzzlemodel = PuyoPuzzleModel.new((12, 6), 1)
    graphicsmodel = PuyoGridGraphicsModel("../ppvs2_skins/gummy.png")

    # puyogrid = PuyoGridView(
    #    graphicsmodel, puzzlemodel.board, puzzlemodel.nhide, isframed=True
    # )

    # puyogrid.clicked.connect(lambda pos: processClick(puzzlemodel, puyogrid, pos))

    grid = PuyoPuzzleModel.new((2, 1), 0)

    drawpile_elem = DrawpileElementView(graphicsmodel, grid.board, parent=widget)
    drawpile_elem.click_insert.connect(lambda: print("insert"))
    drawpile_elem.click_delete.connect(lambda: print("delete"))
    drawpile_elem.click_puyos.connect(
        lambda pos: processClick(grid, drawpile_elem, pos)
    )

    win.show()

    return app.exec_()


def processClick(model, view, pos):
    puyo = model.board[pos]
    model.board[pos] = puyo.next()
    view.setGraphics(model.board)
    view.setIndex(2)
