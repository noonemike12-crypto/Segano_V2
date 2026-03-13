import os
import struct
import shutil
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGroupBox, QPushButton, QFileDialog,
    QTextEdit, QScrollArea, QGridLayout, QMessageBox, QHBoxLayout, QFrame
)

class FileAndFileTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        group = QGroupBox("📁 File-to-File")
        vbox = QVBoxLayout()
        self.btn = QPushButton("Append File to Image")
        vbox.addWidget(self.btn)
        group.setLayout(vbox)
        layout.addWidget(group)
