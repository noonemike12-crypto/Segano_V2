def get_modern_style():
    return """
        QWidget {
            background-color: #0b0e14;
            color: #e0e0e0;
            font-family: 'Sarabun', 'Segoe UI', sans-serif;
            font-size: 10pt;
        }
        
        QMainWindow {
            background-color: #0b0e14;
        }
        
        QGroupBox {
            border: 2px solid #1a222d;
            border-radius: 10px;
            margin-top: 1.5em;
            padding: 15px;
            font-weight: bold;
            color: #00d4ff;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 5px;
        }
        
        QPushButton {
            background-color: #1a222d;
            border: 1px solid #2d3748;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 30px;
        }
        
        QPushButton:hover {
            background-color: #2d3748;
            border-color: #00d4ff;
        }
        
        QPushButton#primaryBtn {
            background-color: #0056b3;
            border-color: #007bff;
            color: white;
        }
        
        QPushButton#primaryBtn:hover {
            background-color: #007bff;
        }
        
        QPushButton#secondaryBtn {
            background-color: #2d3748;
            border-color: #4a5568;
        }
        
        QPushButton#dangerBtn {
            background-color: #742a2a;
            border-color: #9b2c2c;
        }
        
        QPushButton#dangerBtn:hover {
            background-color: #9b2c2c;
        }
        
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #1a222d;
            border: 1px solid #2d3748;
            border-radius: 6px;
            padding: 8px;
            selection-background-color: #00d4ff;
        }
        
        QLineEdit:focus, QTextEdit:focus {
            border-color: #00d4ff;
        }
        
        QComboBox {
            background-color: #1a222d;
            border: 1px solid #2d3748;
            border-radius: 6px;
            padding: 5px 10px;
            min-width: 100px;
        }
        
        QComboBox::drop-down {
            border: none;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #00d4ff;
            margin-right: 10px;
        }
        
        QTabWidget::pane {
            border: 1px solid #1a222d;
            border-radius: 8px;
            background-color: #0f172a;
        }
        
        QTabBar::tab {
            background-color: #1a222d;
            color: #a0aec0;
            padding: 10px 20px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #0f172a;
            color: #00d4ff;
            border-bottom: 2px solid #00d4ff;
        }
        
        QTabBar::tab:hover {
            background-color: #2d3748;
        }
        
        QProgressBar {
            border: 1px solid #2d3748;
            border-radius: 10px;
            text-align: center;
            background-color: #1a222d;
        }
        
        QProgressBar::chunk {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #00d4ff, stop:1 #0099cc);
            border-radius: 10px;
        }
        
        QScrollBar:vertical {
            background-color: #0b0e14;
            width: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #1a222d;
            min-height: 20px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #2d3748;
        }
        
        QTableWidget {
            background-color: #1a222d;
            border: 1px solid #2d3748;
            gridline-color: #2d3748;
            border-radius: 8px;
        }
        
        QHeaderView::section {
            background-color: #1a222d;
            color: #00d4ff;
            padding: 5px;
            border: 1px solid #2d3748;
            font-weight: bold;
        }
        
        QLabel#headerTitle {
            font-size: 24pt;
            font-weight: bold;
            color: #00d4ff;
        }
        
        QLabel#statusReady {
            color: #00ff88;
            font-weight: bold;
        }
    """
