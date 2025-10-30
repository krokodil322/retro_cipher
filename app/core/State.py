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
    CHANGE = auto()
    CHECK_FILE = auto()
    DECRYPT = auto()
    ENCRYPT = auto()

