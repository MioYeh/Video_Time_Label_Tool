import sys
from PyQt5.QtWidgets import QApplication
from ui import VideoPlayer

if __name__ == '__main__':
    language = 'Chinese' #English
    app = QApplication(sys.argv)
    player = VideoPlayer(language)
    player.show()
    sys.exit(app.exec_())
