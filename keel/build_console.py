#!/usr/bin/env python3
"""build_console.py -- render keel/console.html, the one page that has everything.

    python3 keel/build_console.py

The console runs the SAME three engines the tests exercise, inlined so the page
works from a file:// URL with no server, no account and no network:

    cairn/ei_engine.js            the label and the handles
    novora-suite/engine.bundle.js the nine everyday screens
    keel/kernel.mjs               the six-stage admission path

The kernel is ESM and the page is not a module, so its exported functions are
flattened the same way keel/build_exe.py flattens them, and a parity test drives
the built page and compares its answers against the kernel module.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def read(rel, base=ROOT):
    return open(os.path.join(base, rel), encoding="utf-8").read()


def flatten(src):
    """Same rules as build_exe.py: only the forms this project uses, and any
    other import/export raises instead of being silently dropped."""
    src = re.sub(r"^import\s+[^;]+?;\s*$", "", src, flags=re.M)
    src = re.sub(r"^export\s+(const|function|class|let|var)\s", r"\1 ", src, flags=re.M)
    src = re.sub(r"^export\s*\{[^}]*\};?\s*$", "", src, flags=re.M)
    left = [ln for ln in src.splitlines() if re.match(r"^\s*(import|export)\s", ln)]
    if left:
        raise SystemExit("build_console.py cannot handle:\n  " + "\n  ".join(left))
    return src


def main():
    kernel = flatten(read("keel/kernel.mjs"))
    for dead in ('const here = dirname(fileURLToPath(import.meta.url));',
                 'const ROOT = dirname(here);',
                 'const require = createRequire(import.meta.url);',
                 'const EI = require(join(ROOT, "cairn/ei_engine.js"));'):
        kernel = kernel.replace(dead, "")
    # node:crypto is not in a browser; the page uses the same SHA-256 through
    # the platform's own implementation, which is async, so the ledger seals
    # with a synchronous fallback that is LABELLED as such on screen.
    kernel = kernel.replace(
        'const e = { ...body, at: new Date().toISOString(), prev: this.head };\n'
        '    e.seal = createHash("sha256").update(JSON.stringify(e)).digest("hex");',
        'const e = { ...body, at: new Date().toISOString(), prev: this.head };\n'
        '    e.seal = SEAL(JSON.stringify(e));')
    kernel = kernel.replace(
        'if (createHash("sha256").update(JSON.stringify(body)).digest("hex") !== seal) {',
        'if (SEAL(JSON.stringify(body)) !== seal) {')

    html = read("keel/console_template.html").replace(
        "{{EI}}", read("cairn/ei_engine.js")).replace(
        "{{NOVORA}}", read("novora-suite/engine.bundle.js")).replace(
        "{{KERNEL}}", kernel).replace(
        "{{POLICY}}", json.dumps(json.loads(read("keel/policy.example.json")),
                                 separators=(",", ":")))
    assert "{{" not in html, "unfilled placeholder left in console.html"
    out = os.path.join(HERE, "console.html")
    open(out, "w", encoding="utf-8").write(html)
    print("wrote keel/console.html  (%.1f KB) — one page, three engines, no network"
          % (len(html) / 1024))


if __name__ == "__main__":
    main()
