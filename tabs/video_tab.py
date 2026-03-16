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
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- ส่วนจัดการไฟล์วิดีโอ ---
        video_group = QGroupBox("🎬 การจัดการไฟล์วิดีโอ (Video Management)")
        video_layout = QVBoxLayout()
        
        file_selection = QHBoxLayout()
        self.example_selector = QComboBox()
        self.example_selector.setPlaceholderText("เลือกวิดีโอตัวอย่าง...")
        self.example_selector.currentIndexChanged.connect(self.load_example_video)
        file_selection.addWidget(self.example_selector, 1)
        
        self.browse_btn = QPushButton("🔍 เลือกไฟล์วิดีโอ...")
        self.browse_btn.clicked.connect(self.browse_video)
        file_selection.addWidget(self.browse_btn, 1)
        video_layout.addLayout(file_selection)
        
        self.path_label = QLabel("ยังไม่ได้เลือกไฟล์")
        self.path_label.setAlignment(Qt.AlignCenter)
        self.path_label.setStyleSheet("border: 2px dashed #4a5568; border-radius: 10px; padding: 10px;")
        video_layout.addWidget(self.path_label)
        
        # ส่วนแสดงวิดีโอ
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(300)
        self.media_player.setVideoOutput(self.video_widget)
        video_layout.addWidget(self.video_widget)
        
        playback_layout = QHBoxLayout()
        self.play_btn = QPushButton("▶️ เล่น (Play)")
        self.play_btn.clicked.connect(self.play_video)
        self.stop_btn = QPushButton("⏹️ หยุด (Stop)")
        self.stop_btn.clicked.connect(self.stop_video)
        playback_layout.addWidget(self.play_btn)
        playback_layout.addWidget(self.stop_btn)
        video_layout.addLayout(playback_layout)
        
        video_group.setLayout(video_layout)
        layout.addWidget(video_group)

        # --- ส่วนข้อความลับ ---
        message_group = QGroupBox("💬 ข้อความลับ (Secret Message)")
        message_layout = QVBoxLayout()
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("พิมพ์ข้อความที่ต้องการซ่อนในวิดีโอ...")
        message_layout.addWidget(self.message_input)
        message_group.setLayout(message_layout)
        layout.addWidget(message_group)

        # --- ส่วนดำเนินการ ---
        action_layout = QHBoxLayout()
        self.hide_btn = QPushButton("🔒 ซ่อนข้อความ")
        self.hide_btn.setObjectName("primaryBtn")
        self.hide_btn.clicked.connect(self.process_hide)
        
        self.extract_btn = QPushButton("🔓 ถอดข้อความ")
        self.extract_btn.setObjectName("secondaryBtn")
        self.extract_btn.clicked.connect(self.process_extract)
        
        self.folder_btn = QPushButton("📁 โฟลเดอร์ผลลัพธ์")
        self.folder_btn.clicked.connect(self.open_output_folder)
        
        action_layout.addWidget(self.hide_btn)
        action_layout.addWidget(self.extract_btn)
        action_layout.addWidget(self.folder_btn)
        layout.addLayout(action_layout)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("บันทึกการทำงานจะแสดงที่นี่...")
        self.log_output.setMaximumHeight(100)
        layout.addWidget(self.log_output)
        
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
