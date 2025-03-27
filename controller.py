import cv2
import time
from PyQt5.QtWidgets import QListWidgetItem

class VideoController:
    def __init__(self, view):
        self.view = view
        self.recording = False
        self.start_time = None

    def handle_key(self, key):
        current_time = self.view.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
        formatted_time = time.strftime('%M:%S', time.gmtime(current_time))
        if not self.recording:
            self.start_time = formatted_time
            self.recording = True
        else:
            record_text = f"{self.start_time} - {formatted_time}"
            if key == 'C':
                self.view.record_c_list.addItem(QListWidgetItem(record_text))
                self.view.record_c_label.setText(f"Time: ")
            elif key == 'W':
                self.view.record_w_list.addItem(QListWidgetItem(record_text))
                self.view.record_w_label.setText(f"Time: ")
            elif key == 'R':
                self.view.record_r_list.addItem(QListWidgetItem(record_text))
                self.view.record_r_label.setText(f"Time: ")
                
            # elif key == 'R':
            #     self.view.record_r_list.addItem(QListWidgetItem(record_text))
            #     self.view.record_r_label.setText(f"Time: ")
            # elif key == 'R':
            #     self.view.record_r_list.addItem(QListWidgetItem(record_text))
            #     self.view.record_r_label.setText(f"Time: ")
            self.recording = False
