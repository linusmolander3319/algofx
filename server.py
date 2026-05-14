#!/usr/bin/env python3
"""
AlgoFX — IG API Proxy + Static Server
Kör lokalt: python server.py
Railway:    Driftsätts automatiskt
"""

import json
import os
import ssl
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT    = int(os.environ.get("PORT", 3001))
IG_BASE = "https://demo-api.ig.com/gateway/deal"

session = {"CST": None, "X-SECURITY-TOKEN": None}

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode    = ssl.CERT_NONE


def forward_to_ig(method, path, raw_headers, body=None):
    url     = IG_BASE + path
    headers = {}
    for key in ["content-type","x-ig-api-key","version","cst","x-security-token"]:
        val = raw_headers.get(key)
        if val:
            canonical = {"content-type":"Content-Type","x-ig-api-key":"X-IG-API-KEY",
                         "version":"Version","cst":"CST","x-security-token":"X-SECURITY-TOKEN"}[key]
            headers[canonical] = val
    if "CST" not in headers and session["CST"]:
        headers["CST"] = session["CST"]
    if "X-SECURITY-TOKEN" not in headers and session["X-SECURITY-TOKEN"]:
        headers["X-SECURITY-TOKEN"] = session["X-SECURITY-TOKEN"]
    headers.setdefault("Content-Type","application/json")
    headers["Accept"] = "application/json; charset=UTF-8"
    data = body if isinstance(body,bytes) else (body.encode() if body else None)
    req  = urllib.request.Request(url,data=data,headers=headers,method=method)
    try:
        with urllib.request.urlopen(req,timeout=30,context=ssl_ctx) as resp:
            cst=resp.headers.get("CST"); token=resp.headers.get("X-SECURITY-TOKEN")
            if cst:   session["CST"]=cst
            if token: session["X-SECURITY-TOKEN"]=token
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:
        return 502, {}, json.dumps({"error":str(e)}).encode()


class Handler(BaseHTTPRequestHandler):

    def log_message(self,fmt,*args):
        print(f"[{args[1]}] {self.command} {self.path}")

    def cors(self):
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","GET,POST,PUT,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers",
            "Content-Type,X-IG-API-KEY,Version,CST,X-SECURITY-TOKEN,x-ig-api-key,version")
        self.send_header("Access-Control-Expose-Headers","CST,X-SECURITY-TOKEN")

    def do_OPTIONS(self):
        self.send_response(204); self.cors(); self.end_headers()

    def do_GET(self):
        if self.path in ("/","/index.html"):
            try:
                with open("index.html","rb") as f: content=f.read()
                self.send_response(200)
                self.send_header("Content-Type","text/html; charset=utf-8")
                self.send_header("Content-Length",len(content))
                self.end_headers(); self.wfile.write(content)
            except FileNotFoundError:
                self.send_error(404)
            return
        self._handle("GET")

    def do_POST(self):   self._handle("POST")
    def do_DELETE(self): self._handle("DELETE")
    def do_PUT(self):    self._handle("PUT")

    def _handle(self,method):
        if self.path=="/health":
            body=json.dumps({"status":"ok","session":bool(session["CST"])}).encode()
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.cors(); self.end_headers(); self.wfile.write(body)
            return
        n=int(self.headers.get("Content-Length",0))
        body=self.rfile.read(n) if n else None
        status,resp_hdrs,data=forward_to_ig(method,self.path,self.headers,body)
        self.send_response(status)
        self.send_header("Content-Type","application/json")
        self.cors()
        for h in ("CST","X-SECURITY-TOKEN"):
            v=resp_hdrs.get(h) or session.get(h)
            if v: self.send_header(h,v)
        self.end_headers(); self.wfile.write(data)


if __name__=="__main__":
    print(f"\n╔══════════════════════════════╗\n║  AlgoFX Railway  port:{PORT:<5} ║\n╚══════════════════════════════╝\n")
    server=HTTPServer(("0.0.0.0",PORT),Handler)
    try: server.serve_forever()
    except KeyboardInterrupt: server.server_close()
