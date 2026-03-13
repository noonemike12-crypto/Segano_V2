def get_modern_style():
    return """
        /* Global Styles */
        QWidget {
            background-color: #0a0a12;
            color: #e0e0e0;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            font-size: 13px;
        }

        /* Main Window & Header */
        QFrame#headerFrame {
            background-color: #161625;
            border-bottom: 1px solid #2d2d44;
        }

        /* Card System */
        QGroupBox {
            background-color: #1c1c2e;
            border: 1px solid #2d2d44;
            border-radius: 15px;
            margin-top: 20px;
            padding: 20px;
            font-weight: bold;
            color: #00d4ff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 20px;
            padding: 0 10px;
        }

        /* Modern Buttons */
        QPushButton {
            background-color: #2d2d44;
            border: 1px solid #3d3d5c;
            border-radius: 8px;
            padding: 10px 20px;
            color: #ffffff;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #3d3d5c;
            border-color: #00d4ff;
        }
        QPushButton#primaryBtn {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00d4ff, stop:1 #0099ff);
            color: #000000;
            border: none;
        }
        QPushButton#primaryBtn:hover {
            background: #33e0ff;
        }
        QPushButton#secondaryBtn {
            background-color: #1c1c2e;
            border: 1px solid #00ff88;
            color: #00ff88;
        }
        QPushButton#secondaryBtn:hover {
            background-color: rgba(0, 255, 136, 0.1);
        }

        /* Inputs */
        QTextEdit, QLineEdit, QComboBox {
            background-color: #0f0f1a;
            border: 1px solid #2d2d44;
            border-radius: 6px;
            padding: 10px;
            color: #ffffff;
        }
        QTextEdit:focus, QLineEdit:focus {
            border-color: #00d4ff;
        }

        /* Tab Bar Customization */
        QTabWidget::pane {
            border: none;
            background-color: transparent;
        }
        QTabBar::tab {
            background-color: transparent;
            padding: 12px 25px;
            color: #888;
            font-weight: bold;
            border-bottom: 2px solid transparent;
        }
        QTabBar::tab:selected {
            color: #00d4ff;
            border-bottom: 2px solid #00d4ff;
        }
        QTabBar::tab:hover {
            color: #ffffff;
        }

        /* Progress Bar */
        QProgressBar {
            background-color: #0f0f1a;
            border: 1px solid #2d2d44;
            border-radius: 10px;
            text-align: center;
            height: 12px;
        }
        QProgressBar::chunk {
            background-color: #00d4ff;
            border-radius: 9px;
        }

        /* ScrollBar */
        QScrollBar:vertical {
            background: #0a0a12;
            width: 8px;
        }
        QScrollBar::handle:vertical {
            background: #2d2d44;
            border-radius: 4px;
        }
    """
