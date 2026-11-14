#!/usr/bin/env python3
"""Ikona v systémovom paneli (systray) pre server s návodmi.

Spustí server.py, otvorí návody v prehliadači a do panela pridá ikonu:
  - ľavý klik: otvoriť návody v prehliadači
  - pravý klik: menu (otvoriť, kopírovať adresu do siete, reštartovať, zastaviť)

Použitie: python3 tray.py [port]
"""

import os
import signal
import socket
import subprocess
import sys
import warnings

import gi

# Gtk.StatusIcon je v GTK3 označený ako zastaraný, ale v Xfce paneli funguje.
warnings.filterwarnings("ignore", category=DeprecationWarning)

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk  # noqa: E402

DIR = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
ICON = os.path.join(DIR, "ikona.svg")
LOG = os.path.join(os.path.expanduser("~/.cache"), "navody-server.log")
LOCAL_URL = f"http://localhost:{PORT}/"


def lan_ip():
    try:
        out = subprocess.run(["hostname", "-I"], capture_output=True, text=True).stdout.split()
        return out[0] if out else ""
    except OSError:
        return ""


def port_busy(port):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def notify(text):
    subprocess.Popen(["notify-send", "-i", ICON, "Návody", text],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def open_browser(*_):
    subprocess.Popen(["xdg-open", LOCAL_URL], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class Tray:
    def __init__(self):
        self.proc = None
        self.lan_url = f"http://{lan_ip() or 'localhost'}:{PORT}/"

        self.icon = Gtk.StatusIcon()
        if os.path.exists(ICON):
            self.icon.set_from_file(ICON)
        else:
            self.icon.set_from_icon_name("network-server")
        self.icon.set_title("Návody")
        self.icon.connect("activate", open_browser)
        self.icon.connect("popup-menu", self.show_menu)

        self.menu = Gtk.Menu()
        self.status_item = Gtk.MenuItem(label="")
        self.status_item.set_sensitive(False)
        self.menu.append(self.status_item)
        self.menu.append(Gtk.SeparatorMenuItem())
        for label, cb in (
            ("Otvoriť návody v prehliadači", open_browser),
            ("Kopírovať adresu pre sieť", self.copy_lan_url),
            ("Reštartovať server", self.restart),
        ):
            item = Gtk.MenuItem(label=label)
            item.connect("activate", cb)
            self.menu.append(item)
        self.menu.append(Gtk.SeparatorMenuItem())
        quit_item = Gtk.MenuItem(label="Zastaviť server a skončiť")
        quit_item.connect("activate", self.quit)
        self.menu.append(quit_item)
        self.menu.show_all()

        self.start()
        GLib.timeout_add_seconds(2, self.watch)

    # --- server ---------------------------------------------------------
    def start(self):
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        log = open(LOG, "a")
        self.proc = subprocess.Popen(
            [sys.executable, os.path.join(DIR, "server.py"), str(PORT), DIR],
            stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
        )
        log.close()
        self.update_status()

    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self.proc = None

    def restart(self, *_):
        self.stop()
        self.start()
        notify("Server bol reštartovaný.")

    def watch(self):
        if self.proc and self.proc.poll() is not None:
            self.proc = None
            self.update_status()
            notify(f"Server sa neočakávane zastavil. Podrobnosti: {LOG}")
        return True

    def update_status(self):
        running = self.proc is not None and self.proc.poll() is None
        text = f"Server beží: {self.lan_url}" if running else "Server nebeží"
        self.status_item.set_label(text)
        self.icon.set_tooltip_text(f"Návody – {text}")

    # --- menu -----------------------------------------------------------
    def show_menu(self, icon, button, time):
        self.update_status()
        self.menu.popup(None, None, Gtk.StatusIcon.position_menu, icon, button, time)

    def copy_lan_url(self, *_):
        cb = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        cb.set_text(self.lan_url, -1)
        cb.store()
        notify(f"Adresa skopírovaná: {self.lan_url}")

    def quit(self, *_):
        self.stop()
        Gtk.main_quit()


def main():
    if port_busy(PORT):
        # Server už beží (napr. ikona je už v paneli) – len otvoriť prehliadač.
        open_browser()
        notify(f"Server na porte {PORT} už beží, otváram návody.")
        return
    tray = Tray()
    for sig in (signal.SIGINT, signal.SIGTERM):
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, sig, tray.quit)
    GLib.timeout_add(800, lambda: (open_browser(), False)[1])
    notify(f"Server spustený: {tray.lan_url}")
    Gtk.main()


if __name__ == "__main__":
    main()
