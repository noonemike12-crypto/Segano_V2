import os
import cv2
import subprocess
import shutil
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QPushButton, QLabel,
    QHBoxLayout, QComboBox, QFileDialog, QTextEdit, QFrame, QScrollArea
)
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal
from utils.steganography import string_to_binary, binary_to_string

class VideoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.video_path = None
        self.media_player = QMediaPlayer(self)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        group = QGroupBox("🎬 Video Steganography")
        vbox = QVBoxLayout()
        
        self.video_label = QLabel("No video selected")
        self.browse_btn = QPushButton("Browse Video")
        self.browse_btn.clicked.connect(self.select_video)
        
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        
        self.msg_input = QTextEdit()
        self.hide_btn = QPushButton("Hide in Video")
        self.hide_btn.clicked.connect(self.hide_message)
        
        vbox.addWidget(self.video_label)
        vbox.addWidget(self.browse_btn)
        vbox.addWidget(self.video_widget)
        vbox.addWidget(self.msg_input)
        vbox.addWidget(self.hide_btn)
        group.setLayout(vbox)
        layout.addWidget(group)

    def select_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Video (*.mp4 *.avi)")
        if path:
            self.video_path = path
            self.video_label.setText(os.path.basename(path))
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))

    def hide_message(self):
        if not self.video_path: return
        # Implementation logic...
        pass
