import os
import mimetypes
import subprocess
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QPushButton, QComboBox, QTextEdit, QLineEdit, QFrame, 
    QFileDialog, QMessageBox, QListWidget, QScrollArea
)
from PyQt5.QtCore import Qt
import ffmpeg
from utils.logger import logger

class FileInfoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_file = None
        self.init_ui()
        self.setAcceptDrops(True)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # --- Top Section: Intro ---
        intro_layout = QVBoxLayout()
        title = QLabel("Metadata Steganography")
        title.setStyleSheet("font-size: 18pt; font-weight: 800; color: white;")
        subtitle = QLabel("Hide or extract sensitive text payloads within standard file metadata tags.")
        subtitle.setObjectName("subTitle")
        intro_layout.addWidget(title)
        intro_layout.addWidget(subtitle)
        main_layout.addLayout(intro_layout)

        # --- Middle Section: Main Grid ---
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(30)

        # Left Column: File Selection & Payload
        left_col = QVBoxLayout()
        
        # File Selection
        selection_group = QGroupBox("SELECT SOURCE FILE")
        selection_layout = QVBoxLayout(selection_group)
        self.path_label = QLabel("Click to upload or drag & drop\nJPG, PNG, PDF, or MP3")
        self.path_label.setAlignment(Qt.AlignCenter)
        self.path_label.setMinimumSize(300, 100)
        self.path_label.setStyleSheet("""
            border: 2px dashed #1e293b;
            border-radius: 15px;
            color: #64748b;
            font-size: 11pt;
            background-color: #0b0e14;
        """)
        selection_layout.addWidget(self.path_label)
        
        self.browse_btn = QPushButton("📁 Browse Files...")
        self.browse_btn.clicked.connect(self.browse_file)
        selection_layout.addWidget(self.browse_btn)
        left_col.addWidget(selection_group)

        # Metadata Target
        target_group = QGroupBox("SELECT METADATA TARGET")
        target_layout = QVBoxLayout(target_group)
        self.field_selector = QComboBox()
        self.field_selector.addItems(["comment", "title", "artist", "genre", "album", "description"])
        target_layout.addWidget(self.field_selector)
        left_col.addWidget(target_group)
        
        # Secret Message
        payload_group = QGroupBox("SECRET MESSAGE")
        payload_layout = QVBoxLayout(payload_group)
        self.meta_input = QLineEdit()
        self.meta_input.setPlaceholderText("Enter the text message you wish to hide...")
        payload_layout.addWidget(self.meta_input)
        left_col.addWidget(payload_group)
        
        grid_layout.addLayout(left_col, 3)

        # Right Column: Details & Actions
        right_col = QVBoxLayout()
        
        # Details Section
        details_group = QGroupBox("FILE DETAILS")
        details_layout = QVBoxLayout(details_group)
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setPlaceholderText("File metadata details will appear here...")
        details_layout.addWidget(self.details_text)
        right_col.addWidget(details_group)

        # Actions Section
        action_group = QGroupBox("ACTION CONTROL")
        action_layout = QVBoxLayout(action_group)
        
        self.hide_btn = QPushButton("🔒 Hide in Metadata")
        self.hide_btn.setObjectName("primaryBtn")
        self.hide_btn.clicked.connect(self.process_hide)
        
        self.extract_btn = QPushButton("🔍 Extract Metadata")
        self.extract_btn.setObjectName("secondaryBtn")
        self.extract_btn.clicked.connect(self.process_extract)
        
        action_layout.addWidget(self.hide_btn)
        action_layout.addWidget(self.extract_btn)
        right_col.addWidget(action_group)
        
        grid_layout.addLayout(right_col, 2)
        main_layout.addLayout(grid_layout)

        # Extracted Info
        extracted_group = QGroupBox("EXTRACTED PAYLOADS")
        extracted_layout = QVBoxLayout(extracted_group)
        self.extracted_list = QListWidget()
        self.extracted_list.setMaximumHeight(100)
        extracted_layout.addWidget(self.extracted_list)
        main_layout.addWidget(extracted_group)

    def load_file(self, path):
        logger.log("info", f"FileInfoTab: โหลดไฟล์จาก {path}")
        self.selected_file = path
        self.path_label.setText(f"ไฟล์ที่เลือก: {os.path.basename(path)}")
        self.show_details()

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์", "", "Media Files (*.mp3 *.mp4 *.wav *.avi *.mkv)")
        if path: self.load_file(path)

    def show_details(self):
        if not self.selected_file: return
        try:
            size = os.path.getsize(self.selected_file) / (1024 * 1024)
            mime = mimetypes.guess_type(self.selected_file)[0]
            info = f"<b>ชื่อไฟล์:</b> {os.path.basename(self.selected_file)}<br>"
            info += f"<b>ขนาด:</b> {size:.2f} MB<br>"
            info += f"<b>ประเภท:</b> {mime}<br>"
            
            # ใช้ ffprobe ดึงข้อมูลเชิงลึก
            probe = ffmpeg.probe(self.selected_file)
            format_info = probe.get('format', {})
            tags = format_info.get('tags', {})
            
            info += "<br><b>Metadata ที่พบ:</b><br>"
            for k, v in tags.items():
                info += f"- {k}: {v}<br>"
                
            self.details_text.setHtml(info)
        except Exception as e:
            self.details_text.setPlainText(f"ไม่สามารถดึงข้อมูลได้: {str(e)}")

    def process_hide(self):
        if not self.selected_file: return
        field = self.field_selector.currentText()
        val = self.meta_input.text()
        if not val: return
        logger.log("info", f"FileInfoTab: เริ่มซ่อน Metadata (ฟิลด์: {field})")
        
        try:
            output_path = os.path.join(os.path.dirname(self.selected_file), f"meta_{os.path.basename(self.selected_file)}")
            # ใช้ ffmpeg เพื่อเขียน metadata
            (
                ffmpeg
                .input(self.selected_file)
                .output(output_path, metadata=f"{field}={val}", codec="copy")
                .overwrite_output()
                .run()
            )
            QMessageBox.information(self, "สำเร็จ", f"ซ่อนข้อมูลใน Metadata สำเร็จ!\nบันทึกที่: {output_path}")
            self.load_file(output_path)
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", f"ไม่สามารถซ่อนข้อมูลได้: {str(e)}")

    def process_extract(self):
        if not self.selected_file: return
        logger.log("info", "FileInfoTab: เริ่มดึง Metadata")
        self.extracted_list.clear()
        try:
            probe = ffmpeg.probe(self.selected_file)
            tags = probe.get('format', {}).get('tags', {})
            if not tags:
                self.extracted_list.addItem("ไม่พบ Metadata")
            for k, v in tags.items():
                self.extracted_list.addItem(f"{k}: {v}")
        except Exception as e:
            self.extracted_list.addItem(f"ข้อผิดพลาด: {str(e)}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls: self.load_file(urls[0].toLocalFile())
