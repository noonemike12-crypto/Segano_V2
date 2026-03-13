import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QPushButton, QLabel, QFileDialog, QTextEdit, QProgressBar, QFrame, QSplitter
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from utils.stegano_engine import SteganoEngine

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
            self.finished.emit(f"✅ {result}")
        except Exception as e:
            self.finished.emit(f"❌ Error: {str(e)}")

class ImageTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_file = None
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Left Side: Preview & File Selection
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        
        file_group = QGroupBox("📁 Source Image")
        file_vbox = QVBoxLayout()
        
        self.preview_label = QLabel("Drop image here or click browse")
        self.preview_label.setFixedSize(450, 350)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #0f0f1a;
                border: 2px dashed #2d2d44;
                border-radius: 20px;
                color: #555;
                font-size: 16px;
            }
        """)
        self.preview_label.setAlignment(Qt.AlignCenter)
        
        self.browse_btn = QPushButton("🔍 Browse Files")
        self.browse_btn.setCursor(Qt.PointingHandCursor)
        self.browse_btn.clicked.connect(self.browse_image)
        
        file_vbox.addWidget(self.preview_label)
        file_vbox.addWidget(self.browse_btn)
        file_group.setLayout(file_vbox)
        left_layout.addWidget(file_group)
        left_layout.addStretch()

        # Right Side: Controls & Logs
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)

        msg_group = QGroupBox("📝 Steganography Controls")
        msg_vbox = QVBoxLayout()
        
        msg_vbox.addWidget(QLabel("Secret Message:"))
        self.msg_input = QTextEdit()
        self.msg_input.setPlaceholderText("Type your hidden message here...")
        self.msg_input.setMinimumHeight(150)
        
        btn_layout = QHBoxLayout()
        self.hide_btn = QPushButton("🔒 Hide Message")
        self.hide_btn.setObjectName("primaryBtn")
        self.hide_btn.clicked.connect(self.process_hide)
        
        self.extract_btn = QPushButton("🔓 Extract Message")
        self.extract_btn.setObjectName("secondaryBtn")
        self.extract_btn.clicked.connect(self.process_extract)
        
        btn_layout.addWidget(self.hide_btn)
        btn_layout.addWidget(self.extract_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        
        msg_vbox.addWidget(self.msg_input)
        msg_vbox.addLayout(btn_layout)
        msg_vbox.addWidget(self.progress_bar)
        msg_group.setLayout(msg_vbox)
        
        log_group = QGroupBox("📊 Activity Log")
        log_vbox = QVBoxLayout()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #0a0a12; border: none; color: #00ff88;")
        log_vbox.addWidget(self.log_output)
        log_group.setLayout(log_vbox)

        right_layout.addWidget(msg_group)
        right_layout.addWidget(log_group)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)

    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.bmp)")
        if path:
            self.selected_file = path
            pixmap = QPixmap(path).scaled(450, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(pixmap)
            self.preview_label.setStyleSheet("border: 1px solid #00d4ff; border-radius: 20px;")
            self.log_output.append(f"📂 Loaded: {os.path.basename(path)}")

    def process_hide(self):
        if not self.selected_file:
            self.log_output.append("⚠️ Please select an image first.")
            return
        if not self.msg_input.toPlainText():
            self.log_output.append("⚠️ Please enter a message to hide.")
            return
            
        out_path = os.path.join(os.path.dirname(self.selected_file), "stego_result.png")
        self.run_worker(SteganoEngine.hide_lsb, self.selected_file, self.msg_input.toPlainText(), out_path)

    def process_extract(self):
        if not self.selected_file:
            self.log_output.append("⚠️ Please select an image first.")
            return
        self.run_worker(SteganoEngine.extract_lsb, self.selected_file)

    def run_worker(self, func, *args):
        self.worker = WorkerThread(func, *args)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, msg):
        self.log_output.append(msg)
        if "Success" in msg and "extract" in self.sender().func.__name__.lower():
            extracted_text = msg.split(": ")[1]
            self.msg_input.setPlainText(extracted_text)
            self.log_output.append("✨ Message extracted to input field.")
