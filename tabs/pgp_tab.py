import os
import datetime
import subprocess
import tempfile
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QPushButton, QTextEdit, QLineEdit, QFrame, QFileDialog, 
    QMessageBox, QInputDialog, QListWidget, QComboBox, QDialog, QFormLayout
)
from PyQt5.QtCore import Qt
import gnupg

class PGPTab(QWidget):
    def __init__(self):
        super().__init__()
        self.gpg = gnupg.GPG()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # --- Top Section: Intro ---
        intro_layout = QVBoxLayout()
        title = QLabel("PGP Secure Communications")
        title.setStyleSheet("font-size: 18pt; font-weight: 800; color: white;")
        subtitle = QLabel("Implement Pretty Good Privacy (PGP) for end-to-end encrypted messaging and digital signatures.")
        subtitle.setObjectName("subTitle")
        intro_layout.addWidget(title)
        intro_layout.addWidget(subtitle)
        main_layout.addLayout(intro_layout)

        # --- Middle Section: Main Grid ---
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(30)

        # Left Column: Key Management & Identity
        left_col = QVBoxLayout()
        key_group = QGroupBox("KEYRING MANAGEMENT")
        key_layout = QVBoxLayout(key_group)
        
        self.gen_key_btn = QPushButton("✨ Generate New Keypair")
        self.gen_key_btn.clicked.connect(self.generate_keys)
        self.list_keys_btn = QPushButton("📋 View Local Keyring")
        self.list_keys_btn.clicked.connect(self.list_keys)
        self.import_btn = QPushButton("📥 Import External Key")
        self.import_btn.clicked.connect(self.import_key)
        
        key_layout.addWidget(self.gen_key_btn)
        key_layout.addWidget(self.list_keys_btn)
        key_layout.addWidget(self.import_btn)
        left_col.addWidget(key_group)
        
        # Key Details Display
        key_details_group = QGroupBox("ACTIVE KEY DETAILS")
        key_details_layout = QVBoxLayout(key_details_group)
        self.key_input = QTextEdit()
        self.key_input.setPlaceholderText("Paste Public/Private Key block here for manual processing...")
        self.key_input.setMaximumHeight(250)
        key_details_layout.addWidget(self.key_input)
        left_col.addWidget(key_details_group)
        
        grid_layout.addLayout(left_col, 2)

        # Right Column: Message Processing
        right_col = QVBoxLayout()
        msg_group = QGroupBox("MESSAGE PROCESSING")
        msg_layout = QVBoxLayout(msg_group)
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter plaintext message or PGP encrypted block...")
        self.message_input.setMinimumHeight(300)
        msg_layout.addWidget(self.message_input)
        
        action_grid = QGridLayout()
        self.encrypt_btn = QPushButton("🔒 Encrypt")
        self.encrypt_btn.setObjectName("primaryBtn")
        self.encrypt_btn.clicked.connect(self.process_encrypt)
        
        self.decrypt_btn = QPushButton("🔓 Decrypt")
        self.decrypt_btn.setObjectName("secondaryBtn")
        self.decrypt_btn.clicked.connect(self.process_decrypt)
        
        self.sign_btn = QPushButton("✍️ Sign")
        self.sign_btn.clicked.connect(self.process_sign)
        
        self.verify_btn = QPushButton("✅ Verify")
        self.verify_btn.clicked.connect(self.process_verify)
        
        action_grid.addWidget(self.encrypt_btn, 0, 0)
        action_grid.addWidget(self.decrypt_btn, 0, 1)
        action_grid.addWidget(self.sign_btn, 1, 0)
        action_grid.addWidget(self.verify_btn, 1, 1)
        msg_layout.addLayout(action_grid)
        
        right_col.addWidget(msg_group)
        grid_layout.addLayout(right_col, 3)
        main_layout.addLayout(grid_layout)

        # Output Section
        result_group = QGroupBox("COMMAND OUTPUT")
        result_layout = QVBoxLayout(result_group)
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("PGP operation results will be displayed here...")
        self.result_output.setMaximumHeight(150)
        result_layout.addWidget(self.result_output)
        main_layout.addWidget(result_group)

    def generate_keys(self):
        name, ok1 = QInputDialog.getText(self, "สร้างกุญแจ", "ชื่อ-นามสกุล:")
        if not ok1: return
        email, ok2 = QInputDialog.getText(self, "สร้างกุญแจ", "อีเมล:")
        if not ok2: return
        passphrase, ok3 = QInputDialog.getText(self, "สร้างกุญแจ", "รหัสผ่านกุญแจ (Passphrase):", QLineEdit.Password)
        if not ok3: return
        
        try:
            input_data = self.gpg.gen_key_input(
                name_real=name,
                name_email=email,
                passphrase=passphrase,
                key_type="RSA",
                key_length=2048
            )
            key = self.gpg.gen_key(input_data)
            self.result_output.setPlainText(f"✅ สร้างกุญแจสำเร็จ!\nFingerprint: {key.fingerprint}")
        except Exception as e:
            self.result_output.setPlainText(f"❌ เกิดข้อผิดพลาด: {str(e)}")

    def list_keys(self):
        public_keys = self.gpg.list_keys()
        res = "📋 รายการกุญแจสาธารณะ:\n"
        for k in public_keys:
            res += f"- {k['uids'][0]} ({k['fingerprint']})\n"
        self.result_output.setPlainText(res)

    def import_key(self):
        path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์กุญแจ (.asc)")
        if path:
            with open(path, 'r') as f:
                res = self.gpg.import_keys(f.read())
                self.result_output.setPlainText(f"✅ นำเข้าสำเร็จ: {res.count} กุญแจ")

    def process_encrypt(self):
        msg = self.message_input.toPlainText()
        key_text = self.key_input.toPlainText()
        if not msg or not key_text: return
        
        self.gpg.import_keys(key_text)
        # ดึง fingerprint ล่าสุดที่นำเข้า
        fingerprint = self.gpg.list_keys()[-1]['fingerprint']
        
        enc = self.gpg.encrypt(msg, recipients=[fingerprint], always_trust=True)
        if enc.ok:
            self.result_output.setPlainText(str(enc))
        else:
            self.result_output.setPlainText(f"❌ เข้ารหัสไม่สำเร็จ: {enc.status}")

    def process_decrypt(self):
        msg = self.message_input.toPlainText()
        if not msg: return
        
        passphrase, ok = QInputDialog.getText(self, "ถอดรหัส", "ใส่รหัสผ่านกุญแจ:", QLineEdit.Password)
        if not ok: return
        
        dec = self.gpg.decrypt(msg, passphrase=passphrase)
        if dec.ok:
            self.result_output.setPlainText(str(dec.data.decode('utf-8')))
        else:
            self.result_output.setPlainText(f"❌ ถอดรหัสไม่สำเร็จ: {dec.status}")

    def process_sign(self):
        msg = self.message_input.toPlainText()
        if not msg: return
        
        passphrase, ok = QInputDialog.getText(self, "ลงลายเซ็น", "ใส่รหัสผ่านกุญแจ:", QLineEdit.Password)
        if not ok: return
        
        sign = self.gpg.sign(msg, passphrase=passphrase, detach=True)
        if sign.status == 'signature created':
            self.result_output.setPlainText(str(sign))
        else:
            self.result_output.setPlainText(f"❌ ลงลายเซ็นไม่สำเร็จ: {sign.status}")

    def process_verify(self):
        msg = self.message_input.toPlainText()
        # สมมติว่า signature อยู่ในช่อง key_input
        sig = self.key_input.toPlainText()
        if not msg or not sig: return
        
        # เขียนลงไฟล์ชั่วคราวเพื่อตรวจสอบ
        with tempfile.NamedTemporaryFile(delete=False) as f_msg:
            f_msg.write(msg.encode('utf-8'))
            msg_path = f_msg.name
        with tempfile.NamedTemporaryFile(delete=False) as f_sig:
            f_sig.write(sig.encode('utf-8'))
            sig_path = f_sig.name
            
        verify = self.gpg.verify_detached(sig_path, msg_path)
        if verify.status == 'signature valid':
            self.result_output.setPlainText(f"✅ ลายเซ็นถูกต้อง!\nผู้ลงชื่อ: {verify.username}")
        else:
            self.result_output.setPlainText(f"❌ ลายเซ็นไม่ถูกต้อง: {verify.status}")
        
        os.remove(msg_path)
        os.remove(sig_path)
