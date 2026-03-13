import os
import base64
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QPushButton, QLabel, QFileDialog, QTextEdit, QProgressBar, QFrame, QComboBox, QCheckBox, QLineEdit, QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from utils.stegano_engine import SteganoEngine
from utils.crypto_engine import CryptoEngine
from utils.path_manager import PathManager
from utils.logger import logger

class WorkerThread(QThread):
    finished = pyqtSignal(str, object)
    progress = pyqtSignal(int)

    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        try:
            result = self.func(*self.args)
            self.finished.emit("SUCCESS", result)
        except Exception as e:
            self.finished.emit("ERROR", str(e))

class IntegrationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.source_file = None
        self.secret_file = None
        self.priv_key_path = None
        self.pub_key_path = None
        self.crypto = CryptoEngine()
        self.setAcceptDrops(True)
        self.init_ui()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.source_file = files[0]
            self.source_label.setText(f"ไฟล์หลัก: {os.path.basename(self.source_file)}")
            logger.info(f"Dropped file: {self.source_file}")

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 1. File Selection
        files_group = QGroupBox("📁 1. การเลือกไฟล์ (File Selection - Drag & Drop Supported)")
        f_layout = QVBoxLayout()
        
        h1 = QHBoxLayout()
        self.source_label = QLabel("ไฟล์หลัก (Carrier): ยังไม่ได้เลือก")
        self.btn_source = QPushButton("เลือกไฟล์หลัก")
        self.btn_source.clicked.connect(self.select_source)
        h1.addWidget(self.source_label, 1)
        h1.addWidget(self.btn_source)
        
        h2 = QHBoxLayout()
        self.secret_label = QLabel("ไฟล์ที่จะซ่อน (Secret File): (ไม่บังคับ)")
        self.btn_secret = QPushButton("เลือกไฟล์ลับ")
        self.btn_secret.clicked.connect(self.select_secret)
        h2.addWidget(self.secret_label, 1)
        h2.addWidget(self.btn_secret)
        
        f_layout.addLayout(h1)
        f_layout.addLayout(h2)
        files_group.setLayout(f_layout)

        # 2. Cryptography Options
        crypto_group = QGroupBox("🔐 2. วิทยาการรหัสลับ (Cryptography)")
        c_layout = QVBoxLayout()
        
        self.chk_aes = QCheckBox("เข้ารหัส AES-256 bit (Symmetric)")
        self.aes_pass = QLineEdit()
        self.aes_pass.setPlaceholderText("รหัสผ่าน AES (Passphrase)")
        self.aes_pass.setEchoMode(QLineEdit.Password)
        
        self.chk_pgp = QCheckBox("เข้ารหัส OpenPGP (Asymmetric - Session Key)")
        self.pgp_recipient = QLineEdit()
        self.pgp_recipient.setPlaceholderText("อีเมลผู้รับ (Recipient Email)")
        
        self.chk_sign = QCheckBox("ลงลายมือชื่อดิจิทัล (Digital Signature - ECC)")
        h_keys = QHBoxLayout()
        self.btn_load_priv = QPushButton("โหลด Private Key")
        self.btn_load_priv.clicked.connect(self.load_priv_key)
        self.btn_load_pub = QPushButton("โหลด Public Key")
        self.btn_load_pub.clicked.connect(self.load_pub_key)
        h_keys.addWidget(self.btn_load_priv)
        h_keys.addWidget(self.btn_load_pub)
        
        self.chk_integrity = QCheckBox("ตรวจสอบความสมบูรณ์ (Integrity Check - SHA256)")
        
        c_layout.addWidget(self.chk_aes)
        c_layout.addWidget(self.aes_pass)
        c_layout.addWidget(self.chk_pgp)
        c_layout.addWidget(self.pgp_recipient)
        c_layout.addWidget(self.chk_sign)
        c_layout.addLayout(h_keys)
        c_layout.addWidget(self.chk_integrity)
        crypto_group.setLayout(c_layout)

        # 3. Steganography Technique
        stego_group = QGroupBox("🕵️ 3. วิทยาการอำพรางข้อมูล (Steganography)")
        s_layout = QVBoxLayout()
        
        self.method_combo = QComboBox()
        self.method_combo.addItems(SteganoEngine.METHODS)
        
        self.msg_input = QTextEdit()
        self.msg_input.setPlaceholderText("หรือพิมพ์ข้อความที่ต้องการซ่อนที่นี่...")
        self.msg_input.setMaximumHeight(80)
        
        s_layout.addWidget(QLabel("เลือกวิธี:"))
        s_layout.addWidget(self.method_combo)
        s_layout.addWidget(QLabel("ข้อความลับ:"))
        s_layout.addWidget(self.msg_input)
        stego_group.setLayout(s_layout)

        # 4. Action
        self.btn_process = QPushButton("🚀 เริ่มกระบวนการบูรณาการ (Integrated Process)")
        self.btn_process.setObjectName("primaryBtn")
        self.btn_process.setFixedHeight(50)
        self.btn_process.clicked.connect(self.start_integrated_process)
        
        self.btn_extract = QPushButton("🔓 ถอดข้อมูลแบบบูรณาการ (Integrated Extraction)")
        self.btn_extract.setObjectName("secondaryBtn")
        self.btn_extract.clicked.connect(self.start_extraction)

        self.progress = QProgressBar()
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(200)

        layout.addWidget(files_group)
        layout.addWidget(crypto_group)
        layout.addWidget(stego_group)
        layout.addWidget(self.btn_process)
        layout.addWidget(self.btn_extract)
        layout.addWidget(self.progress)
        layout.addWidget(self.log)
        
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def select_source(self):
        path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์หลัก", "", "All Files (*.*)")
        if path:
            self.source_file = path
            self.source_label.setText(f"ไฟล์หลัก: {os.path.basename(path)}")

    def select_secret(self):
        path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์ลับ", "", "All Files (*.*)")
        if path:
            self.secret_file = path
            self.secret_label.setText(f"ไฟล์ลับ: {os.path.basename(path)}")

    def load_priv_key(self):
        path, _ = QFileDialog.getOpenFileName(self, "โหลด Private Key", "", "PEM Files (*.pem)")
        if path: self.priv_key_path = path

    def load_pub_key(self):
        path, _ = QFileDialog.getOpenFileName(self, "โหลด Public Key", "", "PEM Files (*.pem)")
        if path: self.pub_key_path = path

    def start_integrated_process(self):
        if not self.source_file:
            self.log.append("❌ กรุณาเลือกไฟล์หลักก่อน")
            return
            
        # 1. Prepare Data
        data = b""
        if self.secret_file:
            with open(self.secret_file, "rb") as f:
                data = f.read()
            # If it's a file, we might want to preserve filename in EOF mode
        else:
            data = self.msg_input.toPlainText().encode('utf-8')
            
        if not data:
            self.log.append("❌ ไม่มีข้อมูลให้ซ่อน")
            return

        # 2. Integrity Check
        if self.chk_integrity.isChecked():
            checksum = CryptoEngine.get_checksum(data)
            self.log.append(f"🔍 Checksum (SHA256): {checksum}")
            data = checksum.encode() + b"|DATA|" + data

        # 3. Digital Signature
        if self.chk_sign.isChecked():
            if not self.priv_key_path:
                self.log.append("❌ กรุณาโหลด Private Key สำหรับลงลายมือชื่อ")
                return
            with open(self.priv_key_path, "rb") as f:
                priv_pem = f.read()
            sig = CryptoEngine.sign_data(data, priv_pem)
            self.log.append("✍️ ลงลายมือชื่อดิจิทัลสำเร็จ")
            data = base64.b64encode(sig) + b"|SIG|" + data

        # 4. PGP Encryption
        if self.chk_pgp.isChecked():
            recipient = self.pgp_recipient.text()
            if not recipient:
                self.log.append("❌ กรุณาใส่อีเมลผู้รับสำหรับ PGP")
                return
            try:
                data = self.crypto.encrypt_pgp(data, recipient).encode()
                self.log.append("🔐 เข้ารหัส OpenPGP สำเร็จ")
            except Exception as e:
                self.log.append(f"❌ PGP Error: {e}")
                return

        # 5. AES Encryption
        if self.chk_aes.isChecked():
            pwd = self.aes_pass.text()
            if not pwd:
                self.log.append("❌ กรุณาใส่รหัสผ่าน AES")
                return
            data = CryptoEngine.aes_encrypt(data, pwd)
            self.log.append("🔐 เข้ารหัส AES-256 bit สำเร็จ")

        # 6. Steganography
        method = self.method_combo.currentText()
        ext = os.path.splitext(self.source_file)[1].lower()
        cat = "other"
        if ext in [".png", ".jpg", ".jpeg", ".bmp"]: cat = "image"
        elif ext in [".wav", ".mp3", ".flac"]: cat = "audio"
        elif ext in [".mp4", ".avi", ".mov", ".mkv"]: cat = "video"
        
        out_name = f"integrated_{os.path.basename(self.source_file)}"
        if "LSB" in method and cat == "image": out_name = os.path.splitext(out_name)[0] + ".png"
        
        output_path = PathManager.get_output_path(cat, out_name)
        
        self.log.append(f"⏳ กำลังซ่อนข้อมูลด้วยวิธี {method}...")
        
        func = None
        args = [self.source_file, data, output_path]
        
        if method == "LSB (Least Significant Bit)":
            func = SteganoEngine.hide_lsb
        elif method == "EOF (File Append/Join)":
            # For EOF, we can pass the secret file path directly if it exists
            secret_input = self.secret_file if self.secret_file else data
            func = SteganoEngine.hide_eof
            args = [self.source_file, secret_input, output_path]
        elif method == "Metadata (Tag/Comment)":
            data_str = base64.b64encode(data).decode()
            func = SteganoEngine.hide_metadata
            args = [self.source_file, data_str, output_path]
        elif method == "Alpha Channel (PNG/BMP)":
            func = SteganoEngine.hide_alpha
        elif method == "Edge Detection (Advanced)":
            func = SteganoEngine.hide_edge
        elif "Masking" in method:
            func = SteganoEngine.hide_masking
        elif "Palette" in method:
            func = SteganoEngine.hide_palette
        
        if not func:
            self.log.append("❌ ไม่พบฟังก์ชันสำหรับวิธีที่เลือก")
            return
            
        self.worker = WorkerThread(func, *args)
        self.worker.finished.connect(self.on_process_finished)
        self.worker.start()

    def on_process_finished(self, status, result):
        if status == "SUCCESS":
            self.log.append(f"✅ บูรณาการสำเร็จ! ไฟล์: {result}")
            QMessageBox.information(self, "Success", f"บันทึกไฟล์สำเร็จที่:\n{result}")
        else:
            self.log.append(f"❌ ข้อผิดพลาด: {result}")

    def start_extraction(self):
        if not self.source_file: return
        method = self.method_combo.currentText()
        
        self.log.append(f"⏳ กำลังถอดข้อมูลด้วยวิธี {method}...")
        
        func = None
        if method == "LSB (Least Significant Bit)":
            ext = os.path.splitext(self.source_file)[1].lower()
            if ext == ".wav": func = SteganoEngine.extract_audio_lsb
            else: func = SteganoEngine.extract_image_lsb
        elif method == "EOF (File Append/Join)": func = SteganoEngine.extract_eof
        elif method == "Metadata (Tag/Comment)": func = SteganoEngine.extract_metadata
        elif method == "Alpha Channel (PNG/BMP)": func = SteganoEngine.extract_alpha
        elif method == "Edge Detection (Advanced)": func = SteganoEngine.extract_edge
        elif "Masking" in method: func = SteganoEngine.extract_masking
        elif "Palette" in method: func = SteganoEngine.extract_palette
        
        if not func:
            self.log.append("❌ ไม่พบฟังก์ชันถอดข้อมูล")
            return
            
        self.worker = WorkerThread(func, self.source_file)
        self.worker.finished.connect(self.on_extract_finished)
        self.worker.start()

    def on_extract_finished(self, status, result):
        if status == "SUCCESS":
            data = result
            # EOF returns a dict
            if isinstance(result, dict):
                if result["type"] == "file":
                    out = PathManager.get_output_path("other", result["filename"])
                    with open(out, "wb") as f: f.write(result["data"])
                    self.log.append(f"💾 พบไฟล์ลับ: {result['filename']} บันทึกที่ {out}")
                    data = result["data"]
                else:
                    data = result["data"]

            # Metadata is often base64 encoded in our hide logic
            method = self.method_combo.currentText()
            if method == "Metadata (Tag/Comment)":
                try: data = base64.b64decode(data)
                except: pass

            # 1. AES Decrypt
            if self.chk_aes.isChecked():
                pwd = self.aes_pass.text()
                try:
                    data = CryptoEngine.aes_decrypt(data, pwd)
                    self.log.append("🔓 ถอดรหัส AES สำเร็จ")
                except:
                    self.log.append("❌ ถอดรหัส AES ล้มเหลว (รหัสผ่านผิด?)")
                    return

            # 2. PGP Decrypt
            if self.chk_pgp.isChecked():
                pwd = self.aes_pass.text() # Reuse AES pass field or ask for PGP pass?
                try:
                    data = self.crypto.decrypt_pgp(data.decode(), pwd)
                    self.log.append("🔓 ถอดรหัส OpenPGP สำเร็จ")
                except Exception as e:
                    self.log.append(f"❌ PGP Decrypt Error: {e}")
                    return

            # 3. Verify Signature
            if self.chk_sign.isChecked():
                if b"|SIG|" in data:
                    sig_b64, rest = data.split(b"|SIG|", 1)
                    sig = base64.b64decode(sig_b64)
                    if self.pub_key_path:
                        with open(self.pub_key_path, "rb") as f: pub_pem = f.read()
                        if CryptoEngine.verify_signature(rest, sig, pub_pem):
                            self.log.append("✅ ตรวจสอบลายมือชื่อดิจิทัล: ถูกต้อง")
                        else:
                            self.log.append("❌ ตรวจสอบลายมือชื่อดิจิทัล: ไม่ถูกต้อง!")
                    data = rest

            # 4. Integrity Check
            if self.chk_integrity.isChecked():
                if b"|DATA|" in data:
                    checksum, rest = data.split(b"|DATA|", 1)
                    actual = CryptoEngine.get_checksum(rest)
                    if checksum.decode() == actual:
                        self.log.append("✅ ตรวจสอบความสมบูรณ์: ข้อมูลถูกต้อง")
                    else:
                        self.log.append("❌ ตรวจสอบความสมบูรณ์: ข้อมูลถูกแก้ไข!")
                    data = rest

            # Show result
            try:
                text = data.decode('utf-8')
                self.msg_input.setPlainText(text)
                self.log.append("📄 ผลลัพธ์: ข้อความ")
            except:
                out = PathManager.get_output_path("other", "extracted_integrated.bin")
                with open(out, "wb") as f: f.write(data)
                self.log.append(f"💾 ผลลัพธ์: ไฟล์ถูกบันทึกที่ {out}")
        else:
            self.log.append(f"❌ การถอดข้อมูลล้มเหลว: {result}")
