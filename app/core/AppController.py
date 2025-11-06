from PyQt6.QtWidgets import QLabel
from pymsgbox import password

from app.core.Cipher import Cipher
from app.core.FileManager import FileManager
from app.core.State import AuthState, Function
from app.core.UserAuthentication import UserAuthentication
from app.core.CONSTANTS import DEBUG, DEBUG_PASWWORD
from app.ui import MainWindow



class AppController:
    """
        Подкапотный сценарист всего приложения
        Главным убразом управляет сценариями в приложении
        переключая на нужные методы.
        Примерная схема организации данного проекта
            MainWindow  <-- сообщает событие -->  AppController  <-- вызывает --> Cipher/FileManager/UserAuthentication
            ↑                                                       |
            |                                                       |
            +---------------------- получает обновления ------------+
    """
    def __init__(
            self, 
            user_auth: UserAuthentication,
            cipher: Cipher,
            file_manager: FileManager,
            ui: MainWindow
        ):
        """display - рабочая зона программы"""
        # объект отвечающий за аутентификацию юзера
        self.user_auth = user_auth
        # объект шифровщика
        self.cipher = cipher
        # файловый менеджер, передаем ему виджет, с которым 
        # будет функционировать file_manager
        self.file_manager = file_manager
        # объект главного окна
        self.ui = ui
        # устанавливаем первый ивент в зависимости от статуса регистрации
        self.current_event = AuthState.AUTHORIZATION if self.user_auth else AuthState.REGISTRATION_PSWD
        # все ивенты приложения
        # поясню за структуру: Под ключом widgets будут хранится
        # все методы которые отвечают за установку виджетов на экране
        # эти методы вызываются исключительно внутри данного класса
        # под ключом callback хранятся все методы которые вызываются
        # когда юзер нажимает кнопки, вызываются эти методы внутри
        # класса MainWindow через объект класса AppController методом
        # callback_redirection. Внутри этого класса данный метод не используется
        self.EVENTS = {
            # начало регистрации, первый ввод пароля
            AuthState.REGISTRATION_PSWD: { 
                "widgets": {
                    "function": self.ui.set_authentication_widgets, 
                    "kwargs": {"title": "Придумай пароль"}
                },
                "callback": {
                    "function": self._handle_registration
                }
            },
            # повтор ввода пароля при регистрации
            AuthState.REGISTRATION_REPEAT_PSWD: {
                "widgets": {
                    "function": self.ui.set_authentication_widgets, 
                    "kwargs": {"title": "Повтори пароль"}
                },
                "callback": {
                    "function": self._handle_repeat_pswd_registration
                }
            },
            # регистрация не удалась
            AuthState.REGISTRATION_FAILURE: {
                "widgets": {
                    "function": self.ui.set_authentication_widgets, 
                    "kwargs": {"title": "Пароли не совпали\nПридумай пароль"}
                },
                "callback": {
                    "function": self._handle_registration
                }
            },
            # авторизация
            AuthState.AUTHORIZATION: {
                "widgets": {
                    "function": self.ui.set_authentication_widgets,
                    "kwargs": {"title": "Введи пароль"}
                },
                "callback": {
                    "function": self._handle_authorization
                }
            },
            # авторизация не удалась
            AuthState.AUTHORIZATION_FAILURE: {
                "widgets": {
                    "function": self.ui.set_authentication_widgets,
                    "kwargs": {"title": "Ты ввел неправильный пароль\nВведи пароль"}
                },
                "callback": {
                    "function": self._handle_authorization,
                }
            },
            # момент когда юзер зашел и ничего пока не нажал
            Function.NONE: {
                "widgets":{
                    "function": self.ui.set_authentication_widgets,
                    "kwargs": {"is_clear": True}
                },
                "callback": {
                    "function": None, # в том месте просто callback не вызваем
                }
            },
            # выбор файла из дерева
            Function.CHANGE_FILE: { 
                "widgets": {
                    "function": self.ui.set_tree_widgets,
                    "kwargs": {},
                },
                "callback": {
                    "function": self._get_tree_item,
                }
            },
            # проверка файла 
            Function.VIEW_FILE: {
                "widgets": {
                    "function": self.ui.set_change_file_widgets,
                    "kwargs": {"title": "Текущий файл\n--------------------------------"}
                },
                "callback": {
                    "function": None, # ничего не делаем, теперь должен решать юзер
                    "kwargs": {}
                }
            },
            Function.ENCRYPT: {
                "widgets": {
                    "function": self.ui.set_mode_widgets,
                    "kwargs": {}
                },
                "callback": {
                    "function": self._encrypt,
                    "kwargs": {}
                },
            },
            Function.DECRYPT: {
                "widgets": {
                    "function": self.ui.set_mode_widgets,
                    "kwargs": {}
                },
                "callback": {
                    "function": self._decrypt,
                    "kwargs": {}
                }
            },
            Function.ENCRYPT_FAILURE: {
                "widgets": {
                    "function": self.ui.set_cryptography_failure_widgets,
                    "kwargs": {
                        "title": "Текущий файл\n--------------------------------",
                        "status": "Неудалось зашифровать файл.\nПопробуй еще раз."
                    }
                },
                "callback": {
                    "function": None,
                    "kwargs": {}
                }
            },
            Function.DECRYPT_FAILURE: {
                "widgets": {
                    "function": self.ui.set_cryptography_failure_widgets,
                    "kwargs": {
                        "title": "Текущий файл\n--------------------------------",
                        "status": "Неудалось расшифровать файл\nПопробуй еще раз"
                    }
                }
            },
            Function.ENCRYPT_SUCCESS: {
                "widgets": {
                    "function": self.ui.set_cryptography_success_widgets,
                    "kwargs": {
                        "title": "Текущий файл\n--------------------------------",
                        "status": "Файл успешно зашифрован"
                    }
                },
                "callback": {
                    "function": self._encrypt,
                    "kwargs": {}
                }
            },
            Function.DECRYPT_SUCCESS: {
                "widgets": {
                    "function": self.ui.set_cryptography_success_widgets,
                    "kwargs": {
                        "title": "Текущий файл\n--------------------------------",
                        "status": "Файл успешно расшифрован"
                    }
                },
                "callback": {
                    "function": self._decrypt,
                    "kwargs": {}
                }
            },
        }
    
    def change(self) -> None:
        """Этот метод меняет текущий ивент на CHANGE"""
        self.current_event = Function.CHANGE_FILE
        self._widgets_redirection()
    
    def change_mode(self) -> None:
        """Этот метод меняет текущий ивент на ENCRYPT или DECRYPT"""
        # тут место, где можно проверить вхождение текущего файла в список ls
        if self.current_event not in (Function.ENCRYPT, Function.DECRYPT):
            self.current_event = Function.ENCRYPT
        elif self.current_event is Function.ENCRYPT:
            self.current_event = Function.DECRYPT
        elif self.current_event is Function.DECRYPT:
            self.current_event = Function.ENCRYPT
        self._widgets_redirection()
    
    def _encrypt(self):
        item = self.file_manager.currentItem()
        path = item.text(1)
        try:
            self.cipher.encrypter(path)
            self.current_event = Function.ENCRYPT_SUCCESS
        except:
            self.current_event = Function.ENCRYPT_FAILURE
        self._widgets_redirection()
            
    def _decrypt(self):
        item = self.file_manager.currentItem()
        path = item.text(1)
        try:
            self.cipher.decrypter(path)
            self.current_event = Function.DECRYPT_SUCCESS
        except:
            self.current_event = Function.DECRYPT_FAILURE
        self._widgets_redirection()
    
    def _get_tree_item(self):
        item = self.file_manager.currentItem()
        if item:
            # path = item.text(1)
            filename = item.text(0)
            if filename.endswith((".txt", ".md")):
                self.file_manager.tree.setParent(None)
                self.current_event = Function.VIEW_FILE
                # инициализируем путь к выбранному файлу, этот путь тебе пригодится
                self._widgets_redirection()
    
    def _widgets_redirection(self) -> None:
        event_obj = self.EVENTS[self.current_event]["widgets"]
        function = event_obj.get("function", None)
        kwargs = event_obj["kwargs"]
        function(**kwargs)

    def callback_redirection(self) -> None:
        event_obj = self.EVENTS[self.current_event]["callback"]
        function = event_obj["function"]
        function()
    
    def define_event_authentication(self):
        if not DEBUG:
            if self.user_auth.is_registered:
                self.current_event = AuthState.AUTHORIZATION
            else:
                self.current_event = AuthState.REGISTRATION_PSWD
        else:
            # если режим отладки, то скипаем аутентификацию
            # и устанавливаем дефолтный пароль для тестов шифровщика
            self.current_event = Function.NONE
            hash_pswd = self.cipher.hashing(DEBUG_PASWWORD)
            self.cipher.set_password(hash_pswd)
            self.cipher.init_fernet()
        self._widgets_redirection()
    
    def _handle_registration(self) -> None:
        password = self.ui.get_input_password()
        self.user_auth.set_first_pswd(password)
        self.current_event = AuthState.REGISTRATION_REPEAT_PSWD
        self._widgets_redirection()
        
    def _handle_repeat_pswd_registration(self) -> None:
        password = self.ui.get_input_password()
        self.user_auth.set_second_pswd(password)
        # добавляем конфиг 
        self.user_auth.registration()
        if self.user_auth.is_registered:
            self.current_event = AuthState.AUTHORIZATION
        else:
            self.current_event = AuthState.REGISTRATION_FAILURE
        self._widgets_redirection()
        
    def _handle_authorization(self) -> None:
        password = self.ui.get_input_password()
        self.user_auth.set_first_pswd(password)
        self.user_auth.authorization()
        if self.user_auth.is_authorized:
            self.current_event = Function.NONE
            # добавляем хэш пароля в шифровщик
            hash_pswd = self.cipher.hashing(password)
            self.cipher.set_password(hash_pswd)
            self.cipher.init_fernet()
        else:
            self.current_event = AuthState.AUTHORIZATION_FAILURE
        self._widgets_redirection()