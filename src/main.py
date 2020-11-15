from views.main_view import MainControl, MainView
from PyQt5.QtWidgets import QApplication
import sys

SKIN_DIRECTORY = "./ppvs2_skins/"
MODULE_DIRECTORY = "./modules/"

MODULE_PARAMETERS = {
    "board_shape": (range(12, 27), range(6, 17)),
    "board_nhide": range(1, 3),
    "move_shape": (range(2, 3), range(1, 3)),
    "color_limit": range(3, 6),
    "pop_limit": range(2, 7),
}


def main():
    app = QApplication([])
    view = MainView(
        skinpath=SKIN_DIRECTORY,
        modulepath=MODULE_DIRECTORY,
        moduleparams=MODULE_PARAMETERS,
    )
    control = MainControl(view)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
