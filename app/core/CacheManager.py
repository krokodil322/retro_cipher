from app.paths import ROOT_DIR

import os


class CacheManager:
    """
        Класс отвечающий за функционал кнопки LS, а также проверку вхождения
        любого выбранного юзером файла в список зашифрованных файлов.
        Каждый метод проверяет существует ли cache.txt. Если его не существует,
        то отправляет запрос на его создание.
    """
    def __init__(self):
        # путь к файлу cache, где хранится список всех зашифрованных файлов
        self.cache_path = os.path.join(ROOT_DIR, "cache.txt")

    def create_config(self, default: str='') -> None:
        with open(self.cache_path, 'w', encoding="utf-8") as file:
            file.write(default)

    def check_path_in_cache(self, path) -> bool:
        """
            Проверяет есть ли файл path в файле cache.txt
            Возвращает True, если файл найден, иначе False.
        """
        if not os.path.exists(self.cache_path):
            self.create_config(default=path)
            return False
        with open(self.cache_path, encoding="utf-8") as file:
            for row in file:
                if row.rstrip() == path:
                    return True 
        return False

    def add_file(self, path) -> None:
        """Добавляет в конец файла cache.txt путь к новому зашифрованному файлу"""
        mode = 'a' if os.path.exists(self.cache_path) else 'w'
        with open(self.cache_path, mode, encoding="utf-8") as file:
            file.write(path)

    def remove_file(self, path) -> bool:
        """
            Удаляет указанный файл по пути из текстового файла cache.txt
            Делается это таким способом: 
                1) Читаем построчно старый cache.txt
                2) Записываем в файл temp_cache.txt все файлы которые не равны path
                3) Удаляем cache.txt
                4) Переименовываем temp_cache.txt как cache.txt
            Если файл успешно удален, то возвращает True, иначе False
        """
        is_removed = False
        if not os.path.exists(self.cache_path):
            self.create_config()
            return is_removed
        temp_cache_path = os.path.join(ROOT_DIR, "temp_cache.txt")
        with open(self.cache_path, encoding="utf-8") as cache_file, open(temp_cache_path, 'w', encoding="utf-8") as new_cache_file:
            for row in cache_file:
                if row.rstrip() != path:
                    new_cache_file.write(row)
                else:
                    is_removed = True
        # удаляем старый список зашифрованных файлов
        os.remove(self.cache_path)
        # переименовываем новый список под старым именем
        os.rename(temp_cache_path, self.cache_path)
        return is_removed