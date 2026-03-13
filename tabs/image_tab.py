import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QPushButton, QLabel, QFileDialog, QTextEdit, QProgressBar, QFrame, QComboBox
)
from PyQt5.QtGui import QPixmap, QDesktopServices
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from utils.stegano_engine import SteganoEngine
from utils.logger import logger
from utils.path_manager import PathManager

class WorkerThread(QThread):
    finished = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        try:
            self.progress.emit(30)
            result = self.func(*self.args)
            self.progress.emit(100)
            self.finished.emit(f"✅ สำเร็จ: {result}")
        except Exception as e:
            self.finished.emit(f"❌ ข้อผิดพลาด: {str(e)}")

class ImageTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_file = None
        self.output_file = None
        self.setAcceptDrops(True)
        self.init_ui()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(urls[0].toLocalFile().lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.bmp']):
                event.accept()
                return
        event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.selected_file = files[0]
            self.preview_label.setPixmap(QPixmap(self.selected_file).scaled(450, 350, Qt.KeepAspectRatio))
            self.update_capacity_info()
            logger.info(f"Dropped image: {self.selected_file}")

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Left Side
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        
        file_group = QGroupBox("📁 เลือกรูปภาพ")
        file_vbox = QVBoxLayout()
        self.preview_label = QLabel("ลากรูปภาพมาวางที่นี่")
        self.preview_label.setFixedSize(450, 350)
        self.preview_label.setStyleSheet("background-color: #0f0f1a; border: 2px dashed #2d2d44; border-radius: 20px; color: #555;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.browse_btn = QPushButton("🔍 เลือกไฟล์")
        self.browse_btn.clicked.connect(self.browse_image)
        file_vbox.addWidget(self.preview_label)
        file_vbox.addWidget(self.browse_btn)
        file_group.setLayout(file_vbox)
        left_layout.addWidget(file_group)
        
        # Method Selection
        method_group = QGroupBox("🛠️ เลือกเทคนิคการซ่อน")
        method_layout = QVBoxLayout()
        self.method_combo = QComboBox()
        # All methods are somewhat applicable to images or handled by engine
        self.method_combo.addItems(SteganoEngine.METHODS)
        self.method_combo.currentIndexChanged.connect(self.update_capacity_info)
        method_layout.addWidget(self.method_combo)
        method_group.setLayout(method_layout)
        left_layout.addWidget(method_group)

        self.cap_group = QGroupBox("📊 ข้อมูลความจุ")
        cap_layout = QVBoxLayout()
        self.cap_label = QLabel("กรุณาเลือกรูปภาพ...")
        cap_layout.addWidget(self.cap_label)
        self.cap_group.setLayout(cap_layout)
        left_layout.addWidget(self.cap_group)
        left_layout.addStretch()

        # Right Side
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        msg_group = QGroupBox("📝 ข้อความ (รองรับภาษาไทย)")
        msg_vbox = QVBoxLayout()
        self.msg_input = QTextEdit()
        self.msg_input.textChanged.connect(self.check_input_limit)
        self.limit_label = QLabel("ใช้ไป: 0 bits")
        btn_layout = QHBoxLayout()
        self.hide_btn = QPushButton("🔒 ซ่อนข้อความ")
        self.hide_btn.setObjectName("primaryBtn")
        self.hide_btn.clicked.connect(self.process_hide)
        self.extract_btn = QPushButton("🔓 ถอดข้อความ")
        self.extract_btn.setObjectName("secondaryBtn")
        self.extract_btn.clicked.connect(self.process_extract)
        btn_layout.addWidget(self.hide_btn)
        btn_layout.addWidget(self.extract_btn)
        self.open_folder_btn = QPushButton("📂 เปิดโฟลเดอร์ผลลัพธ์")
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        self.progress_bar = QProgressBar()
        msg_vbox.addWidget(self.msg_input)
        msg_vbox.addWidget(self.limit_label)
        msg_vbox.addLayout(btn_layout)
        msg_vbox.addWidget(self.open_folder_btn)
        msg_vbox.addWidget(self.progress_bar)
        msg_group.setLayout(msg_vbox)
        
        log_group = QGroupBox("📊 บันทึกการทำงาน")
        log_vbox = QVBoxLayout()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        log_vbox.addWidget(self.log_output)
        log_group.setLayout(log_vbox)
        right_layout.addWidget(msg_group)
        right_layout.addWidget(log_group)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)

    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "เลือกรูปภาพ", "", "Images (*.png *.jpg *.bmp)")
        if path:
            self.selected_file = path
            self.preview_label.setPixmap(QPixmap(path).scaled(450, 350, Qt.KeepAspectRatio))
            self.update_capacity_info()

    def update_capacity_info(self):
        if not self.selected_file: return
        method = self.method_combo.currentText()
        cap = SteganoEngine.get_image_capacity(self.selected_file, method)
        if cap:
            self.current_cap = cap
            info = (f"🔹 เทคนิค: {method}\n"
                    f"🔤 อังกฤษ: {cap['eng_capacity']:,} ตัว\n"
                    f"🇹🇭 ไทย: {cap['thai_capacity']:,} ตัว")
            self.cap_label.setText(info)
            self.check_input_limit()

    def check_input_limit(self):
        if not self.selected_file or not hasattr(self, 'current_cap'): return
        text = self.msg_input.toPlainText()
        used_bits = len(text.encode('utf-8')) * 8
        total_bits = self.current_cap['total_bits']
        percent = (used_bits / total_bits) * 100 if total_bits > 0 else 0
        self.limit_label.setText(f"ใช้ไป: {used_bits:,} / {total_bits:,} bits ({percent:.1f}%)")
        self.hide_btn.setEnabled(used_bits <= total_bits)

    def process_hide(self):
        if not self.selected_file: return
        method = self.method_combo.currentText()
        filename = f"stego_{method.split(' ')[0].lower()}_{os.path.basename(self.selected_file)}"
        if not filename.lower().endswith(".png"): filename = os.path.splitext(filename)[0] + ".png"
        self.output_file = PathManager.get_output_path("image", filename)
        
        func = None
        if "LSB" in method: func = SteganoEngine.hide_image_lsb
        elif "EOF" in method: func = SteganoEngine.hide_eof
        elif "Metadata" in method: func = SteganoEngine.hide_metadata
        elif "Alpha" in method: func = SteganoEngine.hide_alpha
        elif "Edge" in method: func = SteganoEngine.hide_edge
        elif "Masking" in method: func = SteganoEngine.hide_masking
        elif "Palette" in method: func = SteganoEngine.hide_palette
        
        self.run_worker(func, self.selected_file, self.msg_input.toPlainText().encode('utf-8'), self.output_file)

    def process_extract(self):
        if not self.selected_file: return
        method = self.method_combo.currentText()
        func = None
        if "LSB" in method: func = SteganoEngine.extract_image_lsb
        elif "EOF" in method: func = SteganoEngine.extract_eof
        elif "Metadata" in method: func = SteganoEngine.extract_metadata
        elif "Alpha" in method: func = SteganoEngine.extract_alpha
        elif "Edge" in method: func = SteganoEngine.extract_edge
        elif "Masking" in method: func = SteganoEngine.extract_masking
        elif "Palette" in method: func = SteganoEngine.extract_palette
        self.run_worker(func, self.selected_file)

    def run_worker(self, func, *args):
        self.worker = WorkerThread(func, *args)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, msg):
        self.log_output.append(msg)
        if "สำเร็จ" in msg:
            self.open_folder_btn.setEnabled(True)
            # If it was an extraction, the result might be bytes
            if "extract" in self.worker.func.__name__.lower():
                try:
                    # The msg is "✅ สำเร็จ: <result>"
                    result_part = msg.split("สำเร็จ: ")[1]
                    # If it's a string representation of bytes, we might need to handle it
                    # But WorkerThread returns result as string in finished.emit(f"✅ สำเร็จ: {result}")
                    # So we should probably change WorkerThread to emit the raw result or handle it here
                    pass 
                except:
                    pass

    def open_output_folder(self):
        path = PathManager.get_category_dir("image")
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))
