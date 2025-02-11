# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1010, 900)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.label_videoframe = QtWidgets.QLabel(self.centralwidget)
        self.label_videoframe.setGeometry(QtCore.QRect(40, 50, 800, 450))
        self.label_videoframe.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.label_videoframe.setObjectName("label_videoframe")
    
        
        ''' File Floder and list view '''
        self.button_openfile = QtWidgets.QPushButton(self.centralwidget)
        self.button_openfile.setGeometry(QtCore.QRect(850, 50, 150, 30))
        # self.button_openfile.setGeometry(QtCore.QRect(20, 550, 113, 32))
        self.button_openfile.setObjectName("button_openfile")
        
        self.button_openfolder = QtWidgets.QPushButton(self.centralwidget)
        self.button_openfolder.setGeometry(QtCore.QRect(850, 85, 150, 30))
        # self.button_openfolder.setGeometry(QtCore.QRect(20, 600, 113, 32))
        self.button_openfolder.setObjectName("button_openfolder")
     
        self.list_view = QtWidgets.QListWidget(self.centralwidget)
        # self.list_view.setGeometry(QtCore.QRect(20, 640, 180, 100))
        self.list_view.setGeometry(QtCore.QRect(850, 120, 150, 350))
        
        ''' END File Floder and list view '''
        
        '''Button Play, Stop, Pause'''
        self.button_play = QtWidgets.QPushButton(self.centralwidget)
        self.button_play.setGeometry(QtCore.QRect(920, 545, 80, 32))
        self.button_play.setObjectName("button_play")
        
        self.button_stop = QtWidgets.QPushButton(self.centralwidget)
        self.button_stop.setGeometry(QtCore.QRect(755, 545, 80, 32))
        self.button_stop.setObjectName("button_stop")
        
        self.button_pause = QtWidgets.QPushButton(self.centralwidget)
        self.button_pause.setGeometry(QtCore.QRect(840, 545, 80, 32))
        self.button_pause.setObjectName("button_pause")
        ''' END Button Play, Stop, Pause'''
        
        '''Show file path'''
        self.label_filepath = QtWidgets.QLabel(self.centralwidget)
        self.label_filepath.setGeometry(QtCore.QRect(40, 500, 841, 41))
        # self.label_filepath.setGeometry(QtCore.QRect(40, 790, 841, 41))
        self.label_filepath.setObjectName("label_filepath")
        '''END Show file path'''
        
        '''Slider and frame count'''
        self.slider_videoframe = QtWidgets.QSlider(self.centralwidget)
        self.slider_videoframe.setGeometry(QtCore.QRect(40, 550, 550, 22))
        # self.slider_videoframe.setGeometry(QtCore.QRect(150, 560, 531, 22))
        self.slider_videoframe.setOrientation(QtCore.Qt.Horizontal)
        self.slider_videoframe.setObjectName("slider_videoframe")
        
        self.label_framecnt = QtWidgets.QLabel(self.centralwidget)
        self.label_framecnt.setGeometry(QtCore.QRect(600, 550, 171, 21))
        self.label_framecnt.setObjectName("label_framecnt")
        '''END Slider and frame count'''
        
        '''Time label'''
        self.time_label = QtWidgets.QLabel(self.centralwidget)
        self.time_label.setGeometry(QtCore.QRect(600, 600, 171, 21))
        '''END Time label'''
        
        '''All check time'''
        self.cry_label = QtWidgets.QLabel(self.centralwidget)
        self.cry_label.setGeometry(QtCore.QRect(40, 500, 150, 200))
        
        self.all_time_label = QtWidgets.QLabel(self.centralwidget)
        self.all_time_label.setWordWrap(True)
        
        self.scroll_area = QtWidgets.QScrollArea(self.centralwidget)
        self.scroll_area.setGeometry(QtCore.QRect(40, 610, 150, 150)) #200
        self.scroll_area.setWidgetResizable(True)  # 讓 QLabel 隨著內容增長
        self.scroll_area.setWidget(self.all_time_label)

        self.delete_button = QtWidgets.QPushButton(self.centralwidget)
        self.delete_button.setGeometry(QtCore.QRect(40, 765, 150, 32))
        '''END All check time'''
        
        '''Output bottom'''
        self.selectSaveLocationButton = QtWidgets.QPushButton(self.centralwidget)
        # self.selectSaveLocationButton.clicked.connect(self.selectSaveLocation)
        self.selectSaveLocationButton.setGeometry(QtCore.QRect(40, 15, 150, 30))
        self.saveFolderPath = QtWidgets.QLabel(self.centralwidget)
        self.saveFolderPath.setGeometry(QtCore.QRect(200, 15, 150, 30))

        self.output_button = QtWidgets.QPushButton(self.centralwidget)
        self.output_button.setGeometry(QtCore.QRect(850, 475, 150, 30))
        '''END Output bottom'''
        
        
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "GM Video Label Player"))
        self.label_videoframe.setText(_translate("MainWindow", ""))
        self.button_openfile.setText(_translate("MainWindow", "開啟影片檔案"))
        self.button_openfolder.setText(_translate("MainWindow", "開啟影片資料夾"))
        # self.list_view.setText(_translate("MainWindow", "list_view"))
        self.label_framecnt.setText(_translate("MainWindow", "current_frame/total_frame"))
        self.button_play.setText(_translate("MainWindow", "Play"))
        self.button_stop.setText(_translate("MainWindow", "Stop"))
        self.label_filepath.setText(_translate("MainWindow", "現在正在播放:"))
        self.button_pause.setText(_translate("MainWindow", "Pause"))
        self.time_label.setText(_translate("MainWindow", "紀錄時間：--:--:--"))
        self.all_time_label.setText(_translate("MainWindow", ""))
        self.delete_button.setText(_translate("MainWindow", "刪除最後一行"))
        self.output_button.setText(_translate("MainWindow", "存檔"))
        self.cry_label.setText(_translate("MainWindow", "標註Cry，按下C開始記錄"))
        self.selectSaveLocationButton.setText(_translate("MainWindow", "選擇儲存位置"))
        self.saveFolderPath.setText(_translate("MainWindow", ""))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())