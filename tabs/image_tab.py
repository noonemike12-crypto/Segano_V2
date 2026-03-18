import os
import uuid
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QPushButton, QComboBox, QTextEdit, QProgressBar, QFrame, 
    QFileDialog, QGridLayout
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices

from utils.steganography import (
    hide_lsb_image, extract_lsb_image,
    hide_alpha_channel, extract_alpha_channel,
    hide_edge_detection, extract_edge_detection
)
from utils.check_bit import (
    get_image_capacity_lsb, get_image_capacity_alpha, get_image_capacity_edge
)
from utils.logger import logger

class ImageTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_image = None
        self.capacity = 0
        self.init_ui()
        self.setAcceptDrops(True)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # --- Top Section: Intro ---
        intro_layout = QVBoxLayout()
        title = QLabel("Embed Hidden Data in Images")
        title.setStyleSheet("font-size: 18pt; font-weight: 800; color: white;")
        subtitle = QLabel("Securely hide encrypted messages within high-definition image carriers.")
        subtitle.setObjectName("subTitle")
        intro_layout.addWidget(title)
        intro_layout.addWidget(subtitle)
        main_layout.addLayout(intro_layout)

        # --- Middle Section: Main Grid ---
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(30)

        # Left Column: Preview
        left_col = QVBoxLayout()
        preview_group = QGroupBox("CARRIER IMAGE PREVIEW")
        preview_layout = QVBoxLayout(preview_group)
        
        self.image_preview = QLabel("Drag & Drop Image Here")
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setMinimumSize(400, 300)
        self.image_preview.setStyleSheet("""
            border: 2px dashed #1e293b;
            border-radius: 15px;
            color: #64748b;
            font-size: 12pt;
            background-color: #0b0e14;
        """)
        preview_layout.addWidget(self.image_preview)
        
        self.capacity_label = QLabel("📊 Capacity: 0 bits | Used: 0 bits")
        self.capacity_label.setAlignment(Qt.AlignCenter)
        self.capacity_label.setStyleSheet("color: #94a3b8; font-size: 9pt; margin-top: 10px;")
        preview_layout.addWidget(self.capacity_label)
        
        left_col.addWidget(preview_group)
        
        # File Selection Buttons
        file_btns = QHBoxLayout()
        self.browse_btn = QPushButton("🔍 Browse Files...")
        self.browse_btn.clicked.connect(self.browse_image)
        self.example_selector = QComboBox()
        self.example_selector.setPlaceholderText("Select Example...")
        self.load_example_list()
        self.example_selector.currentIndexChanged.connect(self.load_example_image)
        
        file_btns.addWidget(self.browse_btn)
        file_btns.addWidget(self.example_selector)
        left_col.addLayout(file_btns)
        
        grid_layout.addLayout(left_col, 3)

        # Right Column: Payload & Settings
        right_col = QVBoxLayout()
        
        # Payload Section
        payload_group = QGroupBox("PAYLOAD CONFIGURATION")
        payload_layout = QVBoxLayout(payload_group)
        payload_layout.addWidget(QLabel("Secret Message:"))
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Type the message you want to hide...")
        self.message_input.textChanged.connect(self.update_capacity)
        payload_layout.addWidget(self.message_input)
        right_col.addWidget(payload_group)

        # Settings Section
        settings_group = QGroupBox("ENCODING PARAMETERS")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.addWidget(QLabel("Steganography Mode:"))
        self.mode_selector = QComboBox()
        self.mode_selector.addItems([
            "🔹 LSB (Standard)", 
            "🔍 Alpha Channel (PNG)", 
            "📐 Edge Detection",
            "📡 DCT (Frequency)"
        ])
        self.mode_selector.currentIndexChanged.connect(self.update_capacity)
        settings_layout.addWidget(self.mode_selector)
        right_col.addWidget(settings_group)
        
        grid_layout.addLayout(right_col, 2)
        main_layout.addLayout(grid_layout)

        # --- Bottom Section: Actions ---
        action_group = QGroupBox("ACTIONS")
        action_layout = QHBoxLayout(action_group)
        
        self.hide_btn = QPushButton("🔒 Hide Message & Generate")
        self.hide_btn.setObjectName("primaryBtn")
        self.hide_btn.clicked.connect(self.process_hide)
        
        self.extract_btn = QPushButton("🔍 Auto-Scan & Extract")
        self.extract_btn.setObjectName("secondaryBtn")
        self.extract_btn.clicked.connect(self.process_extract)
        
        self.folder_btn = QPushButton("📁 Open Output Folder")
        self.folder_btn.clicked.connect(self.open_output_folder)
        
        action_layout.addWidget(self.hide_btn)
        action_layout.addWidget(self.extract_btn)
        action_layout.addWidget(self.folder_btn)
        main_layout.addWidget(action_group)
        
        # Progress Bar & Logs
        self.progress_bar = QProgressBar()
        self.progress_bar.setFormat("Processing... %p%")
        main_layout.addWidget(self.progress_bar)
        
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("Operation logs will appear here...")
        self.result_output.setMaximumHeight(100)
        main_layout.addWidget(self.result_output)

    def load_example_list(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        example_dir = os.path.join(base_dir, "photoexample")
        if os.path.exists(example_dir):
            images = [f for f in os.listdir(example_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
            self.example_selector.addItems(images)

    def load_image(self, path):
        if not os.path.exists(path): return
        logger.log("info", f"ImageTab: โหลดภาพจาก {path}")
        self.selected_image = path
        pixmap = QPixmap(path).scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_preview.setPixmap(pixmap)
        self.image_preview.setStyleSheet("border: 1px solid #00d4ff; border-radius: 10px;")
        self.update_capacity()

    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์ภาพ", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if path: self.load_image(path)

    def load_example_image(self):
        name = self.example_selector.currentText()
        if not name: return
        base_dir = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(base_dir, "photoexample", name)
        if os.path.exists(path):
            self.load_image(path)

    def update_capacity(self):
        if not self.selected_image: return
        
        mode = self.mode_selector.currentIndex()
        if mode == 0: self.capacity = get_image_capacity_lsb(self.selected_image)
        elif mode == 1: self.capacity = get_image_capacity_alpha(self.selected_image)
        elif mode == 2: self.capacity = get_image_capacity_edge(self.selected_image)
        
        msg_len = len(self.message_input.toPlainText().encode('utf-8')) * 8
        self.capacity_label.setText(f"📊 ความจุ: {self.capacity:,} บิต | ใช้ไป: {msg_len:,} บิต")
        
        if msg_len > self.capacity:
            self.capacity_label.setStyleSheet("color: #ff4444; font-weight: bold;")
        else:
            self.capacity_label.setStyleSheet("color: #00ff88;")

    def process_hide(self):
        if not self.selected_image: return
        msg = self.message_input.toPlainText()
        if not msg: return
        
        mode = self.mode_selector.currentIndex()
        mode_name = self.mode_selector.currentText()
        logger.log("info", f"ImageTab: เริ่มกระบวนการซ่อนข้อความ (โหมด: {mode_name})")
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "photoexample", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = ".png" # บันทึกเป็น PNG เสมอเพื่อความปลอดภัยของข้อมูล
        output_path = os.path.join(output_dir, f"hidden_{timestamp}{ext}")
        
        try:
            self.progress_bar.setValue(30)
            if mode == 0: hide_lsb_image(self.selected_image, msg, output_path)
            elif mode == 1: hide_alpha_channel(self.selected_image, msg, output_path)
            elif mode == 2: hide_edge_detection(self.selected_image, msg, output_path)
            elif mode == 3: hide_dct_image(self.selected_image, msg, output_path)
            
            self.progress_bar.setValue(100)
            self.result_output.setPlainText(f"✅ ซ่อนข้อมูลสำเร็จ!\nบันทึกที่: {output_path}")
        except Exception as e:
            self.result_output.setPlainText(f"❌ เกิดข้อผิดพลาด: {str(e)}")
            self.progress_bar.setValue(0)

    def process_extract(self):
        if not self.selected_image: return
        logger.log("info", "ImageTab: เริ่มกระบวนการถอดข้อความ (ลองทุกโหมด)")
        
        self.result_output.setPlainText("🔍 กำลังตรวจสอบทุกโหมดการซ่อน...")
        self.progress_bar.setValue(10)
        
        results = []
        try:
            # 1. LSB
            self.progress_bar.setValue(30)
            res_lsb = extract_lsb_image(self.selected_image)
            if res_lsb and res_lsb != "ไม่พบข้อมูลที่ซ่อนอยู่":
                results.append(f"🔹 [LSB]: {res_lsb}")

            # 2. Alpha
            self.progress_bar.setValue(60)
            res_alpha = extract_alpha_channel(self.selected_image)
            if res_alpha and res_alpha not in ["ไม่พบข้อมูลที่ซ่อนอยู่", "ไม่พบช่อง Alpha ในภาพนี้"]:
                results.append(f"🔍 [Alpha]: {res_alpha}")

            # 3. Edge
            self.progress_bar.setValue(80)
            res_edge = extract_edge_detection(self.selected_image)
            if res_edge and res_edge != "ไม่พบข้อมูลที่ซ่อนอยู่":
                results.append(f"📐 [Edge]: {res_edge}")
            
            # 4. DCT
            self.progress_bar.setValue(95)
            res_dct = extract_dct_image(self.selected_image)
            if res_dct and res_dct != "ไม่พบข้อมูลที่ซ่อนอยู่":
                results.append(f"📡 [DCT]: {res_dct}")
            
            self.progress_bar.setValue(100)
            
            if not results:
                self.result_output.setPlainText("❌ ไม่พบข้อมูลที่ซ่อนอยู่ด้วยวิธีใดเลย\n(ตรวจสอบว่าเลือกโหมดการซ่อนถูกตอนบันทึกหรือไม่)")
            else:
                final_text = "🔓 พบข้อมูลที่ซ่อนอยู่:\n" + "="*30 + "\n"
                final_text += "\n\n".join(results)
                self.result_output.setPlainText(final_text)
                
        except Exception as e:
            self.result_output.setPlainText(f"❌ เกิดข้อผิดพลาด: {str(e)}")
            self.progress_bar.setValue(0)

    def open_output_folder(self):
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "photoexample", "output")
        os.makedirs(output_path, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                self.load_image(path)
