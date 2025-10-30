from PyQt6.QtCore import Qt
from pytestqt import qtbot

from app.ui.MainWindow import MainWindow
from app.core.ConfigManager import ConfigManager
from app.core.UserAuthentication import UserAuthentication
from app.core.State import AuthState, Function
from app.core.Cipher import Cipher
from app.paths import CONFIG_DIR

import os


def test_close_button(qtbot):
    """Тест выключения программы"""
    is_closed = False
    def closed() -> None:
        # меняет статус окна на закрытый
        nonlocal is_closed
        is_closed = True
    
    window = MainWindow()
    # включаем флаг чтобы объект удалялся после исполнения метода .close()
    window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
    # подключаем функцию которая сработает перед удалением window
    window.destroyed.connect(closed)
    window.show()
    # не следует его добавлять, ибо под капотом он как-то взаимодейтсвует
    # с window, который в данный момент может быть удален
    # qtbot.addWidget(window)
    # кликаем мышкой по кнопке закрыть программу
    qtbot.mouseClick(window.close_btn, Qt.MouseButton.LeftButton)
    # на всякий выжидаем 1 сек, пока все удалится, но мб объект уже удален
    qtbot.waitUntil(lambda: is_closed, timeout=1000)
    assert is_closed, "Окно не закрывается кнопокй close_btn"

def test_collapse_button(qtbot):
    """Тест кнопки сворачивания программы"""
    window = MainWindow()
    window.show()
    qtbot.mouseClick(window.collapse_btn, Qt.MouseButton.LeftButton)
    assert window.isVisible(), "Окно не сворачивается кнопкой collapse_btn"
    
def test_disabled_enter(qtbot):
    """Проверка блокировки клавиши enter в момент авторизации. То есть до ввода 1-го символа пароля"""
    window = MainWindow()
    window.show()
    qtbot.waitUntil(lambda: not window.enter_btn.isEnabled(), timeout=100)
    assert not window.enter_btn.isEnabled(), "Кнопка enter_btn не заблокирована в первый момент авторизации"
    
def test_disabled_enter_in_empty_pswd_field(qtbot):
    """Проверка блокировки клавиши enter когда в поле пароля нет ни одного символа"""
    window = MainWindow()
    window.show()
    # проверим, что поле пароля вообще существует
    assert hasattr(window, "pswd_field")
    qtbot.keyClicks(window.pswd_field, "123")
    assert window.enter_btn.isEnabled(), "Кнопка enter не разблокируется при вводе символов в поле пароля pswd_field"
    
def test_input_pswd_in_pswd_field(qtbot):
    """Проверка ввода пароля в поле pswd_field"""
    window = MainWindow()
    window.show()
    qtbot.keyClicks(window.pswd_field, "123")
    assert window.pswd_field.text() == "123", f"Поле ввода пароля не работает. Ожидаемый результат: 123 Полученный: {window.pswd_field.text()}"
    
def test_registration_event(qtbot):
    """Тест успешной регистрации"""
    # создадим путь для временного конфига для теста
    temp_config_path = os.path.join(CONFIG_DIR, "temp_config.json")
    # создаем новый объект конфига
    temp_config = ConfigManager()
    # устанавливаем новый путь для конфига
    temp_config.config_path = temp_config_path
    # создаем объект аутентификации
    user_auth = UserAuthentication()
    # загружаем в него новый объект конфига
    user_auth.config_obj = temp_config
    # искусственно меняем значение регистрации на False
    user_auth.check_registered()
    window = MainWindow()
    # меняем объект аутентификации
    window.user_authenticator = user_auth
    assert window.user_authenticator.config_obj.config_path == temp_config_path, f"Неправильный путь к временному конфигу. Твой путь: {window.user_authenticator.config.config_path}"
    # устанавиливаем следующий ивент на регистрацию
    window.next_event = AuthState.REGISTRATION_PSWD
    # меняем виджеты под регистрацию
    window._widgets_controll_authentication(title=window.EVENTS[window.next_event]["msg"])
    window.show()
    # проверяем правильность надписи
    assert window.msg.text() == "Придумай пароль", f"Неправильная надпись, должно быть: Придумай пароль | А у тебя: {window.msg.text()}"
    qtbot.addWidget(window)
    qtbot.keyClicks(window.pswd_field, "1234")
    qtbot.mouseClick(window.enter_btn, Qt.MouseButton.LeftButton)
    # проверяем следующий сценарий
    assert window.next_event is AuthState.REGISTRATION_REPEAT_PSWD, f"Не установлен правильный следующий ивент. Должен быть AuthState.REGISTRATION_REPEAT_PSWD, а у тебя {window.next_event}"
    # проверяем очистилось ли поле пароля
    assert len(window.pswd_field.text()) == 0, "Поле пароля не очистилось!"
    # проверяем правильность подписи
    assert window.msg.text() == "Повтори пароль", f"Неправильная надпись, должно быть: Повтори пароль | А у тебя: {window.msg.text()}"
    # повторяем ввод пароля ПРАВИЛЬНО!
    qtbot.keyClicks(window.pswd_field, "1234")
    qtbot.mouseClick(window.enter_btn, Qt.MouseButton.LeftButton)
    # проверяем правильность следующего ивента
    assert window.next_event is AuthState.AUTHORIZATION, f"Не установлен правильный следующий ивент. Должен быть AuthState.AUTHORIZATION, а у тебя {window.next_event}"
    # проверяем правлиьность подписи
    assert window.msg.text() == "Введи пароль", f"Неправильная надпись, должно быть: Введи пароль | А у тебя: {list(window.msg.text())}"
    # проверямем очистилось ли поле ввода
    assert len(window.pswd_field.text()) == 0, "Поле пароля не очистилось!"
    # qtbot.waitUntil(lambda: os.path.exists(temp_config_path), timeout=3000)
    # проверяем установился ли флаг регистрации на True
    assert window.user_authenticator.check_registered, f"Флаг is_registered != True, хотя пользователь правильно ввел пароли!"
    # проверяем создался ли временный конфиг с хэшэм пароля
    assert window.user_authenticator.config_obj._is_exist_config, f"Не создался конифг по пути temp_config.json"
    # на всякий проверяем правильность пути сохраненного конфига
    assert window.user_authenticator.config_obj.config_path == temp_config_path, "Неправильный путь к временному конфигу"
    # получаем созданный конфиг в виде словаря
    registered_config = window.user_authenticator.config_obj.get_config()
    assert Cipher.hash_compare("1234", registered_config["hash_password"]), f"Хэши паролей не сошлись! 1234 = {Cipher.hashing('1234')} {registered_config['hash_password']}"
    assert os.path.exists(temp_config_path), f"Файла временного конфига {temp_config_path} не существует!"
    qtbot.keyClicks(window.pswd_field, "1234")
    qtbot.mouseClick(window.enter_btn, Qt.MouseButton.LeftButton)
    assert not hasattr(window, "msg") and not hasattr(window, "pswd_msg"), "Не были удалены атрибуты msg и pswd_msg"
    assert window.next_event is Function.NONE, f"Не установлен правильный следующий ивент. Должен быть Function.NONE, а у тебя {window.next_event}"
    os.remove(temp_config_path)
    
def test_registration_event_failure(qtbot):
    """Проверка ивента регистрации при неправильном повторении пароля."""

    # создадим путь для временного конфига для теста
    temp_config_path = os.path.join(CONFIG_DIR, "temp_config.json")
    # создаем новый объект конфига
    temp_config = ConfigManager()
    # устанавливаем новый путь для конфига
    temp_config.config_path = temp_config_path
    # создаем объект аутентификации
    user_auth = UserAuthentication()
    # загружаем в него новый объект конфига
    user_auth.config_obj = temp_config
    # искусственно меняем значение регистрации на False
    user_auth.check_registered()
    window = MainWindow()
    window.user_authenticator = user_auth
    # устанавиливаем следующий ивент на регистрацию
    window.next_event = AuthState.REGISTRATION_PSWD
    # меняем виджеты под регистрацию
    window._widgets_controll_authentication(title=window.EVENTS[window.next_event]["msg"])
    window.show()
    qtbot.addWidget(window)
    qtbot.keyClicks(window.pswd_field, "1234")
    qtbot.mouseClick(window.enter_btn, Qt.MouseButton.LeftButton)
    qtbot.keyClicks(window.pswd_field, "123")
    qtbot.mouseClick(window.enter_btn, Qt.MouseButton.LeftButton)
    assert window.next_event is AuthState.REGISTRATION_FAILURE, f"Не установлен правильный следующий ивент. Должен быть AuthState.REGISTRATION_FAILURE, а у тебя {window.next_event}"
    assert window.msg.text() == "Придумай пароль(Не совпали)", f"Неправильная надпись, должно быть: Придумай пароль(Не совпали) | А у тебя: {list(window.msg.text())}"
    # конфиг файл не должен создаваться в такой ситуации
    assert not window.user_authenticator.config_obj._is_exist_config(), "Временный файл конфига не должен создаваться когда регистрация не удалась!"
    qtbot.keyClicks(window.pswd_field, "1234")
    qtbot.mouseClick(window.enter_btn, Qt.MouseButton.LeftButton)
    assert window.msg.text() == "Повтори пароль", f"Неправильная надпись, должно быть: Повтори пароль | А у тебя: {window.msg.text()}"
    qtbot.keyClicks(window.pswd_field, "1234")
    qtbot.mouseClick(window.enter_btn, Qt.MouseButton.LeftButton)
    # а тут уже должен создаваться, ибо повтор верен
    assert window.user_authenticator.config_obj._is_exist_config(), "Временный файл конфига не должен создаваться когда регистрация не удалась!"
    # проверяем хэши паролей
    registered_config = window.user_authenticator.config_obj.get_config()
    assert Cipher.hash_compare("1234", registered_config["hash_password"]), f"Хэши паролей не сошлись! 1234 = {Cipher.hashing('1234')} {registered_config['hash_password']}"
    # проверяем правильность подписи для авторизации
    # проверяем правильность следующего ивента
    assert window.next_event is AuthState.AUTHORIZATION, f"Не установлен правильный следующий ивент. Должен быть AuthState.AUTHORIZATION, а у тебя {window.next_event}"
    # проверяем правлиьность подписи
    assert window.msg.text() == "Введи пароль", f"Неправильная надпись, должно быть: Введи пароль | А у тебя: {list(window.msg.text())}"
    # проверямем очистилось ли поле ввода
    assert len(window.pswd_field.text()) == 0, "Поле пароля не очистилось!"
    # qtbot.waitUntil(lambda: os.path.exists(temp_config_path), timeout=3000)
    # проверяем установился ли флаг регистрации на True
    assert window.user_authenticator.check_registered, f"Флаг is_registered != True, хотя пользователь правильно ввел пароли!"
    # проверяем создался ли временный конфиг с хэшэм пароля
    assert window.user_authenticator.config_obj._is_exist_config, f"Не создался конифг по пути temp_config.json"
    # на всякий проверяем правильность пути сохраненного конфига
    assert window.user_authenticator.config_obj.config_path == temp_config_path, "Неправильный путь к временному конфигу"
    # получаем созданный конфиг в виде словаря
    registered_config = window.user_authenticator.config_obj.get_config()
    assert Cipher.hash_compare("1234", registered_config["hash_password"]), f"Хэши паролей не сошлись! 1234 = {Cipher.hashing('1234')} {registered_config['hash_password']}"
    assert os.path.exists(temp_config_path), f"Файла временного конфига {temp_config_path} не существует!"
    qtbot.keyClicks(window.pswd_field, "1234")
    qtbot.mouseClick(window.enter_btn, Qt.MouseButton.LeftButton)
    assert not hasattr(window, "msg") and not hasattr(window, "pswd_msg"), "Не были удалены атрибуты msg и pswd_msg"
    assert window.next_event is Function.NONE, f"Не установлен правильный следующий ивент. Должен быть Function.NONE, а у тебя {window.next_event}"
    os.remove(temp_config_path)
