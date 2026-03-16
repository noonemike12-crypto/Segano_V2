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

class FileInfoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_file = None
        self.init_ui()
        self.setAcceptDrops(True)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- ส่วนเลือกไฟล์ ---
        selection_group = QGroupBox("📁 การเลือกไฟล์ (File Selection)")
        selection_layout = QHBoxLayout()
        
        self.path_label = QLabel("ลากไฟล์มาวางที่นี่ หรือกดปุ่มเลือกไฟล์")
        self.path_label.setAlignment(Qt.AlignCenter)
        self.path_label.setStyleSheet("border: 2px dashed #4a5568; border-radius: 10px; padding: 15px;")
        selection_layout.addWidget(self.path_label, 3)
        
        self.browse_btn = QPushButton("🔍 เลือกไฟล์...")
        self.browse_btn.clicked.connect(self.browse_file)
        selection_layout.addWidget(self.browse_btn, 1)
        
        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)

        # --- ส่วนจัดการ Metadata ---
        meta_group = QGroupBox("🏷️ การจัดการ Metadata (Metadata Management)")
        meta_layout = QVBoxLayout()
        
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("ฟิลด์ (Field):"))
        self.field_selector = QComboBox()
        self.field_selector.addItems(["comment", "title", "artist", "genre", "album", "description"])
        input_row.addWidget(self.field_selector, 1)
        
        input_row.addWidget(QLabel("ข้อความ (Text):"))
        self.meta_input = QLineEdit()
        self.meta_input.setPlaceholderText("พิมพ์ข้อความที่ต้องการซ่อนใน Metadata...")
        input_row.addWidget(self.meta_input, 2)
        meta_layout.addLayout(input_row)
        
        btns = QHBoxLayout()
        self.hide_btn = QPushButton("🔒 ซ่อนใน Metadata")
        self.hide_btn.setObjectName("primaryBtn")
        self.hide_btn.clicked.connect(self.process_hide)
        
        self.extract_btn = QPushButton("🔓 ดึงข้อมูล Metadata")
        self.extract_btn.setObjectName("secondaryBtn")
        self.extract_btn.clicked.connect(self.process_extract)
        
        btns.addWidget(self.hide_btn)
        btns.addWidget(self.extract_btn)
        meta_layout.addLayout(btns)
        
        meta_group.setLayout(meta_layout)
        layout.addWidget(meta_group)

        # --- ส่วนแสดงข้อมูลไฟล์ ---
        info_layout = QHBoxLayout()
        
        details_group = QGroupBox("📋 รายละเอียดไฟล์ (File Details)")
        details_layout = QVBoxLayout()
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        details_group.setLayout(details_layout)
        info_layout.addWidget(details_group, 2)
        
        extracted_group = QGroupBox("🔓 ข้อมูลที่พบ (Extracted)")
        extracted_layout = QVBoxLayout()
        self.extracted_list = QListWidget()
        extracted_layout.addWidget(self.extracted_list)
        extracted_group.setLayout(extracted_layout)
        info_layout.addWidget(extracted_group, 1)
        
        layout.addLayout(info_layout)

    def load_file(self, path):
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
