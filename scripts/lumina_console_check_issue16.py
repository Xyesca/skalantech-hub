"""Kurzer Console-/JS-Error-Check für /wissen + Artikel (Issue #16)."""
import json
import os
import socket
import struct
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lumina_ux_check_issue16 import WS, cdp_call, start_chrome  # noqa: E402

BASE = "http://127.0.0.1:9222"


class CollectWS(WS):
    def __init__(self, url):
        self.events = []
        super().__init__(url)

    def send(self, payload):
        self._send_frame(0x1, json.dumps(payload).encode())
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
            if b2 & 0x80:
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
                self.events.append(msg)
            elif opcode == 0x8:
                raise RuntimeError("WS closed by peer")


def main():
    proc = start_chrome()
    try:
        tabs = json.loads(urllib.request.urlopen(f"{BASE}/json/list").read())
        page = next(t for t in tabs if t["type"] == "page")
        ws = CollectWS(page["webSocketDebuggerUrl"])
        cdp_call(ws, "Page.enable", msg_id=1)
        cdp_call(ws, "Runtime.enable", msg_id=2)
        cdp_call(ws, "Log.enable", msg_id=3)
        problems = []
        for i, path in enumerate(["/wissen", "/wissen/kosten-roi-ki-automatisierung",
                                  "/wissen/was-ist-ein-ki-agent", "/wissen/n8n-selbst-hosten",
                                  "/wissen/lokale-ki-vs-cloud-ki", "/wissen/n8n-vs-power-automate",
                                  "/wissen/welche-prozesse-ki-automatisierung",
                                  "/wissen/rag-wissensassistenten"]):
            ws.events.clear()
            cdp_call(ws, "Page.navigate", {"url": "http://127.0.0.1:5098" + path}, msg_id=100 + i * 10)
            time.sleep(1.0)
            errs = []
            for ev in ws.events:
                method = ev.get("method", "")
                if method == "Runtime.exceptionThrown":
                    d = ev["params"]["exceptionDetails"]
                    errs.append("exception: " + d.get("text", "") + " " + d.get("exception", {}).get("description", "")[:200])
                elif method == "Log.entryAdded":
                    e = ev["params"]["entry"]
                    if e.get("level") in ("error", "warning"):
                        errs.append(f"{e.get('level')}: {e.get('text', '')[:200]}")
                elif method == "Runtime.consoleAPICalled" and ev["params"]["type"] == "error":
                    errs.append("console.error")
            if errs:
                problems.append(f"{path}: {errs[:3]}")
                print(f"!! {path}: {errs[:3]}")
            else:
                print(f"OK {path}: keine JS-/Console-Fehler")
        if problems:
            print("\nCONSOLE-PROBLEME:")
            for p in problems:
                print(" -", p)
            sys.exit(1)
        print("\nCONSOLE-CHECK BESTANDEN: keine JS-Fehler auf /wissen + allen Artikeln")
    finally:
        proc.terminate()


if __name__ == "__main__":
    main()
