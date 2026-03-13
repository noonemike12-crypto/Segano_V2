import os
import base64
import random
import string
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QPushButton, QComboBox, QTextEdit, QLineEdit, QFrame, 
    QFileDialog, QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt

from utils.encryption import CryptoUtils

class EncryptionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- ส่วน AES Encryption ---
        aes_group = QGroupBox("🔐 การเข้ารหัส AES-256 (Symmetric)")
        aes_layout = QVBoxLayout()
        
        aes_layout.addWidget(QLabel("📝 ข้อความที่ต้องการเข้ารหัส/ถอดรหัส:"))
        self.aes_input = QTextEdit()
        self.aes_input.setPlaceholderText("ใส่ข้อความที่นี่...")
        aes_layout.addWidget(self.aes_input)
        
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("🔑 กุญแจ (Key):"))
        self.aes_key = QLineEdit()
        self.aes_key.setPlaceholderText("ใส่กุญแจ 16, 24 หรือ 32 ตัวอักษร")
        key_layout.addWidget(self.aes_key)
        
        self.gen_key_btn = QPushButton("🎲 สุ่มกุญแจ")
        self.gen_key_btn.clicked.connect(self.generate_aes_key)
        key_layout.addWidget(self.gen_key_btn)
        aes_layout.addLayout(key_layout)
        
        btns = QHBoxLayout()
        self.aes_encrypt_btn = QPushButton("🔒 เข้ารหัส AES")
        self.aes_encrypt_btn.setObjectName("primaryBtn")
        self.aes_encrypt_btn.clicked.connect(self.aes_encrypt)
        
        self.aes_decrypt_btn = QPushButton("🔓 ถอดรหัส AES")
        self.aes_decrypt_btn.setObjectName("secondaryBtn")
        self.aes_decrypt_btn.clicked.connect(self.aes_decrypt)
        
        btns.addWidget(self.aes_encrypt_btn)
        btns.addWidget(self.aes_decrypt_btn)
        aes_layout.addLayout(btns)
        
        aes_group.setLayout(aes_layout)
        layout.addWidget(aes_group)

        # --- ส่วน RSA Encryption ---
        rsa_group = QGroupBox("🔑 การเข้ารหัส RSA (Asymmetric)")
        rsa_layout = QVBoxLayout()
        
        rsa_layout.addWidget(QLabel("📝 ข้อความสำหรับ RSA:"))
        self.rsa_input = QTextEdit()
        self.rsa_input.setPlaceholderText("ใส่ข้อความที่นี่...")
        rsa_layout.addWidget(self.rsa_input)
        
        keys_layout = QHBoxLayout()
        
        pub_layout = QVBoxLayout()
        pub_layout.addWidget(QLabel("📜 กุญแจสาธารณะ (Public Key):"))
        self.pub_key_text = QTextEdit()
        pub_layout.addWidget(self.pub_key_text)
        keys_layout.addLayout(pub_layout)
        
        priv_layout = QVBoxLayout()
        priv_layout.addWidget(QLabel("🔐 กุญแจส่วนตัว (Private Key):"))
        self.priv_key_text = QTextEdit()
        priv_layout.addWidget(self.priv_key_text)
        keys_layout.addLayout(priv_layout)
        
        rsa_layout.addLayout(keys_layout)
        
        rsa_btns = QHBoxLayout()
        self.gen_rsa_btn = QPushButton("✨ สร้างคู่กุญแจ RSA")
        self.gen_rsa_btn.clicked.connect(self.generate_rsa_keys)
        
        self.rsa_encrypt_btn = QPushButton("🔒 เข้ารหัสด้วย Public Key")
        self.rsa_encrypt_btn.setObjectName("primaryBtn")
        self.rsa_encrypt_btn.clicked.connect(self.rsa_encrypt)
        
        self.rsa_decrypt_btn = QPushButton("🔓 ถอดรหัสด้วย Private Key")
        self.rsa_decrypt_btn.setObjectName("secondaryBtn")
        self.rsa_decrypt_btn.clicked.connect(self.rsa_decrypt)
        
        rsa_btns.addWidget(self.gen_rsa_btn)
        rsa_btns.addWidget(self.rsa_encrypt_btn)
        rsa_btns.addWidget(self.rsa_decrypt_btn)
        rsa_layout.addLayout(rsa_btns)
        
        rsa_group.setLayout(rsa_layout)
        layout.addWidget(rsa_group)

        # --- ส่วนแสดงผลลัพธ์รวม ---
        result_group = QGroupBox("📊 ผลลัพธ์ (Output)")
        result_layout = QVBoxLayout()
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        result_layout.addWidget(self.result_output)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

    def generate_aes_key(self):
        key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        self.aes_key.setText(key)

    def aes_encrypt(self):
        data = self.aes_input.toPlainText()
        key = self.aes_key.text()
        if not data or not key: return
        res = CryptoUtils.aes_encrypt(data, key)
        self.result_output.setPlainText(res)

    def aes_decrypt(self):
        data = self.aes_input.toPlainText()
        key = self.aes_key.text()
        if not data or not key: return
        res = CryptoUtils.aes_decrypt(data, key)
        self.result_output.setPlainText(res)

    def generate_rsa_keys(self):
        priv, pub = CryptoUtils.rsa_generate_keys()
        self.priv_key_text.setPlainText(priv)
        self.pub_key_text.setPlainText(pub)
        self.result_output.setPlainText("✅ สร้างคู่กุญแจ RSA สำเร็จ!")

    def rsa_encrypt(self):
        data = self.rsa_input.toPlainText()
        pub = self.pub_key_text.toPlainText()
        if not data or not pub: return
        try:
            res = CryptoUtils.rsa_encrypt(data, pub)
            self.result_output.setPlainText(res)
        except Exception as e:
            self.result_output.setPlainText(f"❌ ข้อผิดพลาด: {str(e)}")

    def rsa_decrypt(self):
        data = self.rsa_input.toPlainText()
        priv = self.priv_key_text.toPlainText()
        if not data or not priv: return
        try:
            res = CryptoUtils.rsa_decrypt(data, priv)
            self.result_output.setPlainText(res)
        except Exception as e:
            self.result_output.setPlainText(f"❌ ข้อผิดพลาด: {str(e)}")
