#!/usr/bin/env python3
"""Candidate invisible edges, and the quotient pass.

A CANDIDATE IS NEVER AN EDGE. Everything here finds places a file names another
file, which is a superset of the dependencies the import graph misses and also
a superset of the things that are not dependencies at all. A filename in a
docstring looks identical to a filename in a subprocess call.

That asymmetry is the whole point: a static pass can demonstrate its own FALSE
positives and can say nothing about its recall. A computed module name, a
registry filled at import time, or a dependency crossing a process boundary
through a data file leaves no mark this can read.
"""

from __future__ import annotations

import ast
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "page-code"))
sys.path.insert(0, os.path.join(ROOT, "lintel"))

DYNAMIC_CALLS = ("import_module", "__import__", "run", "check_output",
                 "Popen", "call", "open", "read_text", "spawn", "execFile")

#: how a candidate was spotted. Reported per edge, never summed into a score.
KIND_STRING = "string-literal naming a repository file"
KIND_DYNAMIC = "string literal inside a dynamic-dispatch call"
KIND_COMMENT = "comment or docstring naming a repository file"


def _paths_in(text, known):
    """Every known repository path mentioned anywhere in this text."""
    hits = set()
    for p in known:
        if p in text:
            hits.add(p)
        base = os.path.basename(p)
        # a bare basename is only distinctive if it is not a common one
        if base not in COMMON_BASENAMES and re.search(
                r"(?<![\w/.-])" + re.escape(base) + r"(?![\w-])", text):
            hits.add(p)
    return hits


COMMON_BASENAMES = {
    "__init__.py", "index.js", "index.html", "main.py", "app.py", "test.py",
    "setup.py", "utils.py", "config.py", "README.md", "package.json",
}


def dynamic_call_strings(path):
    """String literals passed to import_module/__import__/subprocess/open."""
    try:
        tree = ast.parse(open(path, encoding="utf-8", errors="replace").read())
    except Exception:
        return set()
    out = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = (fn.attr if isinstance(fn, ast.Attribute)
                else fn.id if isinstance(fn, ast.Name) else None)
        if name not in DYNAMIC_CALLS:
            continue
        for a in list(node.args) + [k.value for k in node.keywords]:
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                out.add(a.value)
            elif isinstance(a, (ast.List, ast.Tuple)):
                for e in a.elts:
                    if isinstance(e, ast.Constant) and isinstance(e.value, str):
                        out.add(e.value)
    return out


def _is_comment_or_doc(text, path_str):
    """Does every occurrence of path_str sit in a comment or a docstring?

    Lexical, and deliberately crude: it is here to demonstrate that the
    detector CANNOT separate a mention from a dependency, not to do it well.
    """
    in_prose = 0
    total = 0
    for line in text.splitlines():
        if path_str not in line:
            continue
        total += 1
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("*") or \
                stripped.startswith('"""') or stripped.startswith("'''") or \
                stripped.startswith("//"):
            in_prose += 1
    return total > 0 and in_prose == total


def find_candidates(parts, index_paths, declared):
    """Candidate edges between modules already in the declared graph.

    `declared` is the set of undirected declared pairs, so a candidate that
    merely restates a real import is not counted as new.
    """
    known = set(parts)
    out = []
    for rel in sorted(parts):
        full = index_paths.get(rel)
        if not full or not os.path.exists(full):
            continue
        try:
            text = open(full, encoding="utf-8", errors="replace").read()
        except Exception:
            continue

        dyn = set()
        if rel.endswith(".py"):
            for s in dynamic_call_strings(full):
                for p in known:
                    if p == rel:
                        continue
                    if s == p or s.endswith("/" + os.path.basename(p)) or \
                            os.path.basename(p) == s:
                        dyn.add(p)

        for p in _paths_in(text, known):
            if p == rel:
                continue
            pair = (rel, p) if rel < p else (p, rel)
            if pair in declared:
                continue
            kind = (KIND_DYNAMIC if p in dyn else
                    KIND_COMMENT if _is_comment_or_doc(text, os.path.basename(p))
                    else KIND_STRING)
            out.append({"from": rel, "to": p, "kind": kind})
    # one row per pair, keeping the strongest evidence
    rank = {KIND_DYNAMIC: 0, KIND_STRING: 1, KIND_COMMENT: 2}
    best = {}
    for c in out:
        pair = (c["from"], c["to"]) if c["from"] < c["to"] else (c["to"], c["from"])
        if pair not in best or rank[c["kind"]] < rank[best[pair]["kind"]]:
            best[pair] = c
    return [best[k] for k in sorted(best)]


# ------------------------------------------------------------- quotient ----
def indirection_nodes(parts, links, file_for=None):
    """One-in one-out nodes. The quotient's idea of an indirection node.

    CHOSEN, not derived: a module that re-exports AND does one small thing is
    not caught, and a module that merely happens to have one importer and one
    dependency IS caught whether or not it is indirection.
    """
    ins, outs = {}, {}
    for a, b, *_ in links:
        outs.setdefault(a, set()).add(b)
        ins.setdefault(b, set()).add(a)
    return sorted(n for n in parts
                  if len(ins.get(n, ())) == 1 and len(outs.get(n, ())) == 1
                  and next(iter(ins[n])) != next(iter(outs[n])))


def quotient(parts, links):
    """Collapse every indirection node, repeatedly, until none remain."""
    from lintel import collapse_passthrough
    p, l = list(parts), list(links)
    removed = []
    while True:
        nodes = indirection_nodes(p, l)
        if not nodes:
            break
        n = nodes[0]
        try:
            p, l = collapse_passthrough(p, l, n)
        except ValueError:
            break
        removed.append(n)
    return p, l, removed
