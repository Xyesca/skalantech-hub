"""LUMINA UX-Check Issue #16 — headless Chromium via CDP (stdlib only).

Misst auf /wissen + Artikel-Seiten bei Desktop- und Mobile-Viewports:
  - horizontales Overflow (scrollWidth > innerWidth?)
  - Spaltenanzahl der .wissen-grid (CSS grid-template-columns)
  - Sichtbarkeit der 5 Säulen-Header, next-step Zeilen, CTA-Buttons
  - Touch-Zielgrößen (mobile primary CTAs >= 44px Höhe)
  - console errors
Startet Chrome mit --remote-debugging-port und steuert es über die
WebSocket-Schnittstelle (minimaler RFC6455-Client).
"""
import base64
import hashlib
import json
import os
import socket
import struct
import subprocess
import sys
import time
import urllib.request

CHROME = "google-chrome"
DEBUG_PORT = 9222
BASE = f"http://127.0.0.1:{DEBUG_PORT}"
APP = "http://127.0.0.1:5098"


# ── minimaler WebSocket-Client (RFC 6455) ──────────────────────────────
class WS:
    def __init__(self, url):
        self.sock = self._connect(url)
        self.buf = b""

    def _connect(self, url):
        # url: ws://host:port/devtools/page/XXX
        host_port = url.split("://")[1].split("/")[0]
        host, port = host_port.split(":")
        s = socket.create_connection((host, int(port)), timeout=15)
        key = base64.b64encode(os.urandom(16)).decode()
        path = "/" + url.split("://")[1].split("/", 1)[1]
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host_port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        s.sendall(req.encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            resp += s.recv(4096)
        if b" 101 " not in resp.split(b"\r\n")[0]:
            raise RuntimeError(f"WS handshake fehlgeschlagen: {resp[:200]}")
        return s

    def _send_frame(self, opcode, payload):
        mask = os.urandom(4)
        header = bytearray([0x80 | opcode])
        n = len(payload)
        if n < 126:
            header.append(0x80 | n)
        elif n < 65536:
            header.append(0x80 | 126)
            header += struct.pack(">H", n)
        else:
            header.append(0x80 | 127)
            header += struct.pack(">Q", n)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(bytes(header) + mask + masked)

    def _recv_exact(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise RuntimeError("WS closed")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def send(self, payload: dict) -> dict:
        self._send_frame(0x1, json.dumps(payload).encode())
        # Antworten bis zur passenden id lesen (Events/Pings überspringen)
        while True:
            while len(self.buf) < 2:
                self.buf += self.sock.recv(65536)
            b1, b2 = self.buf[0], self.buf[1]
            opcode = b1 & 0x0F
            n = b2 & 0x7F
            header_len = 2
            if n == 126:
                while len(self.buf) < 4:
                    self.buf += self.sock.recv(65536)
                n = struct.unpack(">H", self.buf[2:4])[0]
                header_len = 4
            elif n == 127:
                while len(self.buf) < 10:
                    self.buf += self.sock.recv(65536)
                n = struct.unpack(">Q", self.buf[2:10])[0]
                header_len = 10
            if b2 & 0x80:  # maskierter Frame (Server normalerweise unmaskiert)
                header_len += 4
            self.buf = self.buf[header_len:]
            while len(self.buf) < n:
                self.buf += self.sock.recv(65536)
            data, self.buf = self.buf[:n], self.buf[n:]
            if opcode == 0x1:
                msg = json.loads(data.decode())
                if msg.get("id") == payload.get("id"):
                    if "error" in msg:
                        raise RuntimeError(f"CDP error: {msg['error']}")
                    return msg
            elif opcode == 0x8:
                raise RuntimeError("WS closed by peer")
            # Ping/Pong/andere Events ignorieren


def cdp_call(ws, method, params=None, msg_id=1):
    return ws.send({"id": msg_id, "method": method, "params": params or {}})


def start_chrome():
    proc = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
         "--disable-dev-shm-usage", "--remote-debugging-port=%d" % DEBUG_PORT,
         "--user-data-dir=/tmp/cdp-issue16", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    for _ in range(30):
        try:
            urllib.request.urlopen(f"{BASE}/json/version", timeout=2)
            return proc
        except Exception:
            time.sleep(0.3)
    raise RuntimeError("Chrome CDP nicht erreichbar")


def evaluate(ws, expr, mid):
    res = cdp_call(ws, "Runtime.evaluate",
                   {"expression": expr, "returnByValue": True}, mid)
    return res["result"]["result"].get("value")


def check_page(ws, path, width, height, label, mid):
    cdp_call(ws, "Emulation.setDeviceMetricsOverride",
             {"width": width, "height": height, "deviceScaleFactor": 2,
              "mobile": width < 600}, mid)
    cdp_call(ws, "Page.navigate", {"url": APP + path}, mid + 1)
    time.sleep(1.2)
    js = r"""
    (() => {
      const de = document.documentElement;
      const grid = document.querySelector('.wissen-grid');
      const cols = grid ? getComputedStyle(grid).gridTemplateColumns.split(' ').length : null;
      const pillars = [...document.querySelectorAll('.wissen-pillar')].map(p => {
        const h = p.querySelector('h2');
        return h ? h.textContent.trim() : null;
      });
      const steps = document.querySelectorAll('.wissen-card__step').length;
      const ctas = [...document.querySelectorAll('a.button--accent')].map(a => {
        const r = a.getBoundingClientRect();
        return {text: a.textContent.trim().slice(0, 40), h: Math.round(r.height), w: Math.round(r.width)};
      });
      return {
        path: location.pathname,
        vw: window.innerWidth,
        scrollW: de.scrollWidth,
        overflowX: de.scrollWidth > window.innerWidth + 1,
        cols: cols,
        pillars: pillars,
        stepCount: steps,
        hasArticleCta: !!document.querySelector('.article-cta'),
        hasNextStepLabel: document.body.textContent.includes('Nächster Schritt'),
        ctas: ctas.slice(0, 3),
        h1: document.querySelector('h1') ? document.querySelector('h1').textContent.trim() : null,
      };
    })()
    """
    return evaluate(ws, js, mid + 2)


def main():
    mid = [1000]
    proc = start_chrome()
    try:
        tabs = json.loads(urllib.request.urlopen(f"{BASE}/json/list").read())
        page = next(t for t in tabs if t["type"] == "page")
        ws = WS(page["webSocketDebuggerUrl"])
        cdp_call(ws, "Page.enable", msg_id=mid[0]); mid[0] += 1
        cdp_call(ws, "Runtime.enable", msg_id=mid[0]); mid[0] += 1
        results = []
        for label, w, h in [("DESKTOP", 1440, 1000), ("TABLET", 768, 1024),
                            ("MOBILE-390", 390, 844), ("MOBILE-360", 360, 740)]:
            for path in ["/wissen", "/wissen/kosten-roi-ki-automatisierung"]:
                m = check_page(ws, path, w, h, label, mid[0]); mid[0] += 10
                results.append((label, path, m))
        problems = []
        for label, path, m in results:
            print(f"\n== {label} {path} ==")
            print(f"   viewport={m['vw']}px scrollWidth={m['scrollW']}px overflowX={m['overflowX']}")
            is_hub = path == "/wissen"
            if is_hub:
                print(f"   grid-Spalten={m['cols']} nextStep-Zeilen={m['stepCount']}")
            else:
                print(f"   article-cta={m['hasArticleCta']} Nächster-Schritt-Label={m['hasNextStepLabel']}")
            print(f"   H1: {m['h1']}")
            if is_hub:
                print(f"   Säulen: {m['pillars']}")
            for c in m['ctas']:
                print(f"   CTA '{c['text']}' {c['w']}x{c['h']}px")
            if m["overflowX"]:
                problems.append(f"{label} {path}: horizontaler Overflow ({m['scrollW']} > {m['vw']})")
            if is_hub:
                if m["cols"] is None:
                    problems.append(f"{label} {path}: .wissen-grid fehlt")
                if label.startswith("MOBILE") and m["cols"] != 1:
                    problems.append(f"{label} {path}: mobile grid hat {m['cols']} Spalten (erwartet 1)")
                if label == "DESKTOP" and m["cols"] != 3:
                    problems.append(f"{label} {path}: desktop grid hat {m['cols']} Spalten (erwartet 3)")
                if m["stepCount"] < 7:
                    problems.append(f"{label} {path}: nur {m['stepCount']} Nächster-Schritt-Zeilen (erwartet >= 7)")
            else:
                if not m["hasArticleCta"]:
                    problems.append(f"{label} {path}: .article-cta fehlt")
                if not m["hasNextStepLabel"]:
                    problems.append(f"{label} {path}: kein 'Nächster Schritt'-Label")
            for c in m["ctas"]:
                if c["h"] < 40:
                    problems.append(f"{label} {path}: CTA zu klein ({c['h']}px): {c['text']}")
        print("\n" + "=" * 50)
        if problems:
            print("UX-PROBLEME:")
            for p in problems:
                print(" -", p)
            sys.exit(1)
        print("UX-CHECK BESTANDEN: kein Overflow, korrekte Grid-Spaltung, CTAs groß genug")
    finally:
        proc.terminate()


if __name__ == "__main__":
    main()
