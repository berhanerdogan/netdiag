from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QTextEdit, QProgressBar
from netdiag.theme import C
from netdiag.workers import PortScanWorker
from netdiag.widgets import GlowButton, StyledInput, StatCard
from netdiag.pages.base import BasePage


class PortScanPage(BasePage):
    def __init__(self, db, parent=None):
        super().__init__("Port Scan", C["portscan"], db, parent)
        self._worker = None
        self._build()

    def _build(self):
        row = QHBoxLayout()
        self._entry = StyledInput("Hostname or IP  —  e.g. 192.168.1.1")
        self._btn   = GlowButton("Scan", C["portscan"])
        self._btn.clicked.connect(self._run)
        self._entry.returnPressed.connect(self._run)
        row.addWidget(self._entry)
        row.addSpacing(10)
        row.addWidget(self._btn)
        self._outer.addLayout(row)

        # ── Progress bar ──────────────────────────────────────
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setFixedHeight(4)   
        self._progress.setTextVisible(False)
        self._progress.setStyleSheet(f"""
            QProgressBar {{
                background: {C['border']};
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background: {C['portscan']};
                border-radius: 2px;
            }}
        """)
        self._progress.hide()   
        self._outer.addWidget(self._progress)

        # ── Stat cards ────────────────────────────────────────
        cards = QHBoxLayout()
        cards.setSpacing(12)
        self._c_open    = StatCard("OPEN",          "—", C["success"])
        self._c_closed  = StatCard("CLOSED",        "—", C["danger"])
        self._c_total   = StatCard("TOTAL SCANNED", "—", C["portscan"])
        self._c_known   = StatCard("KNOWN SERVICE", "—", C["accent"])
        self._c_unknown = StatCard("UNKNOWN",       "—", C["text2"])
        for c in [self._c_open, self._c_closed, self._c_total,
                  self._c_known, self._c_unknown]:
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
        self._btn.setText("Scanning…")
        self._output.setText(f"Scanning {host}…")
        self._progress.setValue(0)
        self._progress.show()   
        self._worker = PortScanWorker(host)
        self._worker.progress.connect(self._progress.setValue)   
        self._worker.done.connect(self._on_done)
        self._worker.start()

    def _on_done(self, host, output, d):
        self._progress.setValue(100)
        self._progress.hide()   
        ok = d["status"] == "Success"
        self._c_open.set_value(str(d["open_count"]),
                               C["success"] if d["open_count"] > 0 else C["text2"])
        self._c_closed.set_value(str(d["closed_count"]))
        self._c_total.set_value(str(d["total_scanned"]))
        self._c_known.set_value(str(d["known_count"]),
                                C["accent"] if d["known_count"] > 0 else C["text2"])
        self._c_unknown.set_value(str(d["unknown_count"]))
        self._output.setText(output)
        self._btn.setEnabled(True)
        self._btn.setText("Scan")
        self.db.insert("portscan", host, d["open_count"], d["status"])
        self.status_msg.emit(f"Port Scan  ·  {host}  ·  {d['open_count']} open")