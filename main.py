from PyQt6.QtWidgets import QApplication, QLabel


from app.ui import MainWindow
from app.core.UserAuthentication import UserAuthentication
from app.core.Cipher import Cipher
from app.paths import BACKGROUNDS_DIR

import sys


class UserAgent:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.user_authenticator = UserAuthentication()
        self.main_window = MainWindow()
        self.main_window.show()
        sys.exit(self.app.exec())
    
    
user_agent = UserAgent()