import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QPushButton, QTextEdit, QLabel, QFileDialog, QHBoxLayout
from PyQt5.QtCore import Qt
import gnupg

class PGPTab(QWidget):
    def __init__(self):
        super().__init__()
        self.gpg = gnupg.GPG()
        self.initUI()

    def initialize_pgp(self):
        # Ensure gpg is working
        pass

    def initUI(self):
        layout = QVBoxLayout(self)
        
        key_group = QGroupBox("🔑 Key Management")
        key_layout = QHBoxLayout()
        self.gen_btn = QPushButton("✨ Generate Key Pair")
        self.gen_btn.clicked.connect(self.generate_key)
        self.list_btn = QPushButton("📋 List Keys")
        self.list_btn.clicked.connect(self.list_keys)
        key_layout.addWidget(self.gen_btn)
        key_layout.addWidget(self.list_btn)
        key_group.setLayout(key_layout)
        layout.addWidget(key_group)

        msg_group = QGroupBox("✍️ Sign & Encrypt")
        msg_layout = QVBoxLayout()
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Enter message...")
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        
        btn_layout = QHBoxLayout()
        self.encrypt_btn = QPushButton("🔒 Encrypt")
        self.decrypt_btn = QPushButton("🔓 Decrypt")
        btn_layout.addWidget(self.encrypt_btn)
        btn_layout.addWidget(self.decrypt_btn)
        
        msg_layout.addWidget(self.input_text)
        msg_layout.addLayout(btn_layout)
        msg_layout.addWidget(self.output_text)
        msg_group.setLayout(msg_layout)
        layout.addWidget(msg_group)

    def generate_key(self):
        input_data = self.gpg.gen_key_input(
            name_real='User',
            name_email='user@example.com',
            passphrase='password'
        )
        key = self.gpg.gen_key(input_data)
        QMessageBox.information(self, "Success", f"Key generated: {key.fingerprint}")

    def list_keys(self):
        keys = self.gpg.list_keys()
        self.output_text.setPlainText(str(keys))
