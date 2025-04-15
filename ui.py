import sys
import os
import cv2
import time
import json

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QFileDialog,
    QSlider,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QTextEdit,
    QListWidgetItem,
    QMessageBox,
    QApplication,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap

from controller import VideoController
from utils import load_json, save_json


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = VideoController(self)
        self.initUI()
        self.video_path = None
        self.cap = None
        self.paused = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.nextFrame)
        self.playback_rate = 1.0
        self.start_name = "pause"

        self.recording = False
        self.start_time = None
        self.start_times = {"C": None, "W": None, "R": None}
        self.screen = QApplication.desktop()
        screen_width = self.screen.width()
        screen_height = self.screen.height()

    def initUI(self):
        self.screen = QApplication.desktop()
        if self.screen.width() <= 1440 or self.screen.height() <= 1440:
            self.video_width = 640
            self.video_height = 480
        else:
            self.video_width = 960
            self.video_height = 720

        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, self.video_width + 150, self.video_height + 80)

        self.video_label = QLabel(self)
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setFixedSize(self.video_width, self.video_height)

        self.video_path_label = QLabel("Video Path: No video selected")
        self.label_path_label = QLabel("Label Path: No label selected")
        self.video_path_label.setWordWrap(True)
        self.label_path_label.setWordWrap(True)

        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.togglePlay)

        self.pause_button = QPushButton("Pause", self)
        self.pause_button.clicked.connect(self.pause_video)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_video)

        self.faster_btn = QPushButton("Faster")
        self.faster_btn.clicked.connect(self.speed_up)

        self.normal_btn = QPushButton("Normal")
        self.normal_btn.clicked.connect(self.original_speed)

        self.slower_btn = QPushButton("Slower")
        self.slower_btn.clicked.connect(self.slow_down)

        self.open_button = QPushButton("Open File", self)
        self.open_button.clicked.connect(self.openFile)

        self.folder_button = QPushButton("Open Folder", self)
        self.folder_button.clicked.connect(self.openFolder)

        self.save_btn = QPushButton("輸出紀錄")
        self.save_btn.clicked.connect(self.save_records)

        self.load_btn = QPushButton("讀取紀錄")
        self.load_btn.clicked.connect(self.load_records)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.sliderMoved.connect(self.setPosition)

        self.time_label = QLabel("00:00 / 00:00", self)

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
        self.record_w_list.setSelectionMode(QListWidget.SingleSelection)
        self.record_r_list.setSelectionMode(QListWidget.SingleSelection)

        self.delete_c_record_btn = QPushButton("Delete Record", self)
        self.delete_c_record_btn.clicked.connect(self.delete_c_selected_record)
        self.delete_w_record_btn = QPushButton("Delete Record", self)
        self.delete_w_record_btn.clicked.connect(self.delete_w_selected_record)
        self.delete_r_record_btn = QPushButton("Delete Record", self)
        self.delete_r_record_btn.clicked.connect(self.delete_r_selected_record)
        # ---------------------------------

        self.record_area = QTextEdit()
        self.record_area.setReadOnly(True)
        self.record_scroll = QScrollArea()
        self.record_scroll.setWidgetResizable(True)
        self.record_scroll.setWidget(self.record_area)

        # 版面配置
        save_layout = QHBoxLayout()
        save_layout.addWidget(self.open_button)
        save_layout.addWidget(self.folder_button)
        save_layout.addWidget(self.load_btn)
        save_layout.addWidget(self.save_btn)

        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.time_label)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.pause_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.slower_btn)
        controls_layout.addWidget(self.normal_btn)
        controls_layout.addWidget(self.faster_btn)

        path_layout = QVBoxLayout()
        path_layout.addWidget(self.video_path_label)
        path_layout.addWidget(self.label_path_label)

        list_layout = QVBoxLayout()
        list_layout.addWidget(QLabel("Video List"))
        list_layout.addWidget(self.list_widget)

        list_path_layout = QHBoxLayout()
        list_path_layout.addLayout(list_layout)
        list_path_layout.addWidget(self.video_label)

        left_layout = QVBoxLayout()
        left_layout.addLayout(list_path_layout)
        left_layout.addLayout(path_layout)
        left_layout.addLayout(save_layout)
        left_layout.addLayout(slider_layout)
        left_layout.addLayout(controls_layout)

        # ------------reocrd list------------
        down_layout = QHBoxLayout()

        down_layout_list_1 = QVBoxLayout()
        down_layout_list_1.addWidget(QLabel("C Records:"))
        down_layout_list_1.addWidget(self.record_c_label)
        down_layout_list_1.addWidget(self.record_c_list)
        down_layout_list_1.addWidget(self.delete_c_record_btn)

        down_layout_list_2 = QVBoxLayout()
        down_layout_list_2.addWidget(QLabel("W Records:"))
        down_layout_list_2.addWidget(self.record_w_label)
        down_layout_list_2.addWidget(self.record_w_list)
        down_layout_list_2.addWidget(self.delete_w_record_btn)

        down_layout_list_3 = QVBoxLayout()
        down_layout_list_3.addWidget(QLabel("R Records:"))
        down_layout_list_3.addWidget(self.record_r_label)
        down_layout_list_3.addWidget(self.record_r_list)
        down_layout_list_3.addWidget(self.delete_r_record_btn)

        down_layout.addLayout(down_layout_list_1)
        down_layout.addLayout(down_layout_list_2)
        down_layout.addLayout(down_layout_list_3)
        # -----------------------------------

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(down_layout)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setLayout(main_layout)

    def openFile(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv)"
        )
        if file_path:
            self.loadVideo(file_path)
            self.clear_records()
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
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder_path:
            self.folder_path = folder_path
            self.list_widget.clear()
            video_files = [
                f
                for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f))
                and f.lower().endswith((".mp4", ".avi", ".mov"))
            ]
            for file in video_files:
                self.list_widget.addItem(file)

    def loadSelectedVideo(self, item):
        if hasattr(self, "folder_path") and self.folder_path:
            file_path = os.path.join(self.folder_path, item.text())
            self.clear_records()
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

    def togglePlay(self):
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

            current_time = time.strftime(
                "%M:%S", time.gmtime(self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)
            )
            total_time = time.strftime(
                "%M:%S", time.gmtime(total_frames / self.cap.get(cv2.CAP_PROP_FPS))
            )
            self.time_label.setText(f"{current_time} / {total_time}")
        else:
            self.timer.stop()

    def setPosition(self, position):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)

    def update_timer_interval(self):
        delay = max(1, int(1000 / (self.frame_rate * self.playback_rate)))
        self.timer.setInterval(delay)

    def speed_up(self):
        self.playback_rate = min(4.0, self.playback_rate + 0.25)
        self.update_timer_interval()

    def original_speed(self):
        self.playback_rate = 1.0
        self.update_timer_interval()

    def slow_down(self):
        self.playback_rate = max(0.25, self.playback_rate - 0.25)
        self.update_timer_interval()

    def seek_relative(self, seconds):
        if self.cap and self.cap.isOpened():
            current_time_ms = self.cap.get(cv2.CAP_PROP_POS_MSEC)
            new_time_ms = max(0, current_time_ms + seconds * 1000)
            self.cap.set(cv2.CAP_PROP_POS_MSEC, new_time_ms)
            # print(f"跳轉至：{new_time_ms / 1000:.2f} 秒")

            # 播放前先讀出該時間點畫面顯示
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
                # print(total_frames, self.cap.get(cv2.CAP_PROP_FPS))
                current_time = time.strftime(
                    "%M:%S", time.gmtime(self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)
                )
                total_time = time.strftime(
                    "%M:%S", time.gmtime(total_frames / self.cap.get(cv2.CAP_PROP_FPS))
                )
                self.time_label.setText(f"{current_time} / {total_time}")
            else:
                self.timer.stop()

    def keyPressEvent(self, event):
        if self.video_path:
            current_time = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
            formatted_time = time.strftime("%M:%S", time.gmtime(current_time))
            # print(formatted_time == "00:00")
            if event.key() == Qt.Key_C and formatted_time != "00:00":
                self.record_c_label.setText(f"Time: {formatted_time}")
                self.controller.handle_key("C")

            elif event.key() == Qt.Key_W and formatted_time != "00:00":
                self.record_w_label.setText(f"Time: {formatted_time}")
                self.controller.handle_key("W")

            elif event.key() == Qt.Key_R and formatted_time != "00:00":
                self.record_r_label.setText(f"Time: {formatted_time}")
                self.controller.handle_key("R")

            elif event.key() == Qt.Key_Space:
                if self.start_name == "pause":
                    self.togglePlay()
                    self.start_name = "play"

                elif self.start_name == "play":
                    self.pause_video()
                    self.start_name = "pause"

            elif event.key() == Qt.Key_Right:
                self.seek_relative(0.1)  # 快轉 0.2 秒

            elif event.key() == Qt.Key_Left:
                self.seek_relative(-0.1)  # 倒退 0.2 秒

            event.accept()

    def clear_records(self):
        self.record_c_list.clear()
        self.record_w_list.clear()
        self.record_r_list.clear()

    def delete_c_selected_record(self):
        selected_items = self.record_c_list.selectedItems()
        for item in selected_items:
            self.record_c_list.takeItem(self.record_c_list.row(item))

    def delete_w_selected_record(self):
        selected_items = self.record_w_list.selectedItems()
        for item in selected_items:
            self.record_w_list.takeItem(self.record_w_list.row(item))

    def delete_r_selected_record(self):
        selected_items = self.record_r_list.selectedItems()
        for item in selected_items:
            self.record_r_list.takeItem(self.record_r_list.row(item))

    def save_records(self):
        if not self.video_path:
            QMessageBox.warning(self, "錯誤", "請先開啟影片")
            return
        file_path = os.path.splitext(self.video_path)[0] + ".json"
        records = {
            "video_path": self.video_path,
            "version": "1.0",
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
