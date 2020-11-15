from PyQt5.QtWidgets import QApplication
from models.puzzle_module import PuzzleModule  # model
from controls.edit_control import EditorVC  # view-controller
import shutil
import os


def run_app():

    app = QApplication([])

    skin = "./ppvs2_skins/gummy.png"
    print(os.path.isfile(skin))
    print(os.getcwd())

    name = "dryrun"
    module = PuzzleModule.new(
        modulename=name,
        board_shape=(12, 6),
        board_nhide=1,
        move_shape=(2, 1),
        color_limit=4,
        pop_limit=4,
        modulereadme="",
    )
    puzzle = module.new_puzzle()
    shutil.rmtree("./modules/" + name + "/")

    editor = EditorVC(puzzle, skin)

    editor.view.show()

    return app.exec_()
