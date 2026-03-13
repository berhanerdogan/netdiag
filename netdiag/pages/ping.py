from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QTextEdit
from PyQt6.QtCore import Qt

from netdiag.theme import C
from netdiag.workers import PingWorker
from netdiag.widgets import GlowButton, StyledInput, StatCard
from netdiag.pages.base import BasePage


class PingPage(BasePage):
    def __init__(self, db, parent=None):
        super().__init__("Ping", C["ping"], db, parent)
        self._worker = None
        self._build()

    def _build(self):
        row = QHBoxLayout()
        self._entry = StyledInput("Hostname or IP  —  e.g. google.com")
        self._btn   = GlowButton("Run Ping", C["ping"])
        self._btn.clicked.connect(self._run)
        self._entry.returnPressed.connect(self._run)
        row.addWidget(self._entry)
        row.addSpacing(10)
        row.addWidget(self._btn)
        self._outer.addLayout(row)

        cards = QHBoxLayout()
        cards.setSpacing(12)
        self._c_status   = StatCard("STATUS",     "—", C["text2"])
        self._c_sent     = StatCard("SENT",        "—", C["ping"])
        self._c_received = StatCard("RECEIVED",    "—", C["success"])
        self._c_loss     = StatCard("PACKET LOSS", "—", C["warning"])
        self._c_latency  = StatCard("AVG LATENCY", "—", C["accent2"])
        for c in [self._c_status, self._c_sent, self._c_received,
                  self._c_loss, self._c_latency]:
            cards.addWidget(c)
        self._outer.addLayout(cards)

        self._outer.addWidget(self._dim_label("Raw output"))
        out_card = self._card()
        v = QVBoxLayout(out_card)
        v.setContentsMargins(0, 0, 0, 0)
        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setStyleSheet(f"""
            QTextEdit {{
                background: transparent;
                color: {C['text2']};
                font-family: 'SF Mono', 'Menlo';
                font-size: 12px;
                border: none;
                padding: 16px;
            }}
            QScrollBar:vertical {{
                background: {C['surface']}; width: 6px; border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {C['border2']}; border-radius: 3px;
            }}
        """)
        v.addWidget(self._output)
        self._outer.addWidget(out_card, 1)

    def _run(self):
        host = self._entry.text().strip()
        if not host:
            return
        self._btn.setEnabled(False)
        self._btn.setText("Running…")
        self._output.setText(f"Pinging {host}…")
        self._worker = PingWorker(host)
        self._worker.done.connect(self._on_done)
        self._worker.start()

    def _on_done(self, host, output, d):
        ok = d["status"] == "Success"
        self._c_status.set_value(d["status"], C["success"] if ok else C["danger"])
        self._c_sent.set_value(d["transmitted"])
        self._c_received.set_value(d["received"])
        self._c_loss.set_value(d["loss"],
                               C["success"] if d["loss"] == "0%" else C["danger"])
        self._c_latency.set_value(
            f"{d['avg_ms']} ms" if d["avg_ms"] != "N/A" else "N/A")
        self._output.setText(output)
        self._btn.setEnabled(True)
        self._btn.setText("Run Ping")
        self.db.insert("ping", host, d["avg_ms"], d["status"])
        self.status_msg.emit(f"Ping  ·  {host}  ·  {d['status']}")
