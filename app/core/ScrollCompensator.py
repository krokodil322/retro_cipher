from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtGui import QFont, QFontMetrics
import os


class ScrollCompensator:
    """Класс компенсирующий длину нижнего скроллбара"""
    def __init__(self):
        """
            словарь expanded хранит пути 
            с раскрытыми папками имеют такую структуру:   
            {str: int} - {"expanded_dir": max_len_filename}
        """
        self.expanded = {}
        self.font = QFont("IBM 3270")
        self.font_metric = QFontMetrics(self.font)

    @property
    def max_len(self) -> int:
        """Возвращает длину максимально длинного имени файла"""
        if len(self.expanded) > 0:
            key = max(self, key=lambda path: self.expanded[path]["size"])
            return self.expanded[key]["size"]
        return 0
    
    def add_dir(self, path_dir: str, indent) -> None:
        """Добавляет путь к раскрытой папке и ищет файл с самым длинным именем в этой папке"""
        files  = os.listdir(path_dir)
        max_filename = max(files, key=len) if files else ''
        level = len(path_dir.split('/')) + 2
        full_path = os.path.join(path_dir, max_filename)
        pixels = self.font_metric.horizontalAdvance(full_path)
        size = pixels + level + indent + 20
        self.expanded[path_dir] = {"size": size}

    def add_child(self, path_dir: str, obj_dir: QTreeWidgetItem):
        self.expanded[path_dir]["item"] = obj_dir 
    
    def remove_dir(self, path_dir) -> None:
        """Удаляет путь к папке которую уже закрыли"""
        # к сожалению без этого условия не работает
        # так и не понял почему. Походу PyQt
        # что-то шаманит под капотом
        if path_dir in self:
            del self.expanded[path_dir]
    
    def get_subdirs(self, path_dir: str) -> list:
        """Получает всех раскрытых потомков раскрытой папки path_dir"""
        subdirs = []
        for dir_ in self:
            if path_dir in dir_ and path_dir is not dir_:
                subdirs.append((dir_, self.expanded[dir_]["item"]))
        subdirs.reverse()
        return subdirs
    
    def __str__(self):
        return f"[{', '.join(self)}]"
        
    def __iter__(self):
        """Для удобства итерируемся по всем открытым папкам"""
        yield from self.expanded
        
