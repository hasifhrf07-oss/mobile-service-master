"""Manual Diagnose Tab"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QTextEdit, QLabel, QComboBox,
                              QGroupBox, QMessageBox, QLineEdit, QFormLayout,
                              QScrollArea)
from PyQt6.QtCore import Qt
from core.analyzer import Analyzer
from core.consent import ConsentManager


SYMPTOM_OPTIONS = {
    "boot": ["ok", "loop", "dead", "fastboot_only"],
    "display": ["ok", "broken", "flicker", "black", "white"],
    "charging": ["ok", "no", "slow", "hot"],
    "touch": ["ok", "no", "partial"],
    "network": ["ok", "no", "weak"],
    "speaker": ["ok", "no", "crackle"],
    "camera": ["ok", "no", "blur"],
    "battery": ["ok", "drain", "swell"],
    "water": ["no", "yes"],
    "lock_screen": ["none", "frp", "icloud", "mi", "pattern"],
}

SYMPTOM_LABELS = {
    "boot": "Boot", "display": "Display", "charging": "Charging",
    "touch": "Touch", "network": "Network", "speaker": "Speaker",
    "camera": "Camera", "battery": "Battery", "water": "Water damage",
    "lock_screen": "Lock screen",
}


class DiagnoseTab(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.analyzer = Analyzer()
        self.consent = ConsentManager()
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

        title = QLabel("🧪 Manual ডায়াগনোস")
        title.setObjectName("title")
        layout.addWidget(title)

        # Client
        client_group = QGroupBox("👤 ক্লায়েন্ট তথ্য")
        cform = QFormLayout()
        cform.setSpacing(6)
        self.f_client_name = QLineEdit()
        self.f_client_name.setPlaceholderText("নাম")
        self.f_client_phone = QLineEdit()
        self.f_client_phone.setPlaceholderText("017xxxxxxxx")
        cform.addRow("নাম", self.f_client_name)
        cform.addRow("ফোন", self.f_client_phone)
        client_group.setLayout(cform)
        layout.addWidget(client_group)

        # Symptoms
        sym_group = QGroupBox("🔍 সমস্যা নির্বাচন")
        sym_form = QFormLayout()
        sym_form.setSpacing(4)
        self.combos = {}
        for key, opts in SYMPTOM_OPTIONS.items():
            cb = QComboBox()
            cb.addItems(opts)
            self.combos[key] = cb
            sym_form.addRow(SYMPTOM_LABELS[key], cb)
        sym_group.setLayout(sym_form)
        layout.addWidget(sym_group)

        # Buttons
        btn_row = QHBoxLayout()
        self.btn_diag = QPushButton("🧪 ডায়াগনোস চালাও")
        self.btn_diag.setObjectName("primary")
        self.btn_diag.clicked.connect(self.run_diagnose)
        btn_row.addWidget(self.btn_diag)

        self.btn_clear = QPushButton("🗑️ Reset")
        self.btn_clear.clicked.connect(self.reset_all)
        btn_row.addWidget(self.btn_clear)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Output
        out_group = QGroupBox("📋 ফলাফল")
        out_layout = QVBoxLayout()
        out_layout.setContentsMargins(6, 6, 6, 6)
        self.out = QTextEdit()
        self.out.setReadOnly(True)
        self.out.setMinimumHeight(180)
        self.out.setMaximumHeight(280)
        out_layout.addWidget(self.out)
        out_group.setLayout(out_layout)
        layout.addWidget(out_group)

        layout.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)

        self.setLayout(outer)

    def run_diagnose(self):
        info = self.app_state.get("device_info")
        if not info:
            QMessageBox.warning(self, "⚠️",
                                "আগে 🔌 Detect tab-এ ফোন connect করো।")
            return

        symptoms = {k: cb.currentText() for k, cb in self.combos.items()}
        diag = self.analyzer.analyze(info, symptoms)

        self.out.clear()
        self.out.append("=" * 50)
        self.out.append(f"📋 ধরন   : {diag.issue_type.value.upper()}")
        self.out.append(f"📝 সারমর্ম : {diag.summary}")
        self.out.append("=" * 50)

        if diag.evidence:
            self.out.append("\n📌 প্রমাণ:")
            for e in diag.evidence:
                self.out.append(f"   • {e}")

        if diag.sw_actions:
            self.out.append("\n💾 সফটওয়্যার অ্যাকশন:")
            for a in diag.sw_actions:
                self.out.append(f"   → {a}")

        if diag.hw_guide:
            self.out.append("\n🔧 হার্ডওয়্যার গাইড:")
            for g in diag.hw_guide:
                self.out.append(f"   • {g}")

        if diag.issue_type.value == "account_lock":
            self.out.append("")
            self.out.append("🚫 এই অ্যাপে bypass নেই।")
            return

        if diag.requires_consent:
            msg = QMessageBox(self)
            msg.setWindowTitle("⚠️ অনুমতি প্রয়োজন")
            msg.setIcon(QMessageBox.Icon.Question)
            msg.setText(f"📱 {info.brand} {info.model}")
            msg.setInformativeText(
                f"সমস্যা: {diag.summary}\n\nসমাধান করবো?"
            )
            msg.setStandardButtons(
                QMessageBox.StandardButton.Ok |
                QMessageBox.StandardButton.Cancel
            )
            granted = msg.exec() == QMessageBox.StandardButton.Ok

            self.consent.request_programmatic(
                action="Manual software service",
                details=f"{info.brand} {info.model} — {diag.summary}",
                client_name=self.f_client_name.text().strip(),
                client_phone=self.f_client_phone.text().strip(),
                granted=granted
            )

            self.out.append("")
            if granted:
                self.out.append("✅ Consent GRANTED — logged")
            else:
                self.out.append("❌ Consent DENIED — logged")

    def reset_all(self):
        for cb in self.combos.values():
            cb.setCurrentIndex(0)
        self.out.clear()
        self.f_client_name.clear()
        self.f_client_phone.clear()