import os
import shutil
import struct
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QPushButton, QTextEdit, QFrame, QFileDialog, QMessageBox, 
    QListWidget, QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

class FileAndFileTab(QWidget):
    def __init__(self):
        super().__init__()
        self.carrier_file = None
        self.secret_files = []
        self.init_ui()
        self.setAcceptDrops(True)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- ส่วนเลือกไฟล์หลัก (Carrier) ---
        carrier_group = QGroupBox("📦 ไฟล์หลักที่ใช้ซ่อน (Carrier File)")
        carrier_layout = QHBoxLayout()
        self.carrier_label = QLabel("ลากไฟล์หลักมาวางที่นี่")
        self.carrier_label.setAlignment(Qt.AlignCenter)
        self.carrier_label.setStyleSheet("border: 2px dashed #4a5568; border-radius: 10px; padding: 15px;")
        carrier_layout.addWidget(self.carrier_label, 3)
        self.carrier_btn = QPushButton("🔍 เลือกไฟล์...")
        self.carrier_btn.clicked.connect(self.browse_carrier)
        carrier_layout.addWidget(self.carrier_btn, 1)
        carrier_group.setLayout(carrier_layout)
        layout.addWidget(carrier_group)

        # --- ส่วนเลือกไฟล์ที่จะซ่อน (Secret Files) ---
        secret_group = QGroupBox("📁 ไฟล์ที่จะนำไปซ่อน (Secret Files)")
        secret_layout = QVBoxLayout()
        
        self.secret_list = QListWidget()
        secret_layout.addWidget(self.secret_list)
        
        btns = QHBoxLayout()
        self.add_secret_btn = QPushButton("➕ เพิ่มไฟล์...")
        self.add_secret_btn.clicked.connect(self.browse_secrets)
        self.clear_secrets_btn = QPushButton("🗑️ ล้างทั้งหมด")
        self.clear_secrets_btn.setObjectName("dangerBtn")
        self.clear_secrets_btn.clicked.connect(self.clear_secrets)
        btns.addWidget(self.add_secret_btn)
        btns.addWidget(self.clear_secrets_btn)
        secret_layout.addLayout(btns)
        
        secret_group.setLayout(secret_layout)
        layout.addWidget(secret_group)

        # --- ส่วนดำเนินการ ---
        action_layout = QHBoxLayout()
        self.hide_btn = QPushButton("🔒 ซ่อนไฟล์ (Append)")
        self.hide_btn.setObjectName("primaryBtn")
        self.hide_btn.clicked.connect(self.process_hide)
        
        self.extract_btn = QPushButton("🔓 แยกไฟล์ออก (Extract)")
        self.extract_btn.setObjectName("secondaryBtn")
        self.extract_btn.clicked.connect(self.process_extract)
        
        action_layout.addWidget(self.hide_btn)
        action_layout.addWidget(self.extract_btn)
        layout.addLayout(action_layout)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("บันทึกการทำงาน...")
        self.log_output.setMaximumHeight(150)
        layout.addWidget(self.log_output)

    def browse_carrier(self):
        path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์หลัก")
        if path:
            self.carrier_file = path
            self.carrier_label.setText(f"ไฟล์หลัก: {os.path.basename(path)}")

    def browse_secrets(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "เลือกไฟล์ที่จะซ่อน")
        if paths:
            self.secret_files.extend(paths)
            for p in paths: self.secret_list.addItem(os.path.basename(p))

    def clear_secrets(self):
        self.secret_files = []
        self.secret_list.clear()

    def process_hide(self):
        if not self.carrier_file or not self.secret_files:
            QMessageBox.warning(self, "คำเตือน", "กรุณาเลือกไฟล์หลักและไฟล์ที่จะซ่อน")
            return
            
        try:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output_files")
            os.makedirs(output_dir, exist_ok=True)
            
            ext = os.path.splitext(self.carrier_file)[1]
            output_path = os.path.join(output_dir, f"appended_{int(time.time())}{ext}")
            
            shutil.copy2(self.carrier_file, output_path)
            
            with open(output_path, 'ab') as f_out:
                original_size = os.path.getsize(self.carrier_file)
                # เขียนจำนวนไฟล์
                f_out.write(struct.pack('<I', len(self.secret_files)))
                
                for s_path in self.secret_files:
                    name = os.path.basename(s_path).encode('utf-8')
                    with open(s_path, 'rb') as f_in:
                        data = f_in.read()
                    # โครงสร้าง: [ความยาวชื่อ][ชื่อไฟล์][ความยาวข้อมูล][ข้อมูล]
                    f_out.write(struct.pack('<I', len(name)))
                    f_out.write(name)
                    f_out.write(struct.pack('<Q', len(data)))
                    f_out.write(data)
                
                # เขียนตำแหน่งเริ่มต้นของข้อมูลที่เพิ่มเข้าไป (ขนาดไฟล์เดิม)
                f_out.write(struct.pack('<Q', original_size))
                
            self.log_output.append(f"✅ ซ่อนไฟล์สำเร็จ!\nบันทึกที่: {output_path}")
        except Exception as e:
            self.log_output.append(f"❌ เกิดข้อผิดพลาด: {str(e)}")

    def process_extract(self):
        path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์ที่ต้องการแยกข้อมูล")
        if not path: return
        
        out_dir = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์ที่จะบันทึกไฟล์ที่แยกออกมา")
        if not out_dir: return
        
        try:
            with open(path, 'rb') as f:
                # อ่านตำแหน่งเริ่มต้นจาก 8 ไบต์สุดท้าย
                f.seek(-8, os.SEEK_END)
                start_pos = struct.unpack('<Q', f.read(8))[0]
                
                f.seek(start_pos)
                num_files = struct.unpack('<I', f.read(4))[0]
                
                for _ in range(num_files):
                    name_len = struct.unpack('<I', f.read(4))[0]
                    name = f.read(name_len).decode('utf-8')
                    data_len = struct.unpack('<Q', f.read(8))[0]
                    data = f.read(data_len)
                    
                    with open(os.path.join(out_dir, name), 'wb') as f_ext:
                        f_ext.write(data)
                        
            self.log_output.append(f"✅ แยกไฟล์สำเร็จ {num_files} ไฟล์ ไปยัง: {out_dir}")
        except Exception as e:
            self.log_output.append(f"❌ ไม่พบข้อมูลที่ซ่อนอยู่ หรือไฟล์เสียหาย: {str(e)}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.carrier_file = path
            self.carrier_label.setText(f"ไฟล์หลัก: {os.path.basename(path)}")
