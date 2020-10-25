from PyQt5.QtWidgets import QApplication
from puyolib.puzzlemodel import PuzzleModel  # model
from puyoapp.editorcontrol import EditorVC  # view-controller


def runApp():

    app = QApplication([])

    skin = "../ppvs2_skins/gummy.png"

    puzzlemodel = PuzzleModel(
        board_size=(12, 6), board_nhide=1, drawpile_elem_size=(3, 3)
    )

    editor = EditorVC(puzzlemodel, skin)

    editor.view.show()

    return app.exec_()
