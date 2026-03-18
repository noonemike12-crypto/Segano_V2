def get_modern_style():
    return """
        QWidget {
            background-color: #101922;
            color: #e2e8f0;
            font-family: 'Inter', 'Sarabun', 'Segoe UI', sans-serif;
            font-size: 10pt;
        }
        
        QMainWindow {
            background-color: #101922;
        }
        
        /* Sidebar Styling */
        QFrame#sidebar {
            background-color: #0b0e14;
            border-right: 1px solid #1e293b;
        }
        
        QPushButton#sidebarBtn {
            background-color: transparent;
            border: none;
            border-radius: 8px;
            padding: 10px 15px;
            text-align: left;
            font-weight: 500;
            color: #94a3b8;
        }
        
        QPushButton#sidebarBtn:hover {
            background-color: #1e293b;
            color: #f8fafc;
        }
        
        QPushButton#sidebarBtn[active="true"] {
            background-color: rgba(13, 127, 242, 0.1);
            color: #0d7ff2;
            font-weight: 700;
        }
        
        /* Content Area */
        QFrame#contentArea {
            background-color: #101922;
        }
        
        QGroupBox {
            border: 1px solid #1e293b;
            border-radius: 12px;
            margin-top: 20px;
            padding: 20px;
            font-weight: bold;
            color: #94a3b8;
            background-color: rgba(30, 41, 59, 0.3);
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 10px;
            color: #0d7ff2;
        }
        
        QPushButton {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
            min-height: 35px;
            color: #f8fafc;
        }
        
        QPushButton:hover {
            background-color: #334155;
            border-color: #0d7ff2;
        }
        
        QPushButton#primaryBtn {
            background-color: #0d7ff2;
            border: none;
            color: white;
        }
        
        QPushButton#primaryBtn:hover {
            background-color: #0b6ed1;
        }
        
        QPushButton#secondaryBtn {
            background-color: rgba(13, 127, 242, 0.1);
            border: 1px solid rgba(13, 127, 242, 0.2);
            color: #0d7ff2;
        }
        
        QPushButton#secondaryBtn:hover {
            background-color: rgba(13, 127, 242, 0.2);
        }
        
        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {
            background-color: #0b0e14;
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 10px;
            color: #f8fafc;
            selection-background-color: #0d7ff2;
        }
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border-color: #0d7ff2;
        }
        
        QProgressBar {
            border: 1px solid #1e293b;
            border-radius: 6px;
            text-align: center;
            background-color: #0b0e14;
            height: 12px;
            font-size: 8pt;
        }
        
        QProgressBar::chunk {
            background-color: #0d7ff2;
            border-radius: 6px;
        }
        
        QScrollBar:vertical {
            background-color: transparent;
            width: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #1e293b;
            min-height: 30px;
            border-radius: 5px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #334155;
        }
        
        QTableWidget {
            background-color: transparent;
            border: 1px solid #1e293b;
            gridline-color: #1e293b;
            border-radius: 12px;
            outline: none;
        }
        
        QHeaderView::section {
            background-color: #0b0e14;
            color: #94a3b8;
            padding: 10px;
            border: none;
            border-bottom: 1px solid #1e293b;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 8pt;
        }
        
        QLabel#headerTitle {
            font-size: 28pt;
            font-weight: 900;
            color: #f8fafc;
            letter-spacing: -1px;
        }
        
        QLabel#subTitle {
            font-size: 11pt;
            color: #94a3b8;
        }
    """
