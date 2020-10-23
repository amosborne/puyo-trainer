from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout

# from PyQt5.QtGui import QPixmap
# from puyoui.editor import Editor
from puyoui.puyoview import PuyoView, PuyoGridView
from puyoui.editorview import DrawpileView
from puyolib.puyomodel import PuyoPuzzleModel, PuyoGridGraphicsModel


def runApp():

    app = QApplication([])
    win = QMainWindow()
    widget = QWidget()
    win.setCentralWidget(widget)

    puzzlemodel = PuyoPuzzleModel.new((12, 6), 1)
    graphicsmodel = PuyoGridGraphicsModel("../ppvs2_skins/gummy.png")

    # puyogrid = PuyoGridView(
    #    graphicsmodel, puzzlemodel.board, puzzlemodel.nhide, isframed=True
    # )

    # puyogrid.clicked.connect(lambda pos: processClick(puzzlemodel, puyogrid, pos))

    drawpileview = DrawpileView(graphicsmodel, puzzlemodel.drawpile)
    drawpileview.click_insert.connect(
        lambda index: insertDrawpile(puzzlemodel, drawpileview, index)
    )
    drawpileview.click_delete.connect(
        lambda index: deleteDrawpile(puzzlemodel, drawpileview, index)
    )
    drawpileview.click_puyos.connect(
        lambda pos: changeDrawpile(puzzlemodel, drawpileview, pos)
    )

    layout = QHBoxLayout(widget)
    layout.addWidget(drawpileview)

    win.show()

    return app.exec_()


def changeDrawpile(model, view, pos):
    puyo = model.drawpile[pos]
    model.drawpile[pos] = puyo.nextColor()
    view.setGraphics(model.drawpile)


def insertDrawpile(model, view, index):
    model.newDrawpileElem(index + 1)
    view.setGraphics(model.drawpile)


def deleteDrawpile(model, view, index):
    if view.count() > 2:
        model.delDrawpileElem(index)
        view.setGraphics(model.drawpile)
