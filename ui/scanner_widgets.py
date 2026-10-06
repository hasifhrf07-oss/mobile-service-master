"""Scanner Widgets — Reusable UI components"""

from PyQt6.QtWidgets import (QWidget, QFrame, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal


class ScanCard(QFrame):
    """একটা scan-এর card display"""
    clicked = pyqtSignal(str)

    def __init__(self, scan_data):
        super().__init__()
        self.scan_id = scan_data.get("scan_id", "N/A")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            "QFrame {"
            "  background-color: #252536;"
            "  border: 1px solid #45475a;"
            "  border-radius: 5px;"
            "  padding: 5px;"
            "}"
            "QFrame:hover {"
            "  border-color: #89b4fa;"
            "  background-color: #2d2d42;"
            "}"
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._build(scan_data)

    def _build(self, d):
        layout = QVBoxLayout()
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(2)

        # Row 1: Scan ID + Status
        row1 = QHBoxLayout()
        sid = QLabel(f"🔖 {d.get('scan_id', 'N/A')}")
        sid.setStyleSheet(
            "color: #89b4fa; font-weight: bold; font-size: 12px;"
        )
        row1.addWidget(sid)
        row1.addStretch()

        dev = d.get("deviation_score", 0) or 0
        if dev == 0:
            badge = QLabel("REF")
            badge.setStyleSheet(
                "background: #a6e3a1; color: #1e1e2e; "
                "padding: 1px 6px; border-radius: 3px; font-size: 10px;"
            )
        elif dev < 30:
            badge = QLabel(f"{int(dev)}%")
            badge.setStyleSheet(
                "background: #a6e3a1; color: #1e1e2e; "
                "padding: 1px 6px; border-radius: 3px; font-size: 10px;"
            )
        elif dev < 60:
            badge = QLabel(f"{int(dev)}%")
            badge.setStyleSheet(
                "background: #f9e2af; color: #1e1e2e; "
                "padding: 1px 6px; border-radius: 3px; font-size: 10px;"
            )
        else:
            badge = QLabel(f"{int(dev)}%")
            badge.setStyleSheet(
                "background: #f38ba8; color: #1e1e2e; "
                "padding: 1px 6px; border-radius: 3px; font-size: 10px;"
            )
        row1.addWidget(badge)
        layout.addLayout(row1)

        # Row 2: Model
        model = QLabel(f"📱 {d.get('brand', '')} {d.get('model', '')}")
        model.setStyleSheet("color: #cdd6f4; font-size: 11px;")
        layout.addWidget(model)

        # Row 3: Diagnosis
        diag = d.get("diagnosis", "") or "(no diagnosis)"
        diag_lbl = QLabel(f"🔧 {diag[:60]}")
        diag_lbl.setStyleSheet("color: #a6adc8; font-size: 10px;")
        diag_lbl.setWordWrap(True)
        layout.addWidget(diag_lbl)

        # Row 4: Time
        ts = QLabel(f"🕒 {str(d.get('ts', ''))[:19]}")
        ts.setStyleSheet("color: #6c7086; font-size: 10px;")
        layout.addWidget(ts)

        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.scan_id)


class ReadingDisplay(QFrame):
    """একটা rail reading-এর display"""

    def __init__(self, rail_name, value, expected=None, unit="V"):
        super().__init__()
        self.setStyleSheet(
            "QFrame {"
            "  background-color: #11111b;"
            "  border: 1px solid #313244;"
            "  border-radius: 4px;"
            "  padding: 4px;"
            "}"
        )

        layout = QHBoxLayout()
        layout.setContentsMargins(6, 3, 6, 3)

        name = QLabel(rail_name.upper())
        name.setStyleSheet(
            "color: #89b4fa; font-weight: bold; font-size: 11px;"
        )
        name.setMinimumWidth(80)
        layout.addWidget(name)

        val_str = f"{value} {unit}" if isinstance(value, (int, float)) else str(value)

        if isinstance(value, (int, float)) and expected:
            try:
                exp = float(str(expected).split("-")[0])
                if value < 0.1:
                    color = "#f38ba8"
                elif abs(value - exp) / exp > 0.2:
                    color = "#f9e2af"
                else:
                    color = "#a6e3a1"
            except Exception:
                color = "#cdd6f4"
        else:
            color = "#cdd6f4"

        val_lbl = QLabel(val_str)
        val_lbl.setStyleSheet(
            f"color: {color}; font-weight: bold; font-size: 12px;"
        )
        layout.addWidget(val_lbl)

        layout.addStretch()

        if expected:
            exp_lbl = QLabel(f"↔ {expected}")
            exp_lbl.setStyleSheet("color: #6c7086; font-size: 10px;")
            layout.addWidget(exp_lbl)

        self.setLayout(layout)


class BoardViewCard(QFrame):
    """BoardView file card"""
    open_clicked = pyqtSignal(str)
    delete_clicked = pyqtSignal(int)

    def __init__(self, file_data):
        super().__init__()
        self.file_data = file_data
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            "QFrame {"
            "  background-color: #252536;"
            "  border: 1px solid #45475a;"
            "  border-radius: 5px;"
            "  padding: 5px;"
            "}"
            "QFrame:hover { border-color: #89b4fa; }"
        )
        self._build()

    def _build(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(6, 3, 6, 3)

        icon = QLabel("📐")
        icon.setStyleSheet("font-size: 16px;")
        layout.addWidget(icon)

        info = QVBoxLayout()
        info.setSpacing(1)

        title = QLabel(
            f"{self.file_data.get('brand', '')} "
            f"{self.file_data.get('model', '')}"
        )
        title.setStyleSheet(
            "color: #cdd6f4; font-weight: bold; font-size: 11px;"
        )
        info.addWidget(title)

        ft = self.file_data.get("file_type", "?").upper()
        size_kb = (self.file_data.get("file_size", 0) or 0) / 1024
        sub = QLabel(f"{ft} • {size_kb:.1f} KB")
        sub.setStyleSheet("color: #6c7086; font-size: 10px;")
        info.addWidget(sub)

        layout.addLayout(info, 1)

        btn_open = QPushButton("Open")
        btn_open.setFixedHeight(24)
        btn_open.setStyleSheet(
            "background: #89b4fa; color: #1e1e2e; font-size: 10px; "
            "padding: 2px 8px; border-radius: 3px; font-weight: bold;"
        )
        btn_open.clicked.connect(
            lambda: self.open_clicked.emit(self.file_data.get("file_path", ""))
        )
        layout.addWidget(btn_open)

        btn_del = QPushButton("X")
        btn_del.setFixedSize(26, 24)
        btn_del.setStyleSheet(
            "background: #f38ba8; color: #1e1e2e; font-size: 10px; "
            "padding: 2px; border-radius: 3px;"
        )
        btn_del.clicked.connect(
            lambda: self.delete_clicked.emit(self.file_data.get("id", 0))
        )
        layout.addWidget(btn_del)

        self.setLayout(layout)


class StatBox(QFrame):
    """একটা stat number-এর box — BIG"""
    def __init__(self, label, value, color="#89b4fa"):
        super().__init__()
        self.color = color
        self.setStyleSheet(
            f"QFrame {{"
            f"  background-color: #181825;"
            f"  border-left: 4px solid {color};"
            f"  border-radius: 5px;"
            f"  padding: 6px;"
            f"}}"
        )
        self.setMinimumHeight(60)

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)

        self.val_label = QLabel(str(value))
        self.val_label.setStyleSheet(
            f"color: {color}; font-size: 22px; font-weight: bold;"
        )
        layout.addWidget(self.val_label)

        self.lbl_label = QLabel(label)
        self.lbl_label.setStyleSheet(
            "color: #a6adc8; font-size: 11px;"
        )
        layout.addWidget(self.lbl_label)

        self.setLayout(layout)

    def set_value(self, value):
        self.val_label.setText(str(value))