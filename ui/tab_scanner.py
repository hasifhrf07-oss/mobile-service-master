"""Multi-Device Scanner Tab"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QLineEdit, QComboBox,
                              QGroupBox, QFormLayout, QScrollArea,
                              QMessageBox, QTextEdit, QListWidget,
                              QListWidgetItem, QSplitter)
from PyQt6.QtCore import Qt
from core.scanner.board_scanner import BoardScanner
from core.scanner.history_manager import HistoryManager
from core.scanner.state_comparator import StateComparator
from ui.scanner_widgets import ScanCard, StatBox


DEFAULT_RAILS = [
    ("vbat", "3.7-4.2"),
    ("vph_pwr", "3.7"),
    ("vdd_cpu", "0.9-1.3"),
    ("vdd_mem", "1.1-1.2"),
    ("vcc_io", "1.8"),
    ("emmc_vcc", "3.3"),
    ("vcc_usb", "5.0"),
]


class ScannerTab(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.scanner = BoardScanner(log_callback=self._log)
        self.history = HistoryManager()
        self.comparator = StateComparator()
        self._build()
        self._refresh()

    def _build(self):
        outer = QVBoxLayout()
        outer.setContentsMargins(6, 4, 6, 4)
        outer.setSpacing(6)

        title = QLabel("🔬 Multi-Device Scanner — Motherboard State")
        title.setObjectName("title")
        outer.addWidget(title)

        # Stats Row (BIG boxes)
        stats_row = QHBoxLayout()
        stats_row.setSpacing(8)

        self.stat_scans = StatBox("Total Scans", 0, "#89b4fa")
        self.stat_bv = StatBox("BoardViews", 0, "#a6e3a1")
        self.stat_ref = StatBox("References", 0, "#f9e2af")
        self.stat_week = StatBox("This Week", 0, "#cba6f7")

        stats_row.addWidget(self.stat_scans, 1)
        stats_row.addWidget(self.stat_bv, 1)
        stats_row.addWidget(self.stat_ref, 1)
        stats_row.addWidget(self.stat_week, 1)
        outer.addLayout(stats_row)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # LEFT: Input form
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(4, 4, 4, 4)
        left_layout.setSpacing(6)

        # Scroll for left
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        left_content = QWidget()
        lc_layout = QVBoxLayout(left_content)
        lc_layout.setContentsMargins(2, 2, 2, 2)
        lc_layout.setSpacing(6)

        # Device info
        info_group = QGroupBox("📱 Device Info")
        info_form = QFormLayout()
        info_form.setSpacing(5)

        self.f_brand = QLineEdit()
        self.f_brand.setPlaceholderText("Samsung")
        self.f_model = QLineEdit()
        self.f_model.setPlaceholderText("SM-A105F")
        self.f_chipset = QLineEdit()
        self.f_chipset.setPlaceholderText("Exynos 7884")
        self.f_phone_serial = QLineEdit()
        self.f_phone_serial.setPlaceholderText("R58M12345XYZ")
        self.f_technician = QLineEdit()
        self.f_technician.setPlaceholderText("Your name")
        self.f_client_name = QLineEdit()
        self.f_client_name.setPlaceholderText("Client name")
        self.f_client_phone = QLineEdit()
        self.f_client_phone.setPlaceholderText("017xxxxxxxx")

        info_form.addRow("Brand", self.f_brand)
        info_form.addRow("Model", self.f_model)
        info_form.addRow("Chipset", self.f_chipset)
        info_form.addRow("Serial", self.f_phone_serial)
        info_form.addRow("Technician", self.f_technician)
        info_form.addRow("Client", self.f_client_name)
        info_form.addRow("Client Phone", self.f_client_phone)
        info_group.setLayout(info_form)
        lc_layout.addWidget(info_group)

        # Readings
        readings_group = QGroupBox("⚡ Power Rail Readings (V)")
        readings_layout = QFormLayout()
        readings_layout.setSpacing(4)

        self.rail_inputs = {}
        for rail, exp in DEFAULT_RAILS:
            inp = QLineEdit()
            inp.setPlaceholderText(f"{exp}V")
            self.rail_inputs[rail] = inp
            readings_layout.addRow(f"{rail.upper()}", inp)

        self.f_current = QLineEdit()
        self.f_current.setPlaceholderText("mA (e.g., 12.5)")
        readings_layout.addRow("Current", self.f_current)

        readings_group.setLayout(readings_layout)
        lc_layout.addWidget(readings_group)

        # Notes
        notes_group = QGroupBox("📝 Notes")
        notes_layout = QVBoxLayout()
        notes_layout.setContentsMargins(6, 6, 6, 6)
        notes_layout.setSpacing(4)

        self.f_diagnosis = QLineEdit()
        self.f_diagnosis.setPlaceholderText("Diagnosis (e.g., PMIC dead)")
        notes_layout.addWidget(self.f_diagnosis)

        self.f_notes = QTextEdit()
        self.f_notes.setPlaceholderText("Notes...")
        self.f_notes.setMaximumHeight(60)
        notes_layout.addWidget(self.f_notes)

        notes_group.setLayout(notes_layout)
        lc_layout.addWidget(notes_group)

        lc_layout.addStretch()

        left_scroll.setWidget(left_content)
        left_layout.addWidget(left_scroll)

        # Save buttons (FIXED at bottom — always visible)
        save_row = QHBoxLayout()
        btn_save = QPushButton("💾 Save Scan")
        btn_save.setObjectName("primary")
        btn_save.setMinimumHeight(38)
        btn_save.clicked.connect(self.save_scan)
        save_row.addWidget(btn_save, 2)

        btn_clear = QPushButton("🗑️ Clear")
        btn_clear.setMinimumHeight(38)
        btn_clear.clicked.connect(self.clear_form)
        save_row.addWidget(btn_clear, 1)

        left_layout.addLayout(save_row)

        # RIGHT: History
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(4, 4, 4, 4)
        right_layout.setSpacing(4)

        hist_group = QGroupBox("🔍 History")
        hist_layout = QVBoxLayout()
        hist_layout.setContentsMargins(6, 6, 6, 6)
        hist_layout.setSpacing(4)

        frow = QHBoxLayout()
        self.f_search = QLineEdit()
        self.f_search.setPlaceholderText("Search scan...")
        self.f_search.textChanged.connect(self._refresh_history)
        frow.addWidget(self.f_search)

        btn_refresh = QPushButton("🔄")
        btn_refresh.setFixedWidth(38)
        btn_refresh.clicked.connect(self._refresh_history)
        frow.addWidget(btn_refresh)
        hist_layout.addLayout(frow)

        self.scan_list = QListWidget()
        self.scan_list.setStyleSheet(
            "QListWidget {"
            "  background-color: #181825;"
            "  border: 1px solid #313244;"
            "  border-radius: 4px;"
            "  padding: 2px;"
            "}"
        )
        hist_layout.addWidget(self.scan_list)

        # Action buttons
        act_row = QHBoxLayout()
        act_row.setSpacing(4)

        btn_load = QPushButton("📂 Load")
        btn_load.setMinimumHeight(32)
        btn_load.clicked.connect(self.load_selected)
        act_row.addWidget(btn_load)

        btn_compare = QPushButton("⚖️ Compare")
        btn_compare.setMinimumHeight(32)
        btn_compare.clicked.connect(self.compare_selected)
        act_row.addWidget(btn_compare)

        btn_ref = QPushButton("⭐ Ref")
        btn_ref.setMinimumHeight(32)
        btn_ref.clicked.connect(self.set_reference)
        act_row.addWidget(btn_ref)

        btn_delete = QPushButton("🗑️ Delete")
        btn_delete.setObjectName("danger")
        btn_delete.setMinimumHeight(32)
        btn_delete.clicked.connect(self.delete_selected)
        act_row.addWidget(btn_delete)

        hist_layout.addLayout(act_row)

        hist_group.setLayout(hist_layout)
        right_layout.addWidget(hist_group, 1)

        # Log
        log_group = QGroupBox("📋 Log")
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(6, 6, 6, 6)
        self.log_out = QTextEdit()
        self.log_out.setReadOnly(True)
        self.log_out.setMaximumHeight(120)
        log_layout.addWidget(self.log_out)
        log_group.setLayout(log_layout)
        right_layout.addWidget(log_group)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        outer.addWidget(splitter, 1)

        self.setLayout(outer)

    def _log(self, msg):
        self.log_out.append(msg)
        sb = self.log_out.verticalScrollBar()
        sb.setValue(sb.maximum())

    def save_scan(self):
        brand = self.f_brand.text().strip()
        model = self.f_model.text().strip()

        if not brand or not model:
            QMessageBox.warning(self, "!", "Brand & Model লাগবে")
            return

        readings = {}
        for rail, inp in self.rail_inputs.items():
            val = inp.text().strip()
            if val:
                try:
                    readings[rail] = float(val)
                except ValueError:
                    pass

        try:
            current = float(self.f_current.text() or 0)
        except ValueError:
            current = 0

        result = self.scanner.capture_state(
            brand=brand,
            model=model,
            chipset=self.f_chipset.text().strip(),
            phone_serial=self.f_phone_serial.text().strip(),
            readings=readings,
            current_draw=current,
            diagnosis=self.f_diagnosis.text().strip(),
            technician=self.f_technician.text().strip(),
            client_name=self.f_client_name.text().strip(),
            client_phone=self.f_client_phone.text().strip(),
            notes=self.f_notes.toPlainText().strip(),
        )

        if result["ok"]:
            QMessageBox.information(
                self, "✅ Saved",
                f"Scan ID: {result['scan_id']}"
            )
            self._refresh()
        else:
            QMessageBox.warning(self, "❌ Failed", result.get("message", ""))

    def clear_form(self):
        for f in [self.f_brand, self.f_model, self.f_chipset,
                  self.f_phone_serial, self.f_technician,
                  self.f_client_name, self.f_client_phone,
                  self.f_current, self.f_diagnosis]:
            f.clear()
        for inp in self.rail_inputs.values():
            inp.clear()
        self.f_notes.clear()

    def _refresh(self):
        self._refresh_history()
        self._refresh_stats()

    def _refresh_stats(self):
        try:
            from data.scanner_db import dashboard_stats
            s = dashboard_stats()
            self.stat_scans.set_value(s.get("scans", 0))
            self.stat_bv.set_value(s.get("boardviews", 0))

            # Reference count
            try:
                scans = self.scanner.list_scans(limit=1000)
                ref_count = sum(1 for s2 in scans if (s2.get("deviation_score") or 0) == 0)
                self.stat_ref.set_value(ref_count)
            except Exception:
                self.stat_ref.set_value(0)

            # Week count
            try:
                from data.scanner_db import scan_recent
                week_scans = scan_recent(days=7, limit=1000)
                self.stat_week.set_value(len(week_scans))
            except Exception:
                self.stat_week.set_value(0)
        except Exception as e:
            self._log(f"❌ Stats fail: {e}")

    def _refresh_history(self):
        q = self.f_search.text().strip()
        if q:
            scans = self.history.search_scans(q, limit=100)
        else:
            scans = self.scanner.list_scans(limit=100)

        self.scan_list.clear()

        if not scans:
            item = QListWidgetItem("   📭 এখনো কোনো scan করা হয়নি")
            item.setForeground(Qt.GlobalColor.gray)
            self.scan_list.addItem(item)
            return

        for s in scans:
            card = ScanCard(s)
            card.clicked.connect(lambda sid: self._select_scan_by_id(sid))
            item = QListWidgetItem()
            item.setSizeHint(card.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, s.get("scan_id"))
            self.scan_list.addItem(item)
            self.scan_list.setItemWidget(item, card)

    def _select_scan_by_id(self, scan_id):
        for i in range(self.scan_list.count()):
            item = self.scan_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == scan_id:
                self.scan_list.setCurrentItem(item)
                break

    def _current_scan_id(self):
        item = self.scan_list.currentItem()
        if not item:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def load_selected(self):
        sid = self._current_scan_id()
        if not sid:
            QMessageBox.warning(self, "!", "কোনো scan select করো")
            return

        scan = self.scanner.get_scan(sid)
        if not scan:
            return

        self.f_brand.setText(scan.get("brand", ""))
        self.f_model.setText(scan.get("model", ""))
        self.f_chipset.setText(scan.get("chipset", ""))
        self.f_phone_serial.setText(scan.get("phone_serial", ""))
        self.f_technician.setText(scan.get("technician", ""))
        self.f_client_name.setText(scan.get("client_name", ""))
        self.f_client_phone.setText(scan.get("client_phone", ""))

        try:
            readings = scan.get("readings", {})
            if isinstance(readings, str):
                import json
                readings = json.loads(readings)
            for rail, inp in self.rail_inputs.items():
                if rail in readings:
                    inp.setText(str(readings[rail]))
        except Exception:
            pass

        self.f_current.setText(str(scan.get("current_draw", 0)))
        self.f_diagnosis.setText(scan.get("diagnosis", ""))
        self.f_notes.setPlainText(scan.get("notes", ""))

        self._log(f"📂 Loaded: {sid}")

    def compare_selected(self):
        sid = self._current_scan_id()
        if not sid:
            QMessageBox.warning(self, "!", "Select করো")
            return

        result = self.comparator.compare_with_reference(sid)

        if not result.get("ok"):
            QMessageBox.warning(self, "!", result.get("message", ""))
            return

        if result.get("is_reference"):
            self._log(f"ℹ️ {sid} is reference")
            QMessageBox.information(self, "Info", "This is the reference board.")
            return

        self._log("─" * 40)
        self._log(f"⚖️ Compare: {result.get('reference_scan_id')} ↔ {sid}")
        self._log(f"   Match: {result.get('match_score')}%")
        self._log(f"   {result['summary']['verdict']}")

        for d in result.get("deviations", []):
            self._log(
                f"   ⚠️ {d['rail']}: "
                f"A={d['a']} B={d['b']} "
                f"({d['diff_pct']}% {d['severity']})"
            )

    def set_reference(self):
        sid = self._current_scan_id()
        if not sid:
            QMessageBox.warning(self, "!", "Select করো")
            return

        ans = QMessageBox.question(
            self, "⭐ Reference",
            f"'{sid}' কে reference mark করবো?"
        )
        if ans != QMessageBox.StandardButton.Yes:
            return

        if self.comparator.mark_as_reference(sid):
            QMessageBox.information(self, "✅", "Reference marked")
            self._refresh()

    def delete_selected(self):
        sid = self._current_scan_id()
        if not sid:
            return

        ans = QMessageBox.question(
            self, "🗑️ Delete",
            f"'{sid}' delete করবো?"
        )
        if ans != QMessageBox.StandardButton.Yes:
            return

        if self.scanner.delete_scan(sid):
            self._log(f"🗑️ Deleted: {sid}")
            self._refresh() 