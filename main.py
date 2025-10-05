from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QFont
import sys
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.icon_path = r"interface/images"
        self.resize(467, 496)

        # QLabel для фона main menu
        self.background_1 = QLabel(self)
        self.background_1.setPixmap(QPixmap(r"interface/images/background_1.png"))
        self.background_1.setScaledContents(True)
        self.background_1.setGeometry(0, 0, self.width(), self.height())
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        self.top_bar = QLabel(self)
        self.top_bar.setPixmap(QPixmap(r"interface/images/top_panel.png"))
        self.top_bar.setScaledContents(True)
        self.top_bar.setGeometry(14, 12, 441, 34)  # позиция и размер
        
        self.font = QFont("IBM 3270", 14)
        self.font.setBold(True)
        self.title = QLabel("CryptoFredi_16_bit.exe", self)
        self.title.setFont(self.font)
        self.title.move(23, 18)
        self.title.resize(300, 21)
        self.title.setStyleSheet("color: rgb(204,36,29);")
        
        self.background_2 = QLabel(self)
        self.background_2.setPixmap(QPixmap(r"interface/images/background_2.png"))
        self.background_2.setScaledContents(True)
        self.background_2.setGeometry(14, 54, 355, 430)
    
        self.monitor = QLabel(self)
        self.monitor.setPixmap(QPixmap(r"interface/images/monitor.png"))
        self.monitor.setScaledContents(True)
        self.monitor.setGeometry(33, 73, 317, 313)
        
        self.collapse_btn = QPushButton(self)
        pixmap = QPixmap(r"interface/images/collapse_default.png")
        collapse_btn_icon = QIcon(pixmap)
        self.collapse_btn.setIcon(collapse_btn_icon)
        self.collapse_btn.setIconSize(pixmap.size())
        self.collapse_btn.move(396, 17)   # позиция на окне
        self.collapse_btn.resize(24, 24) # размер кнопки
        self.collapse_btn.pressed.connect(self.function_btn_pressed("collapse"))
        self.collapse_btn.released.connect(self.function_btn_released("collapse"))
        
        self.close_btn = QPushButton(self)
        pixmap = QPixmap(r"interface/images/close_default.png")
        close_btn_icon = QIcon(pixmap)
        self.close_btn.setIcon(close_btn_icon)
        self.close_btn.setIconSize(pixmap.size())
        self.close_btn.move(426, 17)
        self.close_btn.resize(24, 24)
        self.close_btn.pressed.connect(self.function_btn_pressed("close"))
        self.close_btn.released.connect(self.function_btn_released("close"))
        
        self.enter_btn = QPushButton(self)
        pixmap = QPixmap(r"interface/images/enter_default.png")
        enter_btn_icon = QIcon(pixmap)
        self.enter_btn.setIcon(enter_btn_icon)
        self.enter_btn.setIconSize(pixmap.size())
        self.enter_btn.move(33, 402)
        self.enter_btn.resize(317, 63)
        self.enter_btn.pressed.connect(self.function_btn_pressed("enter"))
        self.enter_btn.released.connect(self.function_btn_released("enter"))
        
        self.help_btn = QPushButton(self)
        pixmap = QPixmap(r"interface/images/help_default.png")
        help_btn_icon = QIcon(pixmap)
        self.help_btn.setIcon(help_btn_icon)
        self.help_btn.setIconSize(pixmap.size())
        self.help_btn.move(377, 54)
        self.help_btn.resize(78, 78)
        self.help_btn.pressed.connect(self.function_btn_pressed("help"))
        self.help_btn.released.connect(self.function_btn_released("help"))
        
        self.settings_btn = QPushButton(self)
        pixmap = QPixmap(r"interface/images/settings_default.png")
        settings_btn_icon = QIcon(pixmap)
        self.settings_btn.setIcon(settings_btn_icon)
        self.settings_btn.setIconSize(pixmap.size())
        self.settings_btn.move(377, 142)
        self.settings_btn.resize(78, 78)
        self.settings_btn.pressed.connect(self.function_btn_pressed("settings"))
        self.settings_btn.released.connect(self.function_btn_released("settings"))
        
        self.change_btn = QPushButton(self)
        pixmap = QPixmap(r"interface/images/change_default.png")
        change_btn_icon = QIcon(pixmap)
        self.change_btn.setIcon(change_btn_icon)
        self.change_btn.setIconSize(pixmap.size())
        self.change_btn.move(377, 230)
        self.change_btn.resize(78, 78)
        self.change_btn.pressed.connect(self.function_btn_pressed("change"))
        self.change_btn.released.connect(self.function_btn_released("change"))
        
        self.logs_btn = QPushButton(self)
        pixmap = QPixmap(r"interface/images/logs_default.png")
        logs_btn_icon = QIcon(pixmap)
        self.logs_btn.setIcon(logs_btn_icon)
        self.logs_btn.setIconSize(pixmap.size())
        self.logs_btn.move(377, 318)
        self.logs_btn.resize(78, 78)
        self.logs_btn.pressed.connect(self.function_btn_pressed("logs"))
        self.logs_btn.released.connect(self.function_btn_released("logs"))
        
        self.list_btn = QPushButton(self)
        pixmap = QPixmap(r"interface/images/list_default.png")
        list_btn_icon = QIcon(pixmap)
        self.list_btn.setIcon(list_btn_icon)
        self.list_btn.setIconSize(pixmap.size())
        self.list_btn.move(377, 406)
        self.list_btn.resize(78, 78)
        self.list_btn.pressed.connect(self.function_btn_pressed("list"))
        self.list_btn.released.connect(self.function_btn_released("list"))
        
        self.functions_btns = {
            "collapse": self.collapse, "close": self.close_,
            "enter": self.enter, "help": self.help_,
            "settings": self.settings, "change": self.change,
            "logs": self.logs, "list": self.list_,
        }

        # Для хранения позиции мыши
        self.old_pos = None
        
        self.authorization = False
    
    def function_btn_released(self, function: str) -> None:
        """
            Полиморфная функция которая отвечает за НЕ зажатые кнопки
            Главным образом работает с атрибутом functions_btns - словарь
            в котором по именам привязаны функции к кнопкам.
            
            Функция меняет иконку на НЕ зажатаю когда кнопку отпускает.
            Вызывает функцию привязанную к кнопке.
        """
        def wrapper():
            relative_path = os.path.join(self.icon_path, function + "_default")
            pixmap = QPixmap(relative_path)
            self.__dict__[function + "_btn"].setIcon(QIcon(pixmap)) 
            if function in self.functions_btns:
                self.functions_btns[function]()
        return wrapper
        
    def function_btn_pressed(self, function: str) -> None:
        def wrapper():
            relative_path = os.path.join(self.icon_path, function + "_pressed")
            pixmap = QPixmap(relative_path)
            self.__dict__[function + "_btn"].setIcon(QIcon(pixmap)) 
        return wrapper
        
    def close_(self):
        self.close()
    
    def collapse(self):
        self.showMinimized()
    
    def enter(self):
        print("enter")
        
    def help_(self):
        print("help")
    
    def settings(self):
        print("settings")
        
    def change(self):
        print("change")

    def logs(self):
        print("logs")
        
    def list_(self):
        print("list")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
    
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
