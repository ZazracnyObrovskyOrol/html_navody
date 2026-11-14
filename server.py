#!/usr/bin/env python3
"""HTTP server pre návody.

Okrem bežných súborov obsluhuje /zoznam.json – zoznam všetkých *.html
súborov v adresári (okrem index.html) s nadpisom a popisom, ktorý
index.html načíta a zobrazí. Nový návod stačí vložiť do adresára.

Použitie: python3 server.py [port] [adresár]
"""

import json
import os
import sys
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class InfoParser(HTMLParser):
    """Vytiahne <title>, meta description, prvé <h1> a prvý <p class="lead">."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.h1 = ""
        self.description = ""
        self.lead = ""
        self._in = None  # "title" | "h1" | "lead"

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title" and not self.title:
            self._in = "title"
        elif tag == "h1" and not self.h1:
            self._in = "h1"
        elif tag == "p" and not self.lead and "lead" in (a.get("class") or "").split():
            self._in = "lead"
        elif tag == "meta" and (a.get("name") or "").lower() == "description":
            self.description = (a.get("content") or "").strip()

    def handle_endtag(self, tag):
        if (self._in, tag) in (("title", "title"), ("h1", "h1"), ("lead", "p")):
            self._in = None

    def handle_data(self, data):
        if self._in:
            setattr(self, self._in, getattr(self, self._in) + data)


def clean(text):
    return " ".join(text.split())


def zoznam(directory):
    items = []
    for name in sorted(os.listdir(directory), key=str.lower):
        path = os.path.join(directory, name)
        if not name.lower().endswith(".html") or name.lower() == "index.html":
            continue
        if not os.path.isfile(path):
            continue
        p = InfoParser()
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                p.feed(f.read())
        except OSError:
            continue
        items.append({
            "subor": name,
            "nadpis": clean(p.h1) or clean(p.title) or name,
            "popis": clean(p.description) or clean(p.lead),
            "zmenene": int(os.path.getmtime(path)),
        })
    return items


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?", 1)[0] == "/zoznam.json":
            body = json.dumps(zoznam(self.directory), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    directory = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))
    server = ThreadingHTTPServer(("0.0.0.0", port), partial(Handler, directory=directory))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer zastavený.")


if __name__ == "__main__":
    main()
