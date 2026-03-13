import os
import base64
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QLineEdit, QPushButton, QLabel,
    QTextEdit, QHBoxLayout, QScrollArea, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt
from utils.crypto_engine import CryptoEngine
from utils.logger import logger

class EncryptionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # AES Section
        aes_group = QGroupBox("🔐 AES-256 Symmetric Encryption")
        aes_layout = QVBoxLayout()
        
        info = QLabel("เข้ารหัสข้อมูลด้วยอัลกอริทึม AES-256 บิต โดยใช้รหัสผ่าน (Passphrase)")
        info.setStyleSheet("color: #888; font-style: italic;")
        aes_layout.addWidget(info)
        
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("ใส่ข้อความที่ต้องการเข้ารหัส/ถอดรหัสที่นี่...")
        
        pass_layout = QHBoxLayout()
        self.passphrase_input = QLineEdit()
        self.passphrase_input.setPlaceholderText("ใส่รหัสผ่าน (Passphrase)")
        self.passphrase_input.setEchoMode(QLineEdit.Password)
        pass_layout.addWidget(QLabel("รหัสผ่าน:"))
        pass_layout.addWidget(self.passphrase_input)
        
        btn_layout = QHBoxLayout()
        self.encrypt_btn = QPushButton("🔒 เข้ารหัส (Encrypt)")
        self.encrypt_btn.setObjectName("primaryBtn")
        self.encrypt_btn.clicked.connect(self.process_encrypt)
        
        self.decrypt_btn = QPushButton("🔓 ถอดรหัส (Decrypt)")
        self.decrypt_btn.setObjectName("secondaryBtn")
        self.decrypt_btn.clicked.connect(self.process_decrypt)
        
        btn_layout.addWidget(self.encrypt_btn)
        btn_layout.addWidget(self.decrypt_btn)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("ผลลัพธ์จะแสดงที่นี่...")
        
        aes_layout.addWidget(self.input_text)
        aes_layout.addLayout(pass_layout)
        aes_layout.addLayout(btn_layout)
        aes_layout.addWidget(self.output_text)
        aes_group.setLayout(aes_layout)
        layout.addWidget(aes_group)

    def process_encrypt(self):
        data = self.input_text.toPlainText()
        password = self.passphrase_input.text()
        if not data or not password:
            QMessageBox.warning(self, "Warning", "กรุณาใส่ข้อมูลและรหัสผ่าน")
            return
        
        try:
            encrypted_bytes = CryptoEngine.aes_encrypt(data.encode('utf-8'), password)
            encrypted_b64 = base64.b64encode(encrypted_bytes).decode('utf-8')
            self.output_text.setPlainText(encrypted_b64)
            logger.log("info", "AES Encryption successful.")
        except Exception as e:
            logger.log("error", f"Encryption error: {e}")
            QMessageBox.critical(self, "Error", f"การเข้ารหัสล้มเหลว: {e}")

    def process_decrypt(self):
        data_b64 = self.input_text.toPlainText()
        password = self.passphrase_input.text()
        if not data_b64 or not password:
            QMessageBox.warning(self, "Warning", "กรุณาใส่ข้อมูลและรหัสผ่าน")
            return
        
        try:
            encrypted_bytes = base64.b64decode(data_b64)
            decrypted = CryptoEngine.aes_decrypt(encrypted_bytes, password)
            self.output_text.setPlainText(decrypted.decode('utf-8'))
            logger.log("info", "AES Decryption successful.")
        except Exception as e:
            logger.log("error", f"Decryption error: {e}")
            QMessageBox.critical(self, "Error", f"การถอดรหัสล้มเหลว: {e}")
