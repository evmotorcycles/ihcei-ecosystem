#!/usr/bin/env python3
"""Serves plexus/ with the headers vercel.json declares, so the CSP is tested
before it is deployed rather than after. REGENERATE whenever vercel.json
changes -- a stale copy of this file cost a whole diagnosis once already."""
import http.server, os, re, sys
RULES = [('/sw.js', {'Cache-Control': 'public, max-age=0, must-revalidate', 'Service-Worker-Allowed': '/'}), ('/manifest.webmanifest', {'Content-Type': 'application/manifest+json', 'Cache-Control': 'public, max-age=0, must-revalidate'}), ('/(index.html)?', {'Cache-Control': 'public, max-age=0, must-revalidate'}), ('/icon-(.*).png', {'Cache-Control': 'public, max-age=31536000, immutable'}), ('/(.*)', {'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer', 'Permissions-Policy': 'geolocation=(), camera=(), microphone=(), interest-cohort=()', 'Content-Security-Policy': "default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; manifest-src 'self'; worker-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"})]

def to_pattern(src):
    return "^" + (src.replace("/(.*)", "/.*")
                     .replace("(index.html)?", "(index[.]html)?")
                     .replace("/icon-(.*).png", "/icon-.*[.]png")) + "$"

class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        path = self.path.split("?")[0]
        for src, hdrs in RULES:
            if re.match(to_pattern(src), path):
                for k, val in hdrs.items():
                    self.send_header(k, val)
        super().end_headers()
    def log_message(self, *a):
        pass

os.chdir(sys.argv[1])
http.server.HTTPServer(("127.0.0.1", int(sys.argv[2])), H).serve_forever()
