from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QComboBox, QMessageBox,
                              QGroupBox, QTableWidget, QTableWidgetItem)
from settings import PAID_TOOLS, add_api_key

class B2BSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        title = QLabel("B2B Paid Tools API Settings")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #89b4fa;")
        layout.addWidget(title)

        info = QLabel("API key add korle tool automatically enable hobe.")
        info.setStyleSheet("color: #a6adc8; font-size: 12px;")
        layout.addWidget(info)

        tool_group = QGroupBox("Tool Select Koro")
        tool_layout = QVBoxLayout()
        self.b2b_tool_combo = QComboBox()
        for tool_name, tool_info in PAID_TOOLS.items():
            status = "Enabled" if tool_info.get("enabled") else "Disabled"
            self.b2b_tool_combo.addItem(f"{tool_info['name']} - {status}", tool_name)
        self.b2b_tool_combo.currentIndexChanged.connect(self._on_tool_change)
        tool_layout.addWidget(QLabel("Tool:"))
        tool_layout.addWidget(self.b2b_tool_combo)
        self.b2b_desc_label = QLabel("")
        self.b2b_desc_label.setStyleSheet("color: #a6adc8; font-size: 11px;")
        tool_layout.addWidget(self.b2b_desc_label)
        self.b2b_api_input = QLineEdit()
        self.b2b_api_input.setPlaceholderText("API Key ekhane paste koro...")
        self.b2b_api_input.setEchoMode(QLineEdit.EchoMode.Password)
        tool_layout.addWidget(QLabel("API Key:"))
        tool_layout.addWidget(self.b2b_api_input)
        self.b2b_show_key = QPushButton("Show")
        self.b2b_show_key.setCheckable(True)
        self.b2b_show_key.toggled.connect(self._toggle_api_visibility)
        tool_layout.addWidget(self.b2b_show_key)
        tool_group.setLayout(tool_layout)
        layout.addWidget(tool_group)

        btn_row = QHBoxLayout()
        btn_save_api = QPushButton("API Key Save Koro")
        btn_save_api.setMinimumHeight(35)
        btn_save_api.clicked.connect(self.save_b2b_api_key)
        btn_row.addWidget(btn_save_api)
        btn_clear_api = QPushButton("Clear")
        btn_clear_api.clicked.connect(lambda: self.b2b_api_input.clear())
        btn_row.addWidget(btn_clear_api)
        layout.addLayout(btn_row)

        status_group = QGroupBox("API Status")
        status_layout = QVBoxLayout()
        self.b2b_status_table = QTableWidget()
        self.b2b_status_table.setColumnCount(4)
        self.b2b_status_table.setHorizontalHeaderLabels(["Tool", "Status", "API Key", "API URL"])
        self.b2b_status_table.setMinimumHeight(200)
        status_layout.addWidget(self.b2b_status_table)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        btn_refresh = QPushButton("Refresh Status")
        btn_refresh.clicked.connect(self.load_b2b_status)
        layout.addWidget(btn_refresh)
        layout.addStretch()

        self._on_tool_change()
        self.load_b2b_status()
        self.setLayout(layout)

    def _on_tool_change(self):
        tool_name = self.b2b_tool_combo.currentData()
        if tool_name and tool_name in PAID_TOOLS:
            info = PAID_TOOLS[tool_name]
            self.b2b_desc_label.setText(f"{info.get('description', 'No description')}")
            if info.get("api_key"):
                self.b2b_api_input.setText(info["api_key"])
            else:
                self.b2b_api_input.clear()

    def _toggle_api_visibility(self, checked):
        if checked:
            self.b2b_api_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.b2b_show_key.setText("Hide")
        else:
            self.b2b_api_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.b2b_show_key.setText("Show")

    def save_b2b_api_key(self):
        tool_name = self.b2b_tool_combo.currentData()
        api_key = self.b2b_api_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Warning", "API key khali rakha jabe na!")
            return
        if add_api_key(tool_name, api_key):
            QMessageBox.information(self, "Success", f"{tool_name} API key added!")
            self.load_b2b_status()
            idx = self.b2b_tool_combo.currentIndex()
            self.b2b_tool_combo.setItemText(idx, f"{PAID_TOOLS[tool_name]['name']} - Enabled")
        else:
            QMessageBox.warning(self, "Error", "API key add korte problem hoyeche.")

    def load_b2b_status(self):
        try:
            self.b2b_status_table.setRowCount(len(PAID_TOOLS))
            for i, (tool_name, info) in enumerate(PAID_TOOLS.items()):
                self.b2b_status_table.setItem(i, 0, QTableWidgetItem(info["name"]))
                status = "Enabled" if info.get("enabled") else "Disabled"
                self.b2b_status_table.setItem(i, 1, QTableWidgetItem(status))
                key_display = "Set" if info.get("api_key") else "Not Set"
                self.b2b_status_table.setItem(i, 2, QTableWidgetItem(key_display))
                self.b2b_status_table.setItem(i, 3, QTableWidgetItem(info.get("api_url", "")))
            self.b2b_status_table.resizeColumnsToContents()
        except Exception as e:
            print(f"B2B Status Load Failed: {e}")
