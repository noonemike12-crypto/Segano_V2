import os
import mimetypes
import json
import subprocess
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QGroupBox, QHBoxLayout, QTextEdit, QComboBox, QMessageBox, QFileDialog,
    QListWidget, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt

class FileInfoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        group = QGroupBox("📋 Metadata Management")
        vbox = QVBoxLayout()
        self.info = QTextEdit()
        self.info.setReadOnly(True)
        self.btn = QPushButton("Select File for Metadata")
        self.btn.clicked.connect(self.select_file)
        vbox.addWidget(self.btn)
        vbox.addWidget(self.info)
        group.setLayout(vbox)
        layout.addWidget(group)

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if path:
            self.info.setPlainText(f"File: {path}\nSize: {os.path.getsize(path)} bytes")
