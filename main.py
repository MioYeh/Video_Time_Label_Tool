from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QBasicTimer
from PyQt5.QtGui import QImage, QPixmap, QKeyEvent
from controller import MainWindow_controller

            
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow_controller()
    window.show()
    sys.exit(app.exec_())