from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QPlainTextEdit, QTreeWidgetItem, QTreeWidget, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QSize, QRect, QUrl, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QFontMetrics, QPalette, QColor, QPainter, QTextCursor
from PyQt5.QtMultimedia import QSoundEffect

from playsound import playsound
from time import sleep
import threading
import json
import os

from app.core import FileManager, ScrollCompensator, Cipher
from app.paths import BACKGROUNDS_DIR, SOUNDS_DIR, STYLES_DIR, BUTTONS_DIR, CONFIG_DIR, ICONS_DIR


from PyQt5.QtWidgets import QTextEdit, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter

from PyQt5.QtWidgets import QTextEdit, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap



class ImageCursorTextEdit(QTextEdit):
    def __init__(self, cursor_image_path, parent=None, max_len: int=30):
        super().__init__(parent)
        # отключаем стандартный курсор
        self.setCursorWidth(0)
        # QLabel-курсор поверх QTextEdit
        self.cursor_label = QLabel(self.viewport())
        self.cursor_label.setPixmap(QPixmap(cursor_image_path))
        self.cursor_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.cursor_label.hide()
        # Таймер мигания
        self.cursor_visible = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.toggle_cursor)
        self.timer.start(500)
        # Слежение за позицией курсора
        self.cursorPositionChanged.connect(self.update_cursor_pos)
        self.textChanged.connect(self.update_cursor_pos)
        # ограничение длины вводимого пароля равен 30 символам
        self.max_len = max_len
        # сюда будем записывать пароль
        self.password = ''

    def toggle_cursor(self):
        if not self.hasFocus():
            self.cursor_label.hide()
            return
        self.cursor_visible = not self.cursor_visible
        self.cursor_label.setVisible(self.cursor_visible)

    def update_cursor_pos(self):
        """Перемещает QLabel-курсор в позицию QTextCursor."""
        cr = self.cursorRect()
        if cr.isNull():
            return
        pixmap = self.cursor_label.pixmap()
        if pixmap is None or pixmap.isNull():
            return
        # вычисляем положение курсора по базовой линии текста
        baseline_offset = int(self.fontMetrics().ascent() * 0.1)
        x = cr.left()
        y = cr.bottom() - pixmap.height() - baseline_offset
        # Обновляем позицию и поднимаем курсор на передний план
        self.cursor_label.move(x, y)
        self.cursor_label.raise_()
        if self.hasFocus():
            self.cursor_label.show()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.cursor_label.show()
        self.update_cursor_pos()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.cursor_label.hide()
    
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) or event.text() == ' ':
            # игнорируем Enter
            event.ignore()
            return None
        # Проверяем длину перед вводом
        if len(self.toPlainText()) >= self.max_len and event.text():
            # Разрешаем только Backspace, Delete, стрелки и т.п.
            if event.key() not in (Qt.Key_Backspace, Qt.Key_Delete, Qt.Key_Left, Qt.Key_Right):
                # игнорируем ввод новых символов
                return None
        if event.key() != Qt.Key_Backspace:
            self.password += event.text()
        else:
            if self.password:
                self.password = self.password[:-1]
        # отображаем звёздочки вместо реальных символов
        self.setPlainText("*" * len(self.password))
    
        # курсор всегда в конце
        cursor = self.textCursor()
        cursor.movePosition(cursor.End)
        self.setTextCursor(cursor)

    def insertFromMimeData(self, source):
        # предотвращаем вставку многострочного текста
        text = source.text().replace("\n", " ").replace("\r", "")
        self.insertPlainText(text)


class MainWindow(QMainWindow):
    """Класс главного окна"""
    def __init__(self):
        super().__init__()
        # ссылка на папку с отрисованным интерфейсом
        self.resize(467, 496)
        # инициализация кнопок
        self._init_interface()
        # связываем объекты кнопок с именами
        # для последущего вызова их функций
        # в полиморфных методах _function_btn_released и
        # _function_btn_pressed
        self._functions_btns = {
            "collapse": self.collapse, "close": self.close_,
            "enter": self.enter, "help": self.help_,
            "settings": self.settings, "change": self.change,
            "logs": self.logs, "list": self.list_,
        }
        # Для хранения позиции мыши
        # этот атрибут нужен, ибо у данного приложения
        # реализовано кастомное окно, а для этого нужно
        # отключить базовые фишки окна PyQt, к сожалению
        # отвечает за перетаскивание окна кнопкой мыши
        self._old_pos = None
        # авторизирован ли пользователь
        # ввод пароля там тырым пырым
        self.is_auth = False
        # зарегестрирован ли пользователь
        # определяется есть файл json с хэшэм пароля
        self.is_regist = False
        # повтор для ввода пароля, дабы подтветрдить
        self.is_retry = False
        # компенастор нижнего скроллбара
        self._scroll_width_compensator = None
        # файловая модель
        self.file_model = None
        # дерево файлов
        self.tree = None
        # измеритель шрифтаэ
        self.font_metric = None
        # файловый менеджер
        self.file_manager = None
        # поле ввода пароля
        self.pswd_field = None
        # пароль
        self.password = None
        # self._authorization()
        self.set_pswd_widgets()
        self._disable_btns()
        
    def _init_interface(self, theme: str="retro_1") -> None:
        """Инициализация кнопок и интерфейса"""
        themes = {
            "retro_1": {
                "background_1": "background_1.png",
                "top_bar": "top_panel.png",
                "background_2": "background_2.png",
                "monitor": ""
            }
        }
        
        # главный задний фон
        self.background_1 = QLabel(self)
        self.background_1.setPixmap(QPixmap(os.path.join(BACKGROUNDS_DIR, "background_1.png")))
        self.background_1.setScaledContents(True)
        self.background_1.setGeometry(0, 0, self.width(), self.height())
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # верхняя панель, где расположены кнопки сворачивания и выключения
        self.top_bar = QLabel(self)
        self.top_bar.setPixmap(QPixmap(os.path.join(BACKGROUNDS_DIR, "top_panel.png")))
        self.top_bar.setScaledContents(True)
        self.top_bar.setGeometry(14, 12, 441, 34)  # позиция и размер
        
        # тут может быть надпись на верхней панели
        # self.title = QLabel("CryptoFredi_16_bit.exe", self)
        # self.title.setFont(self.font)
        # self.title.move(23, 18)
        # self.title.resize(300, 21)
        # self.title.setStyleSheet("color: rgb(204,36,29);")
        
        # второй задний фон для монитора и кнопки enter
        self.background_2 = QLabel(self)
        self.background_2.setPixmap(QPixmap(os.path.join(BACKGROUNDS_DIR, "background_2.png")))
        self.background_2.setScaledContents(True)
        self.background_2.setGeometry(14, 54, 355, 430)

        # дисплей на который будет выводится информация для пользователя
        self.monitor = QLabel(self)
        self.monitor.setPixmap(QPixmap(os.path.join(BACKGROUNDS_DIR, "monitor.png")))
        self.monitor.setScaledContents(True)
        self.monitor.setGeometry(33, 73, 317, 313)
        
        # текстовое поле монитора
        self.monitor_field = QWidget(self)
        self.monitor_field.setGeometry(33, 73, 317, 313)
        self.monitor_field.setStyleSheet("background: transparent;")
        self.monitor_field.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.monitor_field.setStyleSheet("background-repeat: no-repeat; background-position: center;")
        
        # кнопка сворачивания программы
        self.collapse_btn = QPushButton(self)
        pixmap = QPixmap(os.path.join(BUTTONS_DIR, "collapse_default.png"))
        collapse_btn_icon = QIcon(pixmap)
        self.collapse_btn.setIcon(collapse_btn_icon)
        self.collapse_btn.setIconSize(pixmap.size())
        self.collapse_btn.move(396, 17)   # позиция на окне
        self.collapse_btn.resize(24, 24) # размер кнопки
        self.collapse_btn.pressed.connect(self._function_btn_pressed("collapse"))
        self.collapse_btn.released.connect(self._function_btn_released("collapse"))
        
        # кнопки выключения программы
        self.close_btn = QPushButton(self)
        pixmap = QPixmap(os.path.join(BUTTONS_DIR, "close_default.png"))
        close_btn_icon = QIcon(pixmap)
        self.close_btn.setIcon(close_btn_icon)
        self.close_btn.setIconSize(pixmap.size())
        self.close_btn.move(426, 17)
        self.close_btn.resize(24, 24)
        self.close_btn.pressed.connect(self._function_btn_pressed("close"))
        self.close_btn.released.connect(self._function_btn_released("close"))
        
        # кнопка ввода
        self.enter_btn = QPushButton(self)
        pixmap = QPixmap(os.path.join(BUTTONS_DIR, "enter_default.png"))
        enter_btn_icon = QIcon(pixmap)
        self.enter_btn.setIcon(enter_btn_icon)
        self.enter_btn.setIconSize(pixmap.size())
        self.enter_btn.move(33, 402)
        self.enter_btn.resize(317, 63)
        self.enter_btn.pressed.connect(self._function_btn_pressed("enter"))
        self.enter_btn.released.connect(self._function_btn_released("enter"))
        
        # кнопка помощи и общей информации о программе (H)
        self.help_btn = QPushButton(self)
        pixmap = QPixmap(os.path.join(BUTTONS_DIR, "help_default.png"))
        help_btn_icon = QIcon(pixmap)
        self.help_btn.setIcon(help_btn_icon)
        self.help_btn.setIconSize(pixmap.size())
        self.help_btn.move(377, 54)
        self.help_btn.resize(78, 78)
        self.help_btn.pressed.connect(self._function_btn_pressed("help"))
        self.help_btn.released.connect(self._function_btn_released("help"))
        
        # кнопка настроек (ST)
        self.settings_btn = QPushButton(self)
        pixmap = QPixmap(os.path.join(BUTTONS_DIR, "settings_default.png"))
        settings_btn_icon = QIcon(pixmap)
        self.settings_btn.setIcon(settings_btn_icon)
        self.settings_btn.setIconSize(pixmap.size())
        self.settings_btn.move(377, 142)
        self.settings_btn.resize(78, 78)
        self.settings_btn.pressed.connect(self._function_btn_pressed("settings"))
        self.settings_btn.released.connect(self._function_btn_released("settings"))
        
        # кнопка выбора файла (CG)
        self.change_btn = QPushButton(self)
        pixmap = QPixmap(os.path.join(BUTTONS_DIR, "change_default.png"))
        change_btn_icon = QIcon(pixmap)
        self.change_btn.setIcon(change_btn_icon)
        self.change_btn.setIconSize(pixmap.size())
        self.change_btn.move(377, 230)
        self.change_btn.resize(78, 78)
        self.change_btn.pressed.connect(self._function_btn_pressed("change"))
        self.change_btn.released.connect(self._function_btn_released("change"))
        
        # кнопка для показа логов (LG)
        self.logs_btn = QPushButton(self)
        pixmap = QPixmap(os.path.join(BUTTONS_DIR, "logs_default.png"))
        logs_btn_icon = QIcon(pixmap)
        self.logs_btn.setIcon(logs_btn_icon)
        self.logs_btn.setIconSize(pixmap.size())
        self.logs_btn.move(377, 318)
        self.logs_btn.resize(78, 78)
        self.logs_btn.pressed.connect(self._function_btn_pressed("logs"))
        self.logs_btn.released.connect(self._function_btn_released("logs"))
        
        # кнопка для списка зашифрованных файлов (LS)
        self.list_btn = QPushButton(self)
        pixmap = QPixmap(os.path.join(BUTTONS_DIR, "list_default.png"))
        list_btn_icon = QIcon(pixmap)
        self.list_btn.setIcon(list_btn_icon)
        self.list_btn.setIconSize(pixmap.size())
        self.list_btn.move(377, 406)
        self.list_btn.resize(78, 78)
        self.list_btn.pressed.connect(self._function_btn_pressed("list"))
        self.list_btn.released.connect(self._function_btn_released("list"))
        
        self.btn_press_eff = QSoundEffect()
        self.btn_press_eff.setSource(QUrl.fromLocalFile(os.path.join(SOUNDS_DIR, "button.wav")))
        self.tree_expand_eff = QSoundEffect()
        self.tree_expand_eff.setSource(QUrl.fromLocalFile(os.path.join(SOUNDS_DIR, "tree_expand.wav")))
        self.close_collapse_btn_press_eff = QSoundEffect()
        self.close_collapse_btn_press_eff.setSource(
            QUrl.fromLocalFile(os.path.join(SOUNDS_DIR, "collapse_close_button.wav"))
        )
        self._btns = [self.help_btn, self.settings_btn, self.change_btn, self.logs_btn, self.list_btn]
    
    def set_pswd_widgets(self, flag: str="default") -> None:
        if not hasattr(self, "pswd_msg"):
            if os.path.exists(os.path.join(CONFIG_DIR, "config.json")):
                self.pswd_msg = QLabel("Введи пароль: ", self.monitor_field)
            else:
                self.pswd_msg = QLabel("Придумай пароль: ", self.monitor_field)
        self.pswd_msg.setStyleSheet("""
            color: black;
            font-family: 'IBM 3270';
            font-size: 12pt;
            background: transparent;
        """)
        self.pswd_msg.move(20, 10)
        self.pswd_msg.resize(300, 15)
        # Поле ввода (наш кастомный QTextEdit)
        cursor_path = os.path.join(ICONS_DIR, "cursor.png")
        if self.pswd_field:
            # обновляем поле пароля(убираем старые введенные данные)
            self.pswd_msg.setText('')
            self.pswd_field.password = ''
            # устанавливаем старый фокус каретки на место
            self.pswd_field.setFocus()
        self.pswd_field = ImageCursorTextEdit(cursor_path, parent=self.monitor_field)
        self.pswd_field.setGeometry(20, 30, 280, 40)
        self.pswd_field.setStyleSheet("""
            QTextEdit {
                background: transparent;
                color: black;
                border: none;
                font-family: 'IBM 3270';
                font-size: 12pt;
            }
        """)
        self.pswd_field.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.pswd_field.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.pswd_field.setFocus()
                
    def _enable_btns(self) -> None:
        """Разблокирует функциональные кнопки"""
        if self.is_auth:
            for btn in self._btns:
                btn.setEnabled(True)
        
    def _disable_btns(self) -> None:
        """Блокирует функциональные кнопки"""
        for btn in self._btns:
            btn.setEnabled(False)
    
    def _function_btn_released(self, function: str) -> None:
        """
            Полиморфная функция которая отвечает за НЕ зажатые кнопки
            Главным образом работает с атрибутом functions_btns - словарь
            в котором по именам привязаны функции к кнопкам.
            
            Функция меняет иконку на НЕ зажатаю когда кнопку отпускает.
            Вызывает функцию привязанную к кнопке.
        """
        def wrapper():
            relative_path = os.path.join(BUTTONS_DIR, function + "_default")
            pixmap = QPixmap(relative_path)
            self.__dict__[function + "_btn"].setIcon(QIcon(pixmap)) 
            if function in self._functions_btns:
                self._functions_btns[function]()
        return wrapper
        
    def _function_btn_pressed(self, function: str) -> None:
        def wrapper():
            relative_path = os.path.join(BUTTONS_DIR, function + "_pressed")
            pixmap = QPixmap(relative_path)
            self.__dict__[function + "_btn"].setIcon(QIcon(pixmap)) 
        return wrapper
        
    def close_(self) -> None:
        """Выключение программы"""
        # self.close_collapse_btn_press_eff.play()
        path = os.path.join(SOUNDS_DIR, "collapse_close_button.wav")
        threading.Thread(target=lambda: playsound(path), daemon=True).start()
        # небольшая задержка, дабы звук успел воспроизвестись перед завершением программы
        sleep(0.13)
        self.close()
    
    def collapse(self) -> None:
        """Сворачивание программы"""
        self.close_collapse_btn_press_eff.play()
        self.showMinimized()
    
    def enter(self) -> None:
        """Ввод. Главным образом - ввод пароля"""
        self.btn_press_eff.play()
        if self.tree:
            item = self.tree.currentItem()
            if item:
                print(item.text(1))
        config_path = os.path.join(CONFIG_DIR, "config.json")
        # если папка configa была удалена
        if not os.path.exists(CONFIG_DIR):
            os.mkdir(CONFIG_DIR)
        # если файл configa есть, то регистрация не нужна
        elif os.path.exists(config_path):
            self.is_regist = True
        # процесс регистрации   
        if not self.is_regist: 
            # эта часть срабатыват уже после первого ввода пароля
            # за инициализацю первого ввода отвечает метод set_pswd_widgets
            if not self.is_retry:
                # запрос на повтор ввода пароля, дабы убедиться в том,
                # что юзер его верно ввел
                self.password = self.pswd_field.password
                # меняем статус пароля, говоря, что повтор сработал
                self.is_retry = True
                # обновляем текст на виджетах
                self._update_msgs("Повтори пароль: ")
                # выходим из метода
                return None
            # эта часть срабатывает в самом конце, если
            # повторный ввод пароля совпал, то мы записываем
            # хэш пароля в json файл
            elif self.password == self.pswd_field.password:
                self.password = self.pswd_field.password
                hash_pswd = Cipher.hashing(self.password)
                with open(config_path, 'w', encoding="utf-8") as json_file:
                    config = {"hash_pswd": hash_pswd}
                    json.dump(config, fp=json_file)
                # меняем флаг регистрации чтобы эта ветка больше не срабатывала
                self.is_regist = True
                self._update_msgs("Welcome to the club body!")
                # блокируем ввод пароля(я не знаю как его убрать)
                self.pswd_field.setEnabled(False)
                # выходим из функции
                # тут мы разблокируем все функциональные кнопки, ибо
                # пользователь зашел
                self.pswd_msg.setParent(None)
                self.pswd_field.setParent(None)
                self._enable_btns()
                return None
            # если повтор пароля неверный, то делаем все заново
            else:
                self.password = None
                self.is_retry = False
                self._update_msgs("Введи пароль(не совпали): ")
                return None
        # если юзер уже зареган, крч тут авторизация
        if self.is_regist and not self.is_auth:
            # хэшируем введеный пароль и сравниваем его с хэшэм из jsona
            hash_pswd = Cipher.hashing(self.pswd_field.password)
            with open(config_path, encoding="utf-8") as json_file:
                config = json.load(fp=json_file)
            if hash_pswd == config["hash_pswd"]:
                # в этой ветке разблокируем все кнопки и запускам основную прогу
                self._update_msgs("Пароль подошел, ты красавчик Айзербаджан.")
                self.pswd_field.setEnabled(False)
                self.pswd_msg.setParent(None)
                self.pswd_field.setParent(None)
                self.is_auth = True
                self._enable_btns()
            # если введеный пароль не подошел
            else:
                self._update_msgs("Введи пароль(пароль не подошел): ")
                return None
        
    def _update_msgs(self, msg: str) -> None:
        self.pswd_field.password = ''
        self.pswd_field.setText('')
        self.pswd_msg.setText("")
        self.pswd_msg.setText(msg)
        self.pswd_field.setFocus()
     
    def help_(self) -> None:
        """Кнопка помощи"""
        self.btn_press_eff.play()
        print("help")
    
    def settings(self) -> None:
        """Кнопка настроек"""
        self.btn_press_eff.play()
        print("settings")
        
    def change(self) -> None:
        """Кнопка выбора файла для шифроки / разшифровки"""
        # к сожалению воспроизведение звуков через QSoundEffect
        # в этом методе происходит с задержкой. Попытки реализовать
        # воспроизведение через пул не получилось. PyQt категорически
        # запрещает забивать поток чем то еще. А потому вопсроизводить
        # звук будем через костыль из модулeй playsound и threading
        path = os.path.join(SOUNDS_DIR, "button.wav")
        threading.Thread(target=lambda: playsound(path), daemon=True).start()
        # эта часть нужна чтобы обновить дерево файлов
        # при помторном нажатии на кнопку change
        if self.monitor.layout():
            layout = self.monitor.layout()
            if layout is not None:
                while layout.count():
                    item = layout.takeAt(0)
                    child = item.widget()
                    if child is not None:
                        child.setParent(None)
                # отвязываем и удаляем layout
                QWidget().setLayout(layout)
        # инициализация компенсатора скроллбара
        self._scroll_width_compensator = ScrollCompensator()
        # Создаём вспомогательный контейнер для дерева
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        # дерево файлов
        self.tree = QTreeWidget()
        self.tree.setGeometry(QRect(38, 78, 317, 313))
        # добавляем дерево в вспомогательный контейнер
        container_layout.addWidget(self.tree)
        # задаем нужный стиль для дерева файлов
        with open(os.path.join(STYLES_DIR, "tree_style.css"), encoding="utf-8") as tree_style:
            tree_style = tree_style.read()
            self.tree.setStyleSheet(tree_style)
        # настройка дерева
        # убирает треугольники для раскрытия
        self.tree.setRootIsDecorated(False)
        # скрывает шапку столбцов
        self.tree.setHeaderHidden(True)
        # скрыть колонку "Размер"
        self.tree.setColumnHidden(1, True)
        # скрыть колонку "Тип"
        self.tree.setColumnHidden(2, True)
        # скрыть колонку "Дата изменения"
        self.tree.setColumnHidden(3, True)
        # запрещает запускать программы из дерева дабл кликом
        self.tree.setEnabled(True)
        # Убираем иконки
        self.tree.setIconSize(QSize(0, 0))  
        # измеряем размер дерева через его шрифт
        self.font_metric = QFontMetrics(self.tree.font())
        # Создаём вспомогательный контейнер для монитора
        monitor_layout = QVBoxLayout()
        # self.monitor.setParent(None)
        self.monitor.setLayout(monitor_layout)
        monitor_layout.setContentsMargins(0, 0, 0, 0)
        monitor_layout.addWidget(container)
        # объект файлового менеджера
        self.file_manager = FileManager(self.tree)
         # Добавляем все диски
        self.file_manager.add_drives()
        # Сигнал при раскрытии узла
        self.tree.itemExpanded.connect(self.on_item_expanded)
        self.tree.itemCollapsed.connect(self.on_item_collapsed)

    def on_item_expanded(self, item) -> None:
        """Загружаем содержимое директории при раскрытии"""
        self.tree_expand_eff.play()
        path = item.text(1).replace('/', '\\')
        # Очищаем старые "заглушки"
        item.takeChildren()
        try:
            files = os.listdir(path)
            self._scroll_width_compensator.add_dir(path, self.tree.indentation())
            self._scroll_width_compensator.add_child(path, item)
            for entry in files:
                full_path = os.path.join(path, entry)
                child = QTreeWidgetItem([entry, full_path])
                # Если это папка — добавляем индикатор
                if os.path.isdir(full_path):
                    child.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
                item.addChild(child)
            scroll_size = self._scroll_width_compensator.max_len
            self.tree.setColumnWidth(0, scroll_size)
            # пересчет ширины. ИМБА!
            self.tree.resizeColumnToContents(0)
        except PermissionError:
            pass

    def on_item_collapsed(self, item) -> None:
        self.tree_expand_eff.play()
        path = item.text(1).replace('/', '\\')
        subdirs = self._scroll_width_compensator.get_subdirs(path)
        for subdir, item in subdirs:
            self._scroll_width_compensator.remove_dir(subdir)
            self.tree.collapseItem(item)
        scroll_size = self._scroll_width_compensator.max_len
        self.tree.setColumnWidth(0, scroll_size)
        self.tree.resizeColumnToContents(0)

    def logs(self) -> None:
        """кнопка логов LG"""
        self.btn_press_eff.play()
        print("logs")
        
    def list_(self) -> None:
        """кнопка списка зашифрованных файлов LS"""
        self.btn_press_eff.play()
        print("list")

    def mousePressEvent(self, event):
        """для перемещениия окна мышкой - 1"""
        if event.button() == Qt.LeftButton:
            self._old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        """для перемещениия окна мышкой - 2"""
        if self._old_pos:
            delta = event.globalPos() - self._old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        """для перемещениия окна мышкой - 3"""
        self._old_pos = None
    
        






