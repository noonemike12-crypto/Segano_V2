import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QPushButton, QTextEdit, 
    QLabel, QFileDialog, QHBoxLayout, QMessageBox, QLineEdit, QComboBox
)
from PyQt5.QtCore import Qt
from utils.crypto_engine import CryptoEngine
from utils.logger import logger

class PGPTab(QWidget):
    def __init__(self):
        super().__init__()
        self.crypto = CryptoEngine()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # PGP Key Generation
        gen_group = QGroupBox("🔑 OpenPGP Key Management")
        gen_layout = QVBoxLayout()
        
        info_label = QLabel("สร้างและจัดการกุญแจ OpenPGP สำหรับการเข้ารหัสแบบอสมมาตร (Asymmetric Encryption)")
        info_label.setStyleSheet("color: #888; font-style: italic;")
        gen_layout.addWidget(info_label)
        
        form_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("ชื่อ-นามสกุล (Real Name)")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("อีเมล (Email)")
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.email_input)
        gen_layout.addLayout(form_layout)
        
        pass_layout = QHBoxLayout()
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("วลีผ่าน (Passphrase)")
        self.pass_input.setEchoMode(QLineEdit.Password)
        
        self.expiry_combo = QComboBox()
        self.expiry_combo.addItems(["ไม่มีวันหมดอายุ", "6 เดือน", "1 ปี", "2 ปี"])
        self.expiry_map = {"ไม่มีวันหมดอายุ": "0", "6 เดือน": "6m", "1 ปี": "1y", "2 ปี": "2y"}
        
        pass_layout.addWidget(self.pass_input)
        pass_layout.addWidget(QLabel("วันหมดอายุ:"))
        pass_layout.addWidget(self.expiry_combo)
        gen_layout.addLayout(pass_layout)
        
        self.gen_btn = QPushButton("✨ Generate PGP Key Pair")
        self.gen_btn.setObjectName("primaryBtn")
        self.gen_btn.clicked.connect(self.generate_pgp_key)
        gen_layout.addWidget(self.gen_btn)
        
        gen_group.setLayout(gen_layout)
        layout.addWidget(gen_group)

        # Key List
        list_group = QGroupBox("📜 รายการกุญแจในระบบ (Keyring)")
        list_layout = QVBoxLayout()
        
        self.key_list_display = QTextEdit()
        self.key_list_display.setReadOnly(True)
        self.key_list_display.setPlaceholderText("รายการกุญแจจะปรากฏที่นี่...")
        
        refresh_btn = QPushButton("🔄 Refresh Key List")
        refresh_btn.clicked.connect(self.refresh_key_list)
        
        list_layout.addWidget(self.key_list_display)
        list_layout.addWidget(refresh_btn)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)

        self.refresh_key_list()

    def generate_pgp_key(self):
        name = self.name_input.text()
        email = self.email_input.text()
        passphrase = self.pass_input.text()
        expiry = self.expiry_map[self.expiry_combo.currentText()]
        
        if not name or not email or not passphrase:
            QMessageBox.warning(self, "Warning", "กรุณากรอกข้อมูลให้ครบถ้วน")
            return
            
        try:
            logger.log("info", f"Generating PGP key for {email}...")
            key = self.crypto.generate_pgp_key(name, email, passphrase, expiry)
            if key:
                QMessageBox.information(self, "Success", f"สร้างกุญแจ PGP สำหรับ {email} สำเร็จ!")
                self.refresh_key_list()
            else:
                raise Exception("Key generation returned None")
        except Exception as e:
            logger.log("error", f"PGP Gen Error: {e}")
            QMessageBox.critical(self, "Error", f"เกิดข้อผิดพลาด: {e}")

    def refresh_key_list(self):
        try:
            keys = self.crypto.gpg.list_keys()
            if not keys:
                self.key_list_display.setPlainText("ไม่พบกุญแจในระบบ")
                return
                
            display_text = ""
            for key in keys:
                display_text += f"ID: {key['keyid']}\n"
                display_text += f"User: {key['uids'][0]}\n"
                display_text += f"Type: {key['type']}\n"
                display_text += f"Created: {key['date']}\n"
                display_text += f"Expires: {key['expires'] if key['expires'] else 'Never'}\n"
                display_text += "-" * 40 + "\n"
            self.key_list_display.setPlainText(display_text)
        except Exception as e:
            logger.log("error", f"Key List Error: {e}")
            self.key_list_display.setPlainText(f"Error: {e}")
