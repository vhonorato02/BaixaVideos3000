def get_dark_theme():
    return """
        QMainWindow { background-color: #121212; }
        QWidget { background-color: #121212; color: #e0e0e0; }
        QLineEdit, QComboBox, QTableWidget, QTextEdit {
            background-color: #1e1e1e;
            border: 1px solid #333;
            padding: 6px;
            font-family: 'Segoe UI', sans-serif;
            font-size: 11pt;
            color: #e0e0e0;
        }
        QPushButton {
            background-color: #E53935;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-family: 'Segoe UI', sans-serif;
            font-size: 11pt;
        }
        QPushButton:hover { background-color: #D32F2F; }
        QTabWidget::pane { border: none; }
        QTabBar::tab {
            background-color: #1e1e1e;
            padding: 10px 15px;
            min-width: 100px;
            font-family: 'Segoe UI', sans-serif;
            font-size: 11pt;
        }
        QTabBar::tab:selected { background-color: #E53935; }
        QHeaderView::section {
            background-color: #1e1e1e;
            border: 1px solid #333;
            padding: 6px;
        }
        QToolBar { background-color: #1e1e1e; border: none; }
        QProgressBar {
            background-color: #333;
            border: 1px solid #555;
            text-align: center;
            color: white;
        }
        QProgressBar::chunk {
            background-color: #E53935;
        }
    """

def get_light_theme():
    return """
        QMainWindow { background-color: #f5f5f5; }
        QWidget { background-color: #f5f5f5; color: #333; }
        QLineEdit, QComboBox, QTableWidget, QTextEdit {
            background-color: white;
            border: 1px solid #ccc;
            padding: 6px;
            font-family: 'Segoe UI', sans-serif;
            font-size: 11pt;
            color: #333;
        }
        QPushButton {
            background-color: #E53935;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-family: 'Segoe UI', sans-serif;
            font-size: 11pt;
        }
        QPushButton:hover { background-color: #D32F2F; }
        QTabWidget::pane { border: none; }
        QTabBar::tab {
            background-color: white;
            padding: 10px 15px;
            min-width: 100px;
            font-family: 'Segoe UI', sans-serif;
            font-size: 11pt;
        }
        QTabBar::tab:selected { background-color: #E53935; }
        QHeaderView::section {
            background-color: #e0e0e0;
            border: 1px solid #ccc;
            padding: 6px;
        }
        QToolBar { background-color: white; border: none; }
        QProgressBar {
            background-color: #ccc;
            border: 1px solid #aaa;
            text-align: center;
            color: #333;
        }
        QProgressBar::chunk {
            background-color: #E53935;
        }
    """ 