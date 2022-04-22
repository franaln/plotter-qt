import sys

from PySide2.QtCore import (Qt,
                            QAbstractItemModel,
                            QItemSelectionModel,
                            QModelIndex,
                            Slot)
from PySide2.QtWidgets import (QAbstractItemView,
                               QMainWindow,
                               QTreeView,
                               QWidget,
                               QHBoxLayout,
                               QVBoxLayout,
                               QGridLayout,
                               QPushButton,
                               QCheckBox,
                               QSplitter)

import ROOT

from plotter.rootfile import RootFile

from plotter.file_model import TreeModel
from plotter.plot_model import PlotTable, PlotModel

from plotter.plot import Plot
from plotter.history import History
from plotter.style import default_colours

NAME    = 'plotter_qt'
VERSION = '0.1'

class MainWindow(QMainWindow):
    def __init__(self, parent=None, file_paths=[]):
        super().__init__(parent)

        #
        self.resize(1000, 800)
        self.setWindowTitle(f'{NAME} ({VERSION})')

        # Files
        # -------
        self.files = []
        file_names = []
        for i, path in enumerate(file_paths):
            print('Loading file %i: %s' % (i, path))

            f = RootFile(path)

            # check if file is valid
            if f.is_valid():
                self.files.append(f)

                file_name = path.split('/')[-1] if '/' in path else path
                file_names.append(file_name)

            else:
                pass


        # Models
        # ------
        self.file_model = TreeModel(file_names, self.files, self)
        self.plot_model = PlotModel()


        # Window
        # ------
        self.w_main = QSplitter()
        self.setCentralWidget(self.w_main)

        self.l_main = QHBoxLayout(self.w_main)

        # Left: file view
        self.w_left = QWidget()
        self.l_left = QVBoxLayout(self.w_left)

        self.file_view = QTreeView()
        self.file_view.setModel(self.file_model)

        self.file_view.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.file_view.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.file_view.setAnimated(False)
        self.file_view.setAllColumnsShowFocus(True)

        for column in range(self.file_model.columnCount()):
            self.file_view.resizeColumnToContents(column)

        # selection_model = self.file_view.selectionModel()
        # selection_model.selectionChanged.connect(self.on_select)

        self.file_view.doubleClicked.connect(self.on_double_click)
        self.file_view.clicked.connect(self.on_click)

        self.file_view.setHeaderHidden(True)
        self.file_view.expandToDepth(0)
        self.file_view.hideColumn(1)
        self.file_view.hideColumn(2)

        self.l_left.addWidget(self.file_view)

        ## Right: Plot view and buttons
        self.w_right = QWidget()
        self.l_right = QVBoxLayout(self.w_right)

        self.plot_table = PlotTable(self.plot_model)

        self.w_buttons = QWidget()
        self.l_buttons = QVBoxLayout(self.w_buttons)

        self.l_right.addWidget(self.plot_table)
        self.l_right.addWidget(self.w_buttons)


        self.check_logx = QCheckBox('x log')
        self.check_logy = QCheckBox('y log')
        self.check_ratio = QCheckBox('Ratio')

        self.button_clear = QPushButton('Clear')
        self.button_draw = QPushButton('Draw')

        self.l_buttons.addWidget(self.check_logx)
        self.l_buttons.addWidget(self.check_logy)
        self.l_buttons.addWidget(self.check_ratio)
        self.l_buttons.addWidget(self.button_clear)
        self.l_buttons.addWidget(self.button_draw)

        self.button_draw.clicked.connect(self.on_button_draw)
        self.button_clear.clicked.connect(self.on_button_clear)


        # menubar = self.menuBar()
        # file_menu = menubar.addMenu("&File")
        # self.exit_action = file_menu.addAction("E&xit")
        # self.exit_action.setShortcut("Ctrl+Q")
        # self.exit_action.triggered.connect(self.close)

        self.l_main.addWidget(self.w_left)
        self.l_main.addWidget(self.w_right)


        self.w_left.setWindowFlags(Qt.SubWindow)
        self.w_right.setWindowFlags(Qt.SubWindow)

        #         sizeGrip = QSizeGrip(myWidget);

        # QGridLayout * layout = new QGridLayout(myWidget);
        # layout->addWidget(sizeGrip, 0,0,1,1,Qt::AlignBottom | Qt::AlignRight);

        #
        self.plots = []
        self.history = History()


    ## Draw
    def draw(self):

        if not self.plot_model or self.plot_model.rowCount() < 1:
            return

        plot = Plot()

        # add objects
        first_hist_norm = None
        for (ifile, item, path, color, opts, sel) in self.plot_model.getItems():

            obj = self.files[ifile].get_object(path, sel).Clone()
            obj.SetDirectory(0)
            ROOT.SetOwnership(obj, False)
            plot.add(obj, color, opts)

        # create
        plot.create(
            logx=self.check_logx.isChecked(),
            logy=self.check_logy.isChecked()
        )

        self.plots.append(plot)
        plot.canvas.Update()
        self.history.add([ (ifile, item, path, color, opts, sel) for (ifile, item, path, color, opts, sel) in self.plot_model.getItems() ])

        self.clear_plot()

    def clear_plot(self):
        self.plot_model.clear()
        #self.update_plot_label()


    # @Slot()
    # def on_select(self):

    #     selection_model = self.file_view.selectionModel()

    #     index = selection_model.currentIndex()
    #     parent = index.parent()

    #     has_selection = not selection_model.selection().isEmpty()

    #     current_index = selection_model.currentIndex()
    #     has_current = current_index.isValid()

    #     if has_current:

    #         # self.view.close_persistent_editor(current_index)
    #         msg = f"Position: ({current_index.row()},{current_index.column()})"
    #         if not current_index.parent().isValid():
    #             msg += " in top level"
    #         self.statusBar().showMessage(msg)

    #         name, dtype, path = selection_model.model().getItem(current_index).item_data

    #         # check if item is ploteable
    #         if dtype in ('hist', 'graph', 'branch'):

    #             item = self.plot_model.rowCount()

    #             color = default_colours[item]
    #             opts = '' if item == 0 else 'same',

    #             self.plot_model.addItem((0, item, path, color, opts, ''))

    #     return


    def add_to_plot(self, index):
        name, dtype, path = self.file_model.getItem(index).item_data

        if dtype in ('hist', 'graph', 'branch'):
            idx = self.plot_model.rowCount()
            color = default_colours[idx]
            opts = '' if idx == 0 else 'same',
            self.plot_model.addItem((0, idx, path, color, opts, ''))

    @Slot()
    def on_click(self, index):
        print('click')

        if not index.isValid():
            return

        msg = f"Position: ({index.row()},{index.column()})"
        if not index.parent().isValid():
            msg += " in top level"
        self.statusBar().showMessage(msg)

        self.add_to_plot(index)


    @Slot()
    def on_double_click(self, index):
        print('doubleclick')
        self.draw()

    @Slot()
    def on_button_draw(self):
        self.draw()

    @Slot()
    def on_button_clear(self):
        self.clear_plot()
