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
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- ส่วนจัดการกุญแจ ---
        keys_group = QGroupBox("🔑 การจัดการกุญแจ PGP (Key Management)")
        keys_layout = QVBoxLayout()
        
        btns = QHBoxLayout()
        self.gen_key_btn = QPushButton("✨ สร้างคู่กุญแจใหม่")
        self.gen_key_btn.clicked.connect(self.generate_keys)
        self.list_keys_btn = QPushButton("📋 รายการกุญแจทั้งหมด")
        self.list_keys_btn.clicked.connect(self.list_keys)
        self.import_btn = QPushButton("📥 นำเข้ากุญแจ")
        self.import_btn.clicked.connect(self.import_key)
        
        btns.addWidget(self.gen_key_btn)
        btns.addWidget(self.list_keys_btn)
        btns.addWidget(self.import_btn)
        keys_layout.addLayout(btns)
        
        keys_group.setLayout(keys_layout)
        layout.addWidget(keys_group)

        # --- ส่วนเข้ารหัสและลงลายเซ็น ---
        crypto_group = QGroupBox("🔒 การเข้ารหัสและลงลายเซ็น (Encryption & Signing)")
        crypto_layout = QVBoxLayout()
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("พิมพ์ข้อความที่นี่...")
        crypto_layout.addWidget(self.message_input)
        
        self.key_input = QTextEdit()
        self.key_input.setPlaceholderText("วาง Public Key (สำหรับเข้ารหัส) หรือ Private Key (สำหรับถอดรหัส/ลงชื่อ) ที่นี่...")
        self.key_input.setMaximumHeight(150)
        crypto_layout.addWidget(self.key_input)
        
        action_btns = QHBoxLayout()
        self.encrypt_btn = QPushButton("🔒 เข้ารหัส (Encrypt)")
        self.encrypt_btn.setObjectName("primaryBtn")
        self.encrypt_btn.clicked.connect(self.process_encrypt)
        
        self.decrypt_btn = QPushButton("🔓 ถอดรหัส (Decrypt)")
        self.decrypt_btn.setObjectName("secondaryBtn")
        self.decrypt_btn.clicked.connect(self.process_decrypt)
        
        self.sign_btn = QPushButton("✍️ ลงลายเซ็น (Sign)")
        self.sign_btn.clicked.connect(self.process_sign)
        
        self.verify_btn = QPushButton("✅ ตรวจสอบ (Verify)")
        self.verify_btn.clicked.connect(self.process_verify)
        
        action_btns.addWidget(self.encrypt_btn)
        action_btns.addWidget(self.decrypt_btn)
        action_btns.addWidget(self.sign_btn)
        action_btns.addWidget(self.verify_btn)
        crypto_layout.addLayout(action_btns)
        
        crypto_group.setLayout(crypto_layout)
        layout.addWidget(crypto_group)

        # --- ส่วนแสดงผลลัพธ์ ---
        result_group = QGroupBox("📊 ผลลัพธ์ (Output)")
        result_layout = QVBoxLayout()
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        result_layout.addWidget(self.result_output)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

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
