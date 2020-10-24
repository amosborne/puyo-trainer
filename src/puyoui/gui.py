from PyQt5.QtWidgets import QApplication
from puyoui.editorview import EditorView
from puyolib.puyomodel import PuyoPuzzleModel, PuyoGridGraphicsModel
from puyoapp.editorcontrol import EditorController


def runApp():

    app = QApplication([])

    graphics = PuyoGridGraphicsModel("../ppvs2_skins/gummy.png")

    puzzle = PuyoPuzzleModel.new((12, 6), 1)
    editor_window = EditorView(
        graphics, puzzle.board, puzzle.nhide, puzzle.drawpile, npreview=2
    )

    win = EditorController(puzzle, editor_window)

    return app.exec_()
