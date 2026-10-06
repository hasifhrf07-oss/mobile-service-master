# Mobile Service Master v3.0 - Entry Point

import sys
import os

# Ensure project root is on sys.path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Change working directory to project root
os.chdir(ROOT)

from PyQt6.QtWidgets import QApplication, QMessageBox
from ui.main_window import MainWindow
from database.init_db import init as init_db


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Mobile Service Master")
    app.setApplicationVersion("3.0")

    db_path = os.path.join(ROOT, "database", "devices.db")

    if not os.path.exists(db_path):
        init_db()
        QMessageBox.information(
            None, "প্রথমবার চালু",
            "ডেটাবেস তৈরি হয়েছে।\n\n"
            "এখন চালাও:\n"
            "  python database/seed_10000.py"
        )
        return

    win = MainWindow(app)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()