from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from utils.logger import logger

class DebugTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Timer to refresh logs
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_logs)
        self.refresh_timer.start(500) # Refresh every 500ms

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QHBoxLayout()
        header.addWidget(QLabel("🛠️ SYSTEM REAL-TIME DEBUG CONSOLE"))
        header.addStretch()
        
        self.clear_btn = QPushButton("🗑️ Clear Logs")
        self.clear_btn.clicked.connect(self.clear_logs)
        header.addWidget(self.clear_btn)
        
        layout.addLayout(header)

        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setFontFamily("Consolas")
        self.log_viewer.setFontPointSize(10)
        self.log_viewer.setStyleSheet("""
            QTextEdit {
                background-color: #05050a;
                color: #00ff41;
                border: 1px solid #2d2d44;
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.log_viewer)

    def refresh_logs(self):
        current_text = self.log_viewer.toPlainText()
        new_logs = logger.get_buffer()
        
        if current_text != new_logs:
            self.log_viewer.setPlainText(new_logs)
            # Auto-scroll to bottom
            self.log_viewer.verticalScrollBar().setValue(
                self.log_viewer.verticalScrollBar().maximum()
            )

    def clear_logs(self):
        logger.clear_buffer()
        self.log_viewer.clear()
        logger.log("info", "Debug console cleared by user.")
