import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QLabel, QFrame, QHBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from utils.styles import get_modern_style
from utils.logger import logger
import tabs.image_tab as image_tab
import tabs.audio_tab as audio_tab
import tabs.video_tab as video_tab
import tabs.encryption_tab as encryption_tab
import tabs.pgp_tab as pgp_tab
import tabs.integrated_mode_tab as integrated_mode_tab
import tabs.debug_tab as debug_tab

class SIENGApp(QWidget):
    def __init__(self):
        super().__init__()
        logger.log("info", "Initializing SIENG PRO Application...")
        self.setWindowTitle("SIENG : Secure Incognito ENcryption Guard")
        self.setMinimumSize(1280, 850)
        self.setStyleSheet(get_modern_style())
        self.init_ui()
        logger.log("info", "Application UI initialized successfully.")

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Modern Header ---
        header = QFrame()
        header.setObjectName("headerFrame")
        header.setFixedHeight(100)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(30, 0, 30, 0)

        title_vbox = QVBoxLayout()
        title = QLabel("SIENG PRO")
        title.setStyleSheet("font-size: 28px; font-weight: 800; color: #00d4ff; letter-spacing: 2px;")
        subtitle = QLabel("SECURE INCOGNITO ENCRYPTION GUARD")
        subtitle.setStyleSheet("color: #666; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
        title_vbox.addWidget(title)
        title_vbox.addWidget(subtitle)
        title_vbox.setSpacing(0)
        
        h_layout.addLayout(title_vbox)
        h_layout.addStretch()
        
        status_badge = QLabel("🛡️ SYSTEM SECURE")
        status_badge.setStyleSheet("""
            background-color: rgba(0, 255, 136, 0.1);
            color: #00ff88;
            padding: 5px 15px;
            border-radius: 12px;
            border: 1px solid rgba(0, 255, 136, 0.3);
            font-size: 11px;
            font-weight: bold;
        """)
        h_layout.addWidget(status_badge)
        
        main_layout.addWidget(header)

        # --- Content Area ---
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 10, 20, 20)

        self.tabs = QTabWidget()
        self.tabs.addTab(image_tab.ImageTab(), "🖼️ IMAGE")
        self.tabs.addTab(audio_tab.AudioTab(), "🎵 AUDIO")
        self.tabs.addTab(video_tab.VideoTab(), "🎬 VIDEO")
        self.tabs.addTab(encryption_tab.EncryptionTab(), "🔐 CRYPTO")
        self.tabs.addTab(pgp_tab.PGPTab(), "🔑 PGP")
        self.tabs.addTab(integrated_mode_tab.IntegrationTab(), "🔗 INTEGRATED")
        self.tabs.addTab(debug_tab.DebugTab(), "🛠️ DEBUG")
        
        content_layout.addWidget(self.tabs)
        main_layout.addWidget(content_frame)

        # --- Footer ---
        footer = QFrame()
        footer.setFixedHeight(30)
        footer.setStyleSheet("background-color: #0f0f1a; border-top: 1px solid #2d2d44;")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(20, 0, 20, 0)
        
        version = QLabel("v2.5.0 Professional Edition")
        version.setStyleSheet("color: #444; font-size: 10px;")
        f_layout.addWidget(version)
        f_layout.addStretch()
        
        main_layout.addWidget(footer)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SIENGApp()
    window.show()
    sys.exit(app.exec_())
