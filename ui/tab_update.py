"""Update Tab — Auto Confirm on Success"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QTextEdit, QLabel,
                              QLineEdit, QGroupBox, QMessageBox,
                              QScrollArea)
from PyQt6.QtCore import Qt
from core.updater import check_and_update, get_update_url, set_update_url


class UpdateTab(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
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

        title = QLabel("🔄 অটো-আপডেট")
        title.setObjectName("title")
        layout.addWidget(title)

        # URL Group
        url_group = QGroupBox("🔗 Update URL")
        url_layout = QVBoxLayout()
        url_layout.setContentsMargins(6, 6, 6, 6)
        url_layout.setSpacing(4)

        row = QHBoxLayout()
        self.f_url = QLineEdit()
        self.f_url.setPlaceholderText("https://raw.githubusercontent.com/...")
        self.f_url.setText(get_update_url())
        row.addWidget(self.f_url, 1)

        btn_save = QPushButton("💾 Save")
        btn_save.clicked.connect(self.save_url)
        row.addWidget(btn_save)
        url_layout.addLayout(row)

        info = QLabel('Format: {"version": "3.1", "devices": [...]}')
        info.setObjectName("subtitle")
        url_layout.addWidget(info)

        url_group.setLayout(url_layout)
        layout.addWidget(url_group)

        # Buttons
        act_row = QHBoxLayout()
        act_row.setSpacing(6)

        btn_check = QPushButton("▶️ এখনই আপডেট চেক করো")
        btn_check.setObjectName("primary")
        btn_check.clicked.connect(self.run_update)
        act_row.addWidget(btn_check)

        btn_clear = QPushButton("🗑️ Log Clear")
        btn_clear.clicked.connect(lambda: self.out.clear())
        act_row.addWidget(btn_clear)

        act_row.addStretch()
        layout.addLayout(act_row)

        # Log
        log_group = QGroupBox("📋 Update Log")
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(6, 6, 6, 6)

        self.out = QTextEdit()
        self.out.setReadOnly(True)
        self.out.setMinimumHeight(120)
        self.out.setMaximumHeight(240)
        log_layout.addWidget(self.out)

        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        layout.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)

        self.setLayout(outer)

        if get_update_url():
            self.out.append(f"✅ URL সেট আছে")
            self.out.append(f"   {get_update_url()}")
        else:
            self.out.append("⚠️ URL সেট করা নেই")

    def save_url(self):
        url = self.f_url.text().strip()
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            QMessageBox.warning(self, "!", "সঠিক URL দাও")
            return
        set_update_url(url)
        self.out.append("─" * 45)
        self.out.append(f"💾 URL সেভ হয়েছে")
        QMessageBox.information(self, "✅", "URL সেভ হয়েছে")

    def run_update(self):
        """Auto-update with auto-confirmation on success"""

        self.out.append("─" * 45)
        self.out.append("🔄 আপডেট শুরু...")
        self.out.append("")

        try:
            r = check_and_update(verbose=False)
        except Exception as e:
            self.out.append(f"❌ আপডেট ব্যর্থ: {e}")
            self._scroll_bottom()
            return

        # ═══════════════════════════════════════════════════
        # Case 1: SUCCESS with new models added
        # ═══════════════════════════════════════════════════
        if r.get("ok") and r.get("added", 0) > 0:
            self.out.append("✅ SUCCESS — CONFIRMED")
            self.out.append("")
            self.out.append(f"📊 Added    : {r['added']} মডেল")
            self.out.append(f"🔖 Version  : {r['version']}")
            self.out.append("")
            self.out.append("🎉 ডেটাবেস আপডেট সম্পন্ন!")
            self.out.append("")
            self.out.append("👉 Settings tab-এ গিয়ে নতুন মডেল দেখো")
            self._scroll_bottom()
            return

        # ═══════════════════════════════════════════════════
        # Case 2: Already up-to-date
        # ═══════════════════════════════════════════════════
        if r.get("ok") and r.get("added", 0) == 0:
            self.out.append("✅ SUCCESS — CONFIRMED")
            self.out.append("")
            self.out.append(f"📊 Current version : v{r.get('version', '?')}")
            self.out.append("ℹ️  ডেটাবেস ইতিমধ্যেই আপ-টু-ডেট")
            self.out.append("")
            self.out.append("✅ আর কোনো কাজ প্রয়োজন নেই")
            self._scroll_bottom()
            return

        # ═══════════════════════════════════════════════════
        # Case 3: FAILURE
        # ═══════════════════════════════════════════════════
        self.out.append("❌ আপডেট ব্যর্থ")
        self.out.append("")
        self.out.append(f"📝 কারণ: {r.get('message', 'Unknown error')}")
        self.out.append("")
        self.out.append("🔧 সমাধান:")
        self.out.append("   • URL ঠিক আছে কিনা check করো")
        self.out.append("   • Internet connection check করো")
        self.out.append("   • GitHub repository Public কিনা দেখো")
        self._scroll_bottom()

    def _scroll_bottom(self):
        """Auto-scroll log to bottom"""
        sb = self.out.verticalScrollBar()
        sb.setValue(sb.maximum())