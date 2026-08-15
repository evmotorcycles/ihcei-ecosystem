#!/usr/bin/env python3
"""build_panel.py -- render weir/panel.html, the gate's control panel.

    python3 weir/build_panel.py

The page runs the SAME decision function the gate runs, so what a person tries
here is what would actually happen at the gate. It is a control panel, not a
simulation of one.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
engine = open(os.path.join(ROOT, "cairn/ei_engine.js")).read()
key = json.load(open(os.path.join(HERE, "key.example.json")))
tpl = open(os.path.join(HERE, "panel_template.html")).read()
out = tpl.replace("{{ENGINE}}", engine).replace("{{KEY}}", json.dumps(key, separators=(",", ":")))
assert "{{" not in out, "unfilled placeholder left in panel.html"
open(os.path.join(HERE, "panel.html"), "w").write(out)
print("wrote panel.html  (%.1f KB) — self-contained control panel" % (len(out) / 1024))
