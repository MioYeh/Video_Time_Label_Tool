from PyQt5 import QtCore, QtWidgets
# from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QFileDialog
# from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QKeyEvent
from PyQt5.QtCore import QTimer, Qt, QBasicTimer
import time
import os
import json

from UI import Ui_MainWindow
from video_controller import video_controller

class MainWindow_controller(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_control()
        self.folder_path = ""  # 新增類別屬性
        self.timestamps = []

    def setup_control(self):
        self.ui.button_openfile.clicked.connect(self.open_file)
        self.ui.button_openfolder.clicked.connect(self.open_folder)
        self.ui.list_view.itemClicked.connect(self.play_video)
        self.ui.delete_button.clicked.connect(self.delete_last_line)
        self.ui.output_button.clicked.connect(self.save_to_json)
        
    def open_file(self):
        print(self.ui.all_time_label.pixmap())
        print(self.ui.all_time_label.text())
        if self.ui.all_time_label.pixmap() is not None or self.ui.all_time_label.text() != "":
            reply = QtWidgets.QMessageBox.question(self, "警告", "Label 裡面還有資料，是否繼續？",
                                         QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.No:
                return
        self.ui.all_time_label.clear()
        
        filename, filetype = QFileDialog.getOpenFileName(self, "Open file Window", "./", "Video Files(*.mp4 *.avi)") # start path        
        self.video_path = filename
        self.video_controller = video_controller(video_path=self.video_path,
                                                 ui=self.ui)
        self.ui.label_filepath.setText(f"現在正在播放: {self.video_path}")
        self.ui.button_play.clicked.connect(self.video_controller.play) # connect to function()
        self.ui.button_stop.clicked.connect(self.video_controller.stop)
        self.ui.button_pause.clicked.connect(self.video_controller.pause)
        
    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "選擇資料夾")
        if folder_path:
            self.folder_path = folder_path
            
        if folder_path:
            self.ui.list_view.clear()
            # 取得資料夾內所有影片檔案
            video_files = [f for f in os.listdir(folder_path)
                           if os.path.isfile(os.path.join(folder_path, f))
                           and f.lower().endswith(('.mp4', '.avi', '.mov'))]  # 可自行擴充副檔名
            # 將影片檔案加入列表
            for file in video_files:
                self.ui.list_view.addItem(file)
                
    def play_video(self):
        # 取得選取的影片檔案
        selected_file = self.ui.list_view.currentItem()

        # filename, filetype = QFileDialog.getOpenFileName(self, "Open file Window", "./", "Video Files(*.mp4 *.avi)") # start path        
        self.video_path = selected_file.text()
        print(self.video_path)
        print(self.folder_path)
        

        
        if selected_file:
            file_path = os.path.join(self.folder_path, selected_file.text())
            self.video_path = file_path
        self.video_controller = video_controller(video_path=self.video_path,
                                                 ui=self.ui)
        self.ui.label_filepath.setText(f"現在正在播放: {self.video_path}")
        # self.ui.label_filepath.setText(f"video path: {self.video_path}")
        self.ui.button_play.clicked.connect(self.video_controller.play)
        self.ui.button_stop.clicked.connect(self.video_controller.stop)
        self.ui.button_pause.clicked.connect(self.video_controller.pause)
        

    def delete_last_line(self):
        """刪除 QLabel 最後一行"""
        print('delete button clicked')
        lines = self.ui.all_time_label.text().split("\n")  # 拆分成多行
        if len(lines) > 1:  # 避免刪到最後一行
            lines.pop()  # 刪除最後一行
            self.ui.all_time_label.setText("\n".join(lines))  # 重新組合成文字

    def save_to_json(self):
        if len(self.ui.all_time_label.text()) != 0:
            options = QFileDialog.Options()
            file_name = os.path.basename(self.video_path).split(".")[0] + "_label.json"
            file_path, _ = QFileDialog.getSaveFileName(self, "儲存檔案", file_name, "JSON Files (*.json)", options=options)
            all_timer = []
            for i in self.ui.all_time_label.text().split("\n")[1:] :
                timer = []
                timer.append(i.split(" /")[0])
                timer.append(i.split("/ ")[1])
                all_timer.append(timer)
                
            if file_path:
                try:
                    data = {
                        "version": "1.0",
                        "video_path": self.video_path,
                        "annotations": all_timer}
                    with open(file_path, "w") as f:
                        json.dump(data, f)
                    print(f"標註已儲存至 {file_path}")
                except Exception as e:
                    print(f"儲存檔案時發生錯誤：{e}")
                
               
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_C:  # 檢查是否按下 C 鍵
            if hasattr(self, 'video_controller') is not False and self.video_controller.check_video_open():
                current_time = self.video_controller.check_video_time()
                print(current_time)
                minutes = int(current_time / 60)
                seconds = int(current_time % 60)
                milliseconds = int((current_time * 1000) % 1000)
                time_str = f"紀錄時間：{minutes:02d}:{seconds:02d}:{milliseconds:03d}"
                
                if len(self.timestamps) == 0 and current_time > 0:
                    start_time = f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"
                    self.timestamps.append(start_time)
                    print(self.timestamps)
                elif len(self.timestamps) == 1 and current_time > 0:
                    end_time = f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"
                    self.timestamps.append(end_time)
                    print(self.timestamps)
                    start_time, end_time = self.timestamps
                    time_str = f"{start_time} / {end_time}"
                    self.ui.all_time_label.setText(self.ui.all_time_label.text() + "\n" + time_str)
                    self.ui.scroll_area.verticalScrollBar().setValue(self.ui.scroll_area.verticalScrollBar().maximum())
                    self.timestamps = []
                    print(self.timestamps)
                elif len(self.timestamps) == 2 and current_time > 0:

                    start_time = f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"
                    self.timestamps.append(start_time)
                    print(self.timestamps)
                    
                self.ui.time_label.setText(time_str)  # 更新 QLabel 顯示時間
        else:
            super().keyPressEvent(event)  # 處理其他按鍵事件

            
        

 
