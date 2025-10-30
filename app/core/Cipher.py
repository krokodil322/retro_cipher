from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.fernet import Fernet

from typing import Generator
from random import choice
from string import ascii_letters
import hashlib
import base64
import os


class Cipher:
    def __init__(self):
        # хэш пароля из json
        self.hash_pswd: bytes
    
    def set_password(self, password: str) -> None:
        self.hash_pswd = password.encode("utf-8")
        self.init_fernet()
    
    def init_fernet(self, salt: bytes | None=None) -> None:
        """
            Инициализация и декларация fernet.
            Принимает salt - это соль для шифровки.
            Этот метод нужно запускать каждый раз когда юзером
            будет открываться файл, ибо соль для зашифровки/расшифровки
            хранится в начале каждого текстового файла и она всегда разная.
            А потому придется пересоздавать fernet каждый раз.
            Если не передавать salt, то оно сгенерируется методом get_salt.
        """
        self.salt = self.get_salt() if salt is None else salt
        kdf = Scrypt(
            salt=self.salt,
            length=32,
            n=pow(2, 14),
            r=8,
            p=1,
            backend=default_backend()
        )
        key = kdf.derive(self.hash_pswd)
        key = base64.urlsafe_b64encode(key)
        self.fernet = Fernet(key)
    
    @classmethod
    def hash_compare(cls, input_pswd: str, hash_from_json: str) -> bool:
        """
            Сравнивает два значения хэша паролей.
            input_pswd: str - строка пароля(НЕ ХЭШ)
            hash_from_json: str - строка хэша пароля из json-файла(а это уже хэш)
        """
        return cls.hashing(input_pswd) == hash_from_json
    
    @classmethod
    def hashing(cls, input_pswd: str) -> str:
        """
            Хэширует строчное значение, создан для хэширования пароля.
            input_pswd - строка пароля(НЕ ХЭШ)
        """
        input_pswd_bytes = input_pswd.encode("utf-8")
        return hashlib.sha256(input_pswd_bytes).hexdigest()
    
    @classmethod
    def get_salt(cls) -> bytes:
        """Возвращает рандомную соль для шифровки"""
        return os.urandom(16)
    
    def encrypter(self, path) -> None:
        """
            Всякая шифровка будет осуществляться построчно, 
            дабы не жрать ОЗУ на хранения потенциальных ГБтов текстовых данных.
            Любая запись также будет просиходить построчно.
            path - это путь к файлу который нужно зашифровать
        """
        temp_file_name = ''.join(map(choice, ascii_letters)) + ".txt"
        root = os.path.split(path)[0]
        temp_file_name = os.path.join(root, temp_file_name)
        with open(path, encoding="utf-8") as read_file, open(temp_file_name, 'w', encoding="utf-8") as write_file:
            str_salt = self.salt.decode("utf-8")
            # первой строкой записываем соль
            write_file.write(str_salt)
            for row in read_file:
                # перед шифровокой строку нужно перевести в байты
                bytes_row = row.encode("utf-8")
                # шифруем
                encrypt_row = self.fernet.encrypt(bytes_row)
                # переводим из байтов в строку
                str_encrypt_row = encrypt_row.decode("utf-8")
                # записываем в новый файл зашифрованные строки
                write_file.write(str_encrypt_row)
        os.remove(path)
        os.rename(temp_file_name, path)
                
                
            
    def decrypter(self, path) -> Generator:
        """Генератор для расшифровки, аналогичен encrypter'у"""
        with open(path, encoding="utf-8") as file:
            for row in file:
                yield self.fernet.decrypt(row)
        

if __name__ == "__main__":
    hash_pswd_1 = Cipher.hashing("abra")
    hash_pswd_2 = Cipher.hashing("kadabra")
    print(Cipher.hash_compare(hash_pswd_1, hash_pswd_1))