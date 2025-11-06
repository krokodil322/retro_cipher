from app.core import Cipher, ConfigManager


class UserAuthentication:
    """
        Класс отвечающий за аутентификацию юзера. Функционал:
        1) Сверяет введенные юзером пароли.
        2) Хэширует пароль и записывает в config.json
    """
    def __init__(self):
        self.config_obj = ConfigManager()
        self.config = self.config_obj.get_config()
        self.is_registered = bool(self)
        self.is_authorized = False
        self._first_pswd: str
        self._second_pswd: str
        
    def __bool__(self) -> bool:
        """Если конфиг существует и он не дефолтный - True, иначе False"""
        return bool(self.config)

    def set_first_pswd(self, password: str) -> None:
        self._first_pswd = password

    def set_second_pswd(self, password: str) -> None:
        self._second_pswd = password
    
    def registration(self) -> None:
        """Метод отвечающий за статус регистрации юзера. Метод мутабельный будь внимателен"""
        # Если юзер накосячил с повтором ввода пароля, то в множестве будет 2 элемента
        if self._first_pswd == self._second_pswd:
            # хэшируем пароль
            hash_password = {"hash_password": str(Cipher.hashing(self._first_pswd))}
            # создаем конфиг
            self.config_obj.create_config()
            # устанавливаем хэш значения пароля в конфиг
            self.config_obj.update_config(hash_password)
            # регистрация удалась
            self.is_registered = True
            del self._second_pswd
        else:
            self.is_registered = False
            
    def authorization(self) -> None:
        """Метод отвечающий за статус авторизации юзера. Мутабельный метод меняющий статус is_authorized"""
        if not self.is_registered:
            raise Exception("Запуск авторизации без положительного флага регистрации.")
        # если хэши сходятся, то пароль верен
        else:
            # если юзер впервые зареган, то дергаем конфиг заново! Это важно, иначе не пустит при авторизации
            self.config = self.config_obj.get_config()
        if not self.config:
            raise Exception("Во время авторизации был удален файл конфига!")
        self.is_authorized = Cipher.hash_compare(self._first_pswd, self.config["hash_password"])
        if self.is_authorized:
            del self._first_pswd




