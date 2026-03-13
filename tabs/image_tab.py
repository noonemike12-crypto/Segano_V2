import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QPushButton, QLabel, QFileDialog, QTextEdit, QProgressBar
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from utils.stegano_engine import SteganoEngine
from utils.styles import get_main_style

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
            self.finished.emit(f"Success: {result}")
        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")

class ImageTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_file = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # File Selection
        file_group = QGroupBox("🖼️ Image Source")
        file_layout = QHBoxLayout()
        self.preview_label = QLabel("No Image Selected")
        self.preview_label.setFixedSize(300, 200)
        self.preview_label.setStyleSheet("border: 2px dashed #444; border-radius: 10px;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        
        btn_vbox = QVBoxLayout()
        self.browse_btn = QPushButton("🔍 Browse Image")
        self.browse_btn.clicked.connect(self.browse_image)
        btn_vbox.addWidget(self.browse_btn)
        btn_vbox.addStretch()
        
        file_layout.addWidget(self.preview_label)
        file_layout.addLayout(btn_vbox)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Message Input
        msg_group = QGroupBox("📝 Secret Message")
        msg_layout = QVBoxLayout()
        self.msg_input = QTextEdit()
        msg_layout.addWidget(self.msg_input)
        msg_group.setLayout(msg_layout)
        layout.addWidget(msg_group)

        # Actions
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        action_layout = QHBoxLayout()
        self.hide_btn = QPushButton("🔒 Hide Message")
        self.hide_btn.setObjectName("actionPrimary")
        self.hide_btn.clicked.connect(self.process_hide)
        
        self.extract_btn = QPushButton("🔓 Extract Message")
        self.extract_btn.setObjectName("actionSecondary")
        self.extract_btn.clicked.connect(self.process_extract)
        
        action_layout.addWidget(self.hide_btn)
        action_layout.addWidget(self.extract_btn)
        layout.addLayout(action_layout)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(100)
        layout.addWidget(self.log_output)

    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.bmp)")
        if path:
            self.selected_file = path
            self.preview_label.setPixmap(QPixmap(path).scaled(300, 200, Qt.KeepAspectRatio))
            self.log_output.append(f"Loaded: {os.path.basename(path)}")

    def process_hide(self):
        if not self.selected_file or not self.msg_input.toPlainText(): return
        out_path = os.path.join(os.path.dirname(self.selected_file), "output_stego.png")
        self.run_worker(SteganoEngine.hide_lsb, self.selected_file, self.msg_input.toPlainText(), out_path)

    def process_extract(self):
        if not self.selected_file: return
        self.run_worker(SteganoEngine.extract_lsb, self.selected_file)

    def run_worker(self, func, *args):
        self.worker = WorkerThread(func, *args)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, msg):
        self.log_output.append(msg)
        if "Success" in msg and "Extract" in self.sender().func.__name__:
            self.msg_input.setPlainText(msg.split(": ")[1])
