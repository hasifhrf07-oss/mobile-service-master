# Main Window — Full Integration with Multimeter

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                              QTabWidget, QLabel, QStatusBar)
from PyQt6.QtCore import QTimer
from ui.tab_detect import DetectTab
from ui.tab_diagnose import DiagnoseTab
from ui.tab_multimeter import MultimeterTab
from ui.tab_scanner import ScannerTab
from ui.tab_boardview import BoardViewTab
from ui.tab_history import HistoryTab
from ui.tab_settings import SettingsTab
from ui.tab_update import UpdateTab
from ui.style import apply_theme
from data import db


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Mobile Service Master v3.0")
        self.setGeometry(60, 40, 1280, 820)
        self.setMinimumSize(900, 600)

        self.app_state = {
            "device_info": None,
            "clone_reasons": [],
            "diagnosis": None,
            "symptoms": {},
            "client_name": "",
            "client_phone": "",
            "boardview_path": None,
            "schematic_path": None,
            "multimeter_session": {},
        }

        apply_theme(app)
        self._build()

    def _build(self):
        central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)

        header = QLabel("🔧 Mobile Service Master")
        header.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #89b4fa; "
            "padding: 4px 8px;"
        )
        layout.addWidget(header)

        self.tabs = QTabWidget()
        self.tabs.addTab(DetectTab(self.app_state),      "🔌 Detect")
        self.tabs.addTab(DiagnoseTab(self.app_state),    "🧪 Diagnose")
        self.tabs.addTab(MultimeterTab(self.app_state),  "📏 Multimeter")
        self.tabs.addTab(ScannerTab(self.app_state),     "🔬 Scanner")
        self.tabs.addTab(BoardViewTab(self.app_state),   "📐 BoardView")
        self.tabs.addTab(HistoryTab(self.app_state),     "📜 History")
        self.tabs.addTab(SettingsTab(self.app_state),    "⚙️ Settings")
        self.tabs.addTab(UpdateTab(self.app_state),      "🔄 Update")
        layout.addWidget(self.tabs, 1)

        central.setLayout(layout)
        self.setCentralWidget(central)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self._refresh_status()

        self.timer = QTimer()
        self.timer.timeout.connect(self._refresh_status)
        self.timer.start(30000)

    def _refresh_status(self):
        try:
            total = db.total_count()
            clones = db.clone_count()
            ver = db.get_meta("db_version", "?")

            scan_str = ""
            try:
                from data.scanner_db import dashboard_stats
                s = dashboard_stats()
                scans = s.get("scans", 0)
                bv = s.get("boardviews", 0)
                scan_str = f"  |  🔬 {scans}  |  📐 {bv}"
            except Exception:
                pass

            mm_count = len(self.app_state.get("multimeter_session", {}))
            mm_str = f"  |  📏 {mm_count}" if mm_count else ""

            self.status.showMessage(
                f"📱 Devices: {total}  |  🧬 Clones: {clones}  |  "
                f"🔖 DB v{ver}{scan_str}{mm_str}"
            )
        except Exception as e:
            self.status.showMessage(f"⚠️ Status error: {e}")