from PySide2.QtCore import QModelIndex, Qt, QAbstractItemModel, Signal

from plotter.rootfile import RootFile

class TreeItem:
    def __init__(self, data: list, parent: 'TreeItem' = None):
        self.item_data = data
        self.parent_item = parent
        self.child_items = []

    def child(self, number: int) -> 'TreeItem':
        if number < 0 or number >= len(self.child_items):
            return None
        return self.child_items[number]

    def lastChild(self):
        return self.child_items[-1] if self.child_items else None

    def childCount(self) -> int:
        return len(self.child_items)

    def childNumber(self) -> int:
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0

    def columnCount(self) -> int:
        return len(self.item_data)

    def data(self, column: int):
        if column < 0 or column >= len(self.item_data):
            return None
        return self.item_data[column]

    def insertChildren(self, position, count, columns):
        if position < 0 or position > len(self.child_items):
            return False

        for row in range(count):
            data = [None] * columns
            item = TreeItem(data.copy(), self)
            self.child_items.insert(position, item)

        return True

    def insertColumns(self, position, columns):
        if position < 0 or position > len(self.item_data):
            return False

        for column in range(columns):
            self.item_data.insert(position, None)

        for child in self.child_items:
            child.insert_columns(position, columns)

        return True

    def parent(self):
        return self.parent_item

    def removeChildren(self, position, count):
        if position < 0 or position + count > len(self.child_items):
            return False

        for row in range(count):
            self.child_items.pop(position)

        return True

    def removeColumns(self, position, columns):
        if position < 0 or position + columns > len(self.item_data):
            return False

        for column in range(columns):
            self.item_data.pop(position)

        for child in self.child_items:
            child.removeColumns(position, columns)

        return True

    def setDataCol(self, column: int, value):
        if column < 0 or column >= len(self.item_data):
            return False

        self.item_data[column] = value
        return True

    def setData(self, dtype, path, name):
        self.item_data = [name, dtype, path]

    def __repr__(self) -> str:
        result = f"<treeitem.TreeItem at 0x{id(self):x}"
        for d in self.item_data:
            result += f' "{d}"' if d else " <None>"
        result += f", {len(self.child_items)} children>"
        return result


class TreeModel(QAbstractItemModel):
    # Define signals
    # data_changed = Signal(QModelIndex, QModelIndex, object)
    # header_data_changed = Signal(Qt.Orientation, int, int)

    def __init__(self, file_names, root_files, parent=None):
        super().__init__(parent)

        #self.root_data = headers
        self.root_item = TreeItem(['name', 'dtype', 'path'])
        self.setupModelData(file_names, root_files, self.root_item)

    def columnCount(self, parent: QModelIndex = None) -> int:
        return self.root_item.columnCount()

    def data(self, index: QModelIndex, role: int = None):
        if not index.isValid():
            return None

        if role != Qt.DisplayRole and role != Qt.EditRole:
            return None

        item = self.getItem(index)

        return item.data(index.column())

    # def flags(self, index: QModelIndex) -> Qt.ItemFlags:
    #     if not index.isValid():
    #         return Qt.NoItemFlags

    #     return Qt.ItemIsEditable | QAbstractItemModel.flags(self, index)

    def getItem(self, index: QModelIndex = QModelIndex()) -> TreeItem:
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self.root_item

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.root_item.data(section)

        return None

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parent_item: TreeItem = self.getItem(parent)
        if not parent_item:
            return QModelIndex()

        child_item: TreeItem = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    # def insertColumns(self, position: int, columns: int,
    #                   parent: QModelIndex = QModelIndex()) -> bool:
    #     self.beginInsertColumns(parent, position, position + columns - 1)
    #     success = self.root_item.insertColumns(position, columns)
    #     self.endInsertColumns()

        return success

    # def insertRows(self, position: int, rows: int,
    #                parent: QModelIndex = QModelIndex()) -> bool:
    #     parent_item: TreeItem = self.getItem(parent)
    #     if not parent_item:
    #         return False

    #     self.beginInsertRows(parent, position, position + rows - 1)
    #     column_count = self.root_item.columnCount()
    #     success: bool = parent_item.insertChildren(position, rows, column_count)
    #     self.endInsertRows()

    #     return success

    def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child_item: TreeItem = self.getItem(index)
        if child_item:
            parent_item: TreeItem = child_item.parent()
        else:
            parent_item = None

        if parent_item == self.root_item or not parent_item:
            return QModelIndex()

        return self.createIndex(parent_item.childNumber(), 0, parent_item)

    # def removeColumns(self, position: int, columns: int,
    #                   parent: QModelIndex = QModelIndex()) -> bool:
    #     self.begin_remove_columns(parent, position, position + columns - 1)
    #     success: bool = self.root_item.remove_columns(position, columns)
    #     self.end_remove_columns()

    #     if self.root_item.columnCount() == 0:
    #         self.remove_rows(0, self.row_count())

    #     return success

    # def removeRows(self, position: int, rows: int,
    #                parent: QModelIndex = QModelIndex()) -> bool:
    #     parent_item: TreeItem = self.getItem(parent)
    #     if not parent_item:
    #         return False

    #     self.begin_remove_rows(parent, position, position + rows - 1)
    #     success: bool = parent_item.removeChildren(position, rows)
    #     self.end_remove_rows()

    #     return success

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid() and parent.column() > 0:
            return 0

        parent_item: TreeItem = self.getItem(parent)
        if not parent_item:
            return 0
        return parent_item.childCount()

    # def set_data(self, index: QModelIndex, value, role: int) -> bool:
    #     if role != Qt.EditRole:
    #         return False

    #     item: TreeItem = self.get_item(index)
    #     result: bool = item.set_data(index.column(), value)

    #     if result:
    #         self.data_changed.emit(index, index, [Qt.DisplayRole, Qt.EditRole])

    #     return result

    # def set_header_data(self, section: int, orientation: Qt.Orientation, value,
    #                   role: int = None) -> bool:
    #     if role != Qt.EditRole or orientation != Qt.Horizontal:
    #         return False

    #     result: bool = self.root_item.set_data(section, value)

    #     if result:
    #         # todo: Check if emit headerDataChanged signal is correct
    #         # emit headerDataChanged(orientation, section, section)
    #         self.header_data_changed(orientation, section, section)

        return result

    def setupModelData(self, file_names, root_files, parent):

        for name, root_file in zip(file_names, root_files):

            parent.insertChildren(parent.childCount(), 1, 2)
            file_item = parent.lastChild()
            file_item.setData('file', name, name)

            for i, (depth, dtype, path, name) in enumerate(root_file):

                print(depth, dtype, path, name)
                if depth == 0:
                    file_item.insertChildren(file_item.childCount(), 1, 2)
                    file_item.lastChild().setData(dtype, path, name)
                else:
                    last = file_item.lastChild()
                    last.insertChildren(last.childCount(), 1, 2)
                    last.lastChild().setData(dtype, path, name)


    def _repr_recursion(self, item: TreeItem, indent: int = 0) -> str:
        result = " " * indent + repr(item) + "\n"
        for child in item.child_items:
            result += self._repr_recursion(child, indent + 2)
        return result

    def __repr__(self) -> str:
        return self._repr_recursion(self.root_item)
