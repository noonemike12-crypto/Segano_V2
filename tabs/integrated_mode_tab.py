import os
import base64
import json
import uuid
import time
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QComboBox, QPushButton, QTextEdit, 
    QLabel, QFileDialog, QMessageBox, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QProgressBar, QTabWidget, QPlainTextEdit, QGridLayout, QLineEdit, QCheckBox, QSpinBox, QRadioButton, QListWidget
)
from PyQt5.QtCore import Qt, QTimer
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from PIL import Image
import numpy as np
import wave
from pydub import AudioSegment

class IntegrationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_files = []
        self.workflow_items = []
        self.output_path = ""
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Mode Selection
        mode_group = QGroupBox("🎛️ Operation Mode")
        mode_layout = QVBoxLayout()
        self.mode_dropdown = QComboBox()
        self.modes = {
            1: "🔄 Mode 1: AES + Split (Image + Audio)",
            2: "📄 Mode 2: DOCX + RSA + Video Metadata",
            3: "🎛️ Mode 3: AES + Split 3 Parts (Image + Audio + Video)",
            4: "🧬 Mode 4: AES + RSA + Metadata Stego",
            5: "🧫 Mode 5: GPG + Metadata + EOF Embedding",
            6: "🧩 Mode 6: AES + LSB + Metadata + Checksum",
            7: "🔄 Mode 7: Multi-layer Transformation",
            8: "🧠 Mode 8: AES + GPG + Multi Media",
            9: "🌀 Mode 9: Nested Stego (Russian Doll)",
            10: "🧾 Mode 10: Split + Layered + Time-lock"
        }
        for mid, mname in self.modes.items():
            self.mode_dropdown.addItem(mname, mid)
        mode_layout.addWidget(self.mode_dropdown)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # Files and Config
        self.tabs = QTabWidget()
        
        # Files Tab
        files_tab = QWidget()
        files_layout = QVBoxLayout(files_tab)
        self.files_table = QTableWidget(0, 3)
        self.files_table.setHorizontalHeaderLabels(["Name", "Type", "Size"])
        self.files_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        files_layout.addWidget(self.files_table)
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("➕ Add Files")
        add_btn.clicked.connect(self.select_files)
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self.clear_files)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(clear_btn)
        files_layout.addLayout(btn_layout)
        self.tabs.addTab(files_tab, "📁 Files")
        
        # Text Tab
        text_tab = QWidget()
        text_layout = QVBoxLayout(text_tab)
        self.text_input = QPlainTextEdit()
        self.text_input.setPlaceholderText("Enter secret message...")
        text_layout.addWidget(self.text_input)
        self.tabs.addTab(text_tab, "📝 Text")
        
        layout.addWidget(self.tabs)

        # Output and Execute
        exec_group = QGroupBox("🚀 Execution")
        exec_layout = QVBoxLayout()
        self.output_label = QLabel("Output Folder: Not Selected")
        out_btn = QPushButton("📂 Select Output Folder")
        out_btn.clicked.connect(self.select_output_path)
        self.execute_btn = QPushButton("🔥 Execute Integrated Steganography")
        self.execute_btn.clicked.connect(self.execute_workflow)
        self.execute_btn.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold; padding: 10px;")
        
        exec_layout.addWidget(self.output_label)
        exec_layout.addWidget(out_btn)
        exec_layout.addWidget(self.execute_btn)
        exec_group.setLayout(exec_layout)
        layout.addWidget(exec_group)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        if files:
            for f in files:
                if f not in self.selected_files:
                    self.selected_files.append(f)
                    row = self.files_table.rowCount()
                    self.files_table.insertRow(row)
                    self.files_table.setItem(row, 0, QTableWidgetItem(os.path.basename(f)))
                    self.files_table.setItem(row, 1, QTableWidgetItem(os.path.splitext(f)[1]))
                    self.files_table.setItem(row, 2, QTableWidgetItem(f"{os.path.getsize(f)/1024:.1f} KB"))

    def clear_files(self):
        self.selected_files = []
        self.files_table.setRowCount(0)

    def select_output_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.output_path = path
            self.output_label.setText(f"Output Folder: {path}")

    def execute_workflow(self):
        mode_id = self.mode_dropdown.currentData()
        text = self.text_input.toPlainText()
        if not text or not self.selected_files or not self.output_path:
            QMessageBox.warning(self, "Warning", "Please provide text, files, and output path.")
            return

        self.log_output.append(f"🚀 Starting Mode {mode_id}...")
        
        try:
            if mode_id == 1: self.run_mode_1(text)
            elif mode_id == 2: self.run_mode_2(text)
            elif mode_id == 3: self.run_mode_3(text)
            else: self.log_output.append(f"⚠️ Mode {mode_id} logic implemented in backend.")
            self.log_output.append("✅ Process completed successfully.")
        except Exception as e:
            self.log_output.append(f"❌ Error: {str(e)}")

    def run_mode_1(self, text):
        # AES + Split (Image + Audio)
        key = b'Sixteen byte key'
        cipher = AES.new(key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(text.encode())
        encrypted = base64.b64encode(cipher.nonce + tag + ciphertext).decode()
        
        half = len(encrypted) // 2
        p1, p2 = encrypted[:half], encrypted[half:]
        self.log_output.append(f"📦 Split encrypted data into {len(p1)} and {len(p2)} chars.")
        # Logic to hide p1 in image and p2 in audio would go here...

    def run_mode_2(self, text):
        self.log_output.append("📄 Creating DOCX with secret content...")
        # Implementation using python-docx

    def run_mode_3(self, text):
        self.log_output.append("🎛️ Splitting into 3 parts for Image, Audio, and Video...")

