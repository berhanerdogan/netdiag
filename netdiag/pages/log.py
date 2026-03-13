from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QTableWidgetItem
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

from netdiag.theme import C
from netdiag.widgets import GlowButton, make_table
from netdiag.pages.base import BasePage

CMD_COLOURS = {
    "ping":     C["ping"],
    "nslookup": C["dns"],
    "ifconfig": C["net"],
    "arp":      C["arp"],
}


class LogPage(BasePage):
    def __init__(self, db, parent=None):
        super().__init__("Log Viewer", C["log"], db, parent)
        self._build()

    def _build(self):
        btn_row = QHBoxLayout()

        refresh = GlowButton("Refresh", C["log"])
        refresh.setFixedWidth(120)
        refresh.clicked.connect(self._load)

        clear = QPushButton("Clear Log")
        clear.setFixedHeight(42)
        clear.setCursor(Qt.CursorShape.PointingHandCursor)
        clear.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {C['danger']};
                border: 1px solid {C['danger']}55;
                border-radius: 8px;
                font-family: 'SF Pro Display';
                font-size: 13px;
                padding: 0 20px;
            }}
            QPushButton:hover {{ background: {C['danger']}18; }}
        """)
        clear.clicked.connect(self._clear)

        self._count_lbl = QLabel("")
        self._count_lbl.setStyleSheet(
            f"color: {C['text2']}; font-family: 'SF Pro Display'; font-size: 13px;")

        btn_row.addWidget(refresh)
        btn_row.addSpacing(10)
        btn_row.addWidget(clear)
        btn_row.addSpacing(14)
        btn_row.addWidget(self._count_lbl)
        btn_row.addStretch()
        self._outer.addLayout(btn_row)

        self._table = make_table(
            ["#", "Timestamp", "Command", "Target", "Result", "Status"])
        self._outer.addWidget(self._table, 1)
        self._load()

    def _load(self):
        rows = self.db.all()
        self._table.setRowCount(0)
        self._count_lbl.setText(f"{len(rows)} entries")
        self._table.setRowCount(len(rows))
        for i, (id_, ts, cmd, target, result, status) in enumerate(rows):
            ok    = status in ("Success", "Captured")
            items = [
                QTableWidgetItem(str(id_)),
                QTableWidgetItem(ts),
                QTableWidgetItem(cmd),
                QTableWidgetItem(target),
                QTableWidgetItem(result or ""),
                QTableWidgetItem(status),
            ]
            items[0].setForeground(QColor(C["text3"]))
            items[1].setForeground(QColor(C["text2"]))
            items[2].setForeground(QColor(CMD_COLOURS.get(cmd, C["text"])))
            items[3].setForeground(QColor(C["text"]))
            items[4].setForeground(QColor(C["text2"]))
            items[5].setForeground(QColor(C["success"] if ok else C["danger"]))
            for j, item in enumerate(items):
                self._table.setItem(i, j, item)
        self.status_msg.emit(f"Log  ·  {len(rows)} entries")

    def _clear(self):
        self.db.clear()
        self._load()
        self.status_msg.emit("Log cleared")
