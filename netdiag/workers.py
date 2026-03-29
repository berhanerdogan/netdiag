import subprocess
import threading
import socket

from PyQt6.QtCore import QThread, pyqtSignal
from concurrent.futures import ThreadPoolExecutor

from netdiag.parsers import parse_ping, parse_nslookup, parse_mac, parse_arp


class PingWorker(QThread):
    done = pyqtSignal(str, str, dict)   # host, raw_output, parsed_stats

    def __init__(self, host):
        super().__init__()
        self.host = host
        self.lock = threading.Lock()

    def run(self):
        try:
            r = subprocess.run(
                ["ping", "-c", "3", self.host],
                capture_output=True, text=True, timeout=10
            )
            output = r.stdout if r.returncode == 0 else "Ping failed: Host unreachable."
        except subprocess.TimeoutExpired:
            output = "Ping failed: Timed out after 10 s."
        except Exception as e:
            output = f"Ping failed: {e}"
        self.done.emit(self.host, output, parse_ping(output))


class NslookupWorker(QThread):
    done = pyqtSignal(str, dict)        # domain, result_dict

    def __init__(self, domain):
        super().__init__()
        self.domain = domain

    def run(self):
        try:
            r    = subprocess.run(
                ["nslookup", self.domain],
                capture_output=True, text=True, timeout=10
            )
            data = parse_nslookup(r.stdout)
        except subprocess.TimeoutExpired:
            data = {"ip": "Error: Timed out", "status": "Failed"}
        except Exception as e:
            data = {"ip": f"Error: {e}", "status": "Failed"}
        self.done.emit(self.domain, data)


class NetInfoWorker(QThread):
    done = pyqtSignal(str, dict, bool)  # hostname, net_info, success

    def run(self):
        hostname = subprocess.run(
            ["hostname"], capture_output=True, text=True
        ).stdout.strip()
        try:
            r   = subprocess.run(["ifconfig", "en0"],
                                 capture_output=True, text=True)
            net = parse_mac(r.stdout)
            ok  = True
        except Exception as e:
            net = {"mac": f"Error: {e}", "ip": "Error"}
            ok  = False
        self.done.emit(hostname, net, ok)


class ArpWorker(QThread):
    done = pyqtSignal(list, bool)       # devices, success

    def run(self):
        try:
            r       = subprocess.run(["arp", "-a"],
                                     capture_output=True, text=True)
            devices = parse_arp(r.stdout)
            ok      = True
        except Exception as e:
            devices, ok = [], False
        self.done.emit(devices, ok)

class PortScanWorker(QThread):
    done     = pyqtSignal(str, str, dict)
    progress = pyqtSignal(int)

    KNOWN_SERVICES = {
        21: "ftp",    22: "ssh",     23: "telnet",
        25: "smtp",   53: "dns",     80: "http",
        110: "pop3",  143: "imap",   443: "https",
        445: "smb",   3306: "mysql", 3389: "rdp",
        5432: "postgresql", 6379: "redis", 8080: "http-alt",
    }

    PORT_RANGE = range(1, 65536)

    def __init__(self, host, parent=None):
        super().__init__(parent)
        self.host   = host
        self._open  = []
        self._lines = []
        self._lock  = threading.Lock()

    def _scan_port(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((self._ip, port))
            if result == 0:
                service = self.KNOWN_SERVICES.get(port, "unknown")
                line    = f"  {port}/tcp   open   {service}"
                with self._lock:
                    self._open.append(port)
                    self._lines.append(line)
        except socket.error:
            pass
        finally:
            sock.close()

    def run(self):
        try:
            self._ip = socket.gethostbyname(self.host)
        except socket.gaierror:
            data = {
                "status": "Failed", "open_count": 0, "closed_count": 0,
                "total_scanned": 0, "known_count": 0, "unknown_count": 0,
            }
            self.done.emit(self.host, "Error: hostname could not be resolved.", data)
            return

        total = len(self.PORT_RANGE)
        output_lines = [f"Scanning {self.host}  ({self._ip})  —  {total} ports\n"]
        ports    = list(self.PORT_RANGE)
        scanned  = 0

        with ThreadPoolExecutor(max_workers=100) as executor:
            for port in ports:
                executor.submit(self._scan_port, port)
                scanned += 1
                if scanned % 655 == 0:
                    self.progress.emit(min(100, int(scanned / total * 100)))

        self._lines.sort(key=lambda l: int(l.split("/")[0].strip()))
        output_lines += self._lines or ["  No open ports found."]
        output_lines.append(f"\nDone. {len(self._open)} open port(s) found.")

        open_c    = len(self._open)
        known_c   = sum(1 for p in self._open if p in self.KNOWN_SERVICES)
        unknown_c = open_c - known_c

        data = {
            "status":        "Success",
            "open_count":    open_c,
            "closed_count":  total - open_c,
            "total_scanned": total,
            "known_count":   known_c,
            "unknown_count": unknown_c,
        }
        self.done.emit(self.host, "\n".join(output_lines), data)