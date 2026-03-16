import sys
import os
import subprocess

# --- Automatic Setup Section ---
def auto_setup():
    """สร้างโฟลเดอร์ที่จำเป็นโดยอัตโนมัติและตรวจสอบการติดตั้งไลบรารี"""
    directories = [
        "assets", "logs", "audioexample", "audioexample/output",
        "vdio", "vdio/output", "photoexample", "photoexample/output",
        "output_files"
    ]
    for d in directories:
        if not os.path.exists(d):
            try:
                os.makedirs(d)
                print(f"Created directory: {d}")
            except Exception as e:
                print(f"Error creating directory {d}: {e}")

    # --- ส่วนตรวจสอบและติดตั้งไลบรารีอัตโนมัติ ---
    if os.path.exists("requirements.txt"):
        print("📦 กำลังตรวจสอบและติดตั้งไลบรารีจาก requirements.txt...")
        try:
            # รัน pip install -r requirements.txt
            # -q: quiet mode, --disable-pip-version-check: ลดความล่าช้า
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--disable-pip-version-check", "-r", "requirements.txt"])
            print("✅ ตรวจสอบไลบรารีเสร็จสิ้น")
        except Exception as e:
            print(f"⚠️ คำเตือน: ไม่สามารถติดตั้งไลบรารีอัตโนมัติได้: {e}")
            print("กรุณาตรวจสอบการเชื่อมต่ออินเทอร์เน็ตหรือรัน 'pip install -r requirements.txt' ด้วยตนเอง")

    # ตรวจสอบไลบรารีที่จำเป็น (สำหรับแสดงผลใน GUI)
    missing = []
    try: import PyQt5
    except ImportError: missing.append("PyQt5")
    try: import cv2
    except ImportError: missing.append("opencv-python")
    try: import Crypto
    except ImportError: missing.append("pycryptodome")
    try: import gnupg
    except ImportError: missing.append("python-gnupg")
    try: import PIL
    except ImportError: missing.append("Pillow")
    try: import pydub
    except ImportError: missing.append("pydub")
    try: import soundfile
    except ImportError: missing.append("soundfile")
    try: import sounddevice
    except ImportError: missing.append("sounddevice")
    
    # ตรวจสอบ ffmpeg (System dependency)
    ffmpeg_missing = False
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        ffmpeg_missing = True
    
    if missing or ffmpeg_missing:
        error_msg = ""
        if missing:
            error_msg += f"ไม่พบไลบรารี: {', '.join(missing)}\n"
        if ffmpeg_missing:
            error_msg += "ไม่พบโปรแกรม 'ffmpeg' ในระบบ (จำเป็นสำหรับวิดีโอและเสียง)\n"
        
        print(error_msg)
        return missing, ffmpeg_missing
    return [], False

# รัน setup ก่อนเริ่มแอป
missing_libs, ffmpeg_is_missing = auto_setup()

def run_app(app):
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

    import psutil

    class SIENGApp(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("SIENG PRO : Secure Incognito ENcryption Guard")
            self.setMinimumSize(1200, 850)
            
            # Set Window Icon (Support both .png and .ico)
            assets_dir = os.path.join(os.path.dirname(__file__), "assets")
            icon_path = os.path.join(assets_dir, "myicon.ico")
            logo_path = os.path.join(assets_dir, "logo.png")
            
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            elif os.path.exists(logo_path):
                self.setWindowIcon(QIcon(logo_path))
                
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
            
            # Logo in Header
            logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
            if os.path.exists(logo_path):
                logo_label = QLabel()
                logo_pix = QPixmap(logo_path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(logo_pix)
                header_layout.addWidget(logo_label)
                header_layout.addSpacing(15)
            
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

    # Path to logo/icon
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    logo_path = os.path.join(assets_dir, "logo.png")
    icon_path = os.path.join(assets_dir, "myicon.ico")
    
    # แสดงหน้าจอโหลด (Splash Screen)
    splash_pix = QPixmap(600, 400)
    splash_pix.fill(Qt.transparent)
    painter = QPainter(splash_pix)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Background
    painter.setBrush(Qt.black)
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(0, 0, 600, 400, 30, 30)
    
    display_path = logo_path if os.path.exists(logo_path) else icon_path
    
    if os.path.exists(display_path):
        # Draw Logo/Icon
        logo_img = QPixmap(display_path).scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        x = (600 - logo_img.width()) // 2
        y = (400 - logo_img.height()) // 2 - 20
        painter.drawPixmap(x, y, logo_img)
        
        # Text under logo
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 14))
        painter.drawText(splash_pix.rect().adjusted(0, 0, 0, -30), Qt.AlignBottom | Qt.AlignHCenter, "SECURE INCOGNITO ENCRYPTION GUARD")
    else:
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

if __name__ == "__main__":
    # ตรวจสอบว่ามีไลบรารีพื้นฐานสำหรับแจ้งเตือนหรือไม่
    try:
        from PyQt5.QtWidgets import QApplication, QMessageBox
        from PyQt5.QtGui import QPixmap, QPainter, QFont, QIcon
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtWidgets import QSplashScreen
    except ImportError:
        print(f"❌ ไม่พบไลบรารี PyQt5 แม้จะพยายามติดตั้งแล้ว")
        print(f"กรุณารัน 'pip install PyQt5' ด้วยตนเอง")
        sys.exit(1)

    app = QApplication(sys.argv)
    
    if missing_libs or ffmpeg_is_missing:
        msg = ""
        if missing_libs:
            msg += f"❌ ไม่พบไลบรารี: {', '.join(missing_libs)}\nกรุณารัน 'pip install -r requirements.txt'\n\n"
        if ffmpeg_is_missing:
            msg += "❌ ไม่พบโปรแกรม 'ffmpeg' ในระบบ\nกรุณาติดตั้ง ffmpeg และเพิ่มลงใน PATH (จำเป็นสำหรับวิดีโอและเสียง)"
            
        QMessageBox.critical(None, "ข้อผิดพลาดในการเริ่มต้น", msg)
        if missing_libs:
            sys.exit(1)
    
    # รันแอปพลิเคชันหลัก
    run_app(app)
