from PyQt6.QtWidgets import QTreeWidgetItem, QTreeWidget, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QRect, QSize, QUrl, Qt
from PyQt6.QtMultimedia import QSoundEffect

from app.core.getters import style_getter, sound_getter
from app.core import CacheManager

from ctypes import windll
import string
import os



class FileManager:
    def __init__(self, monitor: QLabel):
        """monitor - это виджет куда будет установлено дерево файлов"""
        self.tree = QTreeWidget()
        self.monitor = monitor
        self.drives = []
        self.tree_expand_eff: QSoundEffect = sound_getter("tree_expand.wav")
        self.cache_manager = CacheManager()
    
    def _clear_tree(self) -> None:
        # эта часть нужна чтобы обновить дерево файлов
        # при помторном нажатии на кнопку change
        layout = self.monitor.layout()
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                child = item.widget()
                if child is not None:
                    child.setParent(None)
            # отвязываем и удаляем layout
            QWidget().setLayout(layout)
    
    def set_tree(self):
        # если дерево уже показно юзеру
        # но он заново нажал change, то нам следует обновить его
        if self.monitor.layout():
            self.drives = []
            self._clear_tree()
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
        self.tree.setStyleSheet(style_getter("tree_style.css"))
        # настройка дерева
        # убираем выделение фокуса
        self.tree.setFocusPolicy(Qt.FocusPolicy.NoFocus)
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
        self.font_metric = (self.tree.font())
        # Создаём вспомогательный контейнер для монитора
        monitor_layout = QVBoxLayout()
        # self.monitor.setParent(None)
        self.monitor.setLayout(monitor_layout)
        monitor_layout.setContentsMargins(0, 0, 0, 0)
        monitor_layout.addWidget(container)
         # Добавляем все диски
        self.add_drives()
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
            # self._scroll_width_compensator.add_dir(path, self.tree.indentation())
            # self._scroll_width_compensator.add_child(path, item)
            # print(f"EXPANDED: {self._scroll_compensator.expanded}")
            for entry in files:
                full_path = os.path.join(path, entry)
                child = QTreeWidgetItem([entry, full_path])
                # Если это папка — добавляем индикатор
                if os.path.isdir(full_path):
                    child.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
                item.addChild(child)
            # scroll_size = self._scroll_width_compensator.max_len
            # self.tree.setColumnWidth(0, scroll_size)
            # пересчет ширины. ИМБА!
            self.tree.resizeColumnToContents(0)
        # у некоторых папок нету доступа и вышибает пробку по этому типу
        except PermissionError:
            pass

    def on_item_collapsed(self, item) -> None:
        self.tree_expand_eff.play()
        # path = item.text(1).replace('/', '\\')
        # subdirs = self._scroll_width_compensator.get_subdirs(path)
        # for subdir, item in subdirs:
        #     self._scroll_width_compensator.remove_dir(subdir)
        self.tree.collapseItem(item)
        # scroll_size = self._scroll_width_compensator.max_len
        # print(f"COLLAPSED: {self._scroll_compensator.expanded}")
        # self.tree.setColumnWidth(0, scroll_size)
        self.tree.resizeColumnToContents(0)
    
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
    
    def check_file(self) -> bool:
        item = self.tree.currentItem()
        if item:
            path = item.text(1)
            return self.cache_manager.check_path_in_cache(path)
                