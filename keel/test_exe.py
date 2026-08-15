#!/usr/bin/env python3
"""The shipped file must be the tested file.

    python3 -m pytest -q keel/test_exe.py

keel/dist/keel.cjs is what a person actually downloads and runs. It is built by
flattening three source files into one, which is a hand-rolled bundler and
therefore a liability: a silent extraction error would hand people a DIFFERENT
program from the one the test suite exercises. So the bundle is not trusted, it
is checked -- rebuilt, compared, and then RUN, with its answers compared against
the module the other tests use.
"""
import json
import os
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIST = os.path.join(HERE, "dist")
BUNDLE = os.path.join(DIST, "keel.cjs")

GREEN_TEA = ("According to a 2023 randomised trial of 240 participants in the UK, "
             "green tea reduced self-reported stress by 12%.")
HOLLOW = "The new process is much better and everyone should switch to it."


def build():
    return subprocess.run(["python3", os.path.join(HERE, "build_exe.py")],
                          capture_output=True, text=True, timeout=300)


def keel(*args, **kw):
    return subprocess.run(["node", BUNDLE, *args], capture_output=True, text=True,
                          timeout=120, **kw)


def test_the_bundle_is_current():
    before = open(BUNDLE, encoding="utf-8").read()
    r = build()
    assert r.returncode == 0, r.stderr
    assert open(BUNDLE, encoding="utf-8").read() == before, \
        "keel/dist/keel.cjs is stale — re-run python3 keel/build_exe.py and commit it"


def test_the_bundle_needs_nothing_but_node():
    src = open(BUNDLE, encoding="utf-8").read()
    assert "require(" in src
    for forbidden in ('require("../', "require('../", "node_modules",
                      "import ", "export ", "fetch(", "https://"):
        assert forbidden not in src, f"the bundle reaches outside itself: {forbidden!r}"
    # only node's own built-ins
    import re
    for mod in re.findall(r'require\("([^"]+)"\)', src):
        assert mod.startswith("node:"), f"the bundle requires a package: {mod}"


def test_it_runs_and_agrees_with_the_module_on_the_case_study():
    out = keel("check", GREEN_TEA, "--json")
    assert out.returncode == 0, out.stderr
    a = json.loads(out.stdout)
    assert a["found"] == 5 and a["of"] == 5, "checkable is not true — this must stay 5 of 5"
    assert a["search_line"] == "2023 240 participants 12% randomised trial in the UK"
    assert a["handles"]["source_named"] is False


def test_the_bundled_kernel_still_refuses_the_things_it_should(tmp_path):
    actions = tmp_path / "a.json"
    actions.write_text(json.dumps([
        {"verb": "read", "target": "projects/notes.md"},
        {"verb": "read", "target": ".ssh/id_rsa"},
        {"verb": "write", "target": "posts/x.md", "content": HOLLOW},
        {"verb": "write", "target": "posts/y.md", "content": GREEN_TEA},
    ]))
    out = keel("run", str(actions), "--json")
    r = json.loads(out.stdout)
    outcomes = [x["outcome"] for x in r["results"]]
    assert outcomes == ["ADMITTED", "REFUSED", "HELD", "ADMITTED"]
    assert r["manifest"]["interruptions"] == 1, "only the boundary breach interrupts"
    assert r["manifest"]["sealed"]["ok"] is True
    assert out.returncode == 1, "a run containing a stop must not exit 0"


def test_a_quiet_run_exits_zero(tmp_path):
    actions = tmp_path / "a.json"
    actions.write_text(json.dumps([{"verb": "read", "target": f"projects/n{i}.md"}
                                   for i in range(12)]))
    out = keel("run", str(actions))
    assert out.returncode == 0
    assert "12 done" in out.stdout
    assert "interrupted no times" in out.stdout.replace("\x1b[1m", "").replace("\x1b[0m", "")


def test_the_policy_travels_with_the_binary():
    """A person who downloads one file must not also need a config file."""
    out = keel("key")
    assert out.returncode == 0
    assert "anything in payroll" in out.stdout
    assert "everything else" in out.stdout


def test_the_launchers_are_real_launchers_not_pretend_binaries():
    cmd = open(os.path.join(DIST, "keel.cmd"), encoding="utf-8").read()
    assert "node" in cmd and "keel.cjs" in cmd
    sh = open(os.path.join(DIST, "keel"), encoding="utf-8").read()
    assert sh.startswith("#!/bin/sh")
    assert not os.path.exists(os.path.join(DIST, "keel.exe")), \
        "there must be no file named keel.exe that is not actually a Windows binary"


def test_the_build_refuses_to_mangle_a_module_it_cannot_parse():
    """A bundler that silently drops a line is the failure this guards."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("bx", os.path.join(HERE, "build_exe.py"))
    bx = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bx)
    with pytest.raises(SystemExit):
        bx.strip_esm("import { a } from 'b'\nexport default a\n")


def test_the_honest_limits_travel_with_the_binary():
    out = keel("help")
    text = out.stdout
    assert "cannot stop a program that" in text
    assert "should not rely on alone" in text
    assert "No account, no network, no cost" in text
