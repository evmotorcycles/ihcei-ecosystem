#!/usr/bin/env python3
"""build_app.py -- render smi/app.html, the interactive mesh you can hold.

    python3 smi/build_app.py

Inlines smi/lmd.js so the page works from a file:// URL, offline, on a phone.
The port it inlines is parity-checked against the JAX engine by
smi/test_parity.py over fourteen graphs, so the thing in your hand and the
thing under test are the same arithmetic.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
tpl = open(os.path.join(HERE, "app_template.html"), encoding="utf-8").read()
out = tpl.replace("{{LMD}}", open(os.path.join(HERE, "lmd.js"), encoding="utf-8").read())
assert "{{" not in out, "unfilled placeholder left in app.html"
open(os.path.join(HERE, "app.html"), "w", encoding="utf-8").write(out)
print("wrote smi/app.html  (%.1f KB) — interactive, offline, phone-first" % (len(out) / 1024))
