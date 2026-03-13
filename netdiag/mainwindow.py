import subprocess

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QStackedWidget
)
from PyQt6.QtCore import pyqtSignal

from netdiag.theme import C
from netdiag.widgets import PulsingDot, SidebarButton
from netdiag.database import Database
from netdiag.pages import (
    PingPage, DnsPage, NetInfoPage, ArpPage, LogPage, AnalyzePage
)


class Sidebar(QFrame):
    page_changed = pyqtSignal(int)

    ITEMS = [
        ("⬡", "Ping",         C["ping"]),
        ("◈", "DNS Lookup",   C["dns"]),
        ("◉", "Network Info", C["net"]),
        ("⬡", "ARP Scan",     C["arp"]),
        ("≡", "Log Viewer",   C["log"]),
        ("◎", "Analyze",      C["analyze"]),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setStyleSheet(f"""
            QFrame {{
                background: {C['surface']};
                border-bottom: 1px solid {C['border']};
                border-right: none;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # logo
        logo_frame = QFrame()
        logo_frame.setFixedHeight(64)
        logo_frame.setStyleSheet(f"""
            background: {C['surface']};
            border-bottom: 1px solid {C['border']};
        """)
        ll = QHBoxLayout(logo_frame)
        ll.setContentsMargins(20, 0, 0, 0)
        dot = PulsingDot(C["success"])
        logo_lbl = QLabel("NetDiag")
        logo_lbl.setStyleSheet(f"""
            color: {C['text']};
            font-family: 'SF Pro Display';
            font-size: 16px;
            font-weight: 700;
            letter-spacing: -0.3px;
        """)
        ll.addWidget(dot)
        ll.addSpacing(8)
        ll.addWidget(logo_lbl)
        ll.addStretch()
        layout.addWidget(logo_frame)
        layout.addSpacing(12)

        self._buttons = []
        for i, (icon, label, colour) in enumerate(self.ITEMS):
            btn = SidebarButton(icon, label, colour)
            btn.clicked.connect(lambda _, idx=i: self._select(idx))
            layout.addWidget(btn)
            self._buttons.append(btn)

        layout.addStretch()

        hostname = subprocess.run(
            ["hostname"], capture_output=True, text=True).stdout.strip()
        foot = QLabel(f"  {hostname}")
        foot.setStyleSheet(f"""
            color: {C['text3']};
            font-family: 'SF Mono', 'Menlo';
            font-size: 10px;
            padding: 12px 0;
            border-top: 1px solid {C['border']};
        """)
        layout.addWidget(foot)
        self._select(0)

    def _select(self, idx):
        for i, btn in enumerate(self._buttons):
            btn.set_active(i == idx)
        self.page_changed.emit(idx)


class StatusBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(28)
        self.setStyleSheet(f"""
            QFrame {{
                background: {C['surface']};
                border-top: 1px solid {C['border']};
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        dot = PulsingDot(C["success"])
        self._msg = QLabel("Ready  ·  netdiag.db")
        self._msg.setStyleSheet(
            f"color: {C['text2']}; font-family: 'SF Pro Display'; font-size: 11px;")
        ver = QLabel("v2.0  ·  SQLite")
        ver.setStyleSheet(
            f"color: {C['text3']}; font-family: 'SF Mono','Menlo'; font-size: 10px;")
        layout.addWidget(dot)
        layout.addSpacing(6)
        layout.addWidget(self._msg)
        layout.addStretch()
        layout.addWidget(ver)

    def set_message(self, msg):
        self._msg.setText(msg)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetDiag — Network Diagnostic Logger")
        self.setMinimumSize(960, 640)
        self.resize(1100, 700)

        self._db = Database("netdiag.db")

        central = QWidget()
        central.setStyleSheet(f"background: {C['bg']};")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self._sidebar    = Sidebar()
        self._stack      = QStackedWidget()
        self._status_bar = StatusBar()

        self._pages = [
            PingPage(self._db),
            DnsPage(self._db),
            NetInfoPage(self._db),
            ArpPage(self._db),
            LogPage(self._db),
            AnalyzePage(self._db),
        ]
        for p in self._pages:
            p.status_msg.connect(self._status_bar.set_message)
            self._stack.addWidget(p)

        self._sidebar.page_changed.connect(self._stack.setCurrentIndex)

        body.addWidget(self._sidebar)
        body.addWidget(self._stack, 1)

        root.addLayout(body, 1)
        root.addWidget(self._status_bar)
