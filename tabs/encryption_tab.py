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
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # --- Top Section: Intro ---
        intro_layout = QVBoxLayout()
        title = QLabel("Modern Encryption Suite")
        title.setStyleSheet("font-size: 18pt; font-weight: 800; color: white;")
        subtitle = QLabel("Secure your sensitive data using high-performance symmetric and asymmetric cryptography.")
        subtitle.setObjectName("subTitle")
        intro_layout.addWidget(title)
        intro_layout.addWidget(subtitle)
        main_layout.addLayout(intro_layout)

        # --- Middle Section: Main Grid ---
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(30)

        # Left Column: Input Area
        left_col = QVBoxLayout()
        input_group = QGroupBox("SOURCE INPUT")
        input_layout = QVBoxLayout(input_group)
        self.aes_input = QTextEdit()
        self.aes_input.setPlaceholderText("Paste or type the plaintext to encrypt, or the ciphertext to decrypt...")
        self.aes_input.setMinimumHeight(200)
        input_layout.addWidget(self.aes_input)
        
        btn_row = QHBoxLayout()
        self.aes_encrypt_btn = QPushButton("🔒 Encrypt Data")
        self.aes_encrypt_btn.setObjectName("primaryBtn")
        self.aes_encrypt_btn.clicked.connect(self.aes_encrypt)
        self.aes_decrypt_btn = QPushButton("🔓 Decrypt Data")
        self.aes_decrypt_btn.setObjectName("secondaryBtn")
        self.aes_decrypt_btn.clicked.connect(self.aes_decrypt)
        btn_row.addWidget(self.aes_encrypt_btn)
        btn_row.addWidget(self.aes_decrypt_btn)
        input_layout.addLayout(btn_row)
        
        left_col.addWidget(input_group)
        grid_layout.addLayout(left_col, 3)

        # Right Column: Key Management
        right_col = QVBoxLayout()
        
        key_group = QGroupBox("KEY MANAGEMENT")
        key_layout = QVBoxLayout(key_group)
        
        key_layout.addWidget(QLabel("Encryption Key (Secret):"))
        self.aes_key = QLineEdit()
        self.aes_key.setEchoMode(QLineEdit.Password)
        self.aes_key.setPlaceholderText("Enter security key...")
        key_layout.addWidget(self.aes_key)
        
        self.gen_key_btn = QPushButton("🎲 Generate Random Key")
        self.gen_key_btn.clicked.connect(self.generate_aes_key)
        key_layout.addWidget(self.gen_key_btn)
        
        key_layout.addSpacing(20)
        key_layout.addWidget(QLabel("Mode of Operation:"))
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["AES-256-GCM (Recommended)", "AES-256-CBC"])
        key_layout.addWidget(self.mode_selector)
        
        right_col.addWidget(key_group)
        
        # Security Notice
        notice_group = QGroupBox("SECURITY NOTICE")
        notice_layout = QVBoxLayout(notice_group)
        notice_text = QLabel("🛡️ Quantum Safe\nAES-256 remains resilient against current theoretical quantum computing attacks.")
        notice_text.setWordWrap(True)
        notice_text.setStyleSheet("color: #0d7ff2; font-size: 9pt; font-weight: 600;")
        notice_layout.addWidget(notice_text)
        right_col.addWidget(notice_group)
        
        grid_layout.addLayout(right_col, 2)
        main_layout.addLayout(grid_layout)

        # RSA Section (Simplified for now to fit the new look)
        rsa_group = QGroupBox("ASYMMETRIC (RSA) MODULE")
        rsa_layout = QHBoxLayout(rsa_group)
        self.gen_rsa_btn = QPushButton("✨ Create RSA Keypair")
        self.gen_rsa_btn.clicked.connect(self.generate_rsa_keys)
        rsa_layout.addWidget(self.gen_rsa_btn)
        main_layout.addWidget(rsa_group)

        # --- Result Section ---
        result_group = QGroupBox("CRYPTOGRAPHIC OUTPUT")
        result_layout = QVBoxLayout(result_group)
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("Encrypted/Decrypted output will appear here...")
        result_layout.addWidget(self.result_output)
        main_layout.addWidget(result_group)

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
