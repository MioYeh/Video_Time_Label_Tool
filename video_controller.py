from PyQt5 import QtCore 
from PyQt5.QtGui import QImage, QPixmap, QKeyEvent
from PyQt5.QtCore import QTimer, Qt, QBasicTimer

from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QHBoxLayout, QSlider, QLabel, QFileDialog)

from opencv_engine import opencv_engine
from utils import Timer

import cv2

# videoplayer_state_dict = {
#  "stop":0,   
#  "play":1,
#  "pause":2     
# }

class video_controller(object):
    def __init__(self, video_path, ui):
        self.video_path = video_path
        self.ui = ui
        self.qpixmap_fix_width = 800 # 16x9 = 1920x1080 = 1280x720 = 800x450 = 640x360
        self.qpixmap_fix_height = 450
        self.current_frame_no = 0
        self.videoplayer_state = "pause"
        self.init_video_info()
        self.set_video_player()

    def init_video_info(self):
        videoinfo = opencv_engine.getvideoinfo(self.video_path)
        self.vc = videoinfo["vc"]
        self.video_fps = videoinfo["fps"]
        self.video_total_frame_count = videoinfo["frame_count"]
        self.video_width = videoinfo["width"]
        self.video_height = videoinfo["height"]
        self.video_total_time = self.video_total_frame_count/self.video_fps if self.video_fps > 0 else 0
        self.hour = int(self.video_total_time/3600)
        self.minute = int((self.video_total_time%3600)/60)
        self.second = int(self.video_total_time%60)
                
        self.ui.slider_videoframe.setRange(0, self.video_total_frame_count-1)
        self.ui.slider_videoframe.valueChanged.connect(self.getslidervalue)


    def set_video_player(self):
        self.timer=QTimer() # init QTimer
        self.timer.timeout.connect(self.timer_timeout_job) # when timeout, do run one
        # self.timer.start(1000//self.video_fps) # start Timer, here we set '1000ms//Nfps' while timeout one time
        self.timer.start(1) # but if CPU can not decode as fast as fps, we set 1 (need decode time)

    def set_current_frame_no(self, frame_no):
        
        # self.vc.set(cv2.CAP_PROP_POS_MSEC, frame_no) # bottleneck
        self.vc.set(1, frame_no) # bottleneck

        

                
    #@WongWongTimer
    def __get_next_frame(self):
        ret, frame = self.vc.read()
        # self.ui.label_framecnt.setText(f"frame number: {self.current_frame_no}/{self.video_total_frame_count}")
        total_time = self.video_total_frame_count/self.video_fps
        total_time_hour = int(total_time/3600)
        total_time_minute = int((total_time%3600)/60)
        total_time_second = int(total_time%60)
        
        now_time = self.current_frame_no/self.video_fps
        now_time_hour = int(now_time/3600)
        now_time_minute = int((now_time%3600)/60)
        now_time_second = int(now_time%60)
        self.ui.label_framecnt.setText(f"播放時間: {now_time_hour:02d}:{now_time_minute:02d}:{now_time_second:02d} / {total_time_hour:02d}:{total_time_minute:02d}:{total_time_second:02d}")
        # self.ui.label_framecnt.setText(f"time: {self.current_frame_no/self.video_fps}/{self.video_total_frame_count/self.video_fps}")
        self.setslidervalue(self.current_frame_no)
        return frame

    def __update_label_frame(self, frame):       
        bytesPerline = 3 * self.video_width
        qimg = QImage(frame, self.video_width, self.video_height, bytesPerline, QImage.Format_RGB888).rgbSwapped()
        self.qpixmap = QPixmap.fromImage(qimg)

        if self.qpixmap.width()/16 >= self.qpixmap.height()/9: # like 1600/16 > 90/9, height is shorter, align width
            self.qpixmap = self.qpixmap.scaledToWidth(self.qpixmap_fix_width)
        else: # like 1600/16 < 9000/9, width is shorter, align height
            self.qpixmap = self.qpixmap.scaledToHeight(self.qpixmap_fix_height)
        self.ui.label_videoframe.setPixmap(self.qpixmap)
        # self.ui.label_videoframe.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop) # up and left
        self.ui.label_videoframe.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter) # Center

    def check_video_open(self):
        if self.vc is not None and self.vc.isOpened():
            return True
        else:
            return
        
    def check_video_time(self):
        # current_time = self.vc.get(cv2.CAP_PROP_POS_MSEC) / 1000  # 取得目前時間 (毫秒)
        current_time = self.current_frame_no/self.video_fps
        print(f"video control current_time: {current_time}")
        return current_time
        
    def play(self):
        self.videoplayer_state = "play"

    def stop(self):
        self.videoplayer_state = "stop"

    def pause(self):
        self.videoplayer_state = "pause"

        
    def timer_timeout_job(self):
        if (self.videoplayer_state == "play"):
            if self.current_frame_no >= self.video_total_frame_count-1:
                #self.videoplayer_state = "pause"
                self.current_frame_no = 0 # auto replay
                self.set_current_frame_no(self.current_frame_no)
            else:
                self.current_frame_no += 1

        if (self.videoplayer_state == "stop"):
            self.current_frame_no = 0
            self.set_current_frame_no(self.current_frame_no)

        if (self.videoplayer_state == "pause"):
            self.current_frame_no = self.current_frame_no
            self.set_current_frame_no(self.current_frame_no)

        frame = self.__get_next_frame()
        self.__update_label_frame(frame)

    def getslidervalue(self):
        self.current_frame_no = self.ui.slider_videoframe.value()
        self.set_current_frame_no(self.current_frame_no)

    def setslidervalue(self, value):
        self.ui.slider_videoframe.setValue(self.current_frame_no)







