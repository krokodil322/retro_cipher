from app.paths import CONFIG_DIR

import os
import json


class ConfigManager:
    """
        Класс отвечающий за файл config.json и папку config.
        Осуществляет проверку наличия этих файлов и создает
        их, если таковые отсутствуют.

        Использовать так:
        auth = ConfigManager()
        config = auth.get_config()
        
        Но так лучше:
        config = ConfigManager.get_config()
    """
    def __init__(self):
        self.default = {"hash_password": ''}
        self.config_path = os.path.join(CONFIG_DIR, "config.json")
    
    def _is_exist_config(self) -> bool:
        """Проверяет существует ли файл confing.json"""
        return os.path.exists(self.config_path)        

    def get_config(self) -> dict:
        """
            Возвращает словарь конфига, если такой существует, иначе
            возвращает None.
        """
        if self._is_exist_config():
            with open(self.config_path, encoding="utf-8") as json_file:
                config = json.load(fp=json_file)
            return config
        else:
            return None
        
    def update_config(self, config: dict) -> None:
        """Устанавливает новые данные в конфиг"""
        old_config = self.get_config()
        if not old_config:
            raise "Ты пытаешься обновить конфиг которого пока не существует!"
        old_config.update(config)
        with open(self.config_path, 'w', encoding="utf-8") as json_file:
            json.dump(old_config, fp=json_file, indent=3, ensure_ascii=False)
        
    
    def create_config(self) -> None:
        """
            Создает папку и файл конфига, если таковых нет
            Этот метод вызывается только в том случае, если
            файла конфига действительно нет, а потому и 
            проверять его наличие нет смысла.
        """            
        if not os.path.exists(CONFIG_DIR):
            os.mkdir(CONFIG_DIR)
        with open(self.config_path, 'w', encoding="utf-8") as json_file:
            print(f"СОЗДАНИЕ КОНФИГА ПО ПУТИ: {self.config_path}")
            json.dump(self.default, fp=json_file, indent=3, ensure_ascii=False)
        
            
