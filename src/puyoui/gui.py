from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout

# from PyQt5.QtGui import QPixmap
# from puyoui.editor import Editor
from puyoui.puyoview import PuyoView, PuyoGridView
from puyoui.editorview import PuzzleDefineView
from puyolib.puyomodel import PuyoPuzzleModel, PuyoGridGraphicsModel


def runApp():

    app = QApplication([])
    win = QMainWindow()
    widget = QWidget()
    win.setCentralWidget(widget)

    puzzlemodel = PuyoPuzzleModel.new((12, 6), 1)
    graphicsmodel = PuyoGridGraphicsModel("../ppvs2_skins/gummy.png")

    defineview = PuzzleDefineView(
        graphicsmodel, puzzlemodel.board, puzzlemodel.nhide, puzzlemodel.drawpile
    )

    defineview.click_drawpile_insert.connect(
        lambda index: insertDrawpileElem(puzzlemodel, defineview, index)
    )
    defineview.click_drawpile_delete.connect(
        lambda index: delDrawpileElem(puzzlemodel, defineview, index)
    )
    defineview.click_drawpile_puyos.connect(
        lambda pos: changeDrawpileElem(puzzlemodel, defineview, pos)
    )
    defineview.click_board_puyos.connect(
        lambda pos: changeBoardElem(puzzlemodel, defineview, pos)
    )
    defineview.click_clear_board.connect(lambda: clearBoard(puzzlemodel, defineview))
    defineview.click_reset_drawpile.connect(
        lambda: resetDrawpile(puzzlemodel, defineview)
    )
    defineview.click_start.connect(lambda: print("Start"))

    layout = QHBoxLayout(widget)
    layout.addWidget(defineview)

    win.show()

    return app.exec_()


def clearBoard(model, view):
    model.clearBoard()
    view.setBoardGraphics(model.board)


def resetDrawpile(model, view):
    model.resetDrawpile()
    view.setDrawpileGraphics(model.drawpile)


def changeBoardElem(model, view, pos):
    puyo = model.board[pos]
    model.board[pos] = puyo.next()
    view.setBoardGraphics(model.board)


def changeDrawpileElem(model, view, pos):
    puyo = model.drawpile[pos]
    model.drawpile[pos] = puyo.nextColor()
    view.setDrawpileGraphics(model.drawpile)


def insertDrawpileElem(model, view, index):
    model.newDrawpileElem(index + 1)
    view.setDrawpileGraphics(model.drawpile)


def delDrawpileElem(model, view, index):
    if model.drawpile.shape[0] > 2:
        model.delDrawpileElem(index)
        view.setDrawpileGraphics(model.drawpile)
