# Odoo Module Upgrader (PyQt5 Desktop Application)

A simple desktop application built with PyQt5 to connect to an Odoo instance via XML-RPC, list installed modules, and trigger upgrades for selected modules. The app also supports loading multiple Odoo credentials from an Excel file for quick switching between environments.

---

## Features

- Connect to Odoo using XML-RPC.
- Load multiple credentials from an Excel file.
- Dropdown selection for different Odoo environments.
- Fetch and display installed modules.
- Filter modules using a search bar.
- Upgrade selected modules in a single batch.
- Supports HTTP/HTTPS connections.
- Status output to track connection and upgrade progress.

---

## Requirements

- Python 3.10+
- PyQt5
- openpyxl (for Excel reading)

Install dependencies via pip:

```bash
pip install -r requirements.txt
