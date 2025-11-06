from logging import config
from PyQt6.QtCore import Qt

from app.core import ConfigManager
from app.paths import CONFIG_DIR

from pytestqt import qtbot
import pytest
import os
import json


def get_obj() -> ConfigManager:
    """Возвращает объект ConfigManager с тестовыми параметрами"""
    config = ConfigManager()
    # следует изменить имя конфига для тестов
    config.config_path = os.path.join(CONFIG_DIR, "tmp_config.json")
    return config


def test_create_config(qtbot):
    """Тестируем метод create_config"""
    config = get_obj()
    config.create_config()
    assert os.path.exists(CONFIG_DIR), "Папка config не была создана"
    assert os.path.exists(config.config_path), "Файл config.json не был создан"
    with open(config.config_path, encoding="utf-8") as json_file:
        result = json.load(json_file)
    assert type(result) is dict, "Метод create_config неправильно записал тип данных в config.json. Тип данных НЕ dict"
    assert len(result) == 0, "Метод create_confg неправильно записал значение по умолчанию в config.json. Словарь НЕ пуст."
    os.remove(config.config_path)


def test_get_config_while_not_exist(qtbot):
    """Тестируем метод get_config пока config.json еще не был создан"""
    config = get_obj()
    result = config.get_config()
    assert not result, "Метод get_config не вернул None, хотя файла tmp_config.json пока не существует"


def test_get_config_when_exist(qtbot):
    """Тестируем get_config со значение по умолчанию"""
    config = get_obj()
    config.create_config()
    result = config.get_config()
    assert type(result) is dict, "Метод get_config вернул неправильный тип данных config"
    assert len(result) == 0, "Метод get_config вернул не пустой словарь"
    os.remove(config.config_path)


def test_get_config_with_data(qtbot):
    """Тестируем get_config с некоторыми значениями в config.json"""
    config = get_obj()
    # создадим конфиг сами со своими данными
    default = {"hash_pswd": "abrakadabra"}
    with open(config.config_path, 'w', encoding="utf-8") as json_file:
        json.dump(default, fp=json_file)
    result = config.get_config()
    assert result, "get_config вернул None"
    assert result.get("hash_pswd"), "Метод get_config неправильно вернул словарь. Ключа hash_pswd не существует."
    assert result["hash_pswd"] == default["hash_pswd"], "get_config вернул неверные данные"
    os.remove(config.config_path)


def test_update_config_when_not_exist(qtbot):
    """Тестируем исключение update_config когда config.json еще ны был создан"""
    config = get_obj()
    try:
        config.update_config({})
        raise Exception("Тебе удалось обновить конфиг которого еще не сущесвтует. Как тебе это удалось?")
    except FileNotFoundError:
        pass


def test_update_when_exist(qtbot):
    """Тестируем update_config c некоторыми данными и получаем значение через get_config. Полный тест всех методов"""
    config = get_obj()
    update = {"hash_pswd": "abrakadabra"}
    config.create_config()
    result = config.update_config(update)
    assert not result, "update_config НЕ вернул None"
    result = config.get_config()
    assert result and result.get("hash_pswd"), "update_config неправильно записал переданный ему словарь. Ключа hash_pswd не существует"
    assert result and result["hash_pswd"] == update["hash_pswd"], "update неправильно записал значение под ключом hash_pswd"
    os.remove(config.config_path)
    
    
