# crowwatch
# CrowWatch

CrowWatch is a Python-based network scanner with a raven-themed terminal interface. It is designed for educational and personal use, featuring interactive animations and enhanced terminal visuals.

## Features

- Raven-themed terminal UI
- Fly animation during operations
- Port range scanning
- Service classification with common ports
- HTTP banner grabbing
- Simple target testing (ping & HTTP headers)

## Requirements

- Python 3.8+
- `colorama` library

Install the required library with:

```bash
pip install colorama
##Usage:
python crowwatch.py

##Example output:

 🐦 CrowWatch — Silent. Sharp. Watching.
=== Main Menu ===
1. Network Scan
2. Target Test
3. Exit

Select an option: 1
Target IP or Domain: example.com
[info] Scanning ports 1-1024...
[ok] Open ports found:
  22  🗝️ SSH
  80  🌐 HTTP
HTTP Banner (port 80): 200 OK | Server: Apache/2.4.41 (Ubuntu)
