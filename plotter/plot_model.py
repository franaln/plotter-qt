from PySide2.QtCore import Qt, QModelIndex, QAbstractTableModel
from PySide2.QtWidgets import QWidget, QTableView, QHeaderView, QHBoxLayout, QSizePolicy

from PySide2 import QtGui

from plotter.style import colourdict

class PlotModel(QAbstractTableModel):

    def __init__(self, data=None):
        QAbstractTableModel.__init__(self)

        self._headers = ['File', 'Item', 'Path', 'Color', 'Options', 'Selection']
        self._data = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._headers[section]
        else:
            return f"{section}"

    def data(self, index, role=Qt.DisplayRole):

        col = index.column()
        row = index.row()

        if role == Qt.DisplayRole:
            return self._data[row][col]
        elif role == Qt.BackgroundRole:
            return QtGui.QColor(Qt.white)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft
        elif role == Qt.DecorationRole:
            if col == 3:
                return QtGui.QColor(colourdict[self._data[row][col]])

        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEditable | QAbstractTableModel.flags(self, index)

    def setData(self, index: QModelIndex, value, role: int) -> bool:
        if role != Qt.EditRole:
            return False

        if not value:
            return False

        col, row = index.column(), index.row()

        self._data[row][col] = value

        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])

        return True

    def addItem(self, data):

        parent = QModelIndex()

        self.beginInsertRows(parent, 1, 1)
        self.insertRow(self.rowCount(), parent)
        self._data.append(list(data))
        self.endInsertRows()

        return

    def getItems(self):
        for item in self._data:
            yield item

    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount()-1)
        self._data.clear()
        self.endRemoveRows()



#     def removeItem(self, position: int, rows: int,
#                    parent: QModelIndex = QModelIndex()) -> bool:
#         parent_item = self.getItem(parent)
#         if not parent_item:
#             return False

#         self.begin_remove_rows(parent, position, position + rows - 1)
#         success: bool = parent_item.removeChildren(position, rows)
#         self.end_remove_rows()

#         return success

#     def _repr_recursion(self, item: PlotItem, indent: int = 0) -> str:
#         result = ">> " * indent + repr(item) + "\n"
#         for child in item.child_items:
#             result += self._repr_recursion(child, indent + 2)
#         return result

#     def __repr__(self) -> str:
#         return self._repr_recursion(self.root_item)


class PlotTable(QWidget):
    def __init__(self, model):

        QWidget.__init__(self)

        # Creating a QTableView
        self.view = QTableView()
        self.view.setModel(model)

        self.view.setAlternatingRowColors(True)
        # self.plot_view.setSelectionBehavior(QAbstractItemView.SelectItems)
        #self.plot_view.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        # self.plot_view.setAnimated(False)
        # self.plot_view.setAllColumnsShowFocus(True)

        self.view.hideColumn(0)
        self.view.hideColumn(1)

        # QTableView Headers
        self.h_header = self.view.horizontalHeader()
        self.h_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.h_header.setStretchLastSection(True)
        self.view.verticalHeader().hide()

        # QWidget Layout
        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        ## Left layout
        size.setHorizontalStretch(1)
        self.view.setSizePolicy(size)
        self.main_layout.addWidget(self.view)

        # Set the layout to the QWidget
        self.setLayout(self.main_layout)
