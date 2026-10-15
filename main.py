# Mobile Service Master - Main Entry Point
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

# Core imports
try:
    from ui.tab_b2b_settings import B2BSettingsTab
    HAS_B2B = True
except ImportError as e:
    HAS_B2B = False
    print(f"[WARN] B2B tab not loaded: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mobile Service Master v3.1")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()

    def init_ui(self):
        tabs = QTabWidget()

        # B2B Settings Tab
        if HAS_B2B:
            tabs.addTab(B2BSettingsTab(), "B2B API Settings")
        else:
            placeholder = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(QLabel("B2B Settings Tab not loaded"))
            placeholder.setLayout(layout)
            tabs.addTab(placeholder, "B2B API Settings")

        self.setCentralWidget(tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
