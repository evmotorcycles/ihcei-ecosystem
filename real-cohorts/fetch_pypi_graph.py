#!/usr/bin/env python3
"""
fetch_pypi_graph.py — build a REAL multi-hop dependency graph from the live PyPI registry
=========================================================================================
Written AFTER prereg/realsub_prereg.json was locked (canonical sha256 4e83893b...).
This is the fetcher only: it retrieves and commits rows. It computes NO gate and
reports NO verdict, so it cannot be tuned toward one.

Breadth-first from a fixed seed list, following requires_dist. Every node carries only
quantities the pre-registration named, each read straight off the registry:

    U        number of released versions
    D_enc    release hygiene   1/(1 + months_since_last_release/12)
    D_dec    pin clarity       fraction of requires_dist entries with a version constraint
    depth    BFS hop depth from the seeds
    E        in-degree, filled in after the crawl (how many fetched packages depend on it)

Writes data/pypi/dep_graph_nodes.csv and data/pypi/dep_graph_edges.csv, plus a
manifest with each file's sha256 — so the analysis is pinned to exactly these rows.

    python3 real-cohorts/fetch_pypi_graph.py
"""
from __future__ import annotations
import csv, hashlib, json, os, re, sys, time, urllib.request
from collections import deque
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "pypi")

# Seed roots — broad, well-known, spanning several communities so the crawl is not a
# single vendor's subtree.
#
# ATTEMPT 2. The first crawl used the 12 seeds now at the head of this list and reached
# only 69 nodes, because the transitive RUNTIME closure of those packages is genuinely
# small once extras are excluded. 69 is below the pre-registered KR0 floor of 250, so the
# seed list was widened. The change was made BEFORE any gate was computed — not one KR or
# SR value had been calculated at that point — so no outcome could have influenced which
# seeds were added. Attempt 1 is preserved in data/pypi/MANIFEST.attempt1_n69.json.
# The gates themselves are untouched and remain as locked in 4e83893b...
SEEDS = ["requests", "flask", "django", "pandas", "scikit-learn", "sqlalchemy",
         "celery", "fastapi", "black", "pytest", "rich", "boto3",
         # widened (attempt 2) — still chosen for breadth, blind to all results
         "jupyter", "notebook", "ipython", "matplotlib", "scipy", "sympy",
         "torch", "transformers", "datasets", "gradio", "streamlit", "dash",
         "airflow", "dbt-core", "great-expectations", "prefect", "luigi",
         "scrapy", "beautifulsoup4", "httpx", "aiohttp", "tornado", "sanic",
         "pydantic", "attrs", "marshmallow", "cerberus", "jsonschema",
         "poetry", "tox", "nox", "pre-commit", "mypy", "ruff", "pylint",
         "sphinx", "mkdocs", "pelican", "nbconvert", "papermill",
         "opencv-python", "pillow", "imageio", "scikit-image", "albumentations",
         "plotly", "bokeh", "altair", "seaborn", "holoviews",
         "sqlmodel", "alembic", "peewee", "tortoise-orm", "databases",
         "google-cloud-storage", "azure-storage-blob", "paramiko", "fabric",
         "pyspark", "dask", "ray", "polars", "duckdb", "pyarrow",
         "spacy", "nltk", "gensim", "sentence-transformers", "langchain",
         "openai", "anthropic", "litellm", "instructor", "guardrails-ai",
         "click", "typer", "fire", "docopt", "argcomplete",
         "cryptography", "pyjwt", "passlib", "authlib", "oauthlib",
         "locust", "hypothesis", "faker", "factory-boy", "responses",
         "django-rest-framework", "djangorestframework", "flask-sqlalchemy",
         "starlette", "uvicorn", "gunicorn", "werkzeug", "jinja2"]
# The widened seed list put ~100 packages at depth 0, so a 420-node cap was exhausted
# before BFS ever reached depth 2 — max_depth came out as 1, which cannot satisfy the
# pre-registered KR0 requirement of depth >= 3 or populate SR1's depth profile. The cap
# is raised so the crawl can actually descend. Changed while still blind to every gate
# value; only the sample's size and reach move, never a threshold.
MAX_NODES = 1500
MAX_DEPTH = 4
NAME_RE = re.compile(r"^[A-Za-z0-9._-]+")


def norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def fetch(pkg: str):
    url = "https://pypi.org/pypi/%s/json" % urllib.parse.quote(pkg)
    req = urllib.request.Request(url, headers={"User-Agent": "lism-real-cohorts/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.load(r)
    except Exception:
        return None


def parse_requires(info):
    """Return (dependency names, pin-clarity fraction) from requires_dist.

    Extras are skipped: an optional dependency is not part of the runtime graph.
    Pin clarity = share of runtime requirements that carry a version constraint.
    """
    reqs = info.get("requires_dist") or []
    deps, pinned, total = [], 0, 0
    for raw in reqs:
        if "extra ==" in raw:
            continue
        m = NAME_RE.match(raw.strip())
        if not m:
            continue
        deps.append(norm(m.group(0)))
        total += 1
        rest = raw[m.end():].split(";")[0]
        if any(op in rest for op in (">=", "<=", "==", "~=", "!=", ">", "<")):
            pinned += 1
    # a package with no runtime requirements states nothing about its pinning
    # discipline; the pre-registration's D_dec is undefined there, so we record the
    # neutral 0.5 rather than inventing a perfect or a failing score.
    clarity = (pinned / total) if total else 0.5
    return deps, clarity


def months_since(iso: str) -> float:
    try:
        t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except Exception:
        return 120.0
    return max(0.0, (datetime.now(timezone.utc) - t).days / 30.44)


def last_upload(data) -> str:
    best = ""
    for files in (data.get("releases") or {}).values():
        for f in files:
            u = f.get("upload_time_iso_8601") or f.get("upload_time") or ""
            if u > best:
                best = u
    return best


def main():
    os.makedirs(OUT, exist_ok=True)
    seen, nodes, edges = {}, [], []
    q = deque((norm(s), 0) for s in SEEDS)
    queued = {norm(s) for s in SEEDS}

    print("=" * 84)
    print(" FETCHING A REAL DEPENDENCY GRAPH FROM THE LIVE PyPI REGISTRY")
    print(" spec 4e83893b0eb37567b39c7c5ad128379f11a77416e8d4abdf0da647415110db8c (locked first)")
    print("=" * 84)

    while q and len(nodes) < MAX_NODES:
        pkg, depth = q.popleft()
        if pkg in seen or depth > MAX_DEPTH:
            continue
        data = fetch(pkg)
        if not data:
            continue
        info = data.get("info") or {}
        deps, clarity = parse_requires(info)
        n_versions = len(data.get("releases") or {})
        if n_versions == 0:
            continue
        msince = months_since(last_upload(data))
        seen[pkg] = True
        nodes.append({"package": pkg, "depth": depth, "U_versions": n_versions,
                      "months_since_release": round(msince, 2),
                      "D_enc_release_hygiene": round(1.0 / (1.0 + msince / 12.0), 6),
                      "D_dec_pin_clarity": round(clarity, 6),
                      "n_requires": len(deps)})
        for d in deps:
            edges.append({"src": pkg, "dst": d})
            if d not in queued and depth + 1 <= MAX_DEPTH:
                queued.add(d)
                q.append((d, depth + 1))
        if len(nodes) % 25 == 0:
            print("  fetched %3d nodes (depth %d, queue %d)" % (len(nodes), depth, len(q)))
        time.sleep(0.05)

    # in-degree counted over EDGES BETWEEN FETCHED NODES only — an edge to a package
    # we never fetched cannot be scored, and counting it would inflate E for hubs.
    present = {n["package"] for n in nodes}
    indeg = {p: 0 for p in present}
    kept = []
    for e in edges:
        if e["src"] in present and e["dst"] in present:
            indeg[e["dst"]] += 1
            kept.append(e)
    for n in nodes:
        n["E_indegree"] = indeg[n["package"]]

    npath = os.path.join(OUT, "dep_graph_nodes.csv")
    epath = os.path.join(OUT, "dep_graph_edges.csv")
    with open(npath, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(nodes[0].keys()))
        w.writeheader()
        w.writerows(nodes)
    with open(epath, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["src", "dst"])
        w.writeheader()
        w.writerows(kept)

    man = {"fetched_utc": datetime.now(timezone.utc).isoformat(),
           "spec_sha256_canonical": open(
               os.path.join(HERE, "prereg", "REALSUB.sha256")).read().strip(),
           "seeds": SEEDS, "n_nodes": len(nodes), "n_edges_internal": len(kept),
           "max_depth": max(n["depth"] for n in nodes),
           "sha256": {os.path.basename(p): hashlib.sha256(open(p, "rb").read()).hexdigest()
                      for p in (npath, epath)}}
    json.dump(man, open(os.path.join(OUT, "MANIFEST.json"), "w"), indent=2)

    print("\n  nodes %d | internal edges %d | max depth %d"
          % (len(nodes), len(kept), man["max_depth"]))
    print("  committed -> data/pypi/dep_graph_nodes.csv, dep_graph_edges.csv")
    print("  NOTE: this script computes no gate. Verdicts come from analyze_real.py.")
    return 0


if __name__ == "__main__":
    import urllib.parse
    sys.exit(main())
