"""Settings Tab — with System info"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QLineEdit, QTextEdit,
                              QTableWidget, QTableWidgetItem,
                              QMessageBox, QGroupBox, QFormLayout,
                              QScrollArea, QFrame, QTabWidget)
from PyQt6.QtCore import Qt
from data import db
import os


class SettingsTab(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self._build()
        self.load_table()

    def _build(self):
        outer = QVBoxLayout()
        outer.setContentsMargins(4, 4, 4, 4)
        outer.setSpacing(4)

        title = QLabel("⚙️ সেটিংস")
        title.setObjectName("title")
        outer.addWidget(title)

        # Sub-tabs
        self.sub_tabs = QTabWidget()
        self.sub_tabs.addTab(self._models_tab(), "📱 Models")
        self.sub_tabs.addTab(self._system_tab(), "🔧 System")
        outer.addWidget(self.sub_tabs, 1)

        self.setLayout(outer)

    # ═════════════════════════════════════════════════════════
    # Models Tab
    # ═════════════════════════════════════════════════════════

    def _models_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.lbl_stats = QLabel("")
        self.lbl_stats.setObjectName("subtitle")
        layout.addWidget(self.lbl_stats)

        # Quick actions bar (fixed)
        top_btn_bar = QFrame()
        top_btn_bar.setStyleSheet(
            "QFrame { background-color: #252536; "
            "border-radius: 5px; padding: 4px; }"
        )
        top_btn_layout = QHBoxLayout(top_btn_bar)
        top_btn_layout.setContentsMargins(8, 4, 8, 4)
        top_btn_layout.setSpacing(6)

        lbl_action = QLabel("⚡ Quick:")
        lbl_action.setStyleSheet(
            "color: #89b4fa; font-weight: bold; font-size: 12px;"
        )
        top_btn_layout.addWidget(lbl_action)

        btn_save_top = QPushButton("💾 সেভ করো")
        btn_save_top.setObjectName("primary")
        btn_save_top.setMinimumWidth(120)
        btn_save_top.setMinimumHeight(30)
        btn_save_top.clicked.connect(self.save_device)
        top_btn_layout.addWidget(btn_save_top)

        btn_clear_top = QPushButton("🗑️ Clear Form")
        btn_clear_top.setMinimumHeight(30)
        btn_clear_top.clicked.connect(self.clear_form)
        top_btn_layout.addWidget(btn_clear_top)

        top_btn_layout.addStretch()
        layout.addWidget(top_btn_bar)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        content = QWidget()
        inner = QVBoxLayout(content)
        inner.setContentsMargins(4, 4, 4, 4)
        inner.setSpacing(6)

        # Add Model Form
        add_group = QGroupBox("➕ নতুন মডেল যোগ করো")
        form = QFormLayout()
        form.setSpacing(6)

        self.f_brand = QLineEdit()
        self.f_brand.setPlaceholderText("Type: Samsung")
        self.f_model = QLineEdit()
        self.f_model.setPlaceholderText("Type: SM-A105F")
        self.f_code = QLineEdit()
        self.f_code.setPlaceholderText("Type: a10 (optional)")
        self.f_chip = QLineEdit()
        self.f_chip.setPlaceholderText("Type: Exynos 7884 (optional)")
        self.f_android = QLineEdit()
        self.f_android.setPlaceholderText("Type: 9 (optional)")
        self.f_year = QLineEdit()
        self.f_year.setPlaceholderText("Type: 2019 (optional)")
        self.f_issues = QTextEdit()
        self.f_issues.setMaximumHeight(70)
        self.f_issues.setPlaceholderText("Common issues — প্রতি লাইনে একটা")

        form.addRow("Brand *", self.f_brand)
        form.addRow("Model *", self.f_model)
        form.addRow("Codename", self.f_code)
        form.addRow("Chipset", self.f_chip)
        form.addRow("Android", self.f_android)
        form.addRow("Release Year", self.f_year)
        form.addRow("Common Issues", self.f_issues)
        add_group.setLayout(form)
        inner.addWidget(add_group)

        # In-form buttons
        in_form_btn = QHBoxLayout()
        btn_save_form = QPushButton("💾 সেভ করো (this form)")
        btn_save_form.setObjectName("primary")
        btn_save_form.clicked.connect(self.save_device)
        in_form_btn.addWidget(btn_save_form)

        btn_clear_form = QPushButton("🗑️ Clear Form")
        btn_clear_form.clicked.connect(self.clear_form)
        in_form_btn.addWidget(btn_clear_form)
        in_form_btn.addStretch()
        inner.addLayout(in_form_btn)

        # Search & Table
        search_group = QGroupBox("🔍 মডেল ব্রাউজ")
        search_layout = QVBoxLayout()
        search_layout.setContentsMargins(6, 6, 6, 6)
        search_layout.setSpacing(6)

        srow = QHBoxLayout()
        self.f_search = QLineEdit()
        self.f_search.setPlaceholderText("ব্র্যান্ড / মডেল / চিপসেট লিখো...")
        self.f_search.textChanged.connect(self.load_table)
        srow.addWidget(self.f_search)

        btn_refresh = QPushButton("🔄")
        btn_refresh.setFixedWidth(35)
        btn_refresh.clicked.connect(self.load_table)
        srow.addWidget(btn_refresh)
        search_layout.addLayout(srow)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Brand", "Model", "Chipset", "Year"]
        )
        self.table.setMinimumHeight(250)
        search_layout.addWidget(self.table)

        search_group.setLayout(search_layout)
        inner.addWidget(search_group)

        inner.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        return w

    # ═════════════════════════════════════════════════════════
    # System Tab (DB stats, BoardView paths)
    # ═════════════════════════════════════════════════════════

    def _system_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # DB Stats
        db_group = QGroupBox("📊 Database Statistics")
        db_layout = QVBoxLayout()
        db_layout.setContentsMargins(6, 6, 6, 6)
        self.out_sys_stats = QTextEdit()
        self.out_sys_stats.setReadOnly(True)
        self.out_sys_stats.setMinimumHeight(150)
        db_layout.addWidget(self.out_sys_stats)
        db_group.setLayout(db_layout)
        layout.addWidget(db_group)

        # Folder paths
        paths_group = QGroupBox("📁 Folder Paths")
        paths_layout = QVBoxLayout()
        paths_layout.setContentsMargins(6, 6, 6, 6)

        self.out_paths = QTextEdit()
        self.out_paths.setReadOnly(True)
        self.out_paths.setMinimumHeight(180)
        paths_layout.addWidget(self.out_paths)
        paths_group.setLayout(paths_layout)
        layout.addWidget(paths_group)

        # Buttons
        btn_row = QHBoxLayout()
        btn_refresh = QPushButton("🔄 Refresh Info")
        btn_refresh.setObjectName("primary")
        btn_refresh.clicked.connect(self._refresh_system)
        btn_row.addWidget(btn_refresh)

        btn_open_root = QPushButton("📂 Open Root Folder")
        btn_open_root.clicked.connect(self._open_root)
        btn_row.addWidget(btn_open_root)

        btn_open_bv = QPushButton("📐 Open BoardView Folder")
        btn_open_bv.clicked.connect(self._open_boardview)
        btn_row.addWidget(btn_open_bv)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        layout.addStretch()

        # Load initial
        self._refresh_system()
        return w

    def _refresh_system(self):
        """System stats + folder info"""
        try:
            # Stats
            total = db.total_count()
            clones = db.clone_count()
            ver = db.get_meta("db_version", "?")
            last = db.get_meta("last_update", "?")

            self.out_sys_stats.clear()
            self.out_sys_stats.append("=" * 50)
            self.out_sys_stats.append("📱 DEVICES DATABASE")
            self.out_sys_stats.append("=" * 50)
            self.out_sys_stats.append(f"Total Models : {total}")
            self.out_sys_stats.append(f"Clone Models : {clones}")
            self.out_sys_stats.append(f"DB Version   : {ver}")
            self.out_sys_stats.append(f"Last Update  : {str(last)[:19]}")
            self.out_sys_stats.append("")

            # Scanner stats
            try:
                from data.scanner_db import dashboard_stats
                s = dashboard_stats()
                self.out_sys_stats.append("─" * 50)
                self.out_sys_stats.append("🔬 SCANNER SYSTEM")
                self.out_sys_stats.append("─" * 50)
                self.out_sys_stats.append(f"Board Scans  : {s.get('scans', 0)}")
                self.out_sys_stats.append(f"BoardViews   : {s.get('boardviews', 0)}")
                self.out_sys_stats.append(f"History Evts : {s.get('history_events', 0)}")
            except Exception:
                pass

            self.out_sys_stats.append("=" * 50)

            # Paths
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            self.out_paths.clear()
            self.out_paths.append("=" * 50)
            self.out_paths.append("📁 FOLDER LOCATIONS")
            self.out_paths.append("=" * 50)
            self.out_paths.append(f"Root        : {root}")
            self.out_paths.append(f"Database    : {os.path.join(root, 'database', 'devices.db')}")
            self.out_paths.append(f"BoardView   : {os.path.join(root, 'guides', 'boardview')}")
            self.out_paths.append(f"Schematic   : {os.path.join(root, 'guides', 'schematic')}")
            self.out_paths.append(f"Photos/Scans: {os.path.join(root, 'logs', 'scans')}")
            self.out_paths.append(f"Guides      : {os.path.join(root, 'guides')}")
            self.out_paths.append(f"Logs        : {os.path.join(root, 'logs')}")
            self.out_paths.append("=" * 50)

        except Exception as e:
            self.out_sys_stats.clear()
            self.out_sys_stats.append(f"❌ Error: {e}")

    def _open_root(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        try:
            os.startfile(root)
        except Exception:
            pass

    def _open_boardview(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bv_dir = os.path.join(root, "guides", "boardview")
        os.makedirs(bv_dir, exist_ok=True)
        try:
            os.startfile(bv_dir)
        except Exception:
            pass

    # ═════════════════════════════════════════════════════════
    # Model Actions
    # ═════════════════════════════════════════════════════════

    def update_stats(self):
        try:
            total = db.total_count()
            clones = db.clone_count()
            self.lbl_stats.setText(
                f"📱 মোট: {total}  |  🧬 ক্লোন: {clones}"
            )
        except Exception as e:
            self.lbl_stats.setText(f"⚠️ {e}")

    def save_device(self):
        brand = self.f_brand.text().strip()
        model = self.f_model.text().strip()

        if not brand or not model:
            QMessageBox.warning(
                self, "⚠️ সতর্কতা",
                "Brand ও Model box-এ actual text type করতে হবে।\n"
                "(Grey placeholder নয়)"
            )
            return

        issues = [
            l.strip() for l in self.f_issues.toPlainText().split("\n")
            if l.strip()
        ]
        try:
            year = int(self.f_year.text() or 0)
        except ValueError:
            year = 0

        ok = db.add_device(
            brand=brand, model=model,
            codename=self.f_code.text().strip(),
            chipset=self.f_chip.text().strip(),
            android_ver=self.f_android.text().strip(),
            release_year=year,
            common_issues=issues,
            hw_guide_path=f"guides/{brand.lower()}/{model.lower()}.md"
        )

        if ok:
            QMessageBox.information(
                self, "✅ সফল",
                f"{brand} {model} সেভ হয়েছে"
            )
            self.clear_form()
            self.load_table()
            self.update_stats()

    def clear_form(self):
        for f in [self.f_brand, self.f_model, self.f_code, self.f_chip,
                  self.f_android, self.f_year]:
            f.clear()
        self.f_issues.clear()

    def load_table(self):
        q = self.f_search.text().strip()
        try:
            if q:
                rows = db.search_devices(q, limit=500)
            else:
                from data.db import conn
                with conn() as c:
                    rows = [dict(r) for r in c.execute(
                        "SELECT * FROM devices ORDER BY brand, model LIMIT 200"
                    ).fetchall()]

            self.table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self.table.setItem(i, 0, QTableWidgetItem(r.get("brand", "")))
                self.table.setItem(i, 1, QTableWidgetItem(r.get("model", "")))
                self.table.setItem(i, 2, QTableWidgetItem(r.get("chipset", "")))
                self.table.setItem(
                    i, 3, QTableWidgetItem(str(r.get("release_year", "")))
                )
            self.table.resizeColumnsToContents()
            self.update_stats()
        except Exception as e:
            print(f"Load fail: {e}")