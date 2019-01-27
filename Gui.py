import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5 import uic


class MapperGui(QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(1280, 800)
        self.setWindowTitle("Image Template Mapper")
        self.setStyleSheet("background-color:white;")
        uic.loadUi('mainwindow.ui', self)

        # Center the screen
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())





        self.show()


if __name__ == '__main__':
    app = QApplication([])
    window = MapperGui()

    sys.exit(app.exec())