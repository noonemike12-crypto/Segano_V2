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
        QMenu, QMessageBox, QSplashScreen, QProgressBar, QStackedWidget
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
            # Main Layout: Horizontal (Sidebar + Content)
            main_h_layout = QHBoxLayout(self)
            main_h_layout.setContentsMargins(0, 0, 0, 0)
            main_h_layout.setSpacing(0)

            # --- Sidebar ---
            self.sidebar = QFrame()
            self.sidebar.setObjectName("sidebar")
            self.sidebar.setFixedWidth(260)
            sidebar_layout = QVBoxLayout(self.sidebar)
            sidebar_layout.setContentsMargins(15, 30, 15, 30)
            sidebar_layout.setSpacing(10)

            # Sidebar Logo/Title
            logo_layout = QHBoxLayout()
            logo_icon = QLabel("🛡️")
            logo_icon.setStyleSheet("font-size: 24pt; color: #0d7ff2;")
            logo_text_vbox = QVBoxLayout()
            logo_title = QLabel("StegoTech Pro")
            logo_title.setStyleSheet("font-weight: 900; font-size: 14pt; color: white;")
            logo_subtitle = QLabel("Secure Encoding")
            logo_subtitle.setStyleSheet("font-size: 8pt; color: #94a3b8;")
            logo_text_vbox.addWidget(logo_title)
            logo_text_vbox.addWidget(logo_subtitle)
            logo_layout.addWidget(logo_icon)
            logo_layout.addLayout(logo_text_vbox)
            sidebar_layout.addLayout(logo_layout)
            sidebar_layout.addSpacing(40)

            # Sidebar Buttons
            self.sidebar_buttons = []
            menu_items = [
                ("🖼️ Image Stego", 0),
                ("🎵 Audio Stego", 1),
                ("🎬 Video Stego", 2),
                ("🏷️ Metadata", 3),
                ("📁 File Stego", 4),
                ("🔐 Encryption", 5),
                ("🔑 PGP Keys", 6),
                ("🔗 Integrated", 7)
            ]

            for text, idx in menu_items:
                btn = QPushButton(text)
                btn.setObjectName("sidebarBtn")
                btn.setCheckable(True)
                btn.clicked.connect(lambda checked, i=idx: self.switch_page(i))
                sidebar_layout.addWidget(btn)
                self.sidebar_buttons.append(btn)

            sidebar_layout.addStretch()

            # Sidebar Footer (Storage/Status)
            storage_frame = QFrame()
            storage_frame.setStyleSheet("background-color: #1e293b; border-radius: 12px; padding: 15px;")
            storage_layout = QVBoxLayout(storage_frame)
            storage_title = QLabel("STORAGE")
            storage_title.setStyleSheet("font-size: 7pt; font-weight: 800; color: #64748b; letter-spacing: 1px;")
            self.storage_bar = QProgressBar()
            self.storage_bar.setValue(72)
            storage_info = QLabel("7.2 GB of 10 GB used")
            storage_info.setStyleSheet("font-size: 7pt; color: #94a3b8;")
            storage_layout.addWidget(storage_title)
            storage_layout.addWidget(self.storage_bar)
            storage_layout.addWidget(storage_info)
            sidebar_layout.addWidget(storage_frame)

            main_h_layout.addWidget(self.sidebar)

            # --- Content Area ---
            self.content_area = QFrame()
            self.content_area.setObjectName("contentArea")
            content_v_layout = QVBoxLayout(self.content_area)
            content_v_layout.setContentsMargins(0, 0, 0, 0)
            content_v_layout.setSpacing(0)

            # Header in Content Area
            header = QFrame()
            header.setFixedHeight(70)
            header.setStyleSheet("background-color: rgba(16, 25, 34, 0.8); border-bottom: 1px solid #1e293b;")
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(30, 0, 30, 0)
            
            self.page_title = QLabel("Dashboard")
            self.page_title.setStyleSheet("font-size: 14pt; font-weight: 700; color: white;")
            header_layout.addWidget(self.page_title)
            header_layout.addStretch()
            
            self.help_btn = QPushButton("❓ Help")
            self.help_btn.clicked.connect(self.show_help)
            header_layout.addWidget(self.help_btn)
            
            content_v_layout.addWidget(header)

            # Stacked Widget for Pages
            self.stack = QStackedWidget()
            self.stack.addWidget(image_tab.ImageTab())
            self.stack.addWidget(audio_tab.AudioTab())
            self.stack.addWidget(video_tab.VideoTab())
            self.stack.addWidget(info_tab.FileInfoTab())
            self.stack.addWidget(file_and_FILE.FileAndFileTab())
            self.stack.addWidget(encryption_tab.EncryptionTab())
            self.stack.addWidget(pgp_tab.PGPTab())
            self.stack.addWidget(integrated_mode_tab.IntegrationTab())
            
            content_v_layout.addWidget(self.stack)

            # Footer
            footer = QFrame()
            footer.setFixedHeight(40)
            footer.setStyleSheet("border-top: 1px solid #1e293b;")
            footer_layout = QHBoxLayout(footer)
            footer_layout.setContentsMargins(30, 0, 30, 0)
            
            self.status_label = QLabel("🟢 System Ready")
            self.status_label.setStyleSheet("color: #00ff88; font-weight: bold; font-size: 8pt;")
            footer_layout.addWidget(self.status_label)
            footer_layout.addStretch()
            self.mem_label = QLabel("💾 Memory: 0 MB")
            self.mem_label.setStyleSheet("font-size: 8pt; color: #94a3b8;")
            footer_layout.addWidget(self.mem_label)
            
            content_v_layout.addWidget(footer)
            main_h_layout.addWidget(self.content_area)

            # Initial Page
            self.switch_page(0)

        def switch_page(self, index):
            self.stack.setCurrentIndex(index)
            
            # Update Buttons
            for i, btn in enumerate(self.sidebar_buttons):
                btn.setProperty("active", i == index)
                btn.setChecked(i == index)
                btn.style().unpolish(btn)
                btn.style().polish(btn)
            
            # Update Page Title
            titles = ["Image Steganography", "Audio Steganography", "Video Steganography", 
                      "Metadata Steganography", "File Steganography", "Encryption Module", 
                      "PGP Key Management", "Integrated Mode"]
            self.page_title.setText(titles[index])
            logger.log("info", f"Switched to: {titles[index]}")

        def on_tab_changed(self, index):
            tab_name = self.tabs.tabText(index)
            logger.log("info", f"เปลี่ยนไปยังแท็บ: {tab_name}")

        def update_status(self):
            try:
                process = psutil.Process(os.getpid())
                mem = process.memory_info().rss / (1024 * 1024)
                self.mem_label.setText(f"💾 หน่วยความจำ: {mem:.1f} MB")
            except Exception:
                self.mem_label.setText("💾 หน่วยความจำ: N/A")

        def show_help(self):
            msg = QMessageBox()
            msg.setWindowTitle("Help - StegoTech Pro")
            msg.setText("<b>StegoTech Pro (Secure Incognito ENcryption Guard)</b><br><br>"
                       "This application is designed for high-level data security:<br>"
                       "- Hide data in various media (Steganography)<br>"
                       "- Encrypt data with global standards (AES, RSA, PGP)<br>"
                       "- Manage Metadata and File-in-File hiding<br><br>"
                       "Select a module from the sidebar to begin.")
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
    
    logger.log("info", "SIENG PRO: เริ่มต้นแอปพลิเคชัน")
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
