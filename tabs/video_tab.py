import os
import cv2
import time
import subprocess
import shutil
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QPushButton, QComboBox, QTextEdit, QFrame, QFileDialog, QProgressBar
)
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal
from PyQt5.QtGui import QDesktopServices

from utils.steganography import string_to_binary, binary_to_string, hide_lsb_video, extract_lsb_video
from utils.logger import logger

class VideoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_video = None
        self.media_player = QMediaPlayer(self)
        self.init_ui()
        self.setAcceptDrops(True)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # --- Top Section: Intro ---
        intro_layout = QVBoxLayout()
        title = QLabel("Embed Hidden Data in Video")
        title.setStyleSheet("font-size: 18pt; font-weight: 800; color: white;")
        subtitle = QLabel("Securely hide encrypted messages within high-definition video carriers using LSB injection.")
        subtitle.setObjectName("subTitle")
        intro_layout.addWidget(title)
        intro_layout.addWidget(subtitle)
        main_layout.addLayout(intro_layout)

        # --- Middle Section: Main Grid ---
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(30)

        # Left Column: Video Preview
        left_col = QVBoxLayout()
        video_group = QGroupBox("CARRIER VIDEO PREVIEW")
        video_layout = QVBoxLayout(video_group)
        
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(250)
        self.video_widget.setStyleSheet("background-color: #0b0e14; border-radius: 12px;")
        self.media_player.setVideoOutput(self.video_widget)
        video_layout.addWidget(self.video_widget)
        
        self.path_label = QLabel("No video selected")
        self.path_label.setAlignment(Qt.AlignCenter)
        self.path_label.setStyleSheet("color: #94a3b8; font-size: 9pt; margin-top: 10px;")
        video_layout.addWidget(self.path_label)
        
        # Playback Controls
        playback_layout = QHBoxLayout()
        self.play_btn = QPushButton("▶️ Play")
        self.play_btn.clicked.connect(self.play_video)
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.clicked.connect(self.stop_video)
        playback_layout.addWidget(self.play_btn)
        playback_layout.addWidget(self.stop_btn)
        video_layout.addLayout(playback_layout)
        
        left_col.addWidget(video_group)
        
        # File Selection Buttons
        file_btns = QHBoxLayout()
        self.browse_btn = QPushButton("📁 Browse Video")
        self.browse_btn.clicked.connect(self.browse_video)
        self.example_selector = QComboBox()
        self.example_selector.setPlaceholderText("Select Example...")
        self.example_selector.currentIndexChanged.connect(self.load_example_video)
        file_btns.addWidget(self.browse_btn)
        file_btns.addWidget(self.example_selector)
        left_col.addLayout(file_btns)
        
        grid_layout.addLayout(left_col, 3)

        # Right Column: Payload & Settings
        right_col = QVBoxLayout()
        
        # Payload Section
        payload_group = QGroupBox("PAYLOAD CONFIGURATION")
        payload_layout = QVBoxLayout(payload_group)
        payload_layout.addWidget(QLabel("Secret Message:"))
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Type the message you want to hide...")
        payload_layout.addWidget(self.message_input)
        right_col.addWidget(payload_group)

        # Settings Section
        settings_group = QGroupBox("ENCODING PARAMETERS")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.addWidget(QLabel("LSB Depth:"))
        self.depth_selector = QComboBox()
        self.depth_selector.addItems(["1 BIT (SECURE)", "2 BIT", "4 BIT (RISKY)"])
        settings_layout.addWidget(self.depth_selector)
        right_col.addWidget(settings_group)
        
        grid_layout.addLayout(right_col, 2)
        main_layout.addLayout(grid_layout)

        # --- Bottom Section: Actions ---
        action_group = QGroupBox("ACTIONS")
        action_layout = QHBoxLayout(action_group)
        
        self.hide_btn = QPushButton("🔒 Hide Message")
        self.hide_btn.setObjectName("primaryBtn")
        self.hide_btn.clicked.connect(self.process_hide)
        
        self.extract_btn = QPushButton("🔓 Extract Message")
        self.extract_btn.setObjectName("secondaryBtn")
        self.extract_btn.clicked.connect(self.process_extract)
        
        self.folder_btn = QPushButton("📁 Output Folder")
        self.folder_btn.clicked.connect(self.open_output_folder)
        
        action_layout.addWidget(self.hide_btn)
        action_layout.addWidget(self.extract_btn)
        action_layout.addWidget(self.folder_btn)
        main_layout.addWidget(action_group)
        
        # Logs
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Operation logs...")
        self.log_output.setMaximumHeight(100)
        main_layout.addWidget(self.log_output)
        
        self.load_examples()

    def load_examples(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        example_dir = os.path.join(base_dir, "vdio")
        if os.path.exists(example_dir):
            files = [f for f in os.listdir(example_dir) if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov'))]
            self.example_selector.addItems(files)

    def load_video(self, path):
        logger.log("info", f"VideoTab: โหลดวิดีโอจาก {path}")
        self.selected_video = path
        self.path_label.setText(f"ไฟล์ที่เลือก: {os.path.basename(path)}")
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))

    def browse_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์วิดีโอ", "", "Video Files (*.mp4 *.avi *.mkv *.mov)")
        if path: self.load_video(path)

    def load_example_video(self):
        name = self.example_selector.currentText()
        if name:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            path = os.path.join(base_dir, "vdio", name)
            self.load_video(path)

    def play_video(self):
        if self.selected_video: self.media_player.play()

    def stop_video(self):
        self.media_player.stop()

    def process_hide(self):
        if not self.selected_video: return
        msg = self.message_input.toPlainText()
        if not msg: return
        logger.log("info", "VideoTab: เริ่มกระบวนการซ่อนข้อความในวิดีโอ")
        
        self.log_output.append("🔄 กำลังประมวลผลวิดีโอ (อาจใช้เวลาสักครู่)...")
        try:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vdio", "output")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"hidden_{os.path.basename(self.selected_video)}.avi")
            
            # ดำเนินการจริง
            hide_lsb_video(self.selected_video, msg, output_path)
            
            self.log_output.append(f"✅ ซ่อนสำเร็จ: {output_path}")
            self.log_output.append("⚠️ หมายเหตุ: ไฟล์ผลลัพธ์จะเป็น .avi (Lossless) เพื่อรักษาข้อมูล")
        except Exception as e:
            self.log_output.append(f"❌ เกิดข้อผิดพลาด: {str(e)}")

    def process_extract(self):
        if not self.selected_video: return
        logger.log("info", "VideoTab: เริ่มกระบวนการถอดข้อความจากวิดีโอ")
        self.log_output.append("🔍 กำลังค้นหาข้อมูลที่ซ่อนอยู่...")
        try:
            res = extract_lsb_video(self.selected_video)
            self.log_output.append(f"🔓 ข้อความที่พบ: {res}")
        except Exception as e:
            self.log_output.append(f"❌ เกิดข้อผิดพลาด: {str(e)}")

    def open_output_folder(self):
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vdio", "output")
        os.makedirs(path, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
                self.load_video(path)
