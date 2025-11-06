from tkinter import CENTER
from turtle import isvisible
from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QPlainTextEdit, QTreeWidgetItem, QTreeWidget, QWidget, QVBoxLayout, QScrollArea, QLineEdit, QHBoxLayout
from PyQt6.QtCore import Qt, QSize, QRect, QUrl, QTimer
from PyQt6.QtGui import QPixmap, QIcon, QFontMetrics, QPalette, QColor, QPainter, QTextCursor, QFont, QFontDatabase, QCursor, QMouseEvent
from PyQt6.QtMultimedia import QSoundEffect

from datetime import datetime
from functools import partial
import pickle
import threading
import json
import os

from pymsgbox import password

from app.core import FileManager, Cipher, UserAuthentication, style_getter, font_getter, AuthState, Function, button_icon_getter, sound_getter, background_getter, CONSTANTS
from app.core.AppController import AppController
from app.paths import BACKGROUNDS_DIR, SOUNDS_DIR, BUTTONS_DIR


class MainWindow(QMainWindow):
    """Класс главного окна"""
    def __init__(self):
        super().__init__()
        # устанавливаем размер главного окна
        self.resize(467, 496)
        # инициализация кнопок
        self.init_ui()
        # Для хранения позиции мыши
        # этот атрибут нужен, ибо у данного приложения
        # реализовано кастомное окно, а для этого нужно
        # отключить базовые фишки окна PyQt, к сожалению
        # отвечает за перетаскивание окна кнопкой мыши
        self._mouse_old_pos = None
        # файл шрифта
        self.font_family = "3270-Regular.ttf"
        self.cipher = Cipher()
        self.user_auth = UserAuthentication()
        self.file_manager = FileManager(monitor=self.monitor)
        # контроллер всего приложения
        self.controller = AppController(
            user_auth=self.user_auth,
            cipher=self.cipher,
            file_manager=self.file_manager,
            ui=self
        )
        self.disable_btns()
        self.controller.define_event_authentication()

    def init_ui(self) -> None:
        """Инициализация кнопок и интерфейса"""        
        self.init_backgrounds()
        self.init_buttons()
        self.init_sound_effects()     
       
    def init_backgrounds(self) -> None:
        """Инициализация задних фонов"""
        # главный задний фон(что-то вроде корпуса)
        self.background_1 = QLabel(self)
        self.background_1.setPixmap(background_getter("background_1.png"))
        self.background_1.setGeometry(0, 0, self.width(), self.height())
        # убираем стандартную рамку окна
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # верхняя панель, где расположены кнопки сворачивания и выключения
        self.top_bar = QLabel(self)
        self.top_bar.setPixmap(background_getter("top_panel.png"))
        self.top_bar.setGeometry(14, 12, 441, 34)  # позиция и размер
        
        # тут может быть надпись на верхней панели
        # self.title = QLabel("CryptoFredi_16_bit.exe", self)
        # self.title.setFont(self.font)
        # self.title.move(23, 18)
        # self.title.resize(300, 21)
        # self.title.setStyleSheet("color: rgb(204,36,29);")
        
        # второй задний фон для монитора и кнопки enter
        self.background_2 = QLabel(self)
        self.background_2.setPixmap(background_getter("background_2.png"))
        self.background_2.setGeometry(14, 54, 355, 430)

        # дисплей на который будет выводится информация для пользователя
        self.monitor = QLabel(self)
        self.monitor.setPixmap(background_getter("monitor.png"))
        self.monitor.setGeometry(33, 73, 317, 313)
        # self.monitor.setCursor(Qt.CursorShape.ArrowCursor)
    
    def init_buttons(self) -> None:
        """Инициализация кнопок"""
        # кнопка сворачивания программы
        self.collapse_btn = QPushButton(self)
        pixmap = QPixmap(os.path.join(BUTTONS_DIR, "collapse_default.png"))
        collapse_btn_icon = QIcon(pixmap)
        self.collapse_btn.setIcon(collapse_btn_icon)
        self.collapse_btn.setIconSize(pixmap.size())
        self.collapse_btn.setGeometry(396, 17, 24, 24)
        self.collapse_btn.setCheckable(True)
        self.collapse_btn.pressed.connect(self.collapse_pressed)
        self.collapse_btn.released.connect(self.collapse_released)
        
        # # кнопки выключения программы
        self.close_btn = QPushButton(self)
        pixmap = QPixmap(os.path.join(BUTTONS_DIR, "close_default.png"))
        close_btn_icon = QIcon(pixmap)
        self.close_btn.setIcon(close_btn_icon)
        self.close_btn.setIconSize(pixmap.size())
        self.close_btn.setGeometry(426, 17, 24, 24)
        self.close_btn.pressed.connect(self.close_pressed)
        self.close_btn.released.connect(self.close_released)
        
        # кнопка ввода
        self.enter_btn = QPushButton(self)
        pixmap = QPixmap(os.path.join(BUTTONS_DIR, "enter_default.png"))
        enter_btn_icon = QIcon(pixmap)
        self.enter_btn.setIcon(enter_btn_icon)
        self.enter_btn.setIconSize(pixmap.size())
        self.enter_btn.setGeometry(33, 402, 317, 63)
        self.enter_btn.pressed.connect(self.enter_pressed)
        self.enter_btn.released.connect(self.enter_released)
        
        # кнопка зашифровки
        self.encrypt_btn = QPushButton(self)
        pixmap = QPixmap(os.path.join(BUTTONS_DIR, "encrypt_default.png"))
        encrypt_btn_icon = QIcon(pixmap)
        self.encrypt_btn.setIcon(encrypt_btn_icon)
        self.encrypt_btn.setIconSize(pixmap.size())
        self.encrypt_btn.setGeometry(33, 402, 317, 63)
        self.encrypt_btn.pressed.connect(self.encrypt_pressed)
        self.encrypt_btn.released.connect(self.encrypt_released)
        self.encrypt_btn.hide()
        
        # кнопка расшифровки
        self.decrypt_btn = QPushButton(self)
        pixmap = QPixmap(os.path.join(BUTTONS_DIR, "decrypt_default.png"))
        decrypt_btn_icon = QIcon(pixmap)
        self.decrypt_btn.setIcon(decrypt_btn_icon)
        self.decrypt_btn.setIconSize(pixmap.size())
        self.decrypt_btn.setGeometry(33, 402, 317, 63)
        self.decrypt_btn.pressed.connect(self.decrypt_pressed)
        self.decrypt_btn.released.connect(self.decrypt_released)
        self.decrypt_btn.hide()
        
        # # кнопка помощи и общей информации о программе (H)
        self.help_btn = QPushButton(self)
        pixmap = QPixmap(os.path.join(BUTTONS_DIR, "help_default.png"))
        help_btn_icon = QIcon(pixmap)
        self.help_btn.setIcon(help_btn_icon)
        self.help_btn.setIconSize(pixmap.size())
        self.help_btn.setGeometry(377, 54, 78, 78)
        self.help_btn.pressed.connect(self.help_pressed)
        self.help_btn.released.connect(self.help_released)
        
        # # кнопка настроек (ST)
        self.settings_btn = QPushButton(self)
        pixmap = QPixmap(os.path.join(BUTTONS_DIR, "settings_default.png"))
        settings_btn_icon = QIcon(pixmap)
        self.settings_btn.setIcon(settings_btn_icon)
        self.settings_btn.setIconSize(pixmap.size())
        self.settings_btn.setGeometry(377, 142, 78, 78)
        self.settings_btn.pressed.connect(self.settings_pressed)
        self.settings_btn.released.connect(self.settings_released)
        
        # # кнопка выбора файла (CG)
        self.change_btn = QPushButton(self)
        pixmap = QPixmap(os.path.join(BUTTONS_DIR, "change_default.png"))
        change_btn_icon = QIcon(pixmap)
        self.change_btn.setIcon(change_btn_icon)
        self.change_btn.setIconSize(pixmap.size())
        self.change_btn.setGeometry(377, 230, 78, 78)
        self.change_btn.pressed.connect(self.change_pressed)
        self.change_btn.released.connect(self.change_released)
        
        # # кнопка для показа логов (LG)
        self.mode_btn = QPushButton(self)
        pixmap = QPixmap(os.path.join(BUTTONS_DIR, "mode_default.png"))
        mode_btn_icon = QIcon(pixmap)
        self.mode_btn.setIcon(mode_btn_icon)
        self.mode_btn.setIconSize(pixmap.size())
        # self.mode_btn.setGeometry(377, 318, 78, 78) старое
        self.mode_btn.setGeometry(377, 406, 78, 78)
        self.mode_btn.pressed.connect(self.mode_pressed)
        self.mode_btn.released.connect(self.mode_released)
        
        # # кнопка для списка зашифрованных файлов (LS)
        self.list_btn = QPushButton(self)
        pixmap = QPixmap(os.path.join(BUTTONS_DIR, "list_default.png"))
        list_btn_icon = QIcon(pixmap)
        self.list_btn.setIcon(list_btn_icon)
        self.list_btn.setIconSize(pixmap.size())
        # self.list_btn.setGeometry(377, 406, 78, 78) старое
        self.list_btn.setGeometry(377, 318, 78, 78)
        self.list_btn.pressed.connect(self.list_pressed)
        self.list_btn.released.connect(self.list_released)
        
        # ссылки на функциональные кнопки окна
        self.links_funcs_btns = (
            self.help_btn, self.settings_btn, self.change_btn,
            self.mode_btn, self.list_btn,
        )
            
    def init_sound_effects(self) -> None:
        # звуковые эффекты кнопок
        self.btn_press_eff = sound_getter("button.wav")
        self.close_collapse_btn_press_eff = sound_getter("collapse_close_button.wav")
        
    def enable_btns(self) -> None:
        """Разблокирует функциональные кнопки"""
        for btn in self.links_funcs_btns:
            btn.setEnabled(True)
      
    def disable_btns(self) -> None:
        """Блокирует функциональные кнопки"""
        for btn in self.links_funcs_btns:
            btn.setEnabled(False)

    def list_pressed(self) -> None:
        """Запуска функции кнопки list в момент нажатия"""
        self.btn_press_eff.play()
        self.list_btn.setIcon(button_icon_getter("list_pressed.png"))

    def list_released(self) -> None:
        """Запуска функции кнопки list после нажатия"""
        self.list_btn.setIcon(button_icon_getter("list_default.png")) 
    
    def mode_pressed(self) -> None:
        """Запуска функции кнопки mode в момент нажатия"""
        self.btn_press_eff.play()
        self.mode_btn.setIcon(button_icon_getter("mode_pressed.png"))
    
    def mode_released(self) -> None:
        """Запуска функции кнопки mode после нажатия"""
        self.mode_btn.setIcon(button_icon_getter("mode_default.png")) 
        self.controller.change_mode()
    
    def change_pressed(self) -> None:
        """Запуска функции кнопки change в момент нажатия"""
        self.btn_press_eff.play()
        self.change_btn.setIcon(button_icon_getter("change_pressed.png"))
    
    def change_released(self) -> None:
        """Запуска функции кнокпи change после нажатия"""
        self.change_btn.setIcon(button_icon_getter("change_default.png"))
        self._delete_widgets()
        if self.encrypt_btn.isVisible():
            self.encrypt_btn.hide()
        elif self.decrypt_btn.isVisible():
            self.decrypt_btn.hide()
        if self.mode_btn.isVisible():
            self.mode_btn.setEnabled(False)
        self.enter_btn.setEnabled(True)
        self.controller.change()
        
    def settings_pressed(self) -> None:
        """Запуска функции кнопки settings в момент нажатия"""
        self.btn_press_eff.play()
        self.settings_btn.setIcon(button_icon_getter("settings_pressed.png"))
    
    def settings_released(self) -> None:
        """Запуска функции кнопки settings после нажатия"""
        self.settings_btn.setIcon(button_icon_getter("settings_default.png")) 
        
    def help_pressed(self) -> None:
        """Запуск функции кнопки help в момент нажатия"""
        self.btn_press_eff.play()
        self.help_btn.setIcon(button_icon_getter("help_pressed.png"))        
        
    def help_released(self) -> None:
        """Запуска функции кнопки help после нажатия"""
        self.help_btn.setIcon(button_icon_getter("help_default.png"))        
    
    def close_pressed(self) -> None:
        """Выключение программы"""
        self.close_collapse_btn_press_eff.play()
        self.close_btn.setIcon(button_icon_getter("close_pressed.png"))

    def close_released(self) -> None:
        self.close_btn.setIcon(button_icon_getter("close_default.png"))
        QTimer.singleShot(80, lambda: self.close())
    
    def collapse_pressed(self) -> None:
        """Сворачивание программы"""
        self.close_collapse_btn_press_eff.play()
        self.collapse_btn.setIcon(button_icon_getter("collapse_pressed.png"))

    def collapse_released(self) -> None:
        self.collapse_btn.setIcon(button_icon_getter("collapse_default.png"))
        self.showMinimized()
    
    def enter_pressed(self) -> None:
        """Запуска функции кнопки enter в момент нажатия"""
        self.btn_press_eff.play()
        self.enter_btn.setIcon(button_icon_getter("enter_pressed.png"))
        
    def enter_released(self) -> None:
        """Запуск функции кнопки enter после нажатия"""
        self.enter_btn.setIcon(button_icon_getter("enter_default.png"))
        # if self.current_event is Function.CHANGE:
        #     self.current_event = Function.CHECK_FILE
        self.controller.callback_redirection()

    def encrypt_pressed(self) -> None:
        """Запуск функции кнопки Encrypt"""
        self.btn_press_eff.play()
        self.encrypt_btn.setIcon(button_icon_getter("encrypt_pressed.png"))
        
    def encrypt_released(self) -> None:
        """Запуск функции кнопки Encrypt после нажатия"""
        print("ENCRYPT_RELEASED")
        self.encrypt_btn.setIcon(button_icon_getter("encrypt_default.png"))
        self.controller.current_event = Function.ENCRYPT
        self.controller.callback_redirection()
        
    def decrypt_pressed(self) -> None:
        """Запуск функции кнопки Decrypt"""
        self.btn_press_eff.play()
        self.decrypt_btn.setIcon(button_icon_getter("decrypt_pressed.png"))
        
    def decrypt_released(self) -> None:
        """Запуск функции кнопки Decrypt после нажатия"""
        self.decrypt_btn.setIcon(button_icon_getter("decrypt_default.png"))
        self.controller.current_event = Function.DECRYPT
        self.controller.callback_redirection()

    def _delete_widgets(self):
        """Отчистка виджетов"""
        attrs = ("filename", "msg", "pswd_field", "status")
        for attr in attrs:
            if hasattr(self, attr):
                obj = getattr(self, attr)
                obj.setParent(None)
                delattr(self, attr)

    def set_mode_widgets(self) -> None:
        """Меняет кнопку функции зашифровки/раcшифровки"""
        if self.encrypt_btn.isVisible():
            self.encrypt_btn.hide()
            self.decrypt_btn.show()
        else:
            self.decrypt_btn.hide()
            self.encrypt_btn.show()
    
    def _set_change_file_widgets(self, title: str, status: str='') -> None:
        self._delete_widgets()
        self.msg = QLabel(self.monitor)
        self.msg.setText(title)
        self.msg.setGeometry(8, 10, 300, 30)
        self.msg.setStyleSheet("font-weight: bold;")
        self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg.setFont(font_getter(self.font_family, 12))
        self.msg.show()
        # текстовое поле для названия файла
        self.filename = QPlainTextEdit(self.monitor)
        self.filename.setReadOnly(True)
        self.filename.setPlainText(self.file_manager.currentItem().text(0))
        self.filename.setGeometry(8, 35, 300, 260)
        # переноси строки вниз
        self.filename.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.filename.setStyleSheet(style_getter("filename_field.css"))
        self.filename.setFont(font_getter(self.font_family, 12))
        self.filename.show()
        self.status = QLabel(self.monitor)
        self.status.setText(f"--------------------------------\n{status}")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setFont(font_getter(self.font_family, 12))
        self.status.setGeometry(8, 230, 300, 50)
        self.status.setStyleSheet("font-weight: bold;")
        self.status.show()
        self.mode_btn.setEnabled(True)
    
    def set_tree_widgets(self) -> None:
        """Установка виджетов дерева файлов"""
        self._delete_widgets()
        self.controller.file_manager.set_tree()
    
    def set_authentication_widgets(self, title: str='', is_clear: bool=False) -> None:
        """Установка виджетов аутентификации"""
        self._delete_widgets()
        if not is_clear:
            self.msg = QLabel(self.monitor)
            self.msg.setText(title)
            self.msg.setGeometry(0, 0, 317, 40)
            self.msg.setStyleSheet(style_getter("monitor_title.css"))
            self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.msg.setFont(font_getter(self.font_family, 12))
            self.msg.show()
            self.pswd_field = QLineEdit(self.monitor)
            self.pswd_field.setFont(font_getter(self.font_family, 12))
            self.pswd_field.setGeometry(10, 40, 297, 20)
            self.enter_btn.setEnabled(False)
            self.pswd_field.textChanged.connect(self._change_text)
            self.pswd_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.pswd_field.setStyleSheet(style_getter("password_field.css"))
            self.pswd_field.setEchoMode(QLineEdit.EchoMode.Password)
            # создаем таймер показа пароля
            self.pswd_field.setFocus()
            self.pswd_field.show()
        else:
            self.monitor.show()
            self.enable_btns()
            # кнопку изменения режима крипторафии пока блокируем
            self.mode_btn.setEnabled(False)
            self.enter_btn.setEnabled(False)
    
    def set_change_file_widgets(self, title: str='', status: str='') -> None:
        """Установка виджетов выбранного файла"""
        self._set_change_file_widgets(title, status)
        if self.enter_btn.isVisible():
            self.enter_btn.setEnabled(False)
            self.encrypt_btn.show()

    def set_cryptography_success_widgets(self, title: str='', status: str='') -> None:
        self._set_change_file_widgets(title, status)
        # if self.encrypt_btn.isVisible():
        #     self.encrypt_btn.setDisabled(True)
        # elif self.decrypt_btn.isVisible():
        #     self.decrypt_btn.setDisabled(True)
    
    def set_cryptography_failure_widgets(self, title: str='', status: str='') -> None:
        self._set_change_file_widgets(title, status)   
        # if not self.encrypt_btn.isVisible():
        #     self.encrypt_btn.setEnabled(True)
        # elif not self.decrypt_btn.isVisible():
        #     self.decrypt_btn.setEnabled(True)

    def _change_text(self) -> None:
        """
            Реагирование текстового поля для пароля при вводе хотябы одного симола.
            Тогда кнопка Enter разблокируется.
        """
        if len(self.pswd_field.text()) > 0:
            self.enter_btn.setEnabled(True)
        else:
            self.enter_btn.setEnabled(False)

    def get_input_password(self) -> str:
        """Возвращает пароль из текстового поля pswd_field"""
        password = self.pswd_field.text()
        if password:
            return password
        raise ValueError("Ты запрашиваешь пароль хотя он еще не введен!")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Для перемещения окна мышкой — шаг 1"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._mouse_old_pos = event.globalPosition().toPoint()
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Для перемещения окна мышкой — шаг 2"""
        if hasattr(self, "_mouse_old_pos") and self._mouse_old_pos is not None:
            delta = event.globalPosition().toPoint() - self._mouse_old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._mouse_old_pos = event.globalPosition().toPoint()
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Для перемещения окна мышкой — шаг 3"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._mouse_old_pos = None
            event.accept()
        else:
            event.ignore()

        






