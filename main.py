from PyQt6.QtWidgets import QApplication, QLabel


from app.ui import MainWindow

import sys



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())