#!/usr/bin/env python3
"""build_console.py -- render console.html from the MEASURED results.

The four browser apps (Cairn, Page Code, HELM, CI) are generated from
results_ci.json and the frozen cohort, so the numbers in the console are the
numbers the experiment actually produced. Re-run ci_test.py then this.
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

ci = json.load(open(os.path.join(HERE, "results_ci.json")))
repos = json.load(open(os.path.join(ROOT, "ei-dashboards/data/qwen_deepseek_frozen.json")))["repos"]
rows, cal = ci["rows"], ci["C1_calibration"]

NONE_BADGE = '<b class="bad">none</b>'


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def h(s):
    return hashlib.sha256(s.encode()).hexdigest()


citab = "".join(
    '<tr><td class="n">{}</td><td>{}</td><td>{}</td><td class="neg">{:+}</td><td>{}</td><td>{}</td></tr>'.format(
        esc(r["repo"]), r["confidence"] if r["confidence"] is not None else "—",
        r["structural_truth"], r["gap"],
        "✓" if r["has_next_step"] else "—", "✓" if r["names_signals"] else "—")
    for r in rows)

bins = "".join(
    '<div class="binrow"><span class="bl">{}</span><span class="bn">n={}</span>'
    '<span class="bar2" title="stated confidence"><i style="width:{:.0f}%;background:var(--bl)"></i></span>'
    '<span class="bar2" title="independent truth"><i style="width:{:.0f}%;background:var(--ac)"></i></span>'
    '<span class="bg2">{:+}</span></div>'.format(
        b["bin"], b["n"], (b["mean_conf"] or 0) * 100, (b["mean_truth"] or 0) * 100, b["gap"])
    for b in cal["bins"] if b["n"])

led = "".join(
    '<tr><td class="n">{}</td><td>{:,}</td><td>{}</td><td>{}</td><td class="mono">{}</td></tr>'.format(
        esc(r["full_name"]), r["stars"], r["open_issues"],
        esc(r["license"]) if r["license"] else NONE_BADGE,
        h(r["full_name"] + str(r["stars"]))[:12])
    for r in repos)

PERMS = [("cairn", "projects/**", "read", "—", "allow"),
         ("cairn", "projects/drafts/**", "write", "5 changes", "allow"),
         ("cairn", "contracts/**", "read", "—", "allow"),
         ("cairn", "contracts/**", "write", "—", "deny"),
         ("cairn", "payroll/**", "any", "—", "deny"),
         ("cairn", "~/.ssh/**", "any", "—", "deny"),
         ("cairn", "*.env", "any", "—", "deny"),
         ("cairn", "(anything not listed)", "any", "—", "deny · default")]
pcrows = "".join(
    '<tr><td>{}</td><td class="mono">{}</td><td>{}</td><td>{}</td><td class="{}">{}</td></tr>'.format(
        a, esc(p), ac, lim, "okc" if d.startswith("allow") else "noc", d)
    for a, p, ac, lim, d in PERMS)

D = dict(citab=citab, bins=bins, led=led, pcrows=pcrows,
         ece=cal["ece"], band=cal["band"], diag=cal["diagnosis"], cons=cal["user_consequence"],
         c2=ci["C2_option_space"]["fraction"], c3=ci["C3_self_verifiability"]["fraction"],
         root=ci["C5_stack_on_real_cohort"]["merkle_root"],
         unlic=", ".join(ci["C5_stack_on_real_cohort"]["unlicensed"]), n=ci["cohort_n"])

TPL = open(os.path.join(HERE, "console_template.html")).read()
for k, v in D.items():
    TPL = TPL.replace("{{" + k + "}}", str(v))
open(os.path.join(HERE, "console.html"), "w").write(TPL)
print("wrote console.html  (%.1f KB) from measured results" % (len(TPL) / 1024))
