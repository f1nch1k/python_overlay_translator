import sys
import pytesseract
import pyautogui
from PIL import ImageGrab
from googletrans import Translator as GoogleTranslator, LANGUAGES
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QHBoxLayout, QSlider, QFormLayout, QFrame
)
from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QColor, QPainter
import atexit


class TransparentTranslator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Translator")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(500, 330)

        self.drag_pos = None

        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 180);
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #444;
                color: white;
                padding: 5px;
                border-radius: 4px;
            }
            QComboBox {
                background-color: #222;
                color: white;
            }
            QSlider::handle:horizontal {
                background: #666;
                width: 10px;
            }
            QFrame#controlPanel {
                background-color: rgba(50, 50, 50, 220);
            }
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.create_control_panel()
        self.create_main_area()

    def create_control_panel(self):
        self.control_panel = QFrame()
        self.control_panel.setObjectName("controlPanel")
        self.control_panel.setFixedHeight(150)

        control_layout = QVBoxLayout(self.control_panel)

        size_form = QFormLayout()
        self.width_slider = QSlider(Qt.Horizontal)
        self.width_slider.setMinimum(300)
        self.width_slider.setMaximum(1000)
        self.width_slider.setValue(self.width())
        self.width_slider.setFixedWidth(250)
        self.width_slider.valueChanged.connect(self.update_size)

        self.height_slider = QSlider(Qt.Horizontal)
        self.height_slider.setMinimum(200)
        self.height_slider.setMaximum(800)
        self.height_slider.setValue(self.height())
        self.height_slider.setFixedWidth(250)
        self.height_slider.valueChanged.connect(self.update_size)

        size_form.addRow("Ширина", self.width_slider)
        size_form.addRow("Высота", self.height_slider)

        top_bar = QHBoxLayout()
        self.src_lang = QComboBox()
        self.dst_lang = QComboBox()
        self.src_lang.addItems(sorted(LANGUAGES.values()))
        self.dst_lang.addItems(sorted(LANGUAGES.values()))
        self.src_lang.setCurrentText("chinese")
        self.dst_lang.setCurrentText("russian")

        self.translate_button = QPushButton("Перевести")
        self.translate_button.clicked.connect(self.translate_from_screen)

        self.clear_button = QPushButton("Очистить")
        self.clear_button.clicked.connect(lambda: self.label.setText(""))

        top_bar.addWidget(self.src_lang)
        top_bar.addWidget(self.dst_lang)
        top_bar.addWidget(self.translate_button)
        top_bar.addWidget(self.clear_button)

        control_layout.addLayout(size_form)
        control_layout.addLayout(top_bar)

        self.main_layout.addWidget(self.control_panel)

    def create_main_area(self):
        self.label = QLabel("")
        self.label.setWordWrap(True)
        self.label.setStyleSheet("padding: 10px;")
        self.main_layout.addWidget(self.label)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(30, 30, 30, 180))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    def update_size(self):
        w = self.width_slider.value()
        h = self.height_slider.value()
        self.resize(QSize(w, h))

    def lang_code(self, name):
        for code, lang in LANGUAGES.items():
            if lang.lower() == name.lower():
                return code
        return "en"

    def ocr_lang_code(self, name):
        mapping = {
            'chinese': 'chi_sim',
            'japanese': 'jpn',
            'russian': 'rus',
            'ukrainian': 'ukr',
            'english': 'eng',
            'german': 'deu',
            'french': 'fra',
            'spanish': 'spa'
        }
        return mapping.get(name.lower(), 'eng')

    def translate_text(self, text, src_code, dst_code):
        print("OCR результат:", text)
        translator = GoogleTranslator()
        return translator.translate(text, src=src_code, dest=dst_code).text

    def translate_from_screen(self):
        img = ImageGrab.grab()
        src_code = self.lang_code(self.src_lang.currentText())
        dst_code = self.lang_code(self.dst_lang.currentText())

        try:
            lang_code = self.ocr_lang_code(self.src_lang.currentText())
            text = pytesseract.image_to_string(img, lang=lang_code)
        except:
            text = ""

        print("OCR язык:", lang_code)
        print("OCR результат:", text)

        if text.strip():
            translated = self.translate_text(text, src_code, dst_code)
            self.label.setText(translated)
        else:
            self.label.setText("Текст не распознан")


if __name__ == "__main__":
    import os
    os.environ["QT_QPA_PLATFORM"] = "windows"

    app = QApplication(sys.argv)
    window = TransparentTranslator()
    window.show()
    sys.exit(app.exec_())
