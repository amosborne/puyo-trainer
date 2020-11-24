from PyQt5.QtWidgets import QApplication
from viewcontrols import MainControl
import sys


def main():
    app = QApplication([])
    _ = MainControl()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
