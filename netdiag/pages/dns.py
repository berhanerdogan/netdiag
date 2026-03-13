from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel

from netdiag.theme import C
from netdiag.workers import NslookupWorker
from netdiag.widgets import GlowButton, StyledInput
from netdiag.pages.base import BasePage


class DnsPage(BasePage):
    def __init__(self, db, parent=None):
        super().__init__("DNS Lookup", C["dns"], db, parent)
        self._worker = None
        self._build()

    def _build(self):
        row = QHBoxLayout()
        self._entry = StyledInput("Domain name  —  e.g. example.com")
        self._btn   = GlowButton("Resolve", C["dns"])
        self._btn.clicked.connect(self._run)
        self._entry.returnPressed.connect(self._run)
        row.addWidget(self._entry)
        row.addSpacing(10)
        row.addWidget(self._btn)
        self._outer.addLayout(row)

        card = self._card()
        cl   = QVBoxLayout(card)
        cl.setContentsMargins(24, 20, 24, 20)
        cl.setSpacing(16)
        self._r_status = self._kv("Status",      "—")
        self._r_domain = self._kv("Domain",      "—")
        self._r_ip     = self._kv("Resolved IP", "—")
        for r in [self._r_status, self._r_domain, self._r_ip]:
            cl.addLayout(r["layout"])
        self._outer.addWidget(card)
        self._outer.addStretch(1)

    def _kv(self, label, value):
        layout = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setFixedWidth(130)
        lbl.setStyleSheet(
            f"color: {C['text2']}; font-family: 'SF Pro Display'; font-size: 12px;")
        val = QLabel(value)
        val.setStyleSheet(
            f"color: {C['text']}; font-family: 'SF Mono','Menlo'; font-size: 14px;")
        layout.addWidget(lbl)
        layout.addWidget(val)
        layout.addStretch()
        return {"layout": layout, "val": val}

    def _set(self, row, text, colour=None):
        row["val"].setText(text)
        c = colour or C["text"]
        row["val"].setStyleSheet(
            f"color: {c}; font-family: 'SF Mono','Menlo'; "
            f"font-size: 14px; font-weight: 600;")

    def _run(self):
        domain = self._entry.text().strip()
        if not domain:
            return
        self._btn.setEnabled(False)
        self._btn.setText("Resolving…")
        self._worker = NslookupWorker(domain)
        self._worker.done.connect(self._on_done)
        self._worker.start()

    def _on_done(self, domain, d):
        ok = d["status"] == "Success"
        self._set(self._r_status, d["status"], C["success"] if ok else C["danger"])
        self._set(self._r_domain, domain, C["dns"])
        self._set(self._r_ip, d["ip"], C["success"] if ok else C["danger"])
        self._btn.setEnabled(True)
        self._btn.setText("Resolve")
        self.db.insert("nslookup", domain, d["ip"], d["status"])
        self.status_msg.emit(f"DNS  ·  {domain}  →  {d['ip']}")
