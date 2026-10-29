"""
SPECTRE-SHIELD: Mission-Control Server (Zero External Dependencies Required)
============================================================================
Runs immediately with standard Python 3.12 (`python3 server.py`) on port 8765.
Exposes:
  - GET  /                     -> Interactive Cybersecurity Mission-Control UI (`index.html`)
  - GET  /api/telemetry/tick   -> Advances real CPU cache timing probe & returns waveform/FFT/bitstream
  - POST /api/arena/configure  -> Toggles Nemotron Hardware Jammer Shield, secret payload, or scenario
  - POST /api/nemotron/audit   -> Runs NVIDIA Nemotron-3 Super (Nebius Token Factory) + AST + Tavily audit
  - POST /api/config/keys      -> Hot-swaps Nebius Token Factory & Tavily API keys at runtime
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from covert_channel_engine import (
    COVERT_AGENT_TEMPLATES,
    CovertChannelArena,
    analyze_agent_code_ast,
)
from nemotron_tavily_client import NebiusNemotronWarden


BASE_DIR = Path(__file__).resolve().parent
ARENA = CovertChannelArena()
WARDEN = NebiusNemotronWarden()


class SpectreShieldHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args):
        # Keep console logs clean during high-frequency oscilloscope polling
        if "/api/telemetry/tick" not in (args[0] if args else ""):
            sys.stderr.write(f"[SPECTRE-SHIELD] {self.address_string()} - {format % args}\n")

    def _send_json(self, payload: dict, status: int = 200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html", "/blog", "/blog.html"):
            index_path = BASE_DIR / "index.html"
            content = index_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if path in ("/demo", "/demo.html"):
            demo_path = BASE_DIR / "demo.html"
            content = demo_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if path == "/api/telemetry/tick":
            snapshot = ARENA.step_telemetry()
            self._send_json(snapshot)
            return

        if path == "/api/status":
            self._send_json({
                "status": "ok",
                "cloud": WARDEN.get_status(),
                "calibration": ARENA.calibration,
            })
            return

        self._send_json({"error": "Not found"}, status=404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        if path == "/api/arena/configure":
            snapshot = ARENA.configure(
                secret_message=body.get("secret_message"),
                channel_mode=body.get("channel_mode"),
                transmitting=body.get("transmitting"),
                shield_active=body.get("shield_active"),
            )
            self._send_json(snapshot)
            return

        if path == "/api/nemotron/audit":
            snapshot = ARENA.get_state_snapshot_locked()
            mode = str(snapshot["channel_mode"])
            tpl = COVERT_AGENT_TEMPLATES.get(mode, COVERT_AGENT_TEMPLATES["cpu_l3_cache"])
            combined_code = tpl["sender_code"] + "\n" + tpl["receiver_code"]
            ast_report = analyze_agent_code_ast(combined_code)
            audit = WARDEN.run_nemotron_blue_team_audit(
                channel_mode=mode,
                telemetry_metrics=snapshot["metrics"],
                ast_report=ast_report,
                shield_active=bool(snapshot["shield_active"]),
            )
            self._send_json({
                "ast_report": ast_report,
                "audit": audit,
                "cloud_status": WARDEN.get_status(),
            })
            return

        if path == "/api/config/keys":
            WARDEN.update_keys(
                nebius_key=body.get("nebius_api_key"),
                tavily_key=body.get("tavily_api_key"),
                model=body.get("nemotron_model"),
            )
            self._send_json(WARDEN.get_status())
            return

        self._send_json({"error": "Not found"}, status=404)


def run_server(port: int = 8765):
    server = ThreadingHTTPServer(("127.0.0.1", port), SpectreShieldHandler)
    print("=" * 76)
    print("  SPECTRE-SHIELD: AI Agent Hardware Covert-Channel Defense Arena")
    print("  Powered by NVIDIA Nemotron-3 Super (Nebius Token Factory) + Tavily Intel")
    print("=" * 76)
    print(f"  [+] Host CPU Cache Calibrated : L1 Hit = {ARENA.calibration['host_l1_hit_ns']} ns | "
          f"L3/DRAM Miss = {ARENA.calibration['host_l3_miss_ns']} ns")
    print(f"  [+] Mission Control Dashboard : http://127.0.0.1:{port}")
    print("=" * 76)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down SPECTRE-SHIELD...")
        server.server_close()


if __name__ == "__main__":
    port_num = int(os.environ.get("PORT", "8765"))
    run_server(port_num)
