from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLabel, QFrame, QSizePolicy
)
from PyQt6.QtCore import QTimer

from netdiag.theme import C
from netdiag.widgets import GlowButton, StatCard
from netdiag.pages.base import BasePage

CMD_COLOURS = {
    "ping":     C["ping"],
    "nslookup": C["dns"],
    "ifconfig": C["net"],
    "arp":      C["arp"],
}


class AnalyzePage(BasePage):
    def __init__(self, db, parent=None):
        super().__init__("Analyze", C["analyze"], db, parent)
        self._build()

    def _build(self):
        btn_row = QHBoxLayout()
        btn = GlowButton("Refresh", C["analyze"])
        btn.setFixedWidth(130)
        btn.clicked.connect(self._load)
        btn_row.addWidget(btn)
        btn_row.addStretch()
        self._outer.addLayout(btn_row)

        self._content = QVBoxLayout()
        self._content.setSpacing(20)
        self._outer.addLayout(self._content)
        self._outer.addStretch(1)
        self._load()

    def _load(self):
        # clear previous widgets
        while self._content.count():
            item = self._content.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                nested = item.layout()
                while nested.count():
                    child = nested.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

        total         = self.db.count()
        cmd_counts    = self.db.count_by_command()
        status_counts = self.db.count_by_status()
        success_rate  = self.db.success_rate()

        if total == 0:
            lbl = QLabel("No data yet — run some diagnostics first.")
            lbl.setStyleSheet(
                f"color: {C['text2']}; font-family: 'SF Pro Display'; font-size: 14px;")
            self._content.addWidget(lbl)
            return

        success_n = sum(n for s, n in status_counts if s in ("Success", "Captured"))
        failed_n  = sum(n for s, n in status_counts if s == "Failed")

        # summary cards
        summary = QHBoxLayout()
        summary.setSpacing(12)
        for label, val, colour in [
            ("TOTAL ENTRIES", str(total),         C["analyze"]),
            ("SUCCESSFUL",    str(success_n),     C["success"]),
            ("FAILED",        str(failed_n),      C["danger"]),
            ("SUCCESS RATE",  f"{success_rate}%", C["warning"]),
        ]:
            c = StatCard(label, val, colour)
            c.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            summary.addWidget(c)
        self._content.addLayout(summary)

        # bar chart
        self._content.addWidget(self._dim_label("Commands run"))
        card = self._card()
        cl   = QVBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(14)

        max_n = max((n for _, n in cmd_counts), default=1)

        for cmd, count in cmd_counts:
            row = QHBoxLayout()
            row.setSpacing(12)

            name = QLabel(cmd)
            name.setFixedWidth(90)
            name.setStyleSheet(
                f"color: {C['text']}; font-family: 'SF Mono','Menlo'; font-size: 13px;")

            bar_bg = QFrame()
            bar_bg.setFixedHeight(8)
            bar_bg.setStyleSheet(
                f"background: {C['border']}; border-radius: 4px;")

            colour = CMD_COLOURS.get(cmd, C["accent"])
            fill   = QFrame(bar_bg)
            fill.setFixedHeight(8)
            fill.setStyleSheet(f"""
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {colour}, stop:1 {C['accent2']});
                border-radius: 4px;
            """)

            cnt_lbl = QLabel(f"{count}×")
            cnt_lbl.setFixedWidth(36)
            cnt_lbl.setStyleSheet(
                f"color: {C['text2']}; font-family: 'SF Mono','Menlo'; font-size: 12px;")

            row.addWidget(name)
            row.addWidget(bar_bg, 1)
            row.addWidget(cnt_lbl)
            cl.addLayout(row)

            pct = count / max_n
            def resize(bar=fill, bg=bar_bg, p=pct):
                bar.setFixedWidth(max(6, int(bg.width() * p)))
            QTimer.singleShot(60, resize)

        self._content.addWidget(card)
        self.status_msg.emit(
            f"Analysis  ·  {total} entries  ·  {success_rate}% success")
