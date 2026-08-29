#!/usr/bin/env python3
"""blueprint.py — a project's DECLARED structure, and the joint into the survey.

WHAT THIS IS FOR
================
A coding agent writes files at machine speed. What nobody has afterwards is the
shape of what was written: which module everything routes through, which
"independent" pieces are all standing on one thing, and what breaks if one file
goes. This reads the declared import graph and hands it to `keel.survey`.

WHAT IT DOES NOT DO, AND THIS IS THE WHOLE BOUNDARY
===================================================
    understands_language = False
    proves               = NOTHING

It reads `import` and `require` statements. It does not read code, does not know
what a function does, and cannot tell a good architecture from a bad one. A
module that everything imports may be exactly right -- a shared kernel usually
is. Naming it starts a conversation; it does not end one.

An edge exists here only because somebody WROTE an import. A dependency reached
through a string, a plugin registry, a subprocess, an HTTP call or reflection is
invisible to this file and will not appear in any reading. That is the same
NULL-K1 the survey carries: absence of an edge is absence of a DECLARATION.

WHY IT IS A SEPARATE FILE FROM THE GATE
=======================================
`pagecode.mjs` audits what an agent SAYS and what a diff DOES -- a corroboration
gate on coercion. This audits what a project IS. They are different quantities
and they are never combined; there is no field anywhere that adds a structural
reading to a rhetorical one.
"""
from __future__ import annotations

import ast
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

UNDERSTANDS_LANGUAGE = False
PROVES = "NOTHING"

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv",
             "dist", "build", ".next", "site-packages"}

CANNOT = [
    "It reads import statements. It does not read code and does not know what "
    "any of it does.",
    "A module that everything imports may be exactly right. This says it is "
    "there, never that it is wrong.",
    "A dependency reached through a string, a plugin registry, a subprocess or "
    "reflection is invisible here and will not appear in any reading.",
    "It cannot tell you whether a project works.",
]


# ── Python ──────────────────────────────────────────────────────────────────
def _py_imports(path: str) -> list:
    """Declared imports, by AST rather than regex, so a commented-out or
    string-literal import is not counted as an edge."""
    try:
        tree = ast.parse(open(path, encoding="utf-8", errors="replace").read())
    except (SyntaxError, ValueError):
        return []
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                out.append(node.module)
            elif node.level:
                out.append("." * node.level + (node.module or ""))
    return out


# ── JavaScript / TypeScript ─────────────────────────────────────────────────
_JS_REQ = re.compile(r"""require\(\s*['"]([^'"]+)['"]\s*\)""")
_JS_IMP = re.compile(r"""(?:^|\n)\s*import[^;\n]*?from\s*['"]([^'"]+)['"]""")


def _js_imports(path: str) -> list:
    src = open(path, encoding="utf-8", errors="replace").read()
    # Strip block and line comments so a documented import is not an edge. The
    # limit, stated: a `//` inside a regex literal would be stripped too.
    src = re.sub(r"/\*[\s\S]*?\*/", "", src)
    src = re.sub(r"(?m)^\s*//.*$", "", src)
    return _JS_REQ.findall(src) + _JS_IMP.findall(src)


def modules(root: str) -> dict:
    """Every source file, keyed by the repo-relative path with no extension."""
    found = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            ext = os.path.splitext(fn)[1]
            if ext not in (".py", ".mjs", ".js"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root)
            found[rel] = {"path": full, "lang": "py" if ext == ".py" else "js"}
    return found


def _resolve_py(name: str, importer_rel: str, index: dict):
    """An import name becomes an edge only if it lands on a file in THIS repo."""
    if name.startswith("."):
        base = os.path.dirname(importer_rel)
        tail = name.lstrip(".").replace(".", "/")
        up = len(name) - len(name.lstrip(".")) - 1
        for _ in range(up):
            base = os.path.dirname(base)
        cand = os.path.join(base, tail) if tail else base
    else:
        cand = name.replace(".", "/")
    for suffix in (".py", "/__init__.py"):
        if cand + suffix in index:
            return cand + suffix
    return None


def _resolve_js(spec: str, importer_rel: str, index: dict):
    if not spec.startswith("."):
        return None                      # a package, not a part of this project
    cand = os.path.normpath(os.path.join(os.path.dirname(importer_rel), spec))
    for suffix in ("", ".mjs", ".js", "/index.mjs", "/index.js"):
        if cand + suffix in index:
            return cand + suffix
    return None


def blueprint(root: str, name: str = None) -> dict:
    """Returns a project dict the survey accepts, plus the counts behind it.

    Only files that actually take part in an intra-project edge become parts.
    A repository of 400 unconnected scripts is 400 pieces, and saying so is the
    reading -- but carrying 400 isolated nodes into the survey would drown the
    one finding that matters.
    """
    index = modules(root)
    edges, external, unresolved = [], 0, 0
    for rel, meta in sorted(index.items()):
        names = (_py_imports(meta["path"]) if meta["lang"] == "py"
                 else _js_imports(meta["path"]))
        for n in names:
            hit = (_resolve_py(n, rel, index) if meta["lang"] == "py"
                   else _resolve_js(n, rel, index))
            if hit and hit != rel:
                edges.append((rel, hit, 1.0))
            elif hit is None:
                if meta["lang"] == "py" and not n.startswith("."):
                    external += 1
                elif meta["lang"] == "js" and not n.startswith("."):
                    external += 1
                else:
                    unresolved += 1

    edges = sorted(set(edges))
    parts = sorted({a for a, _, _ in edges} | {b for _, b, _ in edges})
    return {
        "project": {"name": name or os.path.basename(root.rstrip("/")),
                    "parts": parts, "links": edges},
        "counts": {
            "files_scanned": len(index),
            "files_in_graph": len(parts),
            "files_isolated": len(index) - len(parts),
            "edges": len(edges),
            "external_imports_ignored": external,
            "unresolved_relative": unresolved,
        },
    }


def fan_in(bp: dict) -> list:
    """How many distinct modules import each module. Descending."""
    counts = {}
    for a, b, _ in bp["project"]["links"]:
        counts.setdefault(b, set()).add(a)
    return sorted(((k, len(v)) for k, v in counts.items()),
                  key=lambda kv: (-kv[1], kv[0]))


def as_claim(bp: dict, hub: str, claim: str = None) -> dict:
    """The joint. Take the modules that import `hub` and ask the survey whether
    they are separate supports or one support counted many times."""
    supports = sorted({a for a, b, _ in bp["project"]["links"] if b == hub})
    claim = claim or "these modules are independently grounded"
    links = [(s, hub, 1.0) for s in supports] + [(hub, claim, 1.0)]
    return {"name": f"modules importing {hub}",
            "parts": supports + [hub, claim], "links": links,
            "conclusion": claim, "supports": supports}
