import os
import subprocess
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QPushButton, QLabel, QFileDialog, QTextEdit, QProgressBar, QFrame
)
from PyQt5.QtGui import QPixmap, QDesktopServices
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from utils.stegano_engine import SteganoEngine
from utils.logger import logger

class WorkerThread(QThread):
    finished = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        try:
            self.progress.emit(30)
            result = self.func(*self.args)
            self.progress.emit(100)
            self.finished.emit(f"✅ สำเร็จ: {result}")
        except Exception as e:
            self.finished.emit(f"❌ ข้อผิดพลาด: {str(e)}")

class ImageTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_file = None
        self.output_file = None
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Left Side: Preview & File Selection
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        
        file_group = QGroupBox("📁 เลือกรูปภาพต้นฉบับ")
        file_vbox = QVBoxLayout()
        
        self.preview_label = QLabel("ลากรูปภาพมาวางที่นี่ หรือคลิกปุ่มเลือกไฟล์")
        self.preview_label.setFixedSize(450, 350)
        self.preview_label.setStyleSheet("background-color: #0f0f1a; border: 2px dashed #2d2d44; border-radius: 20px; color: #555; font-size: 16px;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        
        self.browse_btn = QPushButton("🔍 เลือกไฟล์รูปภาพ")
        self.browse_btn.clicked.connect(self.browse_image)
        
        file_vbox.addWidget(self.preview_label)
        file_vbox.addWidget(self.browse_btn)
        file_group.setLayout(file_vbox)
        left_layout.addWidget(file_group)
        
        # Capacity Info Card
        self.cap_group = QGroupBox("📊 ข้อมูลความจุ (Capacity)")
        cap_layout = QVBoxLayout()
        self.cap_label = QLabel("กรุณาเลือกรูปภาพเพื่อคำนวณความจุ...")
        self.cap_label.setStyleSheet("color: #00d4ff; font-size: 12px;")
        cap_layout.addWidget(self.cap_label)
        self.cap_group.setLayout(cap_layout)
        left_layout.addWidget(self.cap_group)
        
        left_layout.addStretch()

        # Right Side: Controls & Logs
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)

        msg_group = QGroupBox("📝 ข้อความที่ต้องการซ่อน (รองรับภาษาไทย)")
        msg_vbox = QVBoxLayout()
        
        self.msg_input = QTextEdit()
        self.msg_input.setPlaceholderText("พิมพ์ข้อความภาษาไทยหรืออังกฤษที่นี่...")
        self.msg_input.textChanged.connect(self.check_input_limit)
        
        self.limit_label = QLabel("ใช้ไป: 0 / 0 ตัวอักษร")
        self.limit_label.setStyleSheet("color: #888; font-size: 11px;")
        
        btn_layout = QHBoxLayout()
        self.hide_btn = QPushButton("🔒 ซ่อนข้อความ")
        self.hide_btn.setObjectName("primaryBtn")
        self.hide_btn.clicked.connect(self.process_hide)
        
        self.extract_btn = QPushButton("🔓 ถอดข้อความ")
        self.extract_btn.setObjectName("secondaryBtn")
        self.extract_btn.clicked.connect(self.process_extract)
        
        btn_layout.addWidget(self.hide_btn)
        btn_layout.addWidget(self.extract_btn)
        
        self.open_folder_btn = QPushButton("📂 เปิดโฟลเดอร์ผลลัพธ์")
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        
        self.progress_bar = QProgressBar()
        
        msg_vbox.addWidget(self.msg_input)
        msg_vbox.addWidget(self.limit_label)
        msg_vbox.addLayout(btn_layout)
        msg_vbox.addWidget(self.open_folder_btn)
        msg_vbox.addWidget(self.progress_bar)
        msg_group.setLayout(msg_vbox)
        
        log_group = QGroupBox("📊 บันทึกการทำงาน (Activity Log)")
        log_vbox = QVBoxLayout()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        log_vbox.addWidget(self.log_output)
        log_group.setLayout(log_vbox)

        right_layout.addWidget(msg_group)
        right_layout.addWidget(log_group)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)

    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "เลือกรูปภาพ", "", "Images (*.png *.jpg *.bmp)")
        if path:
            self.selected_file = path
            pixmap = QPixmap(path).scaled(450, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(pixmap)
            self.update_capacity_info()
            self.log_output.append(f"📂 โหลดไฟล์: {os.path.basename(path)}")

    def update_capacity_info(self):
        cap = SteganoEngine.get_image_capacity(self.selected_file)
        if cap:
            self.current_cap = cap
            info = (f"🔹 ความจุทั้งหมด: {cap['total_bits']:,} bits\n"
                    f"🔤 ภาษาอังกฤษ: ได้สูงสุด {cap['eng_capacity']:,} ตัวอักษร\n"
                    f"🇹🇭 ภาษาไทย: ได้สูงสุด {cap['thai_capacity']:,} ตัวอักษร")
            self.cap_label.setText(info)
            self.check_input_limit()

    def check_input_limit(self):
        if not self.selected_file or not hasattr(self, 'current_cap'): return
        
        text = self.msg_input.toPlainText()
        # Calculate size in bits (UTF-8)
        used_bits = len(text.encode('utf-8')) * 8
        total_bits = self.current_cap['total_bits'] - 8
        
        percent = (used_bits / total_bits) * 100 if total_bits > 0 else 0
        color = "#00ff88" if used_bits <= total_bits else "#ff4444"
        
        self.limit_label.setText(f"ใช้ไป: {used_bits:,} / {total_bits:,} bits ({percent:.1f}%)")
        self.limit_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        if used_bits > total_bits:
            self.hide_btn.setEnabled(False)
            self.hide_btn.setToolTip("ข้อความยาวเกินความจุของรูปภาพ!")
        else:
            self.hide_btn.setEnabled(True)
            self.hide_btn.setToolTip("")

    def process_hide(self):
        if not self.selected_file: return
        out_dir = os.path.join(os.path.dirname(self.selected_file), "output_sieng")
        if not os.path.exists(out_dir): os.makedirs(out_dir)
        
        self.output_file = os.path.join(out_dir, f"stego_{os.path.basename(self.selected_file)}")
        if not self.output_file.lower().endswith(".png"):
            self.output_file = os.path.splitext(self.output_file)[0] + ".png"
            
        self.run_worker(SteganoEngine.hide_lsb, self.selected_file, self.msg_input.toPlainText(), self.output_file)

    def process_extract(self):
        if not self.selected_file: return
        self.run_worker(SteganoEngine.extract_lsb, self.selected_file)

    def run_worker(self, func, *args):
        self.worker = WorkerThread(func, *args)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, msg):
        self.log_output.append(msg)
        if "สำเร็จ" in msg:
            self.open_folder_btn.setEnabled(True)
            if "extract" in self.sender().func.__name__.lower():
                extracted_text = msg.split(": ")[1]
                self.msg_input.setPlainText(extracted_text)

    def open_output_folder(self):
        if self.output_file and os.path.exists(os.path.dirname(self.output_file)):
            # Open folder and select file
            path = os.path.abspath(os.path.dirname(self.output_file))
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
            logger.log("info", f"Opened output folder: {path}")
