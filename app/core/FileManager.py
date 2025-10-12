from PyQt5.QtWidgets import QTreeWidgetItem
from ctypes import windll
import string
import os


class FileManager:
    def __init__(self, tree):
        self.tree = tree
        self.drives = []
    
    def add_drives(self) -> None:
        """Добавляем все диски системы"""
        drives = self._get_drives()
        for drive in drives:
            item = QTreeWidgetItem([drive, drive])
            item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
            self.tree.addTopLevelItem(item)

    def _get_drives(self) -> list:
        """Возвращает список дисков"""
        if os.name == 'nt':  # Windows
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    self.drives.append(f"{letter}:/")
                bitmask >>= 1
        else:
            self.drives = ['/']  # Linux/macOS
        return self.drives