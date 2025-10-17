# ========================== CrowWatch v5.3 ==========================
# Karga temalı terminal aracı: Menü, Fly animasyon, renkli uyarılar, port aralığı,
# hedef testi, hacker terminal efekti, servis sınıflandırması ve HTTP banner grab
# ================================================================

import socket
import threading
import itertools
import sys
import time
import os
import subprocess
import http.client
from urllib.parse import urlparse
import random

# ---------------- Tema ve Banner ----------------
from colorama import init as colorama_init, Fore, Style
colorama_init(autoreset=True)

THEME = {
    "primary": Fore.WHITE + Style.BRIGHT,
    "muted": Fore.LIGHTBLACK_EX,
    "accent": Fore.CYAN + Style.BRIGHT,
    "danger": Fore.RED + Style.BRIGHT,
    "success": Fore.GREEN + Style.BRIGHT,
    "warning": Fore.YELLOW + Style.BRIGHT,
    "info": Fore.BLUE + Style.BRIGHT,
    "banner": Fore.LIGHTMAGENTA_EX + Style.BRIGHT
}

ICONS = {
    "raven": "🐦",
    "spark": "⚡",
    "lock": "🔒",
    "eye": "👁️",
    "star": "✦",
    "ok": "🟢",
    "warn": "⚠️",
    "error": "❌",
    "http": "🌐",
    "ssh": "🔑",
    "ftp": "📁",
    "smtp": "✉️",
    "unknown": "❓"
}

# ---------------- Hacker terminal efekti ----------------
_hacker_thread = None
_hacker_stop = None

def _hacker_worker():
    chars = "0123456789abcdef!@#$%^&*()_+-=[]{}|;:,.<>?/\\"
    width = 80
    while not _hacker_stop.is_set():
        line = "".join(random.choice(chars) for _ in range(width))
        sys.stdout.write(Fore.GREEN + line + "\r")
        sys.stdout.flush()
        time.sleep(0.03)
    sys.stdout.write("\r" + " " * width + "\r")
    sys.stdout.flush()

def start_hacker_effect():
    global _hacker_thread, _hacker_stop
    if _hacker_thread and _hacker_thread.is_alive():
        return
    _hacker_stop = threading.Event()
    _hacker_thread = threading.Thread(target=_hacker_worker)
    _hacker_thread.daemon = True
    _hacker_thread.start()

def stop_hacker_effect():
    global _hacker_stop, _hacker_thread
    if _hacker_stop:
        _hacker_stop.set()
    if _hacker_thread:
        _hacker_thread.join(timeout=0.5)
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()

# ---------------- Tema ve Banner ----------------
def print_banner(app_name="CrowWatch"):
    banner = r"""
   ██████╗ ██████╗ ██████╗ ██╗    ██╗    ██╗    ██╗██╗   ██╗███████╗
  ██╔════╝██╔═══██╗██╔══██╗██║    ██║    ██║    ██║██║   ██║██╔════╝
  ██║     ██║   ██║██████╔╝██║ █╗ ██║    ██║ █╗ ██║██║   ██║█████╗  
  ██║     ██║   ██║██╔═══╝ ██║███╗██║    ██║███╗██║██║   ██║██╔══╝  
  ╚██████╗╚██████╔╝██║     ╚███╔███╔╝    ╚███╔███╔╝╚██████╔╝███████╗
   ╚═════╝ ╚═════╝ ╚═╝      ╚══╝╚══╝      ╚══╝╚══╝  ╚═════╝ ╚══════╝
             {raven}  {app} — Silent. Sharp. Watching. 
    """.format(raven=ICONS["raven"], app=app_name)
    print(THEME["banner"] + banner + Style.RESET_ALL)

# ---------------- Çıktı fonksiyonları ----------------
def th_info(msg):
    print(THEME["info"] + "  " + ICONS["http"] + " " + str(msg))

def th_ok(msg):
    print(THEME["success"] + "  " + ICONS["ok"] + " " + str(msg))

def th_warn(msg):
    print(THEME["warning"] + "  " + ICONS["warn"] + " " + str(msg))

def th_err(msg):
    print(THEME["danger"] + "  " + ICONS["error"] + " " + str(msg))

def th_muted(msg):
    print(THEME["muted"] + "  " + str(msg))

# ---------------- Fly Animasyon ----------------
_anim_thread = None
_anim_stop = None

def _anim_worker(frames, delay):
    while not _anim_stop.is_set():
        for f in frames + frames[::-1]:
            if _anim_stop.is_set():
                break
            sys.stdout.write("\r" + f + " " * 10)
            sys.stdout.flush()
            time.sleep(delay)
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()

def start_anim(kind="fly"):
    global _anim_thread, _anim_stop
    if _anim_thread and _anim_thread.is_alive():
        return
    _anim_stop = threading.Event()
    if kind == "fly":
        frames = [
            "  ,_        Karga gözetliyor... ",
            " (o,o)      Karga gözetliyor... ",
            " {`\"}      Karga gözetliyor... ",
            " -\"-\"-     Karga gözetliyor... ",
            "  \\_/      Karga gözetliyor... ",
            " (o,o)~    Karga gözetliyor... ",
        ]
        delay = 0.15
    else:
        frames = ["[·      ]", "[ ·     ]", "[  ·    ]", "[   ·   ]",
                  "[    ·  ]", "[     · ]", "[      ·]", "[     · ]",
                  "[    ·  ]", "[   ·   ]", "[  ·    ]", "[ ·     ]"]
        delay = 0.07
    _anim_thread = threading.Thread(target=_anim_worker, args=(frames, delay))
    _anim_thread.daemon = True
    _anim_thread.start()

def stop_anim():
    global _anim_stop, _anim_thread
    if _anim_stop:
        _anim_stop.set()
    if _anim_thread:
        _anim_thread.join(timeout=0.5)
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()

# ---------------- Port Tarayıcı ve Servis Sınıflandırma ----------------
COMMON_SERVICES = {
    21: ("FTP", ICONS["ftp"]),
    22: ("SSH", ICONS["ssh"]),
    25: ("SMTP", ICONS["smtp"]),
    80: ("HTTP", ICONS["http"]),
    443: ("HTTPS", ICONS["http"]),
    110: ("POP3", ICONS["smtp"]),
    143: ("IMAP", ICONS["smtp"]),
}

def socket_scan(target, port_start=1, port_end=1024, timeout=0.5, max_threads=200):
    open_ports = []
    try:
        target_ip = socket.gethostbyname(target)
    except Exception as e:
        th_err(f"DNS çözümlemesi başarısız: {e}")
        return []

    lock = threading.Lock()
    ports = range(port_start, port_end + 1)

    def worker(port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            res = s.connect_ex((target_ip, port))
            with lock:
                open_ports.append((port, res == 0))
            s.close()
        except Exception:
            pass

    threads = []
    for port in ports:
        while threading.active_count() > max_threads:
            time.sleep(0.01)
        t = threading.Thread(target=worker, args=(port,))
        t.daemon = True
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    open_ports.sort(key=lambda x: x[0])
    return target_ip, open_ports

# ---------------- Tarama Fonksiyonu ----------------
def scan_target(target):
    th_info(f"{target} üzerinde tarama başlatılıyor...")

    try:
        port_start = int(input("Başlangıç portu (default 1): ") or 1)
        port_end = int(input("Bitiş portu (default 1024): ") or 1024)
        if port_start < 1: port_start = 1
        if port_end > 65535: port_end = 65535
        if port_start > port_end:
            port_start, port_end = port_end, port_start
    except:
        th_warn("Geçersiz giriş, varsayılan aralık 1-1024 kullanılıyor.")
        port_start, port_end = 1, 1024

    start_hacker_effect()
    start_anim("fly")
    try:
        ip, ports = socket_scan(target, port_start=port_start, port_end=port_end, timeout=0.4, max_threads=300)
        stop_anim()
        stop_hacker_effect()
        th_ok(f"Target: {target} -> {ip}")
        if ports:
            print(THEME["primary"] + "  Port Durum Tablosu:")
            print(THEME["muted"] + "  ---------------------------")
            print(THEME["muted"] + "  Port\tDurum\tServis")
            for port, is_open in ports:
                status = (Fore.GREEN + "Açık" if is_open else Fore.LIGHTBLACK_EX + "Kapalı") + Style.RESET_ALL
                service_name, icon = COMMON_SERVICES.get(port, ("Unknown", ICONS["unknown"]))
                print(f"  {port}\t{status}\t{icon} {service_name}")
            print(THEME["muted"] + "  ---------------------------")

            # Banner grab HTTP (port 80/443)
            for port, is_open in ports:
                if port in [80, 443] and is_open:
                    try:
                        scheme = "https" if port == 443 else "http"
                        url = f"{scheme}://{target}"
                        parsed = urlparse(url)
                        if scheme == "https":
                            conn = http.client.HTTPSConnection(parsed.netloc, timeout=3)
                        else:
                            conn = http.client.HTTPConnection(parsed.netloc, timeout=3)
                        conn.request("HEAD", "/")
                        resp = conn.getresponse()
                        headers = dict(resp.getheaders())
                        server = headers.get("Server", "Unknown")
                        th_info(f"HTTP Banner (port {port}): {resp.status} {resp.reason} | Server: {server}")
                    except Exception as e:
                        th_warn(f"HTTP banner alınamadı (port {port}): {e}")

        else:
            th_warn("Hiç port bulunamadı veya firewall tüm portları kapatmış olabilir.")
    finally:
        stop_anim()
        stop_hacker_effect()

# ---------------- Hedef Testi ----------------
def target_test(target):
    th_info(f"{target} üzerinde test başlatılıyor...")

    # Ping kontrolü
    try:
        param = "-n" if os.name == "nt" else "-c"
        res = subprocess.run(["ping", param, "1", target],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            th_ok("Ping başarılı (hedef erişilebilir).")
        else:
            th_warn("Ping başarısız (hedef ulaşılmaz).")
    except Exception as e:
        th_err(f"Ping hatası: {e}")

    # HTTP Header kontrolü
    try:
        if not target.startswith("http"):
            target_url = "http://" + target
        else:
            target_url = target
        parsed = urlparse(target_url)
        conn = None
        if parsed.scheme == "https":
            conn = http.client.HTTPSConnection(parsed.netloc, timeout=3)
        else:
            conn = http.client.HTTPConnection(parsed.netloc, timeout=3)
        conn.request("HEAD", "/")
        resp = conn.getresponse()
        headers = dict(resp.getheaders())
        server = headers.get("Server", "Unknown")
        th_info(f"HTTP Durum Kodu: {resp.status} {resp.reason} | Server: {server}")
    except Exception as e:
        th_warn(f"HTTP kontrolü başarısız: {e}")

# ---------------- Menü ----------------
def menu():
    print()
    th_muted("=== Ana Menü ===")
    print(THEME["primary"] + "  1. Ağ taraması")
    print(THEME["primary"] + "  2. Hedef testi")
    print(THEME["primary"] + "  3. Çıkış")
    return input(THEME["accent"] + "\nSeçiminiz: " + Style.RESET_ALL).strip()

def main():
    print_banner("CrowWatch")
    while True:
        choice = menu()
        if choice == "1":
            target = input("Hedef IP veya Domain: ").strip()
            if target:
                scan_target(target)
        elif choice == "2":
            target = input("Hedef IP veya Domain: ").strip()
            if target:
                target_test(target)
        elif choice == "3":
            th_ok("Karga yuvasına dönüyor... Görüşmek üzere 🐦")
            break
        else:
            th_warn("Geçersiz seçim!")

if __name__ == "__main__":
    main()
