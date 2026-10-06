"""Detect Tab — with ADB Manager + Client Guide"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QTextEdit, QLabel, QGroupBox,
                              QMessageBox, QProgressBar, QScrollArea)
from PyQt6.QtCore import Qt, QTimer
from core.multi_detect import MultiDetector
from core.detector import Detector
from core.adb_manager import ADBManager
from core.clone_checker import CloneChecker
from core.analyzer import Analyzer
from core.auto_solver import AutoSolver
from core.consent import ConsentManager
from core.scanner.boardview_manager import BoardViewManager
from ui.dialogs.client_guide import ClientGuideDialog, WaitingDialog
from data import db
import time


class DetectTab(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.multi = MultiDetector()
        self.detector = Detector()
        self.adb = ADBManager()
        self.checker = CloneChecker()
        self.analyzer = Analyzer()
        self.consent = ConsentManager()
        self.solver = AutoSolver(log_callback=self._log_message)
        self.boardview = BoardViewManager()
        self.waiting_dialog = None
        self.wait_timer = None
        self._wait_start = 0
        self._build()

    def _build(self):
        outer = QVBoxLayout()
        outer.setContentsMargins(4, 4, 4, 4)
        outer.setSpacing(4)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        title = QLabel("🔌 ফোন Connect করো (ADB Mode)")
        title.setObjectName("title")
        layout.addWidget(title)

        self.lbl_status = QLabel("👀 Monitoring... USB cable লাগাও")
        self.lbl_status.setStyleSheet(
            "background-color: #181825; color: #f9e2af; "
            "padding: 10px; border-radius: 5px; font-size: 13px;"
        )
        self.lbl_status.setWordWrap(True)
        layout.addWidget(self.lbl_status)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        self.btn_guide = QPushButton("📋 Client Guide")
        self.btn_guide.clicked.connect(self.show_client_guide)
        btn_row.addWidget(self.btn_guide)

        self.btn_auto = QPushButton("🔄 Auto-Detect চালু করো")
        self.btn_auto.setObjectName("primary")
        self.btn_auto.clicked.connect(self.start_auto)
        btn_row.addWidget(self.btn_auto)

        self.btn_detect = QPushButton("🔍 এখনই Detect")
        self.btn_detect.clicked.connect(self.manual_detect)
        btn_row.addWidget(self.btn_detect)

        self.btn_restart_adb = QPushButton("🔄 Restart ADB")
        self.btn_restart_adb.clicked.connect(self.restart_adb)
        btn_row.addWidget(self.btn_restart_adb)

        self.btn_stop = QPushButton("⏹️ Stop")
        self.btn_stop.clicked.connect(self.stop_auto)
        btn_row.addWidget(self.btn_stop)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Device info
        info_group = QGroupBox("📱 ডিভাইস তথ্য")
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(6, 6, 6, 6)
        self.out_info = QTextEdit()
        self.out_info.setReadOnly(True)
        self.out_info.setMinimumHeight(180)
        info_layout.addWidget(self.out_info)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # BoardView
        self.bv_group = QGroupBox("📐 BoardView / Schematic")
        bv_layout = QHBoxLayout()
        bv_layout.setContentsMargins(6, 6, 6, 6)
        self.lbl_bv = QLabel("⏳ Detect হলে BoardView check হবে...")
        self.lbl_bv.setStyleSheet("color: #a6adc8; font-size: 11px;")
        bv_layout.addWidget(self.lbl_bv, 1)

        self.btn_open_bv = QPushButton("📐 Open BoardView")
        self.btn_open_bv.clicked.connect(self.open_boardview)
        self.btn_open_bv.setEnabled(False)
        bv_layout.addWidget(self.btn_open_bv)

        self.btn_open_sch = QPushButton("📄 Open Schematic")
        self.btn_open_sch.clicked.connect(self.open_schematic)
        self.btn_open_sch.setEnabled(False)
        bv_layout.addWidget(self.btn_open_sch)

        self.bv_group.setLayout(bv_layout)
        layout.addWidget(self.bv_group)

        # Detection Mode
        mode_group = QGroupBox("🔍 Detection Mode")
        mode_layout = QVBoxLayout()
        mode_layout.setContentsMargins(6, 6, 6, 6)
        self.out_mode = QTextEdit()
        self.out_mode.setReadOnly(True)
        self.out_mode.setMinimumHeight(100)
        self.out_mode.setMaximumHeight(160)
        mode_layout.addWidget(self.out_mode)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # Diagnosis
        diag_group = QGroupBox("🧪 সমস্যা বিশ্লেষণ")
        diag_layout = QVBoxLayout()
        diag_layout.setContentsMargins(6, 6, 6, 6)
        self.out_diag = QTextEdit()
        self.out_diag.setReadOnly(True)
        self.out_diag.setMinimumHeight(100)
        self.out_diag.setMaximumHeight(180)
        diag_layout.addWidget(self.out_diag)
        diag_group.setLayout(diag_layout)
        layout.addWidget(diag_group)

        # Solve
        solve_group = QGroupBox("💊 Auto Solve / Hardware Guide")
        solve_layout = QVBoxLayout()
        solve_layout.setContentsMargins(6, 6, 6, 6)
        self.out_solve = QTextEdit()
        self.out_solve.setReadOnly(True)
        self.out_solve.setMinimumHeight(120)
        self.out_solve.setMaximumHeight(220)
        solve_layout.addWidget(self.out_solve)
        solve_group.setLayout(solve_layout)
        layout.addWidget(solve_group)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setMaximumHeight(18)
        layout.addWidget(self.progress)

        layout.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)

        self.setLayout(outer)

        self.detection_timer = QTimer()
        self.detection_timer.timeout.connect(self.auto_check)

    # ═════════════════════════════════════════════════════════
    # Logging & Status
    # ═════════════════════════════════════════════════════════

    def _log_message(self, msg):
        self.out_solve.append(msg)
        sb = self.out_solve.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _set_status(self, msg, color="#f9e2af"):
        self.lbl_status.setText(msg)
        self.lbl_status.setStyleSheet(
            f"background-color: #181825; color: {color}; "
            "padding: 10px; border-radius: 5px; font-size: 13px;"
        )

    # ═════════════════════════════════════════════════════════
    # Client Guide
    # ═════════════════════════════════════════════════════════

    def show_client_guide(self):
        brand = ""
        try:
            info = self.detector.info
            brand = info.brand or info.model or ""
        except Exception:
            pass

        dlg = ClientGuideDialog(self, brand=brand)
        if dlg.exec():
            self._log_message("✅ Client ready — Detect শুরু করছি")
            self.start_auto()

    # ═════════════════════════════════════════════════════════
    # ADB Restart
    # ═════════════════════════════════════════════════════════

    def restart_adb(self):
        self._set_status("🔄 ADB Restart হচ্ছে...", "#f9e2af")
        self.adb.restart_server()
        self._set_status("✅ ADB Restarted", "#a6e3a1")

    # ═════════════════════════════════════════════════════════
    # Auto / Manual Detect
    # ═════════════════════════════════════════════════════════

    def start_auto(self):
        self._set_status(
            "👀 Auto-Detect চালু — USB cable লাগাও...", "#f9e2af"
        )
        self.detection_timer.start(2000)

    def stop_auto(self):
        self.detection_timer.stop()
        self._set_status("⏹️ Auto-Detect বন্ধ", "#a6adc8")

    def auto_check(self):
        if not self.detection_timer.isActive():
            return

        result = self.adb.check_connection()
        state = result["state"]

        if state == "device":
            self.detection_timer.stop()
            self._set_status("✅ ফোন Authorized — Connected!", "#a6e3a1")
            self._log_message(f"✅ ADB Connected: {result['primary']['serial']}")
            self._process_adb_device()

        elif state == "unauthorized":
            self.detection_timer.stop()
            self._set_status(
                "⚠️ ফোনে 'Allow USB debugging' popup আসছে...", "#f9e2af"
            )
            self._show_waiting_dialog(result["primary"])

        elif state == "no_device":
            pass

        elif state == "multiple":
            self.detection_timer.stop()
            self._set_status(
                "⚠️ Multiple devices detected — একটি মাত্র connect করো",
                "#f38ba8"
            )

    def manual_detect(self):
        self._set_status("🔄 Manual detect চলছে...", "#f9e2af")
        self.clear_all()

        result = self.adb.check_connection()
        state = result["state"]

        if state == "device":
            self._set_status("✅ Authorized — Connected!", "#a6e3a1")
            self._process_adb_device()
            return

        if state == "unauthorized":
            self._set_status(
                "⚠️ Popup-এ Allow করো", "#f9e2af"
            )
            self._show_waiting_dialog(result["primary"])
            return

        # Try MultiDetector (EDL/MTK/iPhone)
        multi_result = self.multi.auto_detect_all()
        self._show_detection_result(multi_result)

        if multi_result["mode"] != "none":
            self._process_detected(multi_result)
        else:
            self._set_status("❌ কোনো device পাওয়া যায়নি", "#f38ba8")
            self.out_info.clear()
            self.out_info.append("❌ Phone detect হয়নি")
            self.out_info.append("")
            self.out_info.append("👉 'Client Guide' button ক্লিক করো")
            self.out_info.append("")
            self.out_info.append("অথবা manually:")
            self.out_info.append("  ১. Developer Options ON")
            self.out_info.append("  ২. USB Debugging ON")
            self.out_info.append("  ৩. USB cable connect")
            self.out_info.append("  ৪. Popup-এ Allow")

    # ═════════════════════════════════════════════════════════
    # Waiting Dialog
    # ═════════════════════════════════════════════════════════

    def _show_waiting_dialog(self, device_info):
        self.waiting_dialog = WaitingDialog(self)

        self.wait_timer = QTimer()
        self.wait_timer.timeout.connect(self._poll_authorization)
        self.wait_timer.start(1500)
        self._wait_start = time.time()

        result = self.waiting_dialog.exec()
        self.wait_timer.stop()

        if result:
            self._set_status("✅ Authorized — Connected!", "#a6e3a1")
            self._log_message("✅ ADB authorized successfully")
            self.adb.mark_authorized(device_info.get("serial", ""))
            self._process_adb_device()

    def _poll_authorization(self):
        result = self.adb.check_connection()
        elapsed = int(time.time() - self._wait_start)

        if self.waiting_dialog:
            self.waiting_dialog.update_status(result["state"], elapsed)

    # ═════════════════════════════════════════════════════════
    # Process Device
    # ═════════════════════════════════════════════════════════

    def _process_adb_device(self):
        if not self.detector.detect_adb():
            self._log_message("❌ detect_adb failed")
            return

        info = self.detector.info
        self.adb.mark_authorized(info.serial, info.brand, info.model)

        # USB Deep Read
        try:
            from core.usb_reader import USBReader
            reader = USBReader()
            report = reader.format_report()
            self.out_info.clear()
            self.out_info.append(report)
            self.app_state["usb_info"] = reader.info
        except Exception as e:
            self.out_info.clear()
            self.out_info.append(f"❌ USB read fail: {e}")
            self.out_info.append("")
            self.out_info.append(f"📱 Brand: {info.brand}")
            self.out_info.append(f"📱 Model: {info.model}")

        self._check_boardview(info)

        reasons = self.checker.analyze(info)
        info.is_clone = self.checker.is_clone(reasons)
        info.clone_reasons = reasons

        self.out_diag.clear()
        symptoms = self._auto_detect_symptoms(info)
        diag = self.analyzer.analyze(info, symptoms)
        self.progress.setValue(70)

        self.out_diag.append(f"📋 ধরন   : {diag.issue_type.value.upper()}")
        self.out_diag.append(f"📝 সারমর্ম : {diag.summary}")

        if diag.hw_guide:
            self.out_diag.append("")
            self.out_diag.append("🔧 Hardware Guide:")
            for g in diag.hw_guide:
                self.out_diag.append(f"   • {g}")

        self.app_state["device_info"] = info
        self.app_state["diagnosis"] = diag.to_dict()
        self.app_state["symptoms"] = symptoms

        it = diag.issue_type.value
        self.out_solve.clear()

        if it == "software":
            self.out_solve.append("💊 Software Problem — Auto Solve!")
            self._ask_and_solve(info, diag, symptoms)
        elif it == "hardware":
            self.out_solve.append("🔧 Hardware Problem সনাক্ত")
            self.out_solve.append("")
            for g in diag.hw_guide:
                self.out_solve.append(f"  ➤ {g}")
            self.progress.setValue(100)
        elif it == "account_lock":
            self.out_solve.append("🚫 Account Lock — Owner verify required")
            self.progress.setValue(100)

    def _show_detection_result(self, result):
        self.out_mode.clear()
        self.out_mode.append("=" * 50)
        self.out_mode.append(f"📡 Mode      : {result['mode'].upper()}")
        self.out_mode.append(f"📱 Brand     : {result.get('brand', 'N/A')}")
        self.out_mode.append(f"📱 Model     : {result.get('model', 'N/A')}")
        self.out_mode.append(f"⚙️  Chipset   : {result.get('chipset', 'N/A')}")
        self.out_mode.append(f"🔢 Serial    : {result.get('serial', 'N/A')}")
        self.out_mode.append(f"🎯 Confidence: {result.get('confidence', 0)}%")
        self.out_mode.append("")
        self.out_mode.append(result.get("message", ""))
        self.out_mode.append("=" * 50)

    def _process_detected(self, result):
        mode = result["mode"]

        if mode == "fastboot":
            self._set_status("⚙️ Fastboot Mode", "#fab387")
        elif mode == "edl":
            self._set_status("🔴 EDL 9008 — Qualcomm Dead Boot", "#f38ba8")
        elif mode == "mtk":
            self._set_status("🔴 MTK BROM — MediaTek Dead Boot", "#f38ba8")
        elif mode == "iphone":
            self._set_status("🍎 iPhone detected", "#89b4fa")

    def _check_boardview(self, info):
        try:
            bv = self.boardview.find(info.brand, info.model)
            sch = self.boardview.find_schematic(info.brand, info.model)

            if bv and bv.get("file_path"):
                self.app_state["boardview_path"] = bv["file_path"]
                self.btn_open_bv.setEnabled(True)
                bv_txt = f"📐 BoardView: ✅ {bv.get('file_type', '?').upper()}"
            else:
                self.app_state["boardview_path"] = None
                self.btn_open_bv.setEnabled(False)
                bv_txt = "📐 BoardView: ❌ নেই"

            if sch and sch.get("file_path"):
                self.app_state["schematic_path"] = sch["file_path"]
                self.btn_open_sch.setEnabled(True)
                sch_txt = f"📄 Schematic: ✅ {sch.get('file_type', '?').upper()}"
            else:
                self.app_state["schematic_path"] = None
                self.btn_open_sch.setEnabled(False)
                sch_txt = "📄 Schematic: ❌ নেই"

            self.lbl_bv.setText(f"{bv_txt}    |    {sch_txt}")
        except Exception as e:
            self.lbl_bv.setText(f"⚠️ Check fail: {e}")

    def open_boardview(self):
        path = self.app_state.get("boardview_path")
        if path:
            self.boardview.open_file(path)

    def open_schematic(self):
        path = self.app_state.get("schematic_path")
        if path:
            self.boardview.open_file(path)

    def _auto_detect_symptoms(self, info):
        symptoms = {
            "boot": "ok", "display": "ok", "charging": "ok",
            "touch": "ok", "network": "ok", "speaker": "ok",
            "camera": "ok", "battery": "ok", "water": "no",
            "lock_screen": "none",
        }
        battery = self.detector.get_battery_level()
        if 0 <= battery < 15:
            symptoms["battery"] = "drain"
        return symptoms

    def _ask_and_solve(self, info, diag, symptoms):
        msg = QMessageBox(self)
        msg.setWindowTitle("⚠️ অনুমতি প্রয়োজন")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(f"📱 {info.brand} {info.model}")
        msg.setInformativeText(
            f"সমস্যা: {diag.summary}\n\nAuto software solve করবো?"
        )
        msg.setStandardButtons(
            QMessageBox.StandardButton.Ok |
            QMessageBox.StandardButton.Cancel
        )
        ok_btn = msg.button(QMessageBox.StandardButton.Ok)
        ok_btn.setText("✅ OK — Auto Solve")

        granted = msg.exec() == QMessageBox.StandardButton.Ok

        self.consent.request_programmatic(
            action="Auto Software Solve",
            details=f"{info.brand} {info.model} — {diag.summary}",
            client_name=self.app_state.get("client_name", ""),
            client_phone=self.app_state.get("client_phone", ""),
            granted=granted
        )

        if not granted:
            self.out_solve.append("❌ অনুমতি দেয়নি — কাজ হয়নি।")
            self.progress.setValue(100)
            return

        self.out_solve.append("✅ Consent granted — Starting...")
        self.progress.setValue(80)

        diag_dict = {"issue_type": diag.issue_type.value, "symptoms": symptoms}
        result = self.solver.auto_solve(diag_dict)

        self.progress.setValue(95)
        self.out_solve.append("")
        self.out_solve.append("=" * 50)

        if result["success"]:
            self.out_solve.append("🎉 SUCCESS! Software problem সমাধান হয়েছে!")
            self.out_solve.append(f"📝 {result['message']}")
            self._set_status("✅ Software Problem Solved!", "#a6e3a1")
            self.progress.setValue(100)
        else:
            self.out_solve.append("❌ Auto-solve সফল হয়নি")
            self.out_solve.append(f"📝 {result['message']}")
            self._set_status("❌ Solve Fail — Manual Check", "#f38ba8")
            self.progress.setValue(100)

    def clear_all(self):
        self.out_info.clear()
        self.out_mode.clear()
        self.out_diag.clear()
        self.out_solve.clear()
        self.progress.setValue(0)
        self.lbl_bv.setText("⏳ Detect হলে BoardView check হবে...")
        self.btn_open_bv.setEnabled(False)
        self.btn_open_sch.setEnabled(False)
        self.app_state["device_info"] = None
        self.app_state["diagnosis"] = None
        self.app_state["boardview_path"] = None
        self.app_state["schematic_path"] = None