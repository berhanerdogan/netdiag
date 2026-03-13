import subprocess

from PyQt6.QtCore import QThread, pyqtSignal

from netdiag.parsers import parse_ping, parse_nslookup, parse_mac, parse_arp


class PingWorker(QThread):
    done = pyqtSignal(str, str, dict)   # host, raw_output, parsed_stats

    def __init__(self, host):
        super().__init__()
        self.host = host

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
