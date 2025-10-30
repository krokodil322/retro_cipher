from app.core import ConfigManager, Cipher


class UserAuthentication:
    """
        Класс отвечающий за аутентификацию юзера. Функционал:
        1) Сверяет введенные юзером пароли.
        2) Хэширует пароль и записывает в config.json
    """
    def __init__(self):
        self.config_obj = ConfigManager()
        self.config = self.config_obj.get_config()
        self.is_registered = False
        self.is_authorized = False
        self.first_pswd = None
        self.second_pswd = None
        self.check_registered()
        
    def check_registered(self) -> None:
        self.is_registered = False if not self.config else True

    def set_first_pswd(self, password: str) -> None:
        self.first_pswd = password

    def set_second_pswd(self, password: str) -> None:
        self.second_pswd = password
    
    def registration(self) -> None:
        """Метод отвечающий за статус регистрации юзера. Метод мутабельный будь внимателен"""
        # Если юзер накосячил с повтором ввода пароля, то в множестве будет 2 элемента
        if self.first_pswd == self.second_pswd:
            # хэшируем пароль
            hash_password = {"hash_password": str(Cipher.hashing(self.first_pswd))}
            # создаем конфиг
            self.config_obj.create_config()
            # устанавливаем хэш значения пароля в конфиг
            self.config_obj.update_config(hash_password)
            # регистрация удалась
            self.is_registered = True
        else:
            self.is_registered = False
            
    def authorization(self) -> None:
        """Метод отвечающий за статус авторизации юзера. Мутабельный метод меняющий статус is_authorized"""
        if not self.is_registered:
            raise "Запуск авторизации без положительного флага регистрации."
        # если хэши сходятся, то пароль верен
        else:
            # если юзер впервые зареган, то дергаем конфиг заново! Это важно, иначе не пусти при авторизации
            self.config = self.config_obj.get_config()
        self.is_authorized = Cipher.hash_compare(self.first_pswd, self.config["hash_password"])

