# utils/fps_overlay.py
from PyQt5.QtWidgets import QLabel, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import time

class FPSOverlay(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFont(QFont("Arial", 16, QFont.Bold))
        self.setStyleSheet("color: yellow; background-color: rgba(0,0,0,100); padding: 5px;")
        self.fps = 0
        self.frame_count = 0
        self.last_time = time.time()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_fps)
        self.timer.start(1000)
        self.hide()

    def count_frame(self):
        self.frame_count += 1

    def update_fps(self):
        current_time = time.time()
        elapsed = current_time - self.last_time
        if elapsed > 0:
            self.fps = int(self.frame_count / elapsed)
            self.setText(f"FPS: {self.fps}")
        self.frame_count = 0
        self.last_time = current_time

    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()