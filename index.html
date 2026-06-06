#!/usr/bin/env python3
"""AlgoFX — IG API Proxy + Static Server v4 med env-stöd"""

import json, os, ssl, time, urllib.request, urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT    = int(os.environ.get("PORT", 3001))
IG_BASE = "https://demo-api.ig.com/gateway/deal"

# Läs IG-uppgifter från miljövariabler (Railway)
ENV_CREDS = {
    "apiKey":   os.environ.get("IG_API_KEY", ""),
    "username": os.environ.get("IG_USERNAME", ""),
    "password": os.environ.get("IG_PASSWORD", ""),
}

session = {"CST": None, "X-SECURITY-TOKEN": None}

def make_ssl():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode    = ssl.CERT_NONE
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')
    return ctx

def forward(method, path, raw_headers, body=None, retries=3):
    url     = IG_BASE + path
    headers = {}
    for key in ["content-type","x-ig-api-key","version","cst","x-security-token"]:
        val = raw_headers.get(key)
        if val:
            canonical = {
                "content-type":"Content-Type","x-ig-api-key":"X-IG-API-KEY",
                "version":"Version","cst":"CST","x-security-token":"X-SECURITY-TOKEN"
            }[key]
            headers[canonical] = val
    if "CST" not in headers and session["CST"]:
        headers["CST"] = session["CST"]
    if "X-SECURITY-TOKEN" not in headers and session["X-SECURITY-TOKEN"]:
        headers["X-SECURITY-TOKEN"] = session["X-SECURITY-TOKEN"]
    headers.setdefault("Content-Type", "application/json")
    headers["Accept"]     = "application/json; charset=UTF-8"
    headers["Connection"] = "close"
    override = raw_headers.get("_method")
    if override:
        headers["_method"] = override
    data = body if isinstance(body, bytes) else (body.encode() if body else None)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=30, context=make_ssl()) as resp:
                cst   = resp.headers.get("CST")
                token = resp.headers.get("X-SECURITY-TOKEN")
                if cst:   session["CST"]               = cst
                if token: session["X-SECURITY-TOKEN"]  = token
                rd = resp.read()
                print(f"  ← {resp.status} {method} {path[:60]}")
                return resp.status, dict(resp.headers), rd
        except urllib.error.HTTPError as e:
            rd = e.read()
            print(f"  ← {e.code} {method} {path[:60]}")
            return e.code, dict(e.headers), rd
        except (ssl.SSLError, OSError) as e:
            print(f"  SSL/OS fel (försök {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
                continue
            return 502, {}, json.dumps({"error": str(e)}).encode()
        except Exception as e:
            print(f"  FEL: {e}")
            return 502, {}, json.dumps({"error": str(e)}).encode()
    return 502, {}, json.dumps({"error":"Max retries"}).encode()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def cors(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers",
            "Content-Type,X-IG-API-KEY,Version,CST,X-SECURITY-TOKEN,x-ig-api-key,version,_method")
        self.send_header("Access-Control-Expose-Headers", "CST,X-SECURITY-TOKEN")

    def do_OPTIONS(self):
        self.send_response(204); self.cors(); self.end_headers()

    def do_GET(self):
        # Serve index.html
        if self.path in ("/", "/index.html"):
            try:
                with open("index.html", "rb") as f: c = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", len(c))
                self.end_headers(); self.wfile.write(c); return
            except FileNotFoundError:
                self.send_error(404); return

        # Return env credentials to the app (never logs them)
        if self.path == "/env-creds":
            body = json.dumps(ENV_CREDS).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.cors(); self.end_headers(); self.wfile.write(body); return

        self._handle("GET")

    def do_POST(self):   self._handle("POST")
    def do_DELETE(self): self._handle("DELETE")
    def do_PUT(self):    self._handle("PUT")

    def _handle(self, method):
        if self.path == "/health":
            has_creds = bool(ENV_CREDS["apiKey"])
            body = json.dumps({
                "status":   "ok",
                "session":  bool(session["CST"]),
                "proxy":    "v4",
                "env_creds": has_creds,
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.cors(); self.end_headers(); self.wfile.write(body); return

        n    = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n) if n else None
        print(f"  → {method} {self.path[:70]}")
        status, resp_hdrs, data = forward(method, self.path, self.headers, body)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.cors()
        for h in ("CST", "X-SECURITY-TOKEN"):
            v = resp_hdrs.get(h) or session.get(h)
            if v: self.send_header(h, v)
        self.end_headers(); self.wfile.write(data)


if __name__ == "__main__":
    has_env = bool(ENV_CREDS["apiKey"])
    print(f"""
╔══════════════════════════════════════════════════════╗
║        AlgoFX — IG API Proxy  v4                     ║
║  Port      : {PORT:<5}                               ║
║  Env-creds : {'✅ Hittade IG_API_KEY' if has_env else '❌ Inga env-variabler satta'}
╚══════════════════════════════════════════════════════╝
""")
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    try: server.serve_forever()
    except KeyboardInterrupt: server.server_close()
