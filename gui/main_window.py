from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from excel_handler.reader import read_credentials
from odoo_client.client import OdooClient


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Odoo Module Upgrader")
        self.setGeometry(100, 100, 600, 600)
        self.odoo_client = None
        self.credentials_list = []
        self.module_checkboxes = []
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # --- Connection Group ---
        conn_group = QGroupBox("Odoo Connection")
        conn_layout = QGridLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("e.g. localhost:8069")
        self.db_input = QLineEdit()
        self.db_input.setPlaceholderText("Database name")
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)
        conn_layout.addWidget(QLabel("Odoo URL:"), 0, 0)
        conn_layout.addWidget(self.url_input, 0, 1)
        conn_layout.addWidget(QLabel("Username:"), 0, 2)
        conn_layout.addWidget(self.user_input, 0, 3)
        conn_layout.addWidget(QLabel("Database:"), 1, 0)
        conn_layout.addWidget(self.db_input, 1, 1)
        conn_layout.addWidget(QLabel("Password:"), 1, 2)
        conn_layout.addWidget(self.pass_input, 1, 3)
        conn_layout.setColumnStretch(1, 1)
        conn_layout.setColumnStretch(3, 1)
        conn_layout.setHorizontalSpacing(20)
        conn_layout.setVerticalSpacing(8)
        self.use_http_checkbox = QCheckBox("Use HTTP instead of HTTPS")
        http_layout = QHBoxLayout()
        http_layout.addStretch(1)
        http_layout.addWidget(self.use_http_checkbox)
        http_layout.addStretch(1)
        conn_main_layout = QVBoxLayout()
        conn_main_layout.addLayout(conn_layout)
        conn_main_layout.addLayout(http_layout)
        conn_group.setLayout(conn_main_layout)
        main_layout.addWidget(conn_group)

        # --- Excel + Credential ---
        btn_layout = QHBoxLayout()
        self.load_excel_btn = QPushButton("📂 Load Excel File")
        self.load_excel_btn.clicked.connect(self.load_excel)
        self.credential_selector = QComboBox()
        self.credential_selector.setEnabled(False)
        self.credential_selector.currentIndexChanged.connect(
            self.populate_credentials_from_selection
        )
        self.connect_btn = QPushButton("🔌 Connect and Fetch Modules")
        self.connect_btn.clicked.connect(self.connect_and_fetch)
        btn_layout.addWidget(self.load_excel_btn)
        btn_layout.addWidget(self.credential_selector)
        btn_layout.addWidget(self.connect_btn)
        main_layout.addLayout(btn_layout)

        # --- Module Search ---
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search Module:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Type to filter modules...")
        self.search_input.textChanged.connect(self.filter_modules)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        # --- Module List ---
        self.module_groupbox = QGroupBox("Available Modules")
        self.module_layout = QVBoxLayout()
        self.module_groupbox.setLayout(self.module_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.module_groupbox)
        main_layout.addWidget(scroll, stretch=1)

        # --- Upgrade ---
        self.upgrade_btn = QPushButton("⚙️ Upgrade Selected Modules")
        self.upgrade_btn.clicked.connect(self.upgrade_modules)
        main_layout.addWidget(self.upgrade_btn)

        # --- Status ---
        self.status_output = QTextEdit()
        self.status_output.setReadOnly(True)
        main_layout.addWidget(QLabel("Status:"))
        main_layout.addWidget(self.status_output)
        self.setLayout(main_layout)

    # --- Excel ---
    def load_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return
        try:
            self.credentials_list = read_credentials(file_path)
            self.credential_selector.clear()
            for idx, c in enumerate(self.credentials_list):
                self.credential_selector.addItem(
                    f"{idx+1}: {c['db']} - {c['username']}"
                )
            self.credential_selector.setEnabled(bool(self.credentials_list))
            if self.credentials_list:
                self.populate_credentials_from_selection(0)
            self.status_output.append(
                f"📄 Loaded {len(self.credentials_list)} credentials"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read Excel:\n{str(e)}")

    def populate_credentials_from_selection(self, index):
        if index < 0 or index >= len(self.credentials_list):
            return
        cred = self.credentials_list[index]
        self.url_input.setText(cred["url"])
        self.db_input.setText(cred["db"])
        self.user_input.setText(cred["username"])
        self.pass_input.setText(cred["password"])

    # --- Connect & fetch modules ---
    def connect_and_fetch(self):
        self.search_input.clear()
        url = self.url_input.text().strip()
        db = self.db_input.text().strip()
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()
        if not all([url, db, username, password]):
            QMessageBox.warning(self, "Missing Info", "Fill all fields")
            return
        try:
            self.status_output.clear()
            self.status_output.append(f"🔌 Connecting to {url}...")
            self.odoo_client = OdooClient(
                url, db, username, password, self.use_http_checkbox.isChecked()
            )
            self.odoo_client.connect()
            modules = self.odoo_client.fetch_modules()
            self.module_checkboxes.clear()
            self.clear_layout(self.module_layout)
            for mod in modules:
                cb = QCheckBox(
                    f"{mod['name']} ({mod['state']}) - {mod.get('summary','')}"
                )
                cb.setProperty("module_name", mod["name"])
                self.module_checkboxes.append(cb)
                self.module_layout.addWidget(cb)
            self.status_output.append(f"✅ {len(modules)} modules loaded")
        except Exception as e:
            self.status_output.append(f"❌ {str(e)}")

    # --- Upgrade modules ---
    def upgrade_modules(self):
        if not self.odoo_client:
            QMessageBox.warning(self, "Not connected", "Connect first")
            return
        selected = [
            cb.property("module_name")
            for cb in self.module_checkboxes
            if cb.isChecked()
        ]
        if not selected:
            QMessageBox.information(self, "No Selection", "Select modules")
            return
        try:
            self.status_output.append(f"🔄 Upgrading {len(selected)} modules...")
            upgraded = self.odoo_client.upgrade_modules(selected)
            self.status_output.append(f"✅ Upgrade triggered for {upgraded} module(s)")
        except Exception as e:
            self.status_output.append(f"❌ {str(e)}")

    # --- Helpers ---
    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            w and w.deleteLater()

    def filter_modules(self, text):
        text = text.lower().strip()
        for cb in self.module_checkboxes:
            cb.setVisible(text in cb.property("module_name").lower())
