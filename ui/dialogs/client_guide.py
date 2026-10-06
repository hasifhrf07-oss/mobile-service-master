# Client Guide Dialog — Developer Options + USB Debugging ON guide

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton, QFrame, QScrollArea,
                              QWidget)
from PyQt6.QtCore import Qt


class ClientGuideDialog(QDialog):
    """
    Client-কে দেখানোর জন্য popup — ৩০ সেকেন্ডে Developer Options ON
    """

    def __init__(self, parent=None, brand=""):
        super().__init__(parent)
        self.brand = brand or "ফোন"
        self.setWindowTitle(f"📋 {self.brand} — ADB Setup Guide")
        self.setMinimumSize(560, 620)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #e0e0e0;
            }
        """)
        self._build()

    def _build(self):
        outer = QVBoxLayout()
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(8)

        header = QLabel(f"📋 ক্লায়েন্ট গাইড — {self.brand}")
        header.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #89b4fa; "
            "padding: 4px;"
        )
        outer.addWidget(header)

        sub = QLabel("৩০ সেকেন্ডে Developer Options ON করো")
        sub.setStyleSheet("color: #a6adc8; font-size: 12px; padding: 2px;")
        outer.addWidget(sub)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )

        content = QWidget()
        steps_layout = QVBoxLayout(content)
        steps_layout.setContentsMargins(4, 4, 4, 4)
        steps_layout.setSpacing(10)

        steps_layout.addWidget(self._make_step(
            "১",
            "Settings → About Phone খোলো",
            "ফোনের Settings-এ যাও, তারপর About Phone / ফোনের তথ্য select করো।"
        ))
        steps_layout.addWidget(self._make_step(
            "২",
            "Build Number ৭ বার ট্যাপ করো",
            "About Phone-এ 'Build Number' দেখো। ওটাতে পরপর ৭ বার ট্যাপ করো। "
            "একটা message আসবে: 'You are now a developer!'"
        ))
        steps_layout.addWidget(self._make_step(
            "৩",
            "Developer Options-এ যাও",
            "Settings-এ ফিরে যাও → System → Developer Options "
            "(Xiaomi হলে: Additional Settings → Developer Options)"
        ))
        steps_layout.addWidget(self._make_step(
            "৪",
            "USB Debugging ON করো",
            "Developer Options-এ নিচে scroll করো → 'USB Debugging' খোঁজো → "
            "Toggle ON করো"
        ))
        steps_layout.addWidget(self._make_step(
            "৫",
            "USB Cable Connect করো",
            "USB cable দিয়ে ফোন PC-তে connect করো। "
            "ফোন Unlock রাখো (popup আসার জন্য জরুরি)"
        ))
        steps_layout.addWidget(self._make_step(
            "৬",
            "Popup-এ 'Always Allow' ✅ + 'Allow' ক্লিক করো",
            "ফোনে একটা popup আসবে — 'Allow USB debugging?'। "
            "'Always allow from this computer' ✅ tick দাও, তারপর 'Allow' ক্লিক করো।"
        ))

        steps_layout.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)

        info = QFrame()
        info.setStyleSheet(
            "QFrame {"
            "  background-color: #181825;"
            "  border-left: 3px solid #f9e2af;"
            "  border-radius: 4px;"
            "  padding: 8px;"
            "}"
        )
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(8, 6, 8, 6)

        lbl_info = QLabel(
            "ℹ️ একবার Allow করলে — পরেরবার এই ফোন এই PC-তে "
            "auto connect হবে (popup আসবে না)"
        )
        lbl_info.setStyleSheet(
            "color: #f9e2af; font-size: 12px;"
        )
        lbl_info.setWordWrap(True)
        info_layout.addWidget(lbl_info)
        outer.addWidget(info)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        btn_ready = QPushButton("✅ করেছি — Detect করো")
        btn_ready.setMinimumHeight(38)
        btn_ready.setStyleSheet(
            "QPushButton {"
            "  background-color: #89b4fa;"
            "  color: #1e1e2e;"
            "  font-weight: bold;"
            "  font-size: 13px;"
            "  border-radius: 5px;"
            "  padding: 8px 16px;"
            "}"
            "QPushButton:hover { background-color: #b4befe; }"
        )
        btn_ready.clicked.connect(self.accept)
        btn_row.addWidget(btn_ready, 2)

        btn_cancel = QPushButton("❌ Cancel")
        btn_cancel.setMinimumHeight(38)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel, 1)

        outer.addLayout(btn_row)

        self.setLayout(outer)

    def _make_step(self, num, title, description):
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame {"
            "  background-color: #252536;"
            "  border-radius: 6px;"
            "  padding: 8px;"
            "}"
        )
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        num_lbl = QLabel(num)
        num_lbl.setFixedSize(32, 32)
        num_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        num_lbl.setStyleSheet(
            "background-color: #89b4fa;"
            "color: #1e1e2e;"
            "font-weight: bold;"
            "font-size: 15px;"
            "border-radius: 16px;"
        )
        layout.addWidget(num_lbl)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            "color: #cdd6f4; font-weight: bold; font-size: 13px;"
        )
        title_lbl.setWordWrap(True)
        text_layout.addWidget(title_lbl)

        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet("color: #a6adc8; font-size: 12px;")
        desc_lbl.setWordWrap(True)
        text_layout.addWidget(desc_lbl)

        layout.addLayout(text_layout, 1)
        return frame


class WaitingDialog(QDialog):
    """
    Waiting dialog — popup-এ Allow করার জন্য wait
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⏳ Waiting for Allow")
        self.setMinimumSize(420, 280)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #e0e0e0;
            }
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("⏳ ফোনে Popup আসছে...")
        title.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #89b4fa; "
            "padding: 4px;"
        )
        layout.addWidget(title)

        desc = QLabel(
            "ফোনের screen-এ 'Allow USB debugging?' popup আসবে।\n\n"
            "⚠️ 'Always allow from this computer' ✅ tick দাও\n"
            "তারপর 'Allow' ক্লিক করো।"
        )
        desc.setStyleSheet(
            "color: #cdd6f4; font-size: 13px; padding: 8px;"
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self.lbl_status = QLabel("⏱️ waiting...")
        self.lbl_status.setStyleSheet(
            "background-color: #181825;"
            "color: #f9e2af;"
            "padding: 10px;"
            "border-radius: 5px;"
            "font-size: 13px;"
        )
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_status)

        self.lbl_timer = QLabel("০ সেকেন্ড")
        self.lbl_timer.setStyleSheet(
            "color: #6c7086; font-size: 12px;"
        )
        self.lbl_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_timer)

        layout.addStretch()

        btn_cancel = QPushButton("❌ Cancel")
        btn_cancel.setMinimumHeight(36)
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)

        self.setLayout(layout)

    def update_status(self, state, elapsed):
        self.lbl_timer.setText(f"{elapsed} সেকেন্ড")

        if state == "device":
            self.lbl_status.setText("✅ Authorized! Connected.")
            self.lbl_status.setStyleSheet(
                "background-color: #181825;"
                "color: #a6e3a1;"
                "padding: 10px;"
                "border-radius: 5px;"
                "font-size: 13px;"
            )
            self.accept()
        elif state == "unauthorized":
            self.lbl_status.setText(
                "⚠️ Popup এখনো Allow করা হয়নি... ক্লিক করো"
            )
        elif state == "no_device":
            self.lbl_status.setText("📱 Waiting for phone connection...")
        else:
            self.lbl_status.setText(f"⏱️ State: {state}") 
