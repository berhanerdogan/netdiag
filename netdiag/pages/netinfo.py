from PyQt6.QtWidgets import QHBoxLayout, QSizePolicy

from netdiag.theme import C
from netdiag.workers import NetInfoWorker
from netdiag.widgets import GlowButton, StatCard
from netdiag.pages.base import BasePage


class NetInfoPage(BasePage):
    def __init__(self, db, parent=None):
        super().__init__("Network Info", C["net"], db, parent)
        self._worker = None
        self._build()

    def _build(self):
        btn_row = QHBoxLayout()
        self._btn = GlowButton("Refresh", C["net"])
        self._btn.setFixedWidth(140)
        self._btn.clicked.connect(self._run)
        btn_row.addWidget(self._btn)
        btn_row.addStretch()
        self._outer.addLayout(btn_row)

        cards = QHBoxLayout()
        cards.setSpacing(12)
        self._c_host = StatCard("HOSTNAME",    "—", C["net"])
        self._c_mac  = StatCard("MAC ADDRESS", "—", C["warning"])
        self._c_ip   = StatCard("IP ADDRESS",  "—", C["accent"])
        for c in [self._c_host, self._c_mac, self._c_ip]:
            c.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            cards.addWidget(c)
        self._outer.addLayout(cards)
        self._outer.addStretch(1)
        self._run()

    def _run(self):
        self._btn.setEnabled(False)
        self._btn.setText("Loading…")
        self._worker = NetInfoWorker()
        self._worker.done.connect(self._on_done)
        self._worker.start()

    def _on_done(self, hostname, net, ok):
        self._c_host.set_value(hostname)
        self._c_mac.set_value(net["mac"])
        self._c_ip.set_value(net["ip"], C["success"] if ok else C["danger"])
        self._btn.setEnabled(True)
        self._btn.setText("Refresh")
        self.db.insert("ifconfig", "en0",
                       f'{net["mac"]} / {net["ip"]}',
                       "Captured" if ok else "Failed")
        self.status_msg.emit(f"Network info  ·  {net['ip']}")
