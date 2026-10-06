
"""BoardView Manager Tab"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QLineEdit, QComboBox,
                              QGroupBox, QFormLayout, QMessageBox,
                              QFileDialog, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt
from core.scanner.boardview_manager import BoardViewManager
from ui.scanner_widgets import BoardViewCard


BRANDS = ["Samsung", "Xiaomi", "Apple", "Vivo", "Oppo",
          "Realme", "OnePlus", "Huawei", "Tecno", "Itel"]


class BoardViewTab(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.manager = BoardViewManager(log_callback=self._log)
        self._build()
        self._refresh()

    def _build(self):
        outer = QVBoxLayout()
        outer.setContentsMargins(6, 4, 6, 4)
        outer.setSpacing(6)

        title = QLabel("📐 BoardView Manager")
        title.setObjectName("title")
        outer.addWidget(title)

        reg_group = QGroupBox("➕ Register New File")
        reg_form = QFormLayout()
        reg_form.setSpacing(4)

        self.f_brand = QComboBox()
        self.f_brand.setEditable(True)
        self.f_brand.addItems(BRANDS)

        self.f_model = QLineEdit()
        self.f_model.setPlaceholderText("SM-A105F")

        self.f_board = QLineEdit()
        self.f_board.setPlaceholderText("Board number (optional)")

        file_row = QHBoxLayout()
        self.f_path = QLineEdit()
        self.f_path.setPlaceholderText("File path (.brd/.pdf)")
        file_row.addWidget(self.f_path, 1)

        btn_browse = QPushButton("📁 Browse")
        btn_browse.clicked.connect(self.browse_file)
        file_row.addWidget(btn_browse)

        self.f_source = QLineEdit()
        self.f_source.setPlaceholderText("Source (gsmserver, manual, etc.)")

        self.f_license = QComboBox()
        self.f_license.addItems(["personal", "commercial", "unknown"])

        reg_form.addRow("Brand", self.f_brand)
        reg_form.addRow("Model", self.f_model)
        reg_form.addRow("Board #", self.f_board)
        reg_form.addRow("File", file_row)
        reg_form.addRow("Source", self.f_source)
        reg_form.addRow("License", self.f_license)
        reg_group.setLayout(reg_form)
        outer.addWidget(reg_group)

        act_row = QHBoxLayout()

        btn_save = QPushButton("💾 Register")
        btn_save.setObjectName("primary")
        btn_save.clicked.connect(self.register_file)
        act_row.addWidget(btn_save)

        btn_scan = QPushButton("🔍 Scan Folder")
        btn_scan.clicked.connect(self.scan_folder)
        act_row.addWidget(btn_scan)

        btn_clear = QPushButton("🗑️ Clear")
        btn_clear.clicked.connect(self.clear_form)
        act_row.addWidget(btn_clear)

        act_row.addStretch()
        outer.addLayout(act_row)

        list_group = QGroupBox("📋 Registered Files")
        list_layout = QVBoxLayout()
        list_layout.setContentsMargins(6, 6, 6, 6)

        srow = QHBoxLayout()
        self.f_search = QLineEdit()
        self.f_search.setPlaceholderText("Search brand / model...")
        self.f_search.textChanged.connect(self._refresh_list)
        srow.addWidget(self.f_search)

        btn_refresh = QPushButton("🔄")
        btn_refresh.setFixedWidth(35)
        btn_refresh.clicked.connect(self._refresh_list)
        srow.addWidget(btn_refresh)
        list_layout.addLayout(srow)

        self.file_list = QListWidget()
        self.file_list.setStyleSheet(
            "QListWidget {"
            "  background-color: #181825;"
            "  border: 1px solid #313244;"
            "  border-radius: 4px;"
            "  padding: 2px;"
            "}"
        )
        list_layout.addWidget(self.file_list)

        self.lbl_count = QLabel("")
        self.lbl_count.setObjectName("subtitle")
        list_layout.addWidget(self.lbl_count)

        list_group.setLayout(list_layout)
        outer.addWidget(list_group, 1)

        log_group = QGroupBox("📋 Log")
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(6, 6, 6, 6)
        self.log_out = QLabel("")
        self.log_out.setStyleSheet(
            "color: #cdd6f4; font-size: 11px; padding: 4px;"
        )
        self.log_out.setWordWrap(True)
        log_layout.addWidget(self.log_out)
        log_group.setLayout(log_layout)
        outer.addWidget(log_group)

        self.setLayout(outer)

    def _log(self, msg):
        self.log_out.setText(msg)

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select BoardView / Schematic", "",
            "All Files (*.brd *.bvr *.tvw *.gr *.pdf *.png *.jpg);;"
            "BoardView (*.brd *.bvr *.tvw *.gr);;"
            "Schematic (*.pdf *.png *.jpg);;"
            "All Files (*.*)"
        )
        if path:
            self.f_path.setText(path)

    def register_file(self):
        brand = self.f_brand.currentText().strip()
        model = self.f_model.text().strip()
        path = self.f_path.text().strip()

        if not brand or not model or not path:
            QMessageBox.warning(
                self, "⚠️",
                "Brand, Model, এবং File path লাগবে"
            )
            return

        import os
        ext = os.path.splitext(path)[1].lower().lstrip(".")
        if not ext:
            ext = "brd"

        ok = self.manager.register(
            brand=brand,
            model=model,
            board_number=self.f_board.text().strip() or model,
            file_path=path,
            file_type=ext,
            source=self.f_source.text().strip() or "manual",
            license_status=self.f_license.currentText(),
        )

        if ok:
            QMessageBox.information(
                self, "✅",
                f"Registered: {brand} {model}"
            )
            self.clear_form()
            self._refresh()
        else:
            QMessageBox.warning(
                self, "❌",
                "Register fail — file path চেক করো"
            )

    def scan_folder(self):
        brand = self.f_brand.currentText().strip()
        if not brand:
            QMessageBox.warning(self, "⚠️", "Brand select করো")
            return

        ans = QMessageBox.question(
            self, "🔍 Scan Folder",
            f"'{brand}' folder-এ থাকা সব file register করবো?"
        )
        if ans != QMessageBox.StandardButton.Yes:
            return

        n = self.manager.scan_folder(brand, auto_register=True)
        if n > 0:
            QMessageBox.information(
                self, "✅",
                f"{n} file registered"
            )
            self._refresh()

    def clear_form(self):
        self.f_model.clear()
        self.f_board.clear()
        self.f_path.clear()
        self.f_source.clear()
        self.f_license.setCurrentIndex(0)

    def _refresh(self):
        self._refresh_list()
        try:
            n = self.manager.count()
            self.lbl_count.setText(f"📊 মোট {n} file registered")
        except Exception:
            pass

    def _refresh_list(self):
        q = self.f_search.text().strip().lower()

        try:
            files = self.manager.list_all(limit=500)
        except Exception as e:
            self._log(f"❌ List fail: {e}")
            return

        if q:
            files = [
                f for f in files
                if q in (f.get("brand", "") + " " + f.get("model", "")).lower()
            ]

        self.file_list.clear()
        for f in files:
            card = BoardViewCard(f)
            card.open_clicked.connect(self.open_file)
            card.delete_clicked.connect(self.delete_file)

            item = QListWidgetItem()
            item.setSizeHint(card.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, f.get("id"))
            self.file_list.addItem(item)
            self.file_list.setItemWidget(item, card)

    def open_file(self, file_path):
        if not file_path:
            return
        ok = self.manager.open_file(file_path)
        if not ok:
            QMessageBox.warning(
                self, "❌",
                f"File open করা যায়নি:\n{file_path}"
            )

    def delete_file(self, file_id):
        ans = QMessageBox.question(
            self, "🗑️ Remove",
            "Registry থেকে remove করবো?\n(actual file delete হবে না)"
        )
        if ans != QMessageBox.StandardButton.Yes:
            return

        if self.manager.unregister(file_id):
            self._log("🗑️ Removed from registry")
            self._refresh()