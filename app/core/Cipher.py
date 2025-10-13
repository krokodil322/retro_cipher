from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.fernet import Fernet
import hashlib
import base64
import os

password = b"user_password_here"
salt = os.urandom(16)  # можно хранить рядом с файлом

kdf = Scrypt(
    salt=salt,
    length=32,
    n=2**14,
    r=8,
    p=1,
    backend=default_backend()
)
key = kdf.derive(password)
key = base64.urlsafe_b64encode(key)  # Fernet требует base64 ключ
fernet = Fernet(key)
print(fernet)


class Cipher:
    @staticmethod
    def hash_compare(input_pswd: str, hash_from_json: str) -> bool:
        return input_pswd == hash_from_json
    
    @staticmethod
    def hashing(input_psws: str) -> str:
        input_psws_bytes = input_psws.encode("utf-8")
        return hashlib.sha256(input_psws_bytes).hexdigest()
    
    @staticmethod
    def get_salt() -> int:
        return os.urandom(16)
    
    
hash_pswd_1 = Cipher.hashing("abra")
hash_pswd_2 = Cipher.hashing("kadabra")
print(Cipher.hash_compare(hash_pswd_1, hash_pswd_1))