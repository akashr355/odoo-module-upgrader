import sys

from PyQt5.QtWidgets import QApplication

from gui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(
        """
            QWidget { font-size: 18px; }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 6px;
                margin-top: 10px;
                padding: 10px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 6px 10px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QLineEdit, QComboBox {
                padding: 5px;
            }
        """
    )
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
