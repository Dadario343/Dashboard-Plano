"""
ReCarga — Dashboard de simulação de recarga de carros elétricos
"""

import json
import random
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuração / simulação
# ---------------------------------------------------------------------------
VOLTAGE = 230
MAX_CAPACITY_A = 40
PRICE_PRE = 1.35
PRICE_POS = 0.98
TICK_SECONDS = 1.5
TICK_HOURS = TICK_SECONDS / 3600
CAR_NAMES = ["Onix EV", "HB20 e", "Kwid Volt", "Compass e", "Fastback e", "Corolla e+"]
PORT = 5000

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

lock = threading.Lock()


def make_station(i, plan, active):
    return dict(
        id=i, name=CAR_NAMES[(i - 1) % len(CAR_NAMES)], plan=plan, active=active,
        target_a=16 if plan == "pre" else 10, current_a=0.0,
        status="carregando" if active else "livre", energy_kwh=0.0, cost=0.0,
    )


state = {
    "stations": [
        make_station(1, "pre", True), make_station(2, "pos", True),
        make_station(3, "pos", True), make_station(4, "pre", True),
        make_station(5, "pos", False), make_station(6, "pre", False),
    ],
    "history": [dict(t=0, pre=0.0, pos=0.0, load=0.0)],
    "overload_events": 0,
    "overload_flag": False,
}


def step():
    stations = state["stations"]
    active = [s for s in stations if s["active"]]
    pre = [s for s in active if s["plan"] == "pre"]
    pos = [s for s in active if s["plan"] == "pos"]

    pre_target_total = sum(s["target_a"] for s in pre)
    pre_scale = MAX_CAPACITY_A / pre_target_total if pre_target_total > MAX_CAPACITY_A else 1
    reserved = min(pre_target_total, MAX_CAPACITY_A)
    remaining = max(MAX_CAPACITY_A - reserved, 0)

    pos_target_total = sum(s["target_a"] for s in pos)
    pos_scale = min(remaining / pos_target_total, 1) if pos_target_total > 0 else 1

    is_overloaded = pos_target_total > remaining + 0.01
    if is_overloaded and not state["overload_flag"]:
        state["overload_events"] += 1
    state["overload_flag"] = is_overloaded

    for s in stations:
        if not s["active"]:
            s["current_a"] = 0.0
            s["status"] = "livre"
            continue
        jitter = random.uniform(0.9, 1.1)
        if s["plan"] == "pre":
            cur = s["target_a"] * pre_scale * jitter
            power = cur * VOLTAGE / 1000
            dE = power * TICK_HOURS
            s["current_a"] = cur
            s["status"] = "reservado" if pre_scale < 0.999 else "carregando"
            s["energy_kwh"] += dE
            s["cost"] += dE * PRICE_PRE
        else:
            cur = s["target_a"] * pos_scale * jitter
            power = cur * VOLTAGE / 1000
            dE = power * TICK_HOURS
            status = "carregando"
            if pos_scale <= 0.01:
                status = "em fila"
            elif pos_scale < 0.85:
                status = "limitado"
            s["current_a"] = cur
            s["status"] = status
            s["energy_kwh"] += dE
            s["cost"] += dE * PRICE_POS

    pre_revenue = sum(s["cost"] for s in stations if s["plan"] == "pre")
    pos_revenue = sum(s["cost"] for s in stations if s["plan"] == "pos")
    load = sum(s["current_a"] for s in stations)
    hist = state["history"]
    hist.append(dict(t=len(hist), pre=round(pre_revenue, 2), pos=round(pos_revenue, 2), load=round(load, 1)))
    state["history"] = hist[-40:]


def loop():
    while True:
        time.sleep(TICK_SECONDS)
        with lock:
            step()


# ---------------------------------------------------------------------------
# Servidor HTTP (só biblioteca padrão — sem Flask). Lê os arquivos de
# templates/ e static/ do disco a cada requisição.
# ---------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silencia o log de cada requisição no terminal

    def _send(self, code, body, content_type="text/html; charset=utf-8"):
        body_bytes = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)

    def _send_file(self, path: Path, content_type):
        if not path.is_file():
            self._send(404, f"arquivo não encontrado: {path.name}")
            return
        self._send(200, path.read_text(encoding="utf-8"), content_type)

    def do_GET(self):
        if self.path == "/":
            self._send_file(TEMPLATES_DIR / "index.html", "text/html; charset=utf-8")
        elif self.path == "/style.css":
            self._send_file(STATIC_DIR / "style.css", "text/css; charset=utf-8")
        elif self.path == "/app.js":
            self._send_file(STATIC_DIR / "app.js", "application/javascript; charset=utf-8")
        elif self.path == "/api/state":
            with lock:
                stations = state["stations"]
                payload = {
                    "stations": stations,
                    "history": state["history"],
                    "overload_events": state["overload_events"],
                    "total_load": sum(s["current_a"] for s in stations),
                    "total_revenue": sum(s["cost"] for s in stations),
                    "total_energy": sum(s["energy_kwh"] for s in stations),
                    "max_capacity": MAX_CAPACITY_A,
                    "voltage": VOLTAGE,
                    "price_pre": PRICE_PRE,
                    "price_pos": PRICE_POS,
                }
            self._send(200, json.dumps(payload), "application/json")
        else:
            self._send(404, "not found")

    def do_POST(self):
        parts = self.path.strip("/").split("/")
        if len(parts) == 3 and parts[0] == "api" and parts[1] in ("toggle_plug", "toggle_plan"):
            try:
                sid = int(parts[2])
            except ValueError:
                self._send(400, "{}", "application/json")
                return
            with lock:
                for s in state["stations"]:
                    if s["id"] == sid:
                        if parts[1] == "toggle_plug":
                            s["active"] = not s["active"]
                            s["current_a"] = 0.0
                            s["status"] = "carregando" if s["active"] else "livre"
                        else:
                            s["plan"] = "pos" if s["plan"] == "pre" else "pre"
                            s["target_a"] = 10 if s["plan"] == "pos" else 16
            self._send(200, '{"ok": true}', "application/json")
        else:
            self._send(404, "not found")


def open_browser_later():
    time.sleep(0.8)
    try:
        webbrowser.open(f"http://localhost:{PORT}")
    except Exception:
        pass


if __name__ == "__main__":
    threading.Thread(target=loop, daemon=True).start()
    threading.Thread(target=open_browser_later, daemon=True).start()
    print(f"ReCarga rodando em http://localhost:{PORT}  (Ctrl+C para parar)")
    server = ThreadingHTTPServer(("localhost", PORT), Handler)
    server.serve_forever()
