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
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # --- Top Section: Intro ---
        intro_layout = QVBoxLayout()
        title = QLabel("File-in-File Steganography")
        title.setStyleSheet("font-size: 18pt; font-weight: 800; color: white;")
        subtitle = QLabel("Conceal multiple secret files within a single carrier file using advanced appending and offset techniques.")
        subtitle.setObjectName("subTitle")
        intro_layout.addWidget(title)
        intro_layout.addWidget(subtitle)
        main_layout.addLayout(intro_layout)

        # --- Middle Section: Main Grid ---
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(30)

        # Left Column: Carrier Selection
        left_col = QVBoxLayout()
        carrier_group = QGroupBox("CARRIER FILE SELECTION")
        carrier_layout = QVBoxLayout(carrier_group)
        self.carrier_label = QLabel("Click to upload or drag & drop\nCarrier File (e.g., Image, Video, PDF)")
        self.carrier_label.setAlignment(Qt.AlignCenter)
        self.carrier_label.setMinimumSize(300, 150)
        self.carrier_label.setStyleSheet("""
            border: 2px dashed #1e293b;
            border-radius: 15px;
            color: #64748b;
            font-size: 11pt;
            background-color: #0b0e14;
        """)
        carrier_layout.addWidget(self.carrier_label)
        
        self.carrier_btn = QPushButton("📁 Browse Carrier...")
        self.carrier_btn.clicked.connect(self.browse_carrier)
        carrier_layout.addWidget(self.carrier_btn)
        left_col.addWidget(carrier_group)
        grid_layout.addLayout(left_col, 3)

        # Right Column: Secret Files & Actions
        right_col = QVBoxLayout()
        
        # Secret Files List
        secret_group = QGroupBox("SECRET PAYLOAD FILES")
        secret_layout = QVBoxLayout(secret_group)
        self.secret_list = QListWidget()
        self.secret_list.setMinimumHeight(150)
        secret_layout.addWidget(self.secret_list)
        
        btn_row = QHBoxLayout()
        self.add_secret_btn = QPushButton("➕ Add Files")
        self.add_secret_btn.clicked.connect(self.browse_secrets)
        self.clear_secrets_btn = QPushButton("🗑️ Clear All")
        self.clear_secrets_btn.setObjectName("dangerBtn")
        self.clear_secrets_btn.clicked.connect(self.clear_secrets)
        btn_row.addWidget(self.add_secret_btn)
        btn_row.addWidget(self.clear_secrets_btn)
        secret_layout.addLayout(btn_row)
        right_col.addWidget(secret_group)

        # Actions
        action_group = QGroupBox("EXECUTION CONTROL")
        action_layout = QVBoxLayout(action_group)
        self.hide_btn = QPushButton("🔒 Hide Files (Append)")
        self.hide_btn.setObjectName("primaryBtn")
        self.hide_btn.clicked.connect(self.process_hide)
        
        self.extract_btn = QPushButton("🔓 Extract Files")
        self.extract_btn.setObjectName("secondaryBtn")
        self.extract_btn.clicked.connect(self.process_extract)
        
        action_layout.addWidget(self.hide_btn)
        action_layout.addWidget(self.extract_btn)
        right_col.addWidget(action_group)
        
        grid_layout.addLayout(right_col, 2)
        main_layout.addLayout(grid_layout)

        # Logs
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Operation logs...")
        self.log_output.setMaximumHeight(100)
        main_layout.addWidget(self.log_output)

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
