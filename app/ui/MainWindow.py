from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QTreeWidgetItem, QTreeWidget, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QPixmap, QIcon, QFont, QFontMetrics
from app.core import FileManager, ScrollCompensator
import os


class MainWindow(QMainWindow):
    """Класс главного окна"""
    def __init__(self):
        super().__init__()
        # ссылка на папку с отрисованным интерфейсом
        self._icon_path = r"interface/images"
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
        self.authorization = False
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
    
    def _init_interface(self) -> None:
        """Инициализация кнопок и интерфейса"""
        # главный задний фон
        self.background_1 = QLabel(self)
        self.background_1.setPixmap(QPixmap(r"interface/images/background_1.png"))
        self.background_1.setScaledContents(True)
        self.background_1.setGeometry(0, 0, self.width(), self.height())
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # верхняя панель, где расположены кнопки сворачивания и выключения
        self.top_bar = QLabel(self)
        self.top_bar.setPixmap(QPixmap(r"interface/images/top_panel.png"))
        self.top_bar.setScaledContents(True)
        self.top_bar.setGeometry(14, 12, 441, 34)  # позиция и размер
        
        # шрифт
        self.font = QFont("IBM 3270", 14)
        self.font.setBold(True)
        # тут может быть надпись на верхней панели
        # self.title = QLabel("CryptoFredi_16_bit.exe", self)
        # self.title.setFont(self.font)
        # self.title.move(23, 18)
        # self.title.resize(300, 21)
        # self.title.setStyleSheet("color: rgb(204,36,29);")
        
        # второй задний фон для монитора и кнопки enter
        self.background_2 = QLabel(self)
        self.background_2.setPixmap(QPixmap(r"interface/images/background_2.png"))
        self.background_2.setScaledContents(True)
        self.background_2.setGeometry(14, 54, 355, 430)

        # дисплей на который будет выводится информация для пользователя
        self.monitor = QLabel(self)
        self.monitor.setPixmap(QPixmap(r"interface/images/monitor.png"))
        self.monitor.setScaledContents(True)
        self.monitor.setGeometry(33, 73, 317, 313)
        
        # кнопка сворачивания программы
        self.collapse_btn = QPushButton(self)
        pixmap = QPixmap(r"interface/images/collapse_default.png")
        collapse_btn_icon = QIcon(pixmap)
        self.collapse_btn.setIcon(collapse_btn_icon)
        self.collapse_btn.setIconSize(pixmap.size())
        self.collapse_btn.move(396, 17)   # позиция на окне
        self.collapse_btn.resize(24, 24) # размер кнопки
        self.collapse_btn.pressed.connect(self._function_btn_pressed("collapse"))
        self.collapse_btn.released.connect(self._function_btn_released("collapse"))
        
        # кнопки выключения программы
        self.close_btn = QPushButton(self)
        pixmap = QPixmap(r"interface/images/close_default.png")
        close_btn_icon = QIcon(pixmap)
        self.close_btn.setIcon(close_btn_icon)
        self.close_btn.setIconSize(pixmap.size())
        self.close_btn.move(426, 17)
        self.close_btn.resize(24, 24)
        self.close_btn.pressed.connect(self._function_btn_pressed("close"))
        self.close_btn.released.connect(self._function_btn_released("close"))
        
        # кнопка ввода
        self.enter_btn = QPushButton(self)
        pixmap = QPixmap(r"interface/images/enter_default.png")
        enter_btn_icon = QIcon(pixmap)
        self.enter_btn.setIcon(enter_btn_icon)
        self.enter_btn.setIconSize(pixmap.size())
        self.enter_btn.move(33, 402)
        self.enter_btn.resize(317, 63)
        self.enter_btn.pressed.connect(self._function_btn_pressed("enter"))
        self.enter_btn.released.connect(self._function_btn_released("enter"))
        
        # кнопка помощи и общей информации о программе (H)
        self.help_btn = QPushButton(self)
        pixmap = QPixmap(r"interface/images/help_default.png")
        help_btn_icon = QIcon(pixmap)
        self.help_btn.setIcon(help_btn_icon)
        self.help_btn.setIconSize(pixmap.size())
        self.help_btn.move(377, 54)
        self.help_btn.resize(78, 78)
        self.help_btn.pressed.connect(self._function_btn_pressed("help"))
        self.help_btn.released.connect(self._function_btn_released("help"))
        
        # кнопка настроек (ST)
        self.settings_btn = QPushButton(self)
        pixmap = QPixmap(r"interface/images/settings_default.png")
        settings_btn_icon = QIcon(pixmap)
        self.settings_btn.setIcon(settings_btn_icon)
        self.settings_btn.setIconSize(pixmap.size())
        self.settings_btn.move(377, 142)
        self.settings_btn.resize(78, 78)
        self.settings_btn.pressed.connect(self._function_btn_pressed("settings"))
        self.settings_btn.released.connect(self._function_btn_released("settings"))
        
        # кнопка выбора файла (CG)
        self.change_btn = QPushButton(self)
        pixmap = QPixmap(r"interface/images/change_default.png")
        change_btn_icon = QIcon(pixmap)
        self.change_btn.setIcon(change_btn_icon)
        self.change_btn.setIconSize(pixmap.size())
        self.change_btn.move(377, 230)
        self.change_btn.resize(78, 78)
        self.change_btn.pressed.connect(self._function_btn_pressed("change"))
        self.change_btn.released.connect(self._function_btn_released("change"))
        
        # кнопка для показа логов (LG)
        self.logs_btn = QPushButton(self)
        pixmap = QPixmap(r"interface/images/logs_default.png")
        logs_btn_icon = QIcon(pixmap)
        self.logs_btn.setIcon(logs_btn_icon)
        self.logs_btn.setIconSize(pixmap.size())
        self.logs_btn.move(377, 318)
        self.logs_btn.resize(78, 78)
        self.logs_btn.pressed.connect(self._function_btn_pressed("logs"))
        self.logs_btn.released.connect(self._function_btn_released("logs"))
        
        # кнопка для списка зашифрованных файлов (LS)
        self.list_btn = QPushButton(self)
        pixmap = QPixmap(r"interface/images/list_default.png")
        list_btn_icon = QIcon(pixmap)
        self.list_btn.setIcon(list_btn_icon)
        self.list_btn.setIconSize(pixmap.size())
        self.list_btn.move(377, 406)
        self.list_btn.resize(78, 78)
        self.list_btn.pressed.connect(self._function_btn_pressed("list"))
        self.list_btn.released.connect(self._function_btn_released("list"))
    
    def _function_btn_released(self, function: str) -> None:
        """
            Полиморфная функция которая отвечает за НЕ зажатые кнопки
            Главным образом работает с атрибутом functions_btns - словарь
            в котором по именам привязаны функции к кнопкам.
            
            Функция меняет иконку на НЕ зажатаю когда кнопку отпускает.
            Вызывает функцию привязанную к кнопке.
        """
        def wrapper():
            relative_path = os.path.join(self._icon_path, function + "_default")
            pixmap = QPixmap(relative_path)
            self.__dict__[function + "_btn"].setIcon(QIcon(pixmap)) 
            if function in self._functions_btns:
                self._functions_btns[function]()
        return wrapper
        
    def _function_btn_pressed(self, function: str) -> None:
        def wrapper():
            relative_path = os.path.join(self._icon_path, function + "_pressed")
            pixmap = QPixmap(relative_path)
            self.__dict__[function + "_btn"].setIcon(QIcon(pixmap)) 
        return wrapper
        
    def close_(self) -> None:
        """Выключение программы"""
        self.close()
    
    def collapse(self) -> None:
        """Сворачивание программы"""
        self.showMinimized()
    
    def enter(self) -> None:
        """Ввод. Главным образом - ввод пароля"""
        print("enter")
        
    def help_(self) -> None:
        """Кнопка помощи"""
        print("help")
    
    def settings(self) -> None:
        """Кнопка настроек"""
        print("settings")
        
    def change(self) -> None:
        """Кнопка выбора файла для шифроки / разшифровки"""
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
        self.tree.setStyleSheet("""
            QTreeView {
                background: transparent;
                border: none;
                color: black;
                font-family: IBM 3270;
                font-size: 12pt;
                font-weight: bold;
            }
            QTreeView::branch {
                background: transparent;
            }
            QTreeView::item {
                background: transparent;
            }
        
            /* Вертикальный скроллбар */
            QScrollBar:vertical {
                border: none;
                background: rgba(0,0,0,50);
                width: 8px;
                margin: 0px 0px 0px 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgb(39,107,3);
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;  /* скрыть стрелки */
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        
            /* Горизонтальный скроллбар */
            QScrollBar:horizontal {
                border: none;
                background: rgba(0,0,0,50);
                height: 8px;
                margin: 0px 0px 0px 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: rgb(39,107,3);
                min-width: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;  /* скрыть стрелки */
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
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
        print("logs")
        
    def list_(self) -> None:
        """кнопка списка зашифрованных файлов LS"""
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
    
        






