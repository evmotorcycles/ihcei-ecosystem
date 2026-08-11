#!/usr/bin/env python3
"""build_desk.py -- render novora-suite/desk.html, the everyday-object GUI.

    python3 novora-suite/build_bundle.py && python3 novora-suite/build_desk.py

Same tested engine as suite.html; the surface is named for the worry a person
actually has ("Is this for real?") rather than the product code. The three-letter
product codes appear nowhere a user can see them.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
engine = open(os.path.join(HERE, "engine.bundle.js"), encoding="utf-8").read()
readers = open(os.path.join(ROOT, "readers/readers.js"), encoding="utf-8").read()
tpl = open(os.path.join(HERE, "desk_template.html"), encoding="utf-8").read()
out = tpl.replace("{{ENGINE}}", engine).replace("{{READERS}}", readers)
assert "{{" not in out, "unfilled placeholder left in desk.html"
open(os.path.join(HERE, "desk.html"), "w", encoding="utf-8").write(out)
print("wrote desk.html  (%.1f KB) — nine everyday checks, self-contained" % (len(out) / 1024))
