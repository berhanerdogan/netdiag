from PyQt6.QtWidgets import QHBoxLayout, QLabel, QTableWidgetItem
from PyQt6.QtGui import QColor

from netdiag.theme import C
from netdiag.workers import ArpWorker
from netdiag.widgets import GlowButton, make_table
from netdiag.pages.base import BasePage


class ArpPage(BasePage):
    def __init__(self, db, parent=None):
        super().__init__("ARP Scan", C["arp"], db, parent)
        self._worker = None
        self._build()

    def _build(self):
        btn_row = QHBoxLayout()
        self._btn   = GlowButton("Scan Network", C["arp"])
        self._btn.setFixedWidth(160)
        self._count = QLabel("— devices")
        self._count.setStyleSheet(
            f"color: {C['text2']}; font-family: 'SF Pro Display'; font-size: 14px;")
        self._btn.clicked.connect(self._run)
        btn_row.addWidget(self._btn)
        btn_row.addSpacing(16)
        btn_row.addWidget(self._count)
        btn_row.addStretch()
        self._outer.addLayout(btn_row)

        self._table = make_table(["IP Address", "MAC Address"])
        self._outer.addWidget(self._table, 1)


    def _run(self):
        self._btn.setEnabled(False)
        self._btn.setText("Scanning…")
        self._table.setRowCount(0)
        self._worker = ArpWorker()
        self._worker.done.connect(self._on_done)
        self._worker.start()

    def _on_done(self, devices, ok):
        self._table.setRowCount(len(devices))
        for i, d in enumerate(devices):
            ip  = QTableWidgetItem(d["ip"])
            mac = QTableWidgetItem(d["mac"])
            ip.setForeground(QColor(C["arp"]))
            mac.setForeground(QColor(C["text2"]))
            self._table.setItem(i, 0, ip)
            self._table.setItem(i, 1, mac)
        self._count.setText(f"{len(devices)} device(s) found")
        self._btn.setEnabled(True)
        self._btn.setText("Scan Network")
        self.db.insert("arp", "local",
                       f"{len(devices)} devices",
                       "Captured" if ok else "Failed")
        self.status_msg.emit(f"ARP scan  ·  {len(devices)} device(s)")
