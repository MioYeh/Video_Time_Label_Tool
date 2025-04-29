import cv2
import time
from PyQt5.QtWidgets import QListWidgetItem

class VideoController:
    def __init__(self, view):
        self.view = view
        self.recording_c = False
        self.recording_w = False
        self.recording_r = False

        self.start_time = None

    def formatTime(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02}.{millis:03}"
    
    def handle_key(self, key):
        current_time = self.view.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
        formatted_time = self.formatTime(round(current_time, 3))

        if key == 'C':
            if not self.recording_c:
                self.start_time_c = formatted_time
                self.recording_c = True 
            else:
                record_text = f"{self.start_time_c} - {formatted_time}"
                self.view.record_c_list.addItem(QListWidgetItem(record_text))
                self.view.record_c_label.setText(f"Time: ")
                self.recording_c = False
                 
        if key == 'W':
            if not self.recording_w:
                self.start_time_w = formatted_time
                self.recording_w = True 
            else:
                record_text = f"{self.start_time_w} - {formatted_time}"
                self.view.record_w_list.addItem(QListWidgetItem(record_text))
                self.view.record_w_label.setText(f"Time: ")
                self.recording_w = False 
            
        if key == 'R':
            if not self.recording_r:
                self.start_time_r = formatted_time
                self.recording_r = True 
            else:
                record_text = f"{self.start_time_r} - {formatted_time}"
                self.view.record_r_list.addItem(QListWidgetItem(record_text))
                self.view.record_r_label.setText(f"Time: ")
                self.recording_r = False

            
    def delete_c_selected_record(self):
        selected_items = self.view.record_c_list.selectedItems()
        for item in selected_items:
            self.view.record_c_list.takeItem(self.view.record_c_list.row(item))

    def delete_w_selected_record(self):
        selected_items = self.view.record_w_list.selectedItems()
        for item in selected_items:
            self.view.record_w_list.takeItem(self.view.record_w_list.row(item))

    def delete_r_selected_record(self):
        selected_items = self.view.record_r_list.selectedItems()
        for item in selected_items:
            self.view.record_r_list.takeItem(self.view.record_r_list.row(item))
            
    def clear_records(self):
        self.view.record_c_list.clear()
        self.view.record_w_list.clear()
        self.view.record_r_list.clear()
