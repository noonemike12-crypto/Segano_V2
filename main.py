import sys
import os
import psutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QFrame, QPushButton, QSystemTrayIcon, 
    QMenu, QMessageBox, QSplashScreen
)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPainter
from PyQt5.QtCore import Qt, QTimer

from utils.styles import get_modern_style
from utils.logger import logger

import tabs.image_tab as image_tab
import tabs.audio_tab as audio_tab
import tabs.video_tab as video_tab
import tabs.file_info_tab as info_tab
import tabs.file_and_FILE as file_and_FILE
import tabs.encryption_tab as encryption_tab
import tabs.pgp_tab as pgp_tab
import tabs.integrated_mode_tab as integrated_mode_tab

class SIENGApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIENG PRO : Secure Incognito ENcryption Guard")
        self.setMinimumSize(1200, 850)
        self.setStyleSheet(get_modern_style())
        self.init_ui()
        
        # Timer สำหรับอัปเดตสถานะหน่วยความจำ
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(2000)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- ส่วนหัว (Header) ---
        header = QFrame()
        header.setObjectName("headerFrame")
        header.setFixedHeight(100)
        header.setStyleSheet("background-color: #0f172a; border-bottom: 2px solid #1e293b;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        title_vbox = QVBoxLayout()
        title = QLabel("SIENG PRO")
        title.setObjectName("headerTitle")
        subtitle = QLabel("ระบบซ่อนข้อมูลและเข้ารหัสลับขั้นสูง (Advanced Steganography & Encryption)")
        subtitle.setStyleSheet("color: #94a3b8; font-size: 10pt;")
        title_vbox.addWidget(title)
        title_vbox.addWidget(subtitle)
        header_layout.addLayout(title_vbox)
        
        header_layout.addStretch()
        
        # ปุ่มช่วยเหลือและตั้งค่า
        self.help_btn = QPushButton("❓ ช่วยเหลือ")
        self.help_btn.clicked.connect(self.show_help)
        header_layout.addWidget(self.help_btn)
        
        main_layout.addWidget(header)

        # --- ส่วนเนื้อหา (Tabs) ---
        content_area = QFrame()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(15, 15, 15, 15)
        
        self.tabs = QTabWidget()
        self.tabs.addTab(image_tab.ImageTab(), "🖼️ รูปภาพ")
        self.tabs.addTab(audio_tab.AudioTab(), "🎵 เสียง")
        self.tabs.addTab(video_tab.VideoTab(), "🎬 วิดีโอ")
        self.tabs.addTab(info_tab.FileInfoTab(), "🏷️ Metadata")
        self.tabs.addTab(file_and_FILE.FileAndFileTab(), "📁 ซ่อนไฟล์")
        self.tabs.addTab(encryption_tab.EncryptionTab(), "🔐 เข้ารหัส")
        self.tabs.addTab(pgp_tab.PGPTab(), "🔑 PGP")
        self.tabs.addTab(integrated_mode_tab.IntegrationTab(), "🔗 โหมดรวม")
        
        content_layout.addWidget(self.tabs)
        main_layout.addWidget(content_area)

        # --- ส่วนท้าย (Status Bar) ---
        footer = QFrame()
        footer.setFixedHeight(40)
        footer.setStyleSheet("background-color: #0f172a; border-top: 1px solid #1e293b;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 0, 20, 0)
        
        self.status_label = QLabel("🟢 พร้อมใช้งาน (Ready)")
        self.status_label.setObjectName("statusReady")
        footer_layout.addWidget(self.status_label)
        
        footer_layout.addStretch()
        
        self.mem_label = QLabel("💾 หน่วยความจำ: 0 MB")
        footer_layout.addWidget(self.mem_label)
        
        version = QLabel("v2.5.0 Professional Edition")
        version.setStyleSheet("color: #64748b; font-size: 9pt;")
        footer_layout.addWidget(version)
        
        main_layout.addWidget(footer)

    def update_status(self):
        process = psutil.Process(os.getpid())
        mem = process.memory_info().rss / (1024 * 1024)
        self.mem_label.setText(f"💾 หน่วยความจำ: {mem:.1f} MB")

    def show_help(self):
        msg = QMessageBox()
        msg.setWindowTitle("ช่วยเหลือ - SIENG PRO")
        msg.setText("<b>SIENG PRO (Secure Incognito ENcryption Guard)</b><br><br>"
                   "โปรแกรมนี้ถูกออกแบบมาเพื่อความปลอดภัยของข้อมูลขั้นสูง:<br>"
                   "- ซ่อนข้อความในไฟล์สื่อต่างๆ (Steganography)<br>"
                   "- เข้ารหัสข้อมูลด้วยมาตรฐานสากล (AES, RSA, PGP)<br>"
                   "- จัดการ Metadata และไฟล์ซ้อนไฟล์<br><br>"
                   "เลือกแท็บด้านบนเพื่อเริ่มใช้งานในแต่ละโหมด")
        msg.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # แสดงหน้าจอโหลด (Splash Screen)
    splash_pix = QPixmap(600, 300)
    splash_pix.fill(Qt.transparent)
    painter = QPainter(splash_pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(Qt.black)
    painter.drawRoundedRect(0, 0, 600, 300, 20, 20)
    painter.setPen(Qt.white)
    painter.setFont(QFont("Arial", 30, QFont.Bold))
    painter.drawText(splash_pix.rect(), Qt.AlignCenter, "SIENG PRO\nLoading...")
    painter.end()
    
    splash = QSplashScreen(splash_pix)
    splash.show()
    
    # จำลองการโหลด
    QTimer.singleShot(2000, splash.close)
    
    window = SIENGApp()
    QTimer.singleShot(2000, window.show)
    
    sys.exit(app.exec_())
