from PyQt6.QtWidgets import QLabel
from pymsgbox import password

from app.core.Cipher import Cipher
from app.core.FileManager import FileManager
from app.core.State import AuthState, Function
from app.core.UserAuthentication import UserAuthentication
from app.ui import MainWindow



class AppController:
    """
        Подкапотный сценарист всего приложения
        Главным убразом управляет сценариями в приложении
        переключая на нужные методы.
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
        self.current_event = AuthState.AUTHORIZATION if self.user_auth.check_registered() else AuthState.REGISTRATION_PSWD
        # все ивенты приложения
        # поясню за структуру: Под ключом widgets будут хранится
        # все методы которые отвечают за установку виджетов на экране
        # эти методы вызываются исключительно внутри данного класса
        # под ключом callback хранятся все методы которые вызываются
        # когда юзер нажимает кнопки, вызываются эти методы внутри
        # класса MainWindow через объект класса AppController методом
        # callback_redirection. Внутри этого класса данный метод не используется
        self.EVENTS = {
            AuthState.REGISTRATION_PSWD: { 
                "widgets": {
                    "function": self.ui.widgets_controll_authentication, 
                    "kwargs": {"title": "Придумай пароль"}
                },
                "callback": {
                    "function": self._handle_registration
                }
            },
            AuthState.REGISTRATION_REPEAT_PSWD: {
                "widgets": {
                    "function": self.ui.widgets_controll_authentication, 
                    "kwargs": {"title": "Повтори пароль"}
                },
                "callback": {
                    "function": self._handle_repeat_pswd_registration
                }
            },
            AuthState.REGISTRATION_FAILURE: {
                "widgets": {
                    "function": self.ui.widgets_controll_authentication, 
                    "kwargs": {"title": "Пароли не совпали\nПридумай пароль"}
                },
                "callback": {
                    "function": self._handle_registration
                }
            },
            AuthState.AUTHORIZATION: {
                "widgets": {
                    "function": self.ui.widgets_controll_authentication,
                    "kwargs": {"title": "Введи пароль"}
                },
                "callback": {
                    "function": self._handle_authorization
                }
            },
            AuthState.AUTHORIZATION_FAILURE: {
                "widgets": {
                    "function": self.ui.widgets_controll_authentication,
                    "kwargs": {"title": "Ты ввел неправильный пароль\nВведи пароль"}
                },
                "callback": {
                    "function": self._handle_authorization,
                }
            },
            Function.NONE: {
                "widgets":{
                    "function": self.ui.widgets_controll_authentication,
                    "kwargs": {"is_clear": True}
                },
                "callback": {
                    "function": None,
                }
            },
            Function.CHANGE: {
                "widgets": {
                    "function": self.ui.widgets_controll_tree,
                    "kwargs": {},
                },
                "callback": {
                    "function": self._get_tree_item,
                }
            }
        }
    
    def change(self) -> None:
        self.current_event = Function.CHANGE
        # self.file_manager.set_tree()
        # print("CHANGE GOOD")
        self._widgets_redirection()
    
    def _get_tree_item(self):
        print("Тут должен быть tree_item")
    
    def _widgets_redirection(self) -> None:
        event_obj = self.EVENTS[self.current_event]["widgets"]
        function = event_obj["function"]
        kwargs = event_obj["kwargs"]
        function(**kwargs)

    def callback_redirection(self) -> None:
        event_obj = self.EVENTS[self.current_event]["callback"]
        function = event_obj["function"]
        function()
    
    def define_event_authentication(self):
        is_registered = self.user_auth.check_registered()
        if is_registered:
            self.current_event = AuthState.AUTHORIZATION
        else:
            self.current_event = AuthState.REGISTRATION_PSWD
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
        else:
            self.current_event = AuthState.AUTHORIZATION_FAILURE
        self._widgets_redirection()