import os
import wave
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QPushButton, QLabel, QFileDialog, QTextEdit, QProgressBar, QFrame, QComboBox, QScrollArea
)
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
import sounddevice as sd
import soundfile as sf
from utils.stegano_engine import SteganoEngine
from utils.logger import logger
from utils.path_manager import PathManager

class WorkerThread(QThread):
    finished = pyqtSignal(str, object)
    progress = pyqtSignal(int)

    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        try:
            result = self.func(*self.args)
            self.finished.emit("SUCCESS", result)
        except Exception as e:
            self.finished.emit("ERROR", str(e))

class AudioTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_file = None
        self.output_file = None
        self.max_bits = 0
        self.setAcceptDrops(True)
        self.init_ui()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(urls[0].toLocalFile().lower().endswith(ext) for ext in ['.wav', '.mp3', '.flac']):
                event.accept()
                return
        event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.selected_file = files[0]
            self.file_label.setText(os.path.basename(self.selected_file))
            self.update_capacity()
            logger.info(f"Dropped audio: {self.selected_file}")

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)

        # File Selection
        file_group = QGroupBox("🎵 1. เลือกไฟล์เสียง (Source Audio)")
        file_layout = QVBoxLayout()
        self.file_label = QLabel("ยังไม่ได้เลือกไฟล์...")
        self.file_label.setStyleSheet("background: #0f0f1a; border: 2px dashed #2d2d44; padding: 20px; border-radius: 10px; color: #888;")
        self.file_label.setAlignment(Qt.AlignCenter)
        
        btn_layout = QHBoxLayout()
        self.browse_btn = QPushButton("🔍 เลือกไฟล์ .WAV / .MP3")
        self.browse_btn.clicked.connect(self.browse_audio)
        self.play_btn = QPushButton("▶️ เล่นเสียง")
        self.play_btn.clicked.connect(self.play_audio)
        self.stop_btn = QPushButton("⏹️ หยุด")
        self.stop_btn.clicked.connect(lambda: sd.stop())
        btn_layout.addWidget(self.browse_btn)
        btn_layout.addWidget(self.play_btn)
        btn_layout.addWidget(self.stop_btn)
        
        file_layout.addWidget(self.file_label)
        file_layout.addLayout(btn_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Technique & Capacity
        tech_group = QGroupBox("🛠️ 2. เทคนิคและข้อมูลความจุ")
        tech_layout = QHBoxLayout()
        self.method_combo = QComboBox()
        self.method_combo.addItems([m for m in SteganoEngine.METHODS if any(x in m for x in ["LSB", "EOF", "Metadata"])])
        self.method_combo.currentIndexChanged.connect(self.update_capacity)
        
        self.cap_label = QLabel("ความจุ: -")
        self.cap_label.setStyleSheet("color: #00d4ff; font-weight: bold;")
        
        tech_layout.addWidget(QLabel("เทคนิค:"))
        tech_layout.addWidget(self.method_combo, 1)
        tech_layout.addWidget(self.cap_label, 1)
        tech_group.setLayout(tech_layout)
        layout.addWidget(tech_group)

        # Message Input
        msg_group = QGroupBox("📝 3. ข้อความลับ (Secret Message)")
        msg_layout = QVBoxLayout()
        self.msg_input = QTextEdit()
        self.msg_input.setPlaceholderText("พิมพ์ข้อความที่ต้องการซ่อน...")
        self.msg_input.textChanged.connect(self.check_limit)
        self.limit_label = QLabel("ใช้ไป: 0 bits")
        
        action_layout = QHBoxLayout()
        self.hide_btn = QPushButton("🔒 ซ่อนข้อความ")
        self.hide_btn.setObjectName("primaryBtn")
        self.hide_btn.clicked.connect(self.process_hide)
        self.extract_btn = QPushButton("🔓 ถอดข้อความ")
        self.extract_btn.setObjectName("secondaryBtn")
        self.extract_btn.clicked.connect(self.process_extract)
        action_layout.addWidget(self.hide_btn)
        action_layout.addWidget(self.extract_btn)
        
        self.open_folder_btn = QPushButton("📂 เปิดโฟลเดอร์ผลลัพธ์")
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        
        self.progress_bar = QProgressBar()
        msg_layout.addWidget(self.msg_input)
        msg_layout.addWidget(self.limit_label)
        msg_layout.addLayout(action_layout)
        msg_layout.addWidget(self.open_folder_btn)
        msg_layout.addWidget(self.progress_bar)
        msg_group.setLayout(msg_layout)
        layout.addWidget(msg_group)

        # Logs
        log_group = QGroupBox("📊 4. บันทึกการทำงาน")
        log_layout = QVBoxLayout()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        log_layout.addWidget(self.log_output)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def browse_audio(self):
        path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์เสียง", "", "Audio (*.wav *.mp3 *.flac)")
        if path:
            self.selected_file = path
            self.file_label.setText(os.path.basename(path))
            self.update_capacity()
            self.log_output.append(f"📂 โหลดไฟล์: {os.path.basename(path)}")

    def play_audio(self):
        if self.selected_file and os.path.exists(self.selected_file):
            try:
                data, sr = sf.read(self.selected_file)
                sd.play(data, sr)
            except Exception as e:
                self.log_output.append(f"❌ เล่นเสียงไม่ได้: {e}")

    def update_capacity(self):
        if not self.selected_file: return
        method = self.method_combo.currentText()
        cap_info = SteganoEngine.get_capacity(self.selected_file, method)
        if isinstance(cap_info, dict):
            self.max_bits = cap_info['total_bits']
            self.cap_label.setText(f"ความจุ: {self.max_bits:,} bits")
        else:
            self.max_bits = cap_info * 8
            self.cap_label.setText(f"ความจุ: {self.max_bits:,} bits")
        self.check_limit()

    def check_limit(self):
        text = self.msg_input.toPlainText()
        used_bits = len(text.encode('utf-8')) * 8
        color = "#00ff88" if used_bits <= self.max_bits else "#ff4444"
        self.limit_label.setText(f"ใช้ไป: {used_bits:,} / {self.max_bits:,} bits")
        self.limit_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.hide_btn.setEnabled(used_bits <= self.max_bits)

    def process_hide(self):
        if not self.selected_file: return
        method = self.method_combo.currentText()
        filename = f"stego_{os.path.basename(self.selected_file)}"
        if "LSB" in method: filename = os.path.splitext(filename)[0] + ".wav"
        self.output_file = PathManager.get_output_path("audio", filename)
        
        func = None
        if "LSB" in method: func = SteganoEngine.hide_audio_lsb
        elif "EOF" in method: func = SteganoEngine.hide_eof
        elif "Metadata" in method: func = SteganoEngine.hide_metadata
        elif "Alpha" in method: func = SteganoEngine.hide_alpha
        elif "Edge" in method: func = SteganoEngine.hide_edge
        
        data = self.msg_input.toPlainText().encode('utf-8')
        
        self.worker = WorkerThread(func, self.selected_file, data, self.output_file)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def process_extract(self):
        if not self.selected_file: return
        method = self.method_combo.currentText()
        func = None
        if "LSB" in method: func = SteganoEngine.extract_audio_lsb
        elif "EOF" in method: func = SteganoEngine.extract_eof
        elif "Metadata" in method: func = SteganoEngine.extract_metadata
        elif "Alpha" in method: func = SteganoEngine.extract_alpha
        elif "Edge" in method: func = SteganoEngine.extract_edge
        
        self.worker = WorkerThread(func, self.selected_file)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, status, result):
        if status == "SUCCESS":
            self.log_output.append(f"✅ สำเร็จ: {result}")
            self.open_folder_btn.setEnabled(True)
            if isinstance(result, bytes):
                try: self.msg_input.setPlainText(result.decode('utf-8'))
                except: pass
            elif isinstance(result, str) and "extract" in self.sender().func.__name__.lower():
                self.msg_input.setPlainText(result)
        else:
            self.log_output.append(f"❌ ข้อผิดพลาด: {result}")

    def open_output_folder(self):
        path = PathManager.get_category_dir("audio")
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))
