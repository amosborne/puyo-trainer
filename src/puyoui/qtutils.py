def deleteItemsOfLayout(layout):
    if layout is not None:
        while layout.count():
            deleteItemOfLayout(layout, 0)


def deleteItemOfLayout(layout, index):
    item = layout.takeAt(index)
    widget = item.widget()
    if widget is not None:
        widget.setParent(None)
    else:
        deleteItemsOfLayout(item.layout())
