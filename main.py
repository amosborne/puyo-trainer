import sys
from PyQt5.QtWidgets import QApplication, QMainWindow


def main():

    app = QApplication(sys.argv)

    w = QMainWindow()
    w.setWindowTitle("Puyo Trainer")
    w.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
