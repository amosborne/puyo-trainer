from PyQt5.QtWidgets import QApplication, QMainWindow
from puyoui.puyoview import PuyoGridView
from puyolib.puyogridmodel import AbstractPuyoGridModel
from puyolib.puyographicmodel import PuyoGraphicModel

from puyolib.puyomodel import Puyo

# from puyoui.editorview import EditorView
# from puyolib.puyomodel import PuyoPuzzleModel, PuyoGridGraphicsModel
# from puyoapp.editorcontrol import EditorController


def runApp():

    app = QApplication([])

    win = QMainWindow()

    boardmodel = AbstractPuyoGridModel((12, 6), 1)
    boardmodel[:, 2] = Puyo.RED
    boardmodel[4, :] = Puyo.BLUE
    graphicmodel = PuyoGraphicModel("../ppvs2_skins/gummy.png", boardmodel)
    boardview = PuyoGridView(graphicmodel, isframed=True)

    win.setCentralWidget(boardview)
    win.show()

    boardmodel[6, :] = Puyo.GREEN
    boardview.updateView()
    # graphics = PuyoGridGraphicsModel("../ppvs2_skins/gummy.png")

    # puzzle = PuyoPuzzleModel.new((12, 6), 1)
    # editor_window = EditorView(graphics, puzzle.board, puzzle.nhide, puzzle.drawpile)

    # win = EditorController(puzzle, editor_window)

    return app.exec_()
