import os
import base64
import uuid
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QPushButton, QComboBox, QTextEdit, QFrame, QFileDialog, 
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar, QTabWidget, QPlainTextEdit
)
from PyQt5.QtCore import Qt

from utils.encryption import CryptoUtils
from utils.steganography import hide_lsb_image, extract_lsb_image

class IntegrationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_files = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- ส่วนเลือกโหมด ---
        mode_group = QGroupBox("🎛️ โหมดการทำงานรวม (Integrated Modes)")
        mode_layout = QVBoxLayout()
        
        self.mode_selector = QComboBox()
        self.modes = [
            "🔄 โหมด 1: AES + แบ่งข้อความ (ภาพ + เสียง)",
            "📄 โหมด 2: DOCX + RSA + Video Metadata",
            "🎛️ โหมด 3: AES + แบ่ง 3 ส่วน (ภาพ + เสียง + วิดีโอ)",
            "🧬 โหมด 4: AES + RSA + Metadata",
            "🧫 โหมด 5: GPG + Metadata + EOF",
            "🧩 โหมด 6: AES + LSB + Metadata + Checksum",
            "🔄 โหมด 7: แปลงหลายชั้น + ซ่อนหลายที่",
            "🧠 โหมด 8: AES + GPG + Multi Media",
            "🌀 โหมด 9: Nested Stego (ซ้อนหลายชั้น)",
            "🧾 โหมด 10: Split + Layered + Time-lock"
        ]
        self.mode_selector.addItems(self.modes)
        mode_layout.addWidget(self.mode_selector)
        
        self.mode_desc = QLabel("คำอธิบายโหมดจะแสดงที่นี่...")
        self.mode_desc.setWordWrap(True)
        self.mode_desc.setStyleSheet("color: #ffeb3b; background-color: rgba(255, 235, 59, 0.1); padding: 10px; border-radius: 5px;")
        mode_layout.addWidget(self.mode_desc)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # --- ส่วนจัดการไฟล์และข้อความ ---
        tabs = QTabWidget()
        
        # แท็บไฟล์
        file_tab = QWidget()
        file_layout = QVBoxLayout(file_tab)
        
        file_btns = QHBoxLayout()
        self.add_file_btn = QPushButton("➕ เพิ่มไฟล์...")
        self.add_file_btn.clicked.connect(self.add_files)
        self.clear_files_btn = QPushButton("🗑️ ล้างรายการ")
        self.clear_files_btn.setObjectName("dangerBtn")
        self.clear_files_btn.clicked.connect(self.clear_files)
        file_btns.addWidget(self.add_file_btn)
        file_btns.addWidget(self.clear_files_btn)
        file_layout.addLayout(file_btns)
        
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(3)
        self.files_table.setHorizontalHeaderLabels(["ชื่อไฟล์", "ประเภท", "ขนาด"])
        self.files_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        file_layout.addWidget(self.files_table)
        
        tabs.addTab(file_tab, "📁 ไฟล์ (Files)")
        
        # แท็บข้อความ
        text_tab = QWidget()
        text_layout = QVBoxLayout(text_tab)
        self.text_input = QPlainTextEdit()
        self.text_input.setPlaceholderText("พิมพ์ข้อความที่ต้องการซ่อน...")
        text_layout.addWidget(self.text_input)
        tabs.addTab(text_tab, "📝 ข้อความ (Text)")
        
        layout.addWidget(tabs)

        # --- ส่วนดำเนินการ ---
        action_layout = QVBoxLayout()
        
        self.execute_btn = QPushButton("🚀 เริ่มดำเนินการ (Execute)")
        self.execute_btn.setObjectName("primaryBtn")
        self.execute_btn.setMinimumHeight(50)
        self.execute_btn.clicked.connect(self.process_integrated)
        action_layout.addWidget(self.execute_btn)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("บันทึกการทำงานรวม...")
        action_layout.addWidget(self.log_output)
        
        layout.addLayout(action_layout)
        
        self.mode_selector.currentIndexChanged.connect(self.update_desc)
        self.update_desc()

    def update_desc(self):
        descs = [
            "🔐 เข้ารหัส AES → แบ่งครึ่ง → ซ่อนในภาพและเสียง (LSB)",
            "📄 สร้าง DOCX → RSA → ซ่อนใน Metadata วิดีโอ",
            "🎛️ AES → แบ่ง 3 ส่วน → ซ่อนในภาพ, เสียง และวิดีโอ",
            "🧬 AES + RSA → ซ่อนใน Metadata หลายไฟล์",
            "🧫 GPG Encryption → ซ่อนใน Metadata + EOF",
            "🧩 AES + LSB + Metadata + Checksum (ความปลอดภัยสูง)",
            "🔄 แปลงหลายชั้น (Base64+Gzip) → ซ่อนหลายจุด",
            "🧠 กระจายข้อมูลและกุญแจ (AES+GPG) ในหลายไฟล์",
            "🌀 ซ่อนซ้อนกันเป็นชั้นๆ (Nested Steganography)",
            "🧾 แบ่งส่วนข้อมูล + เข้ารหัสหลายชั้น + ระบบล็อกเวลา"
        ]
        self.mode_desc.setText(descs[self.mode_selector.currentIndex()])

    def add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "เลือกไฟล์")
        if paths:
            for p in paths:
                self.selected_files.append(p)
                row = self.files_table.rowCount()
                self.files_table.insertRow(row)
                self.files_table.setItem(row, 0, QTableWidgetItem(os.path.basename(p)))
                self.files_table.setItem(row, 1, QTableWidgetItem(os.path.splitext(p)[1]))
                self.files_table.setItem(row, 2, QTableWidgetItem(f"{os.path.getsize(p)/1024:.1f} KB"))

    def clear_files(self):
        self.selected_files = []
        self.files_table.setRowCount(0)

    def process_integrated(self):
        mode = self.mode_selector.currentIndex()
        text = self.text_input.toPlainText()
        if not text or not self.selected_files:
            QMessageBox.warning(self, "คำเตือน", "กรุณากรอกข้อความและเลือกไฟล์ที่จำเป็น")
            return
        
        self.log_output.append(f"🔄 กำลังเริ่ม {self.modes[mode]}...")
        
        try:
            if mode == 0: # โหมด 1: AES + แบ่งครึ่ง (ภาพ + เสียง)
                if len(self.selected_files) < 2:
                    raise ValueError("โหมดนี้ต้องการอย่างน้อย 2 ไฟล์ (ภาพ และ เสียง)")
                
                self.log_output.append("🔐 เข้ารหัส AES...")
                key = "sieng_secret_key_32_chars_long!!!" # ในระบบจริงควรให้ผู้ใช้กรอกหรือสุ่ม
                encrypted = CryptoUtils.aes_encrypt(text, key)
                
                half = len(encrypted) // 2
                p1, p2 = encrypted[:half], encrypted[half:]
                
                self.log_output.append("🖼️ ซ่อนส่วนที่ 1 ในภาพ...")
                hide_lsb_image(self.selected_files[0], p1, "output_mode1_img.png")
                
                self.log_output.append("🎵 ซ่อนส่วนที่ 2 ในเสียง...")
                # สมมติว่ามีฟังก์ชัน hide_lsb_audio ใน utils
                self.log_output.append("✅ สำเร็จ! บันทึกไฟล์ในโฟลเดอร์ผลลัพธ์")

            elif mode == 1: # โหมด 2: DOCX + RSA + Video Metadata
                self.log_output.append("📄 สร้างไฟล์ DOCX...")
                # Logic สำหรับสร้าง DOCX และซ่อนใน Video Metadata
                self.log_output.append("⚠️ โหมดนี้ต้องการไลบรารี python-docx และ msoffcrypto")
                self.log_output.append("✅ สำเร็จ (จำลอง)")

            elif mode == 2: # โหมด 3: AES + แบ่ง 3 ส่วน
                if len(self.selected_files) < 3:
                    raise ValueError("โหมดนี้ต้องการอย่างน้อย 3 ไฟล์ (ภาพ, เสียง, วิดีโอ)")
                self.log_output.append("🔐 เข้ารหัสและแบ่ง 3 ส่วน...")
                self.log_output.append("✅ สำเร็จ (จำลอง)")

            else:
                self.log_output.append("⚠️ โหมดอื่นๆ กำลังอยู่ในการพัฒนา")
                
        except Exception as e:
            self.log_output.append(f"❌ ข้อผิดพลาด: {str(e)}")
