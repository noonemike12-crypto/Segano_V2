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

class ImageTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_image = None
        self.capacity = 0
        self.init_ui()
        self.setAcceptDrops(True)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- ส่วนเลือกภาพและตั้งค่า ---
        config_group = QGroupBox("🖼️ การเลือกภาพและตั้งค่า (Image Selection & Config)")
        config_layout = QGridLayout()
        
        config_layout.addWidget(QLabel("📁 เลือกภาพตัวอย่าง:"), 0, 0)
        self.example_selector = QComboBox()
        self.example_selector.addItems([f"ตัวอย่าง {i+1}" for i in range(10)])
        self.example_selector.currentIndexChanged.connect(self.load_example_image)
        config_layout.addWidget(self.example_selector, 0, 1)
        
        self.browse_btn = QPushButton("🔍 เลือกไฟล์ภาพ...")
        self.browse_btn.clicked.connect(self.browse_image)
        config_layout.addWidget(self.browse_btn, 0, 2)
        
        config_layout.addWidget(QLabel("⚙️ โหมดการซ่อน:"), 1, 0)
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["🔹 LSB (มาตรฐาน)", "🔍 Alpha Channel (PNG)", "📐 Edge Detection (ขอบภาพ)"])
        self.mode_selector.currentIndexChanged.connect(self.update_capacity)
        config_layout.addWidget(self.mode_selector, 1, 1, 1, 2)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        # --- ส่วนแสดงผลและข้อความ ---
        content_layout = QHBoxLayout()
        
        # ฝั่งซ้าย: พรีวิวภาพ
        preview_frame = QFrame()
        preview_frame.setFrameShape(QFrame.StyledPanel)
        preview_layout = QVBoxLayout(preview_frame)
        
        preview_layout.addWidget(QLabel("🖼️ ตัวอย่างภาพ:"))
        self.image_preview = QLabel("ลากภาพมาวางที่นี่\nหรือกดปุ่มเลือกไฟล์")
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setFixedSize(400, 300)
        self.image_preview.setStyleSheet("border: 2px dashed #4a5568; border-radius: 10px; color: #718096;")
        preview_layout.addWidget(self.image_preview)
        
        self.capacity_label = QLabel("📊 ความจุ: 0 บิต | ใช้ไป: 0 บิต")
        self.capacity_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.capacity_label)
        
        content_layout.addWidget(preview_frame)
        
        # ฝั่งขวา: ข้อความลับ
        message_frame = QFrame()
        message_layout = QVBoxLayout(message_frame)
        
        message_layout.addWidget(QLabel("✏️ ข้อความลับ:"))
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("พิมพ์ข้อความที่ต้องการซ่อนที่นี่...")
        self.message_input.textChanged.connect(self.update_capacity)
        message_layout.addWidget(self.message_input)
        
        message_layout.addWidget(QLabel("📤 ผลลัพธ์:"))
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("ผลลัพธ์การถอดรหัสจะแสดงที่นี่...")
        message_layout.addWidget(self.result_output)
        
        content_layout.addWidget(message_frame)
        layout.addLayout(content_layout)

        # --- ส่วนปุ่มดำเนินการ ---
        action_layout = QHBoxLayout()
        
        self.hide_btn = QPushButton("🔒 ซ่อนข้อความ (Hide)")
        self.hide_btn.setObjectName("primaryBtn")
        self.hide_btn.clicked.connect(self.process_hide)
        
        self.extract_btn = QPushButton("🔓 ถอดข้อความ (Extract)")
        self.extract_btn.setObjectName("secondaryBtn")
        self.extract_btn.clicked.connect(self.process_extract)
        
        self.folder_btn = QPushButton("📁 เปิดโฟลเดอร์ผลลัพธ์")
        self.folder_btn.clicked.connect(self.open_output_folder)
        
        action_layout.addWidget(self.hide_btn)
        action_layout.addWidget(self.extract_btn)
        action_layout.addWidget(self.folder_btn)
        
        layout.addLayout(action_layout)
        
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

    def load_image(self, path):
        if not os.path.exists(path): return
        self.selected_image = path
        pixmap = QPixmap(path).scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_preview.setPixmap(pixmap)
        self.image_preview.setStyleSheet("border: 1px solid #00d4ff; border-radius: 10px;")
        self.update_capacity()

    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์ภาพ", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if path: self.load_image(path)

    def load_example_image(self):
        idx = self.example_selector.currentIndex()
        base_dir = os.path.dirname(os.path.dirname(__file__))
        example_dir = os.path.join(base_dir, "photoexample")
        if not os.path.exists(example_dir): return
        
        images = sorted([f for f in os.listdir(example_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))])
        if idx < len(images):
            self.load_image(os.path.join(example_dir, images[idx]))

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
            
            self.progress_bar.setValue(100)
            self.result_output.setPlainText(f"✅ ซ่อนข้อมูลสำเร็จ!\nบันทึกที่: {output_path}")
        except Exception as e:
            self.result_output.setPlainText(f"❌ เกิดข้อผิดพลาด: {str(e)}")
            self.progress_bar.setValue(0)

    def process_extract(self):
        if not self.selected_image: return
        mode = self.mode_selector.currentIndex()
        
        try:
            self.progress_bar.setValue(50)
            res = ""
            if mode == 0: res = extract_lsb_image(self.selected_image)
            elif mode == 1: res = extract_alpha_channel(self.selected_image)
            elif mode == 2: res = extract_edge_detection(self.selected_image)
            
            self.progress_bar.setValue(100)
            self.result_output.setPlainText(f"🔓 ข้อความที่พบ:\n{res}")
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
