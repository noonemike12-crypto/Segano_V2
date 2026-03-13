from PyQt5.QtWidgets import (
  QWidget, QVBoxLayout, QGroupBox, QLineEdit, QComboBox, QPushButton, QLabel,
  QTextEdit, QHBoxLayout, QScrollArea, QFrame, QMessageBox
)
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QDesktopServices
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
import os
import random
import string

class EncryptionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        
        aes_group = QGroupBox("🔐 AES Encryption")
        aes_layout = QVBoxLayout()
        self.aes_msg = QTextEdit()
        self.aes_key = QLineEdit()
        self.aes_encrypt_btn = QPushButton("Encrypt AES")
        self.aes_encrypt_btn.clicked.connect(self.encrypt_aes)
        aes_layout.addWidget(QLabel("Message:"))
        aes_layout.addWidget(self.aes_msg)
        aes_layout.addWidget(QLabel("Key:"))
        aes_layout.addWidget(self.aes_key)
        aes_layout.addWidget(self.aes_encrypt_btn)
        aes_group.setLayout(aes_layout)
        layout.addWidget(aes_group)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

    def encrypt_aes(self):
        msg = self.aes_msg.toPlainText()
        key = self.aes_key.text()
        if len(key) not in [16, 24, 32]:
            self.log.append("Key must be 16, 24 or 32 bytes")
            return
        cipher = AES.new(key.encode(), AES.MODE_CBC)
        ct = cipher.encrypt(pad(msg.encode(), AES.block_size))
        res = base64.b64encode(cipher.iv + ct).decode()
        self.log.append(f"AES Result: {res}")
