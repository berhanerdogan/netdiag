def parse_ping(output):
    s = {"transmitted": 0, "received": 0,
         "loss": "100%", "avg_ms": "N/A", "status": "Failed"}
    for line in output.strip().split("\n"):
        if "packets transmitted" in line:
            parts = line.split(", ")
            try:
                s["transmitted"] = int(parts[0].strip().split()[0])
                s["received"]    = int(parts[1].strip().split()[0])
                s["loss"]        = parts[2].strip().split()[0]
            except Exception:
                pass
        if "round-trip" in line or "rtt" in line:
            try:
                s["avg_ms"] = line.split("=")[1].strip().split("/")[1]
            except Exception:
                pass
    if s["received"] > 0:
        s["status"] = "Success"
    return s


def parse_nslookup(output):
    found = False
    for line in output.strip().split("\n"):
        if "Non-authoritative answer" in line:
            found = True
        if found and "Address:" in line:
            ip = line.split("Address:")[1].strip()
            if ip and "." in ip:
                return {"ip": ip, "status": "Success"}
    return {"ip": "Not found", "status": "Failed"}


def parse_mac(output):
    info = {"mac": "Not found", "ip": "Not found"}
    for line in output.strip().split("\n"):
        line = line.strip()
        if line.startswith("ether"):
            info["mac"] = line.split()[1]
        if "inet " in line and "inet6" not in line:
            info["ip"] = line.split()[1]
    return info


def parse_arp(output):
    devices = []
    for line in output.strip().split("\n"):
        if "at" in line and "on" in line:
            parts   = line.split()
            ip, mac = "unknown", "unknown"
            for p in parts:
                if p.startswith("(") and p.endswith(")"):
                    ip = p[1:-1]
            idx = parts.index("at")
            if idx + 1 < len(parts):
                mac = parts[idx + 1]
            devices.append({"ip": ip, "mac": mac})
    return devices
