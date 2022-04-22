import sys

from PySide2.QtWidgets import QApplication

from plotter.mainwindow import MainWindow

if __name__ == '__main__':
    app = QApplication()
    window = MainWindow(None, sys.argv[1:])
    window.show()
    sys.exit(app.exec_())
