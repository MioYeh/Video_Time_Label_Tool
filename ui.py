import sys
import os
import cv2
import time
import json

from PyQt5.QtWidgets import (
    QLabel,
    QWidget,
    QSlider,
    QTextEdit,
    # QComboBox,
    QPushButton,
    QFileDialog,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QMessageBox,
    QApplication
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QIcon

from controller import VideoController
# from video_controller import ButtonController
from utils import load_json, save_json


class VideoPlayer(QWidget):
    def __init__(self, language):
        super().__init__()
        self.controller = VideoController(self)
        self.screen = QApplication.desktop()
        self.language = language
        
        self.initUI()
        self.video_path = None
        self.cap = None
        self.paused = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.nextFrame)
        self.playback_rate = 1.0
        self.start_name = "pause"
        self.version = "1.0.4"
        self.recording = False
        self.save_check = True
        self.start_time = None
        self.start_times = {"C": None, "W": None, "R": None}
        self.screen = QApplication.desktop()

    def initUI(self):
        if self.screen.width() <= 1440 or self.screen.height() <= 1440:
            self.video_width = 640
            self.video_height = 480
        else:
            self.video_width = 960
            self.video_height = 720


        self.setWindowTitle("Video Time Label Tool")
        self.setWindowIcon(QIcon('./lab_icon.ico'))
        self.setGeometry(100, 100, self.video_width + 400, self.video_height + 50)

        self.video_label = QLabel(self)
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setFixedSize(self.video_width, self.video_height)
        
        self.video_path_label = QLabel("Video Path: No video selected")
        # self.video_path_label = QLabel("影片路徑：沒有影片被選取" if self.language == 'Chinese' else "Video Path: No video selected")
        self.label_path_label = QLabel("Label Path: No label selected")
        # self.label_path_label = QLabel("標註路徑：沒有標註被選取" if self.language == 'Chinese' else "Label Path: No label selected")
        self.video_path_label.setWordWrap(True)
        self.label_path_label.setWordWrap(True)

        self.play_button = QPushButton("播放" if self.language == 'Chinese' else "Play", self)
        self.play_button.clicked.connect(self.play_video)

        self.pause_button = QPushButton("暫停" if self.language == 'Chinese' else "Pause", self)
        self.pause_button.clicked.connect(self.pause_video)

        self.stop_button = QPushButton("停止" if self.language == 'Chinese' else "Stop", self)
        self.stop_button.clicked.connect(self.stop_video)

        self.faster_button = QPushButton("加快" if self.language == 'Chinese' else "Faster", self)
        self.faster_button.clicked.connect(self.speed_up)

        self.normal_button = QPushButton("正常" if self.language == 'Chinese' else "Normal", self)
        self.normal_button.clicked.connect(self.original_speed)

        self.slower_button = QPushButton("放慢" if self.language == 'Chinese' else "Slower", self)
        self.slower_button.clicked.connect(self.slow_down)

        self.open_button = QPushButton("開啟檔案" if self.language == 'Chinese' else "Open File", self)
        self.open_button.clicked.connect(self.openFile)

        self.folder_button = QPushButton("開啟資料夾" if self.language == 'Chinese' else "Open Folder", self)
        self.folder_button.clicked.connect(self.openFolder)

        self.save_button = QPushButton("輸出紀錄" if self.language == 'Chinese' else "Export Labels", self)
        self.save_button.clicked.connect(self.save_records)

        self.load_button = QPushButton("讀取紀錄" if self.language == 'Chinese' else "Import Labels", self)
        self.load_button.clicked.connect(self.load_records)

        self.prev_button = QPushButton("<")
        self.prev_button.clicked.connect(self.play_prev)
        
        self.next_button = QPushButton(">")
        self.next_button.clicked.connect(self.play_next)
        
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.sliderMoved.connect(self.setPosition)

        self.time_label = QLabel("00:00:00.0 / 00:00:00.0", self)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.loadSelectedVideo)

        # -----設定不同紀錄框和刪除按鈕-----
        self.record_c_label = QLabel("Time:")
        self.record_w_label = QLabel("Time:")
        self.record_r_label = QLabel("Time:")

        self.record_c_list = QListWidget()
        self.record_w_list = QListWidget()
        self.record_r_list = QListWidget()

        self.record_c_list.setSelectionMode(QListWidget.SingleSelection)
        self.record_c_list.itemClicked.connect(self.SelectLabel)
        self.record_w_list.setSelectionMode(QListWidget.SingleSelection)
        self.record_w_list.itemClicked.connect(self.SelectLabel)
        self.record_r_list.setSelectionMode(QListWidget.SingleSelection)
        self.record_r_list.itemClicked.connect(self.SelectLabel)

        self.delete_c_record_button = QPushButton("Delete Record", self)
        self.delete_c_record_button.clicked.connect(self.controller.delete_c_selected_record)
        self.delete_w_record_button = QPushButton("Delete Record", self)
        self.delete_w_record_button.clicked.connect(self.controller.delete_w_selected_record)
        self.delete_r_record_button = QPushButton("Delete Record", self)
        self.delete_r_record_button.clicked.connect(self.controller.delete_r_selected_record)
        # ---------------------------------

        self.record_area = QTextEdit()
        self.record_area.setReadOnly(True)
        self.record_scroll = QScrollArea()
        self.record_scroll.setWidgetResizable(True)
        self.record_scroll.setWidget(self.record_area)

        prev_next_layout = QHBoxLayout()
        prev_next_layout.addWidget(self.prev_button)
        prev_next_layout.addWidget(self.next_button)
        
        list_layout = QVBoxLayout()
        list_layout.addWidget(QLabel("Video List"))
        list_layout.addWidget(self.list_widget)
        list_layout.addLayout(prev_next_layout)

        list_path_layout = QHBoxLayout()
        list_path_layout.addLayout(list_layout)
        list_path_layout.addWidget(self.video_label)
        
        save_layout = QHBoxLayout()
        save_layout.addWidget(self.open_button)
        save_layout.addWidget(self.folder_button)
        save_layout.addWidget(self.load_button)
        save_layout.addWidget(self.save_button)

        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.time_label)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.pause_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.slower_button)
        controls_layout.addWidget(self.normal_button)
        controls_layout.addWidget(self.faster_button)

        path_layout = QVBoxLayout()
        path_layout.addWidget(self.video_path_label)
        path_layout.addWidget(self.label_path_label)

        # ------------reocrd list------------
        down_layout = QVBoxLayout()
        down_layout_list_1 = QVBoxLayout()
        down_layout_list_1.addWidget(QLabel("C Records:"))
        down_layout_list_1.addWidget(self.record_c_label)
        down_layout_list_1.addWidget(self.record_c_list)
        down_layout_list_1.addWidget(self.delete_c_record_button)

        down_layout_list_2 = QVBoxLayout()
        down_layout_list_2.addWidget(QLabel("W Records:"))
        down_layout_list_2.addWidget(self.record_w_label)
        down_layout_list_2.addWidget(self.record_w_list)
        down_layout_list_2.addWidget(self.delete_w_record_button)

        down_layout_list_3 = QVBoxLayout()
        down_layout_list_3.addWidget(QLabel("R Records:"))
        down_layout_list_3.addWidget(self.record_r_label)
        down_layout_list_3.addWidget(self.record_r_list)
        down_layout_list_3.addWidget(self.delete_r_record_button)

        down_layout.addLayout(down_layout_list_1)
        down_layout.addLayout(down_layout_list_2)
        down_layout.addLayout(down_layout_list_3)
        list_path_layout.addLayout(down_layout)
        # -----------------------------------
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(list_path_layout)
        main_layout.addLayout(path_layout)
        main_layout.addLayout(save_layout)
        main_layout.addLayout(slider_layout)
        main_layout.addLayout(controls_layout)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setLayout(main_layout)

    def play_prev(self):
        if self.check_save():
            if hasattr(self, "folder_path") and self.folder_path:
                if self.current_index > 0:
                    self.current_index -= 1
                    self.loadPrevNextVideo()

    def play_next(self):
        if self.check_save():
            if hasattr(self, "folder_path") and self.folder_path:
                if self.current_index < len(self.video_files) - 1:
                    self.current_index += 1
                    self.loadPrevNextVideo()

    def check_save(self):
        if self.save_check == False:
            reply = QMessageBox.question(self, "警告", "Label尚未存檔，是否繼續開啟新影片？",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
            elif reply == QMessageBox.Yes:
                self.save_check = True
                return True
        elif self.save_check == True:
            return True

    def openFile(self):
        if self.check_save():
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv)"
            )
            if file_path:
                self.loadVideo(file_path)
                self.controller.clear_records()
                self.video_path_label.setText(f"Video Path: {file_path}")
                json_path = os.path.splitext(self.video_path)[0] + ".json"
                if os.path.exists(json_path) and os.path.isfile(json_path):
                    try:
                        records = load_json(json_path)
                        for item in records.get("C", []):
                            self.record_c_list.addItem(item)
                        for item in records.get("W", []):
                            self.record_w_list.addItem(item)
                        for item in records.get("R", []):
                            self.record_r_list.addItem(item)
                        self.label_path_label.setText(f"Label Path: {json_path}")
                    except Exception as e:
                        self.label_path_label.setText("Label Path: Fail load label")

    def openFolder(self):
        if self.check_save():
            folder_path = QFileDialog.getExistingDirectory(self, "Open Folder")
            if folder_path:
                self.folder_path = folder_path
                self.list_widget.clear()
                self.video_files = [
                    f
                    for f in os.listdir(folder_path)
                    if os.path.isfile(os.path.join(folder_path, f))
                    and f.lower().endswith((".mp4", ".avi", ".mov"))
                ]
                self.current_index = 0

                for file in self.video_files:
                    self.list_widget.addItem(file)

    def loadPrevNextVideo(self):
        if self.check_save():
            if hasattr(self, "folder_path") and self.folder_path:
                file_path = os.path.join(self.folder_path, self.video_files[self.current_index])
                self.list_widget.setCurrentRow(self.current_index)
                self.controller.clear_records()
                self.loadVideo(file_path)
                self.video_path_label.setText(f"Video Path: {file_path}")
                json_path = os.path.splitext(self.video_path)[0] + ".json"
                if os.path.exists(json_path) and os.path.isfile(json_path):
                    try:
                        records = load_json(json_path)
                        for item in records.get("C", []):
                            self.record_c_list.addItem(item)
                        for item in records.get("W", []):
                            self.record_w_list.addItem(item)
                        for item in records.get("R", []):
                            self.record_r_list.addItem(item)
                        self.label_path_label.setText(f"Label Path: {json_path}")
                    except Exception as e:
                        self.label_path_label.setText("Label Path: Fail load label")
                else:
                    self.label_path_label.setText("Label Path: No label selected")
                    
    def loadSelectedVideo(self, item):
        if self.check_save():
            if hasattr(self, "folder_path") and self.folder_path:
                file_path = os.path.join(self.folder_path, item.text())                
                self.controller.clear_records()
                self.loadVideo(file_path)
                self.video_path_label.setText(f"Video Path: {file_path}")
                json_path = os.path.splitext(self.video_path)[0] + ".json"
                if os.path.exists(json_path) and os.path.isfile(json_path):
                    try:
                        records = load_json(json_path)
                        for item in records.get("C", []):
                            self.record_c_list.addItem(item)
                        for item in records.get("W", []):
                            self.record_w_list.addItem(item)
                        for item in records.get("R", []):
                            self.record_r_list.addItem(item)
                        self.label_path_label.setText(f"Label Path: {json_path}")
                    except Exception as e:
                        self.label_path_label.setText("Label Path: Fail load label")
                else:
                    self.label_path_label.setText("Label Path: No label selected")

    def SelectLabel(self, item):
        start_time = item.text().split(' - ')[0]
        start_time_h, start_time_m, start_time_s = int(start_time.split(':')[0]), int(start_time.split(':')[1]), float(start_time.split(':')[2])
        start_frame = start_time_h*60*60 + start_time_m*60 + start_time_s
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_MSEC, start_frame * 1000)
            self.frame_rate = int(self.cap.get(cv2.CAP_PROP_FPS))
            self.slider.setMaximum(int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)))
            self.timer.start(30)
            
    def loadVideo(self, path):
        if self.cap:
            self.cap.release()
        self.video_path = path
        self.cap = cv2.VideoCapture(path)
        if self.cap.isOpened():
            start_time = 1.5
            self.cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
            self.frame_rate = int(self.cap.get(cv2.CAP_PROP_FPS))
            self.slider.setMaximum(int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)))
            self.timer.start(30)
            self.timer.stop()

    def play_video(self):
        if self.cap and self.cap.isOpened():
            self.paused = not self.paused
            if self.cap:
                self.timer.start(30)

    def pause_video(self):
        self.paused = True
        self.timer.stop()

    def stop_video(self):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.paused = True
            self.timer.stop()
            start_time = 1.5
            self.cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
            self.video_label.clear()
            self.play_button.setEnabled(True)

    def speed_up(self):
        self.playback_rate = min(4.0, self.playback_rate + 0.25)
        self.update_timer_interval()

    def original_speed(self):
        self.playback_rate = 1.0
        self.update_timer_interval()

    def slow_down(self):
        self.playback_rate = max(0.25, self.playback_rate - 0.25)
        self.update_timer_interval()
        
    def nextFrame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            max_width, max_height = self.video_width, self.video_height
            scale = min(max_width / width, max_height / height)
            new_width, new_height = int(width * scale), int(height * scale)
            frame = cv2.resize(
                frame, (new_width, new_height), interpolation=cv2.INTER_AREA
            )
            qimg = QImage(frame.data, new_width, new_height, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(qimg))

            current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.slider.setValue(current_frame)
                   
            current_time = self.controller.formatTime(round(self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000, 3))
            total_time = self.controller.formatTime(round(total_frames / self.cap.get(cv2.CAP_PROP_FPS), 3))
            self.time_label.setText(f"{current_time} / {total_time}")
        else:
            self.timer.stop()

    def setPosition(self, position):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)

    def update_timer_interval(self):
        delay = max(1, int(1000 / (self.frame_rate * self.playback_rate)))
        self.timer.setInterval(delay)

    def seek_relative(self, seconds):
        if self.cap and self.cap.isOpened():
            current_time_ms = self.cap.get(cv2.CAP_PROP_POS_MSEC)
            new_time_ms = max(0, current_time_ms + seconds * 1000)
            self.cap.set(cv2.CAP_PROP_POS_MSEC, new_time_ms)
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = frame.shape
                max_width, max_height = self.video_width, self.video_height
                scale = min(max_width / width, max_height / height)
                new_width, new_height = int(width * scale), int(height * scale)
                frame = cv2.resize(
                    frame, (new_width, new_height), interpolation=cv2.INTER_AREA
                )
                qimg = QImage(frame.data, new_width, new_height, QImage.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(qimg))

                current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.slider.setValue(current_frame)
                    
                current_time = self.controller.formatTime(round(self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000, 3))
                total_time = self.controller.formatTime(round(total_frames / self.cap.get(cv2.CAP_PROP_FPS), 3))
                self.time_label.setText(f"{current_time} / {total_time}")
            else:
                self.timer.stop()

    def keyPressEvent(self, event):
        if self.video_path:
            current_time = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
            formatted_time = self.controller.formatTime(round(current_time, 3))
            if event.key() == Qt.Key_C and formatted_time != "00:00":
                self.save_check = False
                self.record_c_label.setText(f"Time: {formatted_time}")
                self.controller.handle_key("C")

            elif event.key() == Qt.Key_W and formatted_time != "00:00":
                self.save_check = False
                self.record_w_label.setText(f"Time: {formatted_time}")
                self.controller.handle_key("W")

            elif event.key() == Qt.Key_R and formatted_time != "00:00":
                self.save_check = False
                self.record_r_label.setText(f"Time: {formatted_time}")
                self.controller.handle_key("R")

            elif event.key() == Qt.Key_Space:
                if self.start_name == "pause":
                    self.play_video()
                    self.start_name = "play"

                elif self.start_name == "play":
                    self.pause_video()
                    self.start_name = "pause"

            elif event.key() == Qt.Key_Right:
                self.seek_relative(0.1)  # 快轉 0.1 秒

            elif event.key() == Qt.Key_Left:
                self.seek_relative(-0.1)  # 倒退 0.1 秒
            event.accept()

    def save_records(self):
        if not self.video_path:
            QMessageBox.warning(self, "錯誤", "請先開啟影片")
            return
        file_path = os.path.splitext(self.video_path)[0] + ".json"
        records = {
            "video_path": self.video_path,
            "version": self.version,
            "C": [
                self.record_c_list.item(i).text()
                for i in range(self.record_c_list.count())
            ],
            "W": [
                self.record_w_list.item(i).text()
                for i in range(self.record_w_list.count())
            ],
            "R": [
                self.record_r_list.item(i).text()
                for i in range(self.record_r_list.count())
            ],
        }
        save_json(file_path, records)
        self.save_check = True
        QMessageBox.information(self, "成功", f"紀錄已儲存至 {file_path}")

    def load_records(self):
        if not self.video_path:
            QMessageBox.warning(self, "錯誤", "請先開啟影片")
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self, "讀取紀錄", "", "JSON Files (*.json)"
        )
        try:
            records = load_json(file_path)

            records_video_path = records.get("video_path").replace("\\", "/")

            if self.video_path == records_video_path:
                self.record_c_list.clear()
                self.record_w_list.clear()
                self.record_r_list.clear()
                for item in records.get("C", []):
                    self.record_c_list.addItem(item)
                for item in records.get("W", []):
                    self.record_w_list.addItem(item)
                for item in records.get("R", []):
                    self.record_r_list.addItem(item)
                self.label_path_label.setText(f"Label Path: {file_path}")
            else:
                self.label_path_label.setText("Label Path: label not for video")
        except Exception as e:
            self.label_path_label.setText("Label Path: Fail load label")

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        event.accept()
