"""History Tab — Scrollable"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QTableWidget,
                              QTableWidgetItem, QGroupBox, QTextEdit,
                              QScrollArea)
from PyQt6.QtCore import Qt
from data import db


class HistoryTab(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self._build()
        self.refresh()

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

        title = QLabel("📜 সার্ভিস হিস্ট্রি")
        title.setObjectName("title")
        layout.addWidget(title)

        # Stats
        stats_group = QGroupBox("📊 পরিসংখ্যান")
        stats_layout = QVBoxLayout()
        stats_layout.setContentsMargins(6, 6, 6, 6)
        self.out_stats = QTextEdit()
        self.out_stats.setReadOnly(True)
        self.out_stats.setMinimumHeight(100)
        self.out_stats.setMaximumHeight(160)
        stats_layout.addWidget(self.out_stats)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Refresh
        btn_row = QHBoxLayout()
        btn = QPushButton("🔄 Refresh")
        btn.setObjectName("primary")
        btn.clicked.connect(self.refresh)
        btn_row.addWidget(btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Table
        table_group = QGroupBox("📋 সাম্প্রতিক সার্ভিস")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(6, 6, 6, 6)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Time", "Brand", "Model", "Type", "Summary", "Client"]
        )
        self.table.setMinimumHeight(250)
        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        layout.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)

        self.setLayout(outer)

    def refresh(self):
        try:
            s = db.history_stats()
            self.out_stats.clear()
            self.out_stats.append(f"📊 মোট সার্ভিস : {s['total']}")
            if s["by_type"]:
                self.out_stats.append("")
                self.out_stats.append("🔧 ধরন অনুযায়ী:")
                for row in s["by_type"]:
                    self.out_stats.append(
                        f"   • {row['issue_type']}: {row['n']}"
                    )
            if s["top_brands"]:
                self.out_stats.append("")
                self.out_stats.append("📱 Top ব্র্যান্ড:")
                for row in s["top_brands"]:
                    self.out_stats.append(f"   • {row['brand']}: {row['n']}")

            rows = db.recent_history(limit=200)
            self.table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self.table.setItem(i, 0, QTableWidgetItem(str(r["ts"])[:19]))
                self.table.setItem(i, 1, QTableWidgetItem(r["brand"] or ""))
                self.table.setItem(i, 2, QTableWidgetItem(r["model"] or ""))
                self.table.setItem(i, 3, QTableWidgetItem(r["issue_type"] or ""))
                self.table.setItem(i, 4, QTableWidgetItem((r["summary"] or "")[:50]))
                self.table.setItem(i, 5, QTableWidgetItem(r["client_name"] or ""))
            self.table.resizeColumnsToContents()
        except Exception as e:
            self.out_stats.clear()
            self.out_stats.append(f"❌ Refresh ব্যর্থ: {e}")