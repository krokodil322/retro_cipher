from email.mime import audio
from enum import Enum, auto



class AuthState(Enum):
    VIEW_WIDGETS = auto()
    REGISTRATION_PSWD = auto()
    REGISTRATION_REPEAT_PSWD = auto()
    REGISTRATION_FAILURE = auto()
    AUTHORIZATION = auto()
    AUTHORIZATION_FAILURE = auto()


class Function(Enum):
    NONE = auto()
    CHANGE_FILE = auto()
    VIEW_FILE = auto()
    DECRYPT = auto()
    ENCRYPT = auto()
    CHANGE_MODE = auto()
    DECRYPT_FAILURE = auto()
    ENCRYPT_FAILURE = auto()
    DECRYPT_SUCCESS = auto()
    ENCRYPT_SUCCESS = auto()
    

