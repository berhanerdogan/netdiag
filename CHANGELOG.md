# Changelog

All notable changes to NetDiag will be documented here.


## [1.1.0] - 2026-03-29
### Added
- **Port Scanner** — scan all 65535 ports on any host or IP
- Open, closed, total scanned, known service, and unknown port statistics
- Real-time progress bar during scan
- Known services labelled (ftp, ssh, http, https, mysql etc.)
- Unknown open ports counted and displayed separately

## [1.0.0] - 2026-03-12

### Initial Release
- Ping with latency stats (sent, received, packet loss, avg ms)
- DNS Lookup — resolve domains to IP
- Network Info — MAC address, IP, interface details
- ARP Scan — discover devices on local network
- Log Viewer — persistent SQLite log with timestamp, command, target, result, status
- Analyze — command usage breakdown and success rate
- macOS pre-built binaries (.dmg and .zip)
