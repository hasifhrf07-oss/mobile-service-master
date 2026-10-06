"""Dark Theme — Compact Layout"""

STYLESHEET = """
QWidget {
    background-color: #1e1e2e;
    color: #e0e0e0;
    font-family: "Nirmala UI", "Segoe UI", Arial, sans-serif;
    font-size: 12px;
}

QMainWindow { background-color: #181825; }

/* ===== Compact Header ===== */
QLabel#header {
    font-size: 14px;
    font-weight: bold;
    color: #89b4fa;
    padding: 4px 10px;
    background-color: #181825;
    border-radius: 4px;
}

QLabel#title {
    font-size: 14px;
    font-weight: bold;
    color: #89b4fa;
    padding: 4px 0;
}

QLabel#subtitle {
    font-size: 11px;
    color: #a6adc8;
    padding: 2px;
}

/* ===== Buttons ===== */
QPushButton {
    background-color: #313244;
    color: #e0e0e0;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 5px 12px;
    font-size: 12px;
    min-height: 22px;
}
QPushButton:hover {
    background-color: #45475a;
    border-color: #89b4fa;
}
QPushButton:pressed { background-color: #585b70; }
QPushButton#primary {
    background-color: #89b4fa;
    color: #1e1e2e;
    font-weight: bold;
}
QPushButton#primary:hover { background-color: #b4befe; }
QPushButton#danger {
    background-color: #f38ba8;
    color: #1e1e2e;
    font-weight: bold;
}

/* ===== Inputs ===== */
QLineEdit {
    background-color: #11111b;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 5px 8px;
    font-size: 12px;
    min-height: 20px;
}
QLineEdit:focus { border-color: #89b4fa; }

QTextEdit, QPlainTextEdit {
    background-color: #11111b;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 6px;
    font-size: 11px;
    font-family: "Consolas", monospace;
}

QComboBox {
    background-color: #313244;
    color: #e0e0e0;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
    min-height: 22px;
    min-width: 110px;
}
QComboBox::drop-down { border: none; width: 18px; }

/* ===== Compact Tabs ===== */
QTabWidget::pane {
    border: 1px solid #313244;
    background-color: #1e1e2e;
    border-radius: 4px;
    top: -1px;
}
QTabBar::tab {
    background-color: #313244;
    color: #a6adc8;
    padding: 6px 14px;
    margin-right: 1px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-size: 11px;
    min-width: 80px;
}
QTabBar::tab:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
    font-weight: bold;
}
QTabBar::tab:hover:!selected { background-color: #45475a; }

/* ===== Group Box ===== */
QGroupBox {
    border: 1px solid #45475a;
    border-radius: 4px;
    margin-top: 6px;
    padding: 6px 6px 4px 6px;
    font-size: 11px;
    font-weight: bold;
    color: #89b4fa;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 8px;
    padding: 0 4px;
    background-color: #1e1e2e;
}

/* ===== Tables ===== */
QTableWidget {
    background-color: #11111b;
    color: #cdd6f4;
    gridline-color: #313244;
    border: 1px solid #313244;
    border-radius: 4px;
    font-size: 11px;
}
QTableWidget::item { padding: 3px; }
QTableWidget::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}
QHeaderView::section {
    background-color: #313244;
    color: #cdd6f4;
    padding: 4px 6px;
    border: none;
    border-right: 1px solid #45475a;
    border-bottom: 1px solid #45475a;
    font-weight: bold;
    font-size: 11px;
}

/* ===== Scrollbar (Thin & Modern) ===== */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #89b4fa; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}

QScrollBar:horizontal {
    background: transparent;
    height: 8px;
}
QScrollBar::handle:horizontal {
    background: #45475a;
    border-radius: 4px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover { background: #89b4fa; }

/* ===== Status Bar ===== */
QStatusBar {
    background-color: #181825;
    color: #a6adc8;
    font-size: 11px;
    padding: 2px 8px;
    border-top: 1px solid #313244;
}

/* ===== Form Layout ===== */
QFormLayout { spacing: 4px; }

/* ===== Progress Bar ===== */
QProgressBar {
    background: #181825;
    border: 1px solid #313244;
    border-radius: 4px;
    text-align: center;
    color: #e0e0e0;
    font-size: 11px;
    height: 16px;
}
QProgressBar::chunk {
    background: #89b4fa;
    border-radius: 4px;
}

/* ===== Scroll Area ===== */
QScrollArea {
    border: none;
    background: transparent;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}
"""


def apply_theme(app):
    app.setStyleSheet(STYLESHEET)