import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QLabel, QFrame, QHBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from utils.styles import get_main_style
import tabs.image_tab as image_tab
import tabs.audio_tab as audio_tab
import tabs.video_tab as video_tab
import tabs.encryption_tab as encryption_tab
import tabs.pgp_tab as pgp_tab
import tabs.integrated_mode_tab as integrated_mode_tab

class SIENGApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIENG : Secure Incognito ENcryption Guard")
        self.setMinimumSize(1200, 850)
        self.setStyleSheet(get_main_style())
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Header
        header = QFrame()
        header.setObjectName("headerFrame")
        header.setFixedHeight(80)
        h_layout = QHBoxLayout(header)
        title = QLabel("🔒 SIENG SUITE")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00d4ff;")
        subtitle = QLabel("Advanced Steganography & Encryption")
        subtitle.setStyleSheet("color: #888; font-style: italic;")
        h_layout.addWidget(title)
        h_layout.addStretch()
        h_layout.addWidget(subtitle)
        main_layout.addWidget(header)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(image_tab.ImageTab(), "🖼️ Image")
        self.tabs.addTab(audio_tab.AudioTab(), "🎵 Audio")
        self.tabs.addTab(video_tab.VideoTab(), "🎬 Video")
        self.tabs.addTab(encryption_tab.EncryptionTab(), "🔐 Encryption")
        self.tabs.addTab(pgp_tab.PGPTab(), "🔑 PGP")
        self.tabs.addTab(integrated_mode_tab.IntegrationTab(), "🔗 Integrated")
        
        main_layout.addWidget(self.tabs)

        # Footer
        footer = QLabel("Ready | v2.0.1 Refactored")
        footer.setStyleSheet("color: #555; font-size: 10px;")
        main_layout.addWidget(footer, alignment=Qt.AlignRight)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SIENGApp()
    window.show()
    sys.exit(app.exec_())
