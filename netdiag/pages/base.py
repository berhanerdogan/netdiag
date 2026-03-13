from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel
from PyQt6.QtCore import pyqtSignal

from netdiag.theme import C


class BasePage(QWidget):
    """Shared layout scaffold for every page: title, accent line, outer padding."""

    status_msg = pyqtSignal(str)

    def __init__(self, title, accent, db, parent=None):
        super().__init__(parent)
        self.db      = db
        self._accent = accent
        self.setStyleSheet(f"background: {C['bg']};")

        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(32, 28, 32, 24)
        self._outer.setSpacing(20)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"""
            color: {C['text']};
            font-family: 'SF Pro Display';
            font-size: 24px;
            font-weight: 700;
            letter-spacing: -0.5px;
        """)

        line = QFrame()
        line.setFixedHeight(3)
        line.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {accent}, stop:0.6 {C['accent2']}, stop:1 transparent);
            border-radius: 2px;
        """)

        self._outer.addWidget(title_lbl)
        self._outer.addWidget(line)

    def _card(self):
        """Return a styled card QFrame."""
        f = QFrame()
        f.setStyleSheet(f"""
            QFrame {{
                background: {C['card']};
                border: 1px solid {C['border']};
                border-radius: 12px;
            }}
        """)
        return f

    def _dim_label(self, text):
        """Return a small all-caps dimmed section label."""
        l = QLabel(text.upper())
        l.setStyleSheet(f"""
            color: {C['text2']};
            font-family: 'SF Pro Display';
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 1.5px;
        """)
        return l
