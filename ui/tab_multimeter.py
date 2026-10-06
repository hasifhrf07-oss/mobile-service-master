"""Manual Multimeter Tab"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QLineEdit, QComboBox,
                              QGroupBox, QFormLayout, QScrollArea,
                              QMessageBox, QTextEdit, QFrame)
from PyQt6.QtCore import Qt
from core.multimeter.reading_analyzer import ReadingAnalyzer
from core.multimeter.rail_database import (
    all_rails, get_rail_info, COMMON_RAILS
)
from core.scanner.board_scanner import BoardScanner
from ui.scanner_widgets import StatBox


class MultimeterTab(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.analyzer = ReadingAnalyzer()
        self.scanner = BoardScanner()
        self.session_readings = {}
        self._build()

    def _build(self):
        outer = QVBoxLayout()
        outer.setContentsMargins(6, 4, 6, 4)
        outer.setSpacing(6)

        title = QLabel("📏 Multimeter — Manual Mode")
        title.setObjectName("title")
        outer.addWidget(title)

        subtitle = QLabel(
            "Multimeter-এ reading দেখো → এইখানে type করো → অ্যাপ analysis দেবে"
        )
        subtitle.setObjectName("subtitle")
        outer.addWidget(subtitle)

        # ─── Info bar ───
        info_bar = QFrame()
        info_bar.setStyleSheet(
            "QFrame {"
            "  background: #181825;"
            "  border-left: 3px solid #89b4fa;"
            "  border-radius: 4px;"
            "  padding: 6px;"
            "}"
        )
        info_layout = QHBoxLayout(info_bar)
        info_layout.setContentsMargins(8, 4, 8, 4)

        self.lbl_device = QLabel("📱 Model: (detect from Detect tab)")
        self.lbl_device.setStyleSheet(
            "color: #cdd6f4; font-size: 12px;"
        )
        info_layout.addWidget(self.lbl_device)
        info_layout.addStretch()

        btn_clear = QPushButton("🗑️ Clear Session")
        btn_clear.clicked.connect(self.clear_session)
        info_layout.addWidget(btn_clear)

        outer.addWidget(info_bar)

        # ─── Main splitter: Left = input, Right = analysis ───
        main_row = QHBoxLayout()
        main_row.setSpacing(6)

        # ══════════════════════════════════════════════════
        # LEFT: Input form
        # ══════════════════════════════════════════════════
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        # Rail selector
        rail_group = QGroupBox("⚙️ Rail Selection")
        rail_form = QFormLayout()
        rail_form.setSpacing(5)

        self.f_rail = QComboBox()
        for key, info in all_rails():
            self.f_rail.addItem(
                f"{info['label']}  ({info['min']}-{info['max']}V)",
                key
            )
        self.f_rail.currentIndexChanged.connect(self._on_rail_change)
        rail_form.addRow("Rail:", self.f_rail)

        self.lbl_expected = QLabel("")
        self.lbl_expected.setStyleSheet(
            "color: #89b4fa; font-size: 11px; padding: 2px;"
        )
        rail_form.addRow("Expected:", self.lbl_expected)

        self.lbl_test_point = QLabel("")
        self.lbl_test_point.setStyleSheet(
            "color: #a6adc8; font-size: 11px; padding: 2px;"
        )
        self.lbl_test_point.setWordWrap(True)
        rail_form.addRow("Test Point:", self.lbl_test_point)

        rail_group.setLayout(rail_form)
        left_layout.addWidget(rail_group)

        # Value input
        value_group = QGroupBox("📏 Reading Input")
        value_form = QFormLayout()
        value_form.setSpacing(6)

        self.f_value = QLineEdit()
        self.f_value.setPlaceholderText("3.78")
        self.f_value.setMinimumHeight(32)
        self.f_value.returnPressed.connect(self.check_reading)
        value_form.addRow("Voltage (V):", self.f_value)

        value_group.setLayout(value_form)
        left_layout.addWidget(value_group)

        # Buttons
        btn_row = QHBoxLayout()
        btn_check = QPushButton("✅ Check Reading")
        btn_check.setObjectName("primary")
        btn_check.setMinimumHeight(38)
        btn_check.clicked.connect(self.check_reading)
        btn_row.addWidget(btn_check, 2)

        btn_reset = QPushButton("🔄 Reset")
        btn_reset.setMinimumHeight(38)
        btn_reset.clicked.connect(lambda: self.f_value.clear())
        btn_row.addWidget(btn_reset, 1)

        left_layout.addLayout(btn_row)

        # Quick Select Presets
        preset_group = QGroupBox("⚡ Quick Rails")
        preset_layout = QVBoxLayout()
        preset_layout.setContentsMargins(6, 6, 6, 6)
        preset_layout.setSpacing(3)

        for key, info in all_rails()[:8]:
            btn = QPushButton(f"{info['label']}  ({info['min']}-{info['max']}V)")
            btn.setStyleSheet(
                "text-align: left; padding: 5px 8px; font-size: 11px;"
            )
            btn.clicked.connect(lambda _, k=key: self._quick_select(k))
            preset_layout.addWidget(btn)

        preset_group.setLayout(preset_layout)
        left_layout.addWidget(preset_group)

        left_layout.addStretch()

        # ══════════════════════════════════════════════════
        # RIGHT: Analysis + History
        # ══════════════════════════════════════════════════
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        # Current Analysis
        analysis_group = QGroupBox("📊 Analysis Result")
        analysis_layout = QVBoxLayout()
        analysis_layout.setContentsMargins(6, 6, 6, 6)

        self.out_analysis = QTextEdit()
        self.out_analysis.setReadOnly(True)
        self.out_analysis.setMinimumHeight(140)
        analysis_layout.addWidget(self.out_analysis)

        analysis_group.setLayout(analysis_layout)
        right_layout.addWidget(analysis_group)

        # Summary
        summary_group = QGroupBox("📈 Session Summary")
        summary_layout = QVBoxLayout()
        summary_layout.setContentsMargins(6, 6, 6, 6)

        self.out_summary = QTextEdit()
        self.out_summary.setReadOnly(True)
        self.out_summary.setMinimumHeight(180)
        summary_layout.addWidget(self.out_summary)

        summary_group.setLayout(summary_layout)
        right_layout.addWidget(summary_group, 1)

        # Save button
        save_btn = QPushButton("💾 Save to Board Scanner")
        save_btn.setObjectName("primary")
        save_btn.setMinimumHeight(38)
        save_btn.clicked.connect(self.save_to_scanner)
        right_layout.addWidget(save_btn)

        # Add to main row
        main_row.addWidget(left, 1)
        main_row.addWidget(right, 1)
        outer.addLayout(main_row, 1)

        self.setLayout(outer)

        # Initial state
        self._on_rail_change()

    # ═════════════════════════════════════════════════════════

    def _on_rail_change(self):
        rail = self.f_rail.currentData()
        info = get_rail_info(rail)
        if info:
            self.lbl_expected.setText(
                f"{info['min']} - {info['max']}V  (typical: {info.get('typical', '?')}V)"
            )
            self.lbl_test_point.setText(
                f"{info.get('test_point', 'N/A')}"
            )
        self.f_value.setFocus()

    def _quick_select(self, rail_key):
        """Preset button → set rail combo"""
        for i in range(self.f_rail.count()):
            if self.f_rail.itemData(i) == rail_key:
                self.f_rail.setCurrentIndex(i)
                break
        self.f_value.setFocus()

    def check_reading(self):
        rail = self.f_rail.currentData()
        raw = self.f_value.text().strip()

        if not raw:
            QMessageBox.warning(self, "!", "Reading type করো")
            return

        try:
            val = float(raw)
        except ValueError:
            QMessageBox.warning(self, "!", f"Invalid number: {raw}")
            return

        # Analyze
        result = self.analyzer.analyze_voltage(rail, val)
        if not result.get("ok"):
            QMessageBox.warning(self, "!", result.get("message", ""))
            return

        # Save to session
        self.session_readings[rail] = val

        # Display
        self._display_reading(result)

        # Clear value
        self.f_value.clear()

        # Refresh summary
        self._refresh_summary()

        # Auto-suggest next rail
        self._auto_suggest_next()

        # Log to app_state
        self.app_state["multimeter_session"] = dict(self.session_readings)

    def _display_reading(self, r):
        color = r["color"]

        self.out_analysis.clear()
        self.out_analysis.append("═" * 50)
        self.out_analysis.append(f"📊 {r['label']}")
        self.out_analysis.append("═" * 50)
        self.out_analysis.append(f"📏 Reading  : {r['value']} V")
        self.out_analysis.append(f"📐 Expected : {r['expected']}")
        self.out_analysis.append(f"🎯 Typical  : {r.get('typical', '?')} V")
        self.out_analysis.append("")

        # Message with color (rich text)
        self.out_analysis.append(r["message"])
        self.out_analysis.append("")

        if r["hint"]:
            self.out_analysis.append(f"🔧 Hint:")
            self.out_analysis.append(f"   {r['hint']}")
            self.out_analysis.append("")

        self.out_analysis.append(f"🔌 Source     : {r.get('source', 'N/A')}")
        self.out_analysis.append(f"📍 Test Point : {r.get('test_point', 'N/A')}")
        self.out_analysis.append("═" * 50)

    def _refresh_summary(self):
        if not self.session_readings:
            self.out_summary.clear()
            self.out_summary.append("📭 এখনো কোনো reading check করা হয়নি")
            return

        batch = self.analyzer.analyze_batch(self.session_readings)

        self.out_summary.clear()
        self.out_summary.append("═" * 50)
        self.out_summary.append("📈 Session Summary")
        self.out_summary.append("═" * 50)
        self.out_summary.append("")

        for r in batch["readings"]:
            marker = "✅" if r["severity"] == "OK" else ("⚠️" if r["severity"] == "WARN" else "❌")
            self.out_summary.append(
                f"{marker} {r['label']:<25}  {r['value']}V   (exp: {r['expected']})"
            )

        self.out_summary.append("")
        self.out_summary.append("─" * 50)

        s = batch["summary"]
        self.out_summary.append(f"✅ OK       : {s['ok']}")
        self.out_summary.append(f"⚠️ Warning  : {s['warning']}")
        self.out_summary.append(f"❌ Critical : {s['critical']}")
        self.out_summary.append("")
        self.out_summary.append(s["verdict"])
        self.out_summary.append("═" * 50)

    def _auto_suggest_next(self):
        checked = list(self.session_readings.keys())
        nxt = self.analyzer.suggest_next_rail(checked)
        if nxt:
            self._quick_select(nxt["rail"])

    def clear_session(self):
        ans = QMessageBox.question(
            self, "🗑️ Clear Session",
            "সব readings মুছবো?"
        )
        if ans != QMessageBox.StandardButton.Yes:
            return

        self.session_readings.clear()
        self.out_analysis.clear()
        self._refresh_summary()
        self.f_value.clear()

    def save_to_scanner(self):
        """Session readings → Board Scanner-এ save"""
        if not self.session_readings:
            QMessageBox.warning(self, "!", "কোনো reading নেই")
            return

        # Try to get device info from app state
        info = self.app_state.get("device_info")

        if not info:
            QMessageBox.warning(
                self, "!",
                "আগে Detect tab-এ ফোন connect করো,\n"
                "অথবা manual entry করো"
            )
            return

        # Prepare diagnosis text
        batch = self.analyzer.analyze_batch(self.session_readings)
        verdict = batch["summary"]["verdict"]

        # Save via scanner
        result = self.scanner.capture_state(
            brand=info.brand,
            model=info.model,
            chipset=info.chipset,
            phone_serial=info.serial,
            readings=self.session_readings,
            diagnosis=verdict,
            notes="Multimeter session — manual input",
        )

        if result["ok"]:
            QMessageBox.information(
                self, "✅ Saved",
                f"Scan ID: {result['scan_id']}"
            )
        else:
            QMessageBox.warning(self, "❌", result.get("message", ""))