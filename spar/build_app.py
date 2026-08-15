#!/usr/bin/env python3
"""build_app.py -- render spar/app.html, offline and phone-first.

    python3 spar/build_app.py

Inlines smi/lmd.js, which is the same metric engine SPAR's Python uses and is
parity-checked against the JAX engine over fourteen graphs by
smi/test_parity.py. The page in your hand and the arithmetic under test are the
same arithmetic.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

tpl = open(os.path.join(HERE, "app_template.html"), encoding="utf-8").read()
engine = open(os.path.join(ROOT, "smi", "lmd.js"), encoding="utf-8").read()
out = tpl.replace("{{LMD}}", engine)
assert "{{" not in out, "unfilled placeholder left in app.html"
open(os.path.join(HERE, "app.html"), "w", encoding="utf-8").write(out)
print("wrote spar/app.html  (%.1f KB) — offline, no server, no account" % (len(out) / 1024))
