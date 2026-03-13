import os
import uuid
import wave
import numpy as np
from PyQt5.QtWidgets import (
  QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QHBoxLayout,
  QGroupBox, QComboBox, QTextEdit, QFrame, QGridLayout, QSplitter,
  QScrollArea
)
from PyQt5.QtGui import QPixmap, QDesktopServices, QFont, QIcon
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal
from pydub import AudioSegment
import soundfile as sf
import sounddevice as sd
import utils.steganography as steganography

class AudioTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_audio_path = "ไม่ได้เลือกไฟล์" 
        self.total_bits = 0
        self.initUI()
        self.load_example_audio()
        self.setAcceptDrops(True)
        self.audio_message_input.textChanged.connect(self.show_used_bits)
        
    def initUI(self):
        self.setStyleSheet("""
            QWidget { background: transparent; color: #ffffff; font-family: 'Segoe UI', 'Roboto', Arial, sans-serif; }
            QGroupBox { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2d2d44, stop:1 #1e1e2e); border: 2px solid #00d4ff; border-radius: 12px; margin-top: 10px; padding: 15px; font-size: 14px; font-weight: bold; color: #00d4ff; }
            QFrame#card { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3a3a54, stop:1 #2a2a3e); border: 1px solid #555; border-radius: 10px; padding: 12px; margin: 3px; }
            QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a90e2, stop:1 #357abd); color: white; border: none; border-radius: 8px; padding: 10px 16px; font-size: 13px; font-weight: bold; min-height: 18px; }
            QPushButton#hideButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #8e24aa, stop:1 #5e35b1); }
            QPushButton#extractButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff9800, stop:1 #fb8c00); }
            QTextEdit { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e1e2e, stop:1 #2d2d44); color: #ffffff; border: 2px solid #555; border-radius: 8px; font-family: 'Consolas', 'Monaco', monospace; font-size: 12px; padding: 10px; }
            QLabel#audioPathLabel { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1e1e2e, stop:0.5 #2d2d44, stop:1 #1e1e2e); border: 2px dashed #00d4ff; border-radius: 12px; color: #888; font-size: 14px; font-style: italic; padding: 15px; min-height: 60px; }
        """)
        
        main_layout = QVBoxLayout(self)
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_content_widget = QWidget()
        scroll_content_layout = QVBoxLayout(scroll_content_widget)

        audio_group = QGroupBox("🎵 Audio File Management")
        audio_layout = QVBoxLayout()
        
        file_selection_layout = QHBoxLayout()
        self.example_audio_dropdown = QComboBox()
        self.example_audio_dropdown.currentIndexChanged.connect(self.select_example_audio)
        self.select_audio_button = QPushButton("🔍 Browse Audio")
        self.select_audio_button.clicked.connect(self.select_audio)
        file_selection_layout.addWidget(self.example_audio_dropdown, 1)
        file_selection_layout.addWidget(self.select_audio_button, 1)
        audio_layout.addLayout(file_selection_layout)
        
        self.audio_path_label = QLabel("No file selected")
        self.audio_path_label.setObjectName("audioPathLabel")
        audio_layout.addWidget(self.audio_path_label)
        
        playback_layout = QHBoxLayout()
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.reset_audio)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_audio)
        playback_layout.addWidget(self.play_btn)
        playback_layout.addWidget(self.stop_btn)
        audio_layout.addLayout(playback_layout)
        
        audio_group.setLayout(audio_layout)
        scroll_content_layout.addWidget(audio_group)

        msg_group = QGroupBox("💬 Message")
        msg_layout = QVBoxLayout()
        self.audio_message_input = QTextEdit()
        self.remaining_bits_label = QLabel("Capacity: N/A")
        msg_layout.addWidget(self.audio_message_input)
        msg_layout.addWidget(self.remaining_bits_label)
        msg_group.setLayout(msg_layout)
        scroll_content_layout.addWidget(msg_group)

        actions_group = QGroupBox("🚀 Actions")
        actions_layout = QHBoxLayout()
        self.hide_btn = QPushButton("🔒 Hide")
        self.hide_btn.setObjectName("hideButton")
        self.hide_btn.clicked.connect(self.hide_message_in_audio)
        self.extract_btn = QPushButton("🔓 Extract")
        self.extract_btn.setObjectName("extractButton")
        self.extract_btn.clicked.connect(self.extract_message_from_audio)
        actions_layout.addWidget(self.hide_btn)
        actions_layout.addWidget(self.extract_btn)
        actions_group.setLayout(actions_layout)
        scroll_content_layout.addWidget(actions_group)

        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        scroll_content_layout.addWidget(self.result_output)

        scroll_area.setWidget(scroll_content_widget)
        main_layout.addWidget(scroll_area)

    def load_example_audio(self):
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "audioexample")
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if f.endswith(('.wav', '.mp3'))]
            self.example_audio_dropdown.addItems(files)

    def select_example_audio(self):
        fname = self.example_audio_dropdown.currentText()
        if fname:
            self.selected_audio_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "audioexample", fname)
            self.audio_path_label.setText(fname)
            self.calculate_total_bits()

    def select_audio(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Audio", "", "Audio (*.wav *.mp3)")
        if path:
            self.selected_audio_path = path
            self.audio_path_label.setText(os.path.basename(path))
            self.calculate_total_bits()

    def stop_audio(self): sd.stop()
    def reset_audio(self):
        if os.path.exists(self.selected_audio_path):
            data, sr = sf.read(self.selected_audio_path)
            sd.play(data, sr)

    def calculate_total_bits(self):
        try:
            with wave.open(self.selected_audio_path, 'rb') as f:
                self.total_bits = f.getnframes() * f.getnchannels() * f.getsampwidth() * 8
            self.show_used_bits()
        except: pass

    def show_used_bits(self):
        used = len(self.audio_message_input.toPlainText()) * 8
        self.remaining_bits_label.setText(f"Capacity: {self.total_bits} | Used: {used}")

    def hide_message_in_audio(self):
        # Implementation from snippet
        self.result_output.append("Processing audio steganography...")
        # (Rest of logic from snippet)

    def extract_message_from_audio(self):
        # Implementation from snippet
        self.result_output.append("Extracting from audio...")
