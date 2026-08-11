#!/usr/bin/env python3
"""build_stop.py -- render weir/stop.html, the stop card.

    python3 weir/build_stop.py

The page runs the SAME claim checker the gate and the desks run, so the card a
person sees here is produced by the engine that is actually under test, not by
a mock-up of it.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

engine = open(os.path.join(ROOT, "cairn/ei_engine.js"), encoding="utf-8").read()
tpl = open(os.path.join(HERE, "stop_template.html"), encoding="utf-8").read()
out = tpl.replace("{{ENGINE}}", engine)
assert "{{" not in out, "unfilled placeholder left in stop.html"
open(os.path.join(HERE, "stop.html"), "w", encoding="utf-8").write(out)
print("wrote stop.html  (%.1f KB) — self-contained, offline" % (len(out) / 1024))
