from PyQt6.QtGui import QFont, QFontDatabase, QPixmap, QIcon
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QSoundEffect

from app.paths import BACKGROUNDS_DIR, ICONS_DIR, STYLES_DIR, FONTS_DIR, SOUNDS_DIR, BUTTONS_DIR

import os


def style_getter(css_filename: str) -> str:
    """Возвращает файл стиля css"""
    path = os.path.join(STYLES_DIR, css_filename)
    with open(path, encoding="utf-8") as file:
        style = file.read()
    return style


def font_getter(font_filename: str, size: int) -> QFont:
    """Возвращает объект QFont по полученному имени шрифта из папки fonts"""
    font_path = os.path.join(FONTS_DIR, font_filename)
    font_id = QFontDatabase.addApplicationFont(font_path)
    font = QFontDatabase.applicationFontFamilies(font_id)[0]
    return QFont(font, size)


def sound_getter(sound_filename: str) -> QSoundEffect:
    """Возвращает объект QSoundEffect по полученному имени аудиофайла из папки sounds"""
    sound_path = os.path.join(SOUNDS_DIR, sound_filename)
    sound_effect = QSoundEffect()
    sound_effect.setSource(QUrl.fromLocalFile(sound_path))
    return sound_effect

def button_icon_getter(icon_filename: str) -> QIcon:
    """Возвращает QIcon по полученному имени иконки из папки buttons"""
    icon_path = os.path.join(BUTTONS_DIR, icon_filename)
    icon_obj = QIcon(QPixmap(icon_path))
    return icon_obj

def background_getter(background_filename: str) -> QPixmap:
    """Возвращает QPixmap по полученному имени бэкграунда из папки backgrounds"""
    background_path = os.path.join(BACKGROUNDS_DIR, background_filename)
    background_obj = QPixmap(background_path)
    return background_obj