from PyQt6.QtWidgets import QWidget, QLineEdit, QApplication, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QPainter, QPixmap, QFontMetrics


class CustomCaretLineEdit(QWidget):
    """Прозрачный overlay для кастомной каретки и временного показа символа"""
    def __init__(self, line_edit: QLineEdit, caret_image_path: str):
        super().__init__(line_edit)
        self.line_edit = line_edit
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(line_edit.size())

        self.caret_pixmap = QPixmap(caret_image_path)
        self.caret_visible = True
        self.temp_char_index = None
        self.temp_char_duration = 800  # мс

        # Таймер мигания каретки
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.blink_caret)
        self.blink_timer.start(500)

        # Таймер временного показа последнего символа
        self.show_char_timer = QTimer(self)
        self.show_char_timer.setSingleShot(True)
        self.show_char_timer.timeout.connect(self.hide_temp_char)

        # Подключаем событие изменения текста
        self.line_edit.textChanged.connect(self.on_text_changed)

    def resizeEvent(self, event):
        self.resize(self.line_edit.size())
        super().resizeEvent(event)

    def on_text_changed(self):
        # Запоминаем индекс последнего символа для временного показа
        cursor_pos = self.line_edit.cursorPosition()
        if cursor_pos > 0:
            self.temp_char_index = cursor_pos - 1
            self.show_char_timer.start(self.temp_char_duration)
        self.update()

    def blink_caret(self):
        self.caret_visible = not self.caret_visible
        self.update()

    def hide_temp_char(self):
        self.temp_char_index = None
        self.update()

    def paintEvent(self, event):
        if not self.line_edit.hasFocus():
            return

        painter = QPainter(self)
        fm = QFontMetrics(self.line_edit.font())
        text = self.line_edit.text()
        cursor_pos = self.line_edit.cursorPosition()

        # Рисуем временный символ, если нужно
        if self.temp_char_index is not None and 0 <= self.temp_char_index < len(text):
            offset = fm.horizontalAdvance(text[:self.temp_char_index])
            y = (self.height() + fm.ascent() - fm.descent()) // 2
            painter.drawText(offset + 2, y, text[self.temp_char_index])

        # Рисуем кастомную каретку
        if self.caret_visible:
            cursor_offset = fm.horizontalAdvance(text[:cursor_pos])
            x = cursor_offset + 2
            y = (self.height() + fm.ascent() - fm.descent()) // 2 - self.caret_pixmap.height() // 2
            painter.drawPixmap(x, y, self.caret_pixmap)