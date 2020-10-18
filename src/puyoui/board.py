from PyQt5.QtWidgets import QGridLayout
from puyoui.panel import PuyoPanel

"""
Creates a grid of puyo panels to represent the board,
hidden row, and the incoming puyo to be dropped.
"""


class PuyoBoard:
    def __init__(self, skin_pixmap):
        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(0)
        self.layout.setVerticalSpacing(0)

        # Populate the grid layout with the puyo panels.
        for row in range(15):
            for col in range(6):
                if row > 1:  # First two rows hold the piece about to be placed.
                    if row == 2:  # Third row is the hidden row.
                        panel = PuyoPanel(skin_pixmap, clickable=True, opaque=True)
                    else:
                        panel = PuyoPanel(skin_pixmap, clickable=True, opaque=False)
                else:
                    panel = PuyoPanel(skin_pixmap, clickable=False, opaque=False)
                self.layout.addWidget(panel, row, col)

        # Assign panel adjacencies.
        self.assignAdjacencies(3, 15)
        self.assignAdjacencies(0, 2)

    def assignAdjacencies(self, rowmin, rowmax):
        for row in range(rowmin, rowmax):
            for col in range(6):
                this_panel = self.layout.itemAtPosition(row, col).widget()
                if row < rowmax - 1:
                    this_panel.south = self.layout.itemAtPosition(row + 1, col).widget()
                if row > rowmin:
                    this_panel.north = self.layout.itemAtPosition(row - 1, col).widget()
                if col < 5:
                    this_panel.east = self.layout.itemAtPosition(row, col + 1).widget()
                if col > 0:
                    this_panel.west = self.layout.itemAtPosition(row, col - 1).widget()

    def clear(self):
        for row in range(2, 15):
            for col in range(6):
                panel = self.layout.itemAtPosition(row, col).widget()
                panel.clear()
