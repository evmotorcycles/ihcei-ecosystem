#!/usr/bin/env python3
"""build_suite.py -- render novora-suite/suite.html, the offline nine-product GUI.

    python3 novora-suite/build_bundle.py && python3 novora-suite/build_suite.py

Inlines the generated engine bundle so the page is a single self-contained file
that runs from file:// with no server, no account, no network and no API key.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
engine = open(os.path.join(HERE, "engine.bundle.js"), encoding="utf-8").read()
tpl = open(os.path.join(HERE, "suite_template.html"), encoding="utf-8").read()

out = tpl.replace("{{ENGINE}}", engine)
assert "{{" not in out, "unfilled placeholder left in suite.html"
path = os.path.join(HERE, "suite.html")
open(path, "w", encoding="utf-8").write(out)
print("wrote suite.html  (%.1f KB) — self-contained, nine products, no network"
      % (len(out) / 1024))
