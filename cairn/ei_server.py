#!/usr/bin/env python3
"""
ei_server.py -- serves the Python EI engine to the Cairn browser GUI.
================================================================================
    python3 cairn/ei_server.py            # then open cairn/cairn.html

Pure stdlib HTTP server. Binds to 127.0.0.1 only -- it is a local engine, not a
web service, and nothing it sees leaves the machine.

  GET  /health          -> {"ok": true, "engine": "..."}
  POST /assay           -> body {"text": "...", "model": "slate", "parent": "..."}
                           returns the full EI verdict from ei_llm.assay()

CORS is set to '*' so the page works when opened directly from file:// (origin
"null"). The server refuses any request that is not one of the two routes above.
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ei_llm import assay                                     # noqa: E402

HOST, PORT = "127.0.0.1", 8765
MAX_BODY = 64 * 1024


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def do_GET(self):
        if self.path.rstrip("/") == "/health":
            return self._json({"ok": True, "engine": "cairn-ei/1.0 (python)", "host": HOST, "port": PORT})
        self._json({"error": "not found"}, 404)

    def do_POST(self):
        if self.path.rstrip("/") != "/assay":
            return self._json({"error": "not found"}, 404)
        try:
            n = int(self.headers.get("Content-Length") or 0)
            if n <= 0 or n > MAX_BODY:
                return self._json({"error": "bad body size"}, 400)
            req = json.loads(self.rfile.read(n).decode("utf-8"))
            return self._json(assay(req.get("text", ""), req.get("model", "slate"), req.get("parent")))
        except Exception as e:
            return self._json({"error": type(e).__name__, "detail": str(e)[:200]}, 400)

    def log_message(self, *a):
        pass                                                  # quiet


def main():
    srv = HTTPServer((HOST, PORT), Handler)
    print(f"Cairn EI engine listening on http://{HOST}:{PORT}")
    print("Now open cairn/cairn.html — the GUI will detect this engine automatically.")
    print("Ctrl-C to stop.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
