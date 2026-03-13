def get_main_style():
    return """
        QWidget {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0c0c0c, stop:0.3 #1a1a2e, stop:0.7 #16213e, stop:1 #0f3460);
            color: #ffffff;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
        }
        QGroupBox {
            background: rgba(45, 45, 68, 0.6);
            border: 2px solid #00d4ff;
            border-radius: 12px;
            margin-top: 15px;
            padding: 15px;
            font-weight: bold;
            color: #00d4ff;
        }
        QFrame#card {
            background: rgba(58, 58, 84, 0.5);
            border: 1px solid #444;
            border-radius: 10px;
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a90e2, stop:1 #357abd);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 16px;
            font-weight: bold;
        }
        QPushButton:hover { background: #5ba0f2; }
        QPushButton#actionPrimary { background: #8e24aa; }
        QPushButton#actionSecondary { background: #4caf50; }
        QPushButton#actionWarning { background: #ff9800; }
        QPushButton#actionDanger { background: #e74c3c; }
        
        QTextEdit, QLineEdit {
            background: #1e1e2e;
            color: #ffffff;
            border: 1px solid #444;
            border-radius: 6px;
            padding: 8px;
        }
        QProgressBar {
            background: #333;
            border-radius: 10px;
            text-align: center;
        }
        QProgressBar::chunk {
            background: #00d4ff;
            border-radius: 8px;
        }
    """
