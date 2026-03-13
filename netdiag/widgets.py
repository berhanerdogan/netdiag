from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QTableWidget, QHeaderView, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QBrush

from netdiag.theme import C


class GlowButton(QPushButton):
    def __init__(self, text, colour=None, parent=None):
        super().__init__(text, parent)
        colour = colour or C["accent"]
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(42)
        r, g, b = int(colour[1:3], 16), int(colour[3:5], 16), int(colour[5:7], 16)
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {colour}, stop:1 {C['accent2']});
                color: white;
                border: none;
                border-radius: 8px;
                font-family: 'SF Pro Display';
                font-size: 13px;
                font-weight: 600;
                padding: 0 28px;
                letter-spacing: 0.3px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #6fa3ff, stop:1 #9d7dff);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #3a7ae8, stop:1 #6a4de8);
            }}
            QPushButton:disabled {{
                background: {C['border2']};
                color: {C['text3']};
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(r, g, b, 100))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)


class StyledInput(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(44)
        self.setStyleSheet(f"""
            QLineEdit {{
                background: {C['card']};
                color: {C['text']};
                border: 1.5px solid {C['border2']};
                border-radius: 8px;
                font-family: 'SF Mono', 'Menlo';
                font-size: 13px;
                padding: 0 14px;
                selection-background-color: {C['accent']};
            }}
            QLineEdit:focus {{
                border-color: {C['accent']};
                background: #1a1a28;
            }}
        """)


class StatCard(QFrame):
    def __init__(self, label, value="—", accent=None, parent=None):
        super().__init__(parent)
        self._accent = accent or C["accent"]
        self.setStyleSheet(f"""
            QFrame {{
                background: {C['card']};
                border: 1px solid {C['border']};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        self._val = QLabel(value)
        self._val.setStyleSheet(f"""
            color: {self._accent};
            font-family: 'SF Mono', 'Menlo';
            font-size: 22px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"""
            color: {C['text2']};
            font-family: 'SF Pro Display';
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 1px;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self._val)
        layout.addWidget(lbl)

    def set_value(self, v, colour=None):
        self._val.setText(str(v))
        c = colour or self._accent
        self._val.setStyleSheet(f"""
            color: {c};
            font-family: 'SF Mono', 'Menlo';
            font-size: 22px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)


class SidebarButton(QPushButton):
    def __init__(self, icon, label, colour, parent=None):
        super().__init__(parent)
        self._colour = colour
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(48)
        self.setCheckable(True)
        self.setText(f"  {icon}  {label}")
        self._apply(False)

    def _apply(self, active):
        c = self._colour
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {c}18;
                    border: none;
                    border-left: 3px solid {c};
                    color: {c};
                    font-family: 'SF Pro Display';
                    font-size: 13px;
                    font-weight: 600;
                    text-align: left;
                    padding-left: 20px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-left: 3px solid transparent;
                    color: {C['text2']};
                    font-family: 'SF Pro Display';
                    font-size: 13px;
                    text-align: left;
                    padding-left: 20px;
                }}
                QPushButton:hover {{
                    background: {C['surface']};
                    color: {C['text']};
                }}
            """)

    def set_active(self, v):
        self._apply(v)
        self.setChecked(v)


class PulsingDot(QWidget):
    def __init__(self, colour=None, parent=None):
        super().__init__(parent)
        self.setFixedSize(10, 10)
        self._colour  = QColor(colour or C["success"])
        self._opacity = 1.0
        self._dir     = -1
        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(30)

    def _tick(self):
        self._opacity += self._dir * 0.03
        if self._opacity <= 0.3:
            self._dir = 1
        elif self._opacity >= 1.0:
            self._dir = -1
        self.update()

    def paintEvent(self, _):
        from PyQt6.QtGui import QPainter
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = QColor(self._colour)
        c.setAlphaF(self._opacity)
        p.setBrush(QBrush(c))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(0, 0, 10, 10)


def make_table(columns):
    """Factory for a consistently styled QTableWidget."""
    t = QTableWidget(0, len(columns))
    t.setHorizontalHeaderLabels(columns)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    t.verticalHeader().setVisible(False)
    t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    t.setShowGrid(False)
    t.setAlternatingRowColors(True)
    t.setStyleSheet(f"""
        QTableWidget {{
            background: {C['card']};
            alternate-background-color: {C['surface']};
            color: {C['text']};
            border: 1px solid {C['border']};
            border-radius: 12px;
            font-family: 'SF Mono', 'Menlo';
            font-size: 12px;
            gridline-color: transparent;
            outline: 0;
        }}
        QTableWidget::item {{
            padding: 9px 14px;
            border: none;
        }}
        QTableWidget::item:selected {{
            background: {C['accent']}22;
            color: {C['text']};
        }}
        QHeaderView::section {{
            background: {C['surface']};
            color: {C['text2']};
            font-family: 'SF Pro Display';
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 1.2px;
            padding: 10px 14px;
            border: none;
            border-bottom: 1px solid {C['border']};
        }}
        QScrollBar:vertical {{
            background: {C['surface']};
            width: 6px;
            border-radius: 3px;
        }}
        QScrollBar::handle:vertical {{
            background: {C['border2']};
            border-radius: 3px;
        }}
    """)
    return t
