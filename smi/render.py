#!/usr/bin/env python3
"""render.py -- draw a composed frame as SVG.

    python3 smi/render.py          writes smi/frames/*.svg and smi/smi.html

The frames are rendered by the real engine, here, offline. The page shows them
side by side so the difference a gesture makes is something you look at rather
than something you are told about. Nothing on the page recomputes anything --
a JavaScript reimplementation of the metric would be a second engine to keep in
step, and this project already treats that as a liability.
"""
from __future__ import annotations

import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smi.compositor import compose, simulate_human_pull_gesture   # noqa: E402
from smi.mesh import SMIMesh                                      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES = os.path.join(HERE, "frames")
W, H = 760.0, 470.0


def demo_mesh():
    """A small invoice: two inputs, three derived figures, and a stray note."""
    m = SMIMesh()
    m.add_node("qty", "Quantity", 12)
    m.add_node("unit", "Unit price", 4.50)
    m.add_node("net", "Net")
    m.add_node("vat", "VAT 20%")
    m.add_node("total", "Total due")
    m.add_node("terms", "Payment terms")
    m.add_node("late", "Late fee")
    m.connect("qty", "net", lambda q: q * 4.50, J=4.0, label="× price")
    m.connect("unit", "net", lambda u: u * 12, J=4.0, label="× qty")
    m.connect("net", "vat", lambda n: round(n * 0.20, 2), J=8.0, label="20%")
    m.connect("net", "total", lambda n: round(n * 1.20, 2), J=8.0, label="+ VAT")
    m.connect("vat", "total", lambda v: None, J=2.0, label="cross-check")
    m.connect("terms", "late", lambda t: t, J=0.5, label="if overdue")
    return m


def svg(frame, title, note=""):
    """One frame as standalone SVG. Colours come from the compositor, not here."""
    out = [f'<svg viewBox="0 0 {W:.0f} {H:.0f}" xmlns="http://www.w3.org/2000/svg" '
           f'role="img" aria-label="{html.escape(title)}" '
           'style="width:100%;height:auto;font-family:system-ui,sans-serif">',
           '<rect width="100%" height="100%" fill="var(--frame-bg,#0B1220)" rx="12"/>']
    # The title and the strapline are chrome. A node drawn underneath them is a
    # node you cannot read, so the drawable band excludes both rather than
    # letting the layout use the whole rectangle and hoping.
    TOP, BOT = 44.0, 36.0
    inner = H - TOP - BOT
    pos = {n["id"]: (n["x"] * W / 1000.0, TOP + n["y"] * inner / 640.0)
           for n in frame["nodes"]}

    labelled = []
    for w in frame["wires"]:
        x1, y1 = pos[w["source"]]
        x2, y2 = pos[w["target"]]
        dash = "" if w["dash"] == "none" else f' stroke-dasharray="{w["dash"]}"'
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                   f'stroke="{w["stroke"]}" stroke-width="{w["width"]:.2f}" '
                   f'stroke-opacity="{w["opacity"]:.2f}"{dash}/>')
        if w["state"] == "ROTTED" or not w["label"]:
            continue
        # Two wires between nearly the same pair put their captions on the same
        # pixel and the text turns to mush. Drop the second rather than draw it.
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if any(abs(mx - lx) < 46 and abs(my - ly) < 12 for lx, ly in labelled):
            continue
        labelled.append((mx, my))
        out.append(f'<text x="{mx:.1f}" y="{my - 6:.1f}" fill="{w["stroke"]}" '
                   f'font-size="9" text-anchor="middle" opacity=".75">'
                   f'{html.escape(w["label"])}</text>')

    for n in frame["nodes"]:
        x, y = pos[n["id"]]
        val = "—" if n["value"] is None else f'{n["value"]}'
        label = html.escape(n["text"])
        wpx = max(74, 8 + 7.0 * max(len(label), len(val) + 2))
        out.append(
            f'<g opacity="{n["opacity"]:.2f}">'
            f'<rect x="{x - wpx / 2:.1f}" y="{y - 19:.1f}" width="{wpx:.0f}" height="38" rx="9" '
            f'fill="#0F172A" stroke="{n["colour"]}" stroke-width="1.4"/>'
            f'<text x="{x:.1f}" y="{y - 4:.1f}" fill="#94A3B8" font-size="9" '
            f'text-anchor="middle">{label}</text>'
            f'<text x="{x:.1f}" y="{y + 11:.1f}" fill="{n["colour"]}" font-size="13" '
            f'font-weight="650" text-anchor="middle" '
            f'font-family="ui-monospace,monospace">{html.escape(val)}</text>'
            f'</g>')

    out.append(f'<text x="14" y="22" fill="#E2E8F0" font-size="12" font-weight="650">'
               f'{html.escape(title)}</text>')
    if note:
        # the strapline sits on its own band so it never lands on a node
        out.append(f'<rect x="0" y="{H - 26:.0f}" width="{W:.0f}" height="26" '
                   f'fill="#0B1220" opacity=".92"/>'
                   f'<text x="14" y="{H - 9:.0f}" fill="#64748B" font-size="10">'
                   f'{html.escape(note)}</text>')
    out.append("</svg>")
    return "\n".join(out)


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Synaptic Mesh Interface</title>
<style>
:root{{--bg:#F1F3EF;--card:#FFFFFF;--ink:#12171A;--ink2:#46504B;--stone:#6A746E;
  --line:#D7DBD4;--sea:#20535F;--frame-bg:#0B1220;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#0C100F;--card:#151A18;
  --ink:#E8EDEA;--ink2:#B0BAB4;--stone:#8B958F;--line:#232927;--sea:#6FB6C9}}}}
:root[data-theme=dark]{{--bg:#0C100F;--card:#151A18;--ink:#E8EDEA;--ink2:#B0BAB4;
  --stone:#8B958F;--line:#232927;--sea:#6FB6C9}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.65 var(--sans);
  -webkit-font-smoothing:antialiased}}
.wrap{{max-width:52rem;margin:0 auto;padding:2.6rem 1.1rem 5rem}}
h1,h2{{margin:0;font-weight:660;letter-spacing:-.02em;line-height:1.18;text-wrap:balance}}
h1{{font-size:clamp(1.9rem,5vw,2.6rem)}}
h2{{font-size:1.15rem;margin:2.6rem 0 .3rem}}
p{{margin:.85rem 0}}
.lede{{font-size:1.12rem;color:var(--ink2)}}
.eyebrow{{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--stone);font-weight:700}}
figure{{margin:1.4rem 0}}
figcaption{{color:var(--stone);font-size:.88rem;margin-top:.6rem;line-height:1.5}}
.key{{display:flex;flex-wrap:wrap;gap:.5rem;margin:1rem 0}}
.key span{{display:inline-flex;align-items:center;gap:.4rem;background:var(--card);
  border:1px solid var(--line);border-radius:99px;padding:.25rem .7rem;font-size:.82rem;color:var(--stone)}}
.key i{{width:.65rem;height:.65rem;border-radius:99px;display:block}}
.note{{background:var(--card);border:1px solid var(--line);border-left:3px solid #D97706;
  border-radius:0 12px 12px 0;padding:.9rem 1.1rem;margin:1.5rem 0}}
.note b{{display:block;font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;
  color:#D97706;margin-bottom:.3rem}}
.scroll{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;font-size:.92rem;min-width:22rem}}
th,td{{text-align:left;padding:.5rem .55rem;border-bottom:1px solid var(--line);vertical-align:top}}
th{{font-size:.68rem;letter-spacing:.09em;text-transform:uppercase;color:var(--stone);font-weight:700}}
td:first-child{{color:var(--stone)}}
code{{font-family:var(--mono);font-size:.87em}}
.foot{{margin-top:3rem;padding-top:1.1rem;border-top:1px solid var(--line);
  color:var(--stone);font-size:.87rem}}
</style></head><body><div class="wrap">

<p class="eyebrow">Synaptic Mesh Interface</p>
<h1>Nothing on this screen was positioned.</h1>
<p class="lede">Every element is a node in a graph of what depends on what. The distance
between two of them is the electrical resistance between them on that graph, and the
picture is whatever best preserves those distances. Move a dependency and the layout
rearranges because the arithmetic changed.</p>

<div class="key">
  <span><i style="background:#0EA5E9"></i>live — connected and resolved</span>
  <span><i style="background:#D97706"></i>held — connected, no value yet</span>
  <span><i style="background:#475569"></i>rotted — no path back</span>
</div>

{frames}

<h2>The −0.5 slope is arithmetic, not a discovery</h2>
<p>Scaling every wire by the same <code>J</code> contracts every distance by
<code>J<sup>−1/2</sup></code> — exactly, with an R² of 1.000000. That is not a property of
this graph or any graph: <code>pinv(J·L) = J⁻¹·pinv(L)</code>, so it holds on a ring, a
path, a star, a dense random graph, and anything else you pass it.</p>

<div class="scroll"><table>
<tr><th>graph</th><th>slope</th><th>R²</th></tr>
{slopes}
</table></div>

<p>The sweep is kept because it is a good smoke test — it fails the moment the
pseudo-inverse, the Laplacian or the clipping breaks. It is reported as
<b>IDENTITY (CONTROL)</b>, never as a pass, and never as evidence that space is emergent.</p>

<h2>Two things the specification got wrong</h2>
<div class="note">
  <b>Broken links do not give infinite distance</b>
  <p>Cut a mesh in two and the pseudo-inverse still returns a modest finite number between
  the halves — <code>1.118</code> here, <em>smaller</em> than a real distance inside one half.
  Unguarded, the layout would place two unrelated elements next to each other. Components are
  detected explicitly, and the engine returns infinity itself.</p>
</div>
<div class="note">
  <b>Zero coupling gives zero distance, not infinity</b>
  <p>With every wire cut, the Laplacian is zero, its pseudo-inverse is zero, and every distance
  is <code>0.0</code>. A completely dead mesh measures as <em>perfectly contracted</em> — visually
  identical to a perfectly coupled one. The dead case is caught before the metric is trusted.</p>
</div>

<div class="foot">
<p>Rendered by the real engine, offline, on this machine. No model, no weights, no network,
no cloud. The whole layout for a hundred elements is one pseudo-inverse. Frames are static
on this page on purpose: a JavaScript reimplementation of the metric would be a second
engine to keep in step with the first.</p>
</div>
</div></body></html>
"""


def main():
    os.makedirs(FRAMES, exist_ok=True)
    m = demo_mesh()

    frames = []
    f0 = compose(m, anchor="qty", width=1000.0, height=640.0)
    frames.append(("rest", "At rest", f0,
                   "Two inputs at the edges, the derived figures pulled into the middle. "
                   "Payment terms and late fee have no path to the invoice, so they sit "
                   "apart in grey.",
                   "terms and late are in their own component — grey, dashed, and parked"))

    pull = simulate_human_pull_gesture(m, "net", "total", -0.97, anchor="qty")
    frames.append(("pulled", "Total dragged away from Net", pull["after"],
                   "The coupling on one wire drops from 8.0 to 0.24. Total swings out, VAT "
                   "follows part of the way, and Quantity does not move at all — a local pull "
                   "stays local.",
                   "one wire changed: J 8.00 → 0.24"))

    cut = simulate_human_pull_gesture(m, "net", "vat", -1.0, anchor="qty")
    frames.append(("cut", "The VAT wire cut", cut["after"],
                   "With the wire gone, VAT has no path back to the invoice. It does not become "
                   "a distant live element — it rots: grey, dashed, parked, and carrying no "
                   "number at all.",
                   "VAT is unreachable — no value is shown rather than a stale one"))

    blocks = []
    for name, title, frame, caption, note in frames:
        s = svg(frame, title, note)
        open(os.path.join(FRAMES, f"{name}.svg"), "w", encoding="utf-8").write(s)
        blocks.append(f"<figure>{s}<figcaption>{html.escape(caption)}</figcaption></figure>")

    results = json.load(open(os.path.join(HERE, "results_smi.json"), encoding="utf-8"))
    names = ["ring N=7 (odd)", "path N=40", "star N=50",
             "random p=0.05 N=80", "random p=0.50 N=30"]
    rows = [f"<tr><td>ring N=100 (specified)</td><td>"
            f"{results['phase2_test']['H0_identity']['slope']:.6f}</td>"
            f"<td>{results['phase2_test']['H0_identity']['r_squared']:.6f}</td></tr>"]
    rows += [f"<tr><td>{html.escape(n)}</td><td>{s:.6f}</td><td>1.000000</td></tr>"
             for n, s in zip(names, results["phase2_test"]["H0_identity"]["other_graph_slopes"])]

    page = PAGE.format(frames="\n".join(blocks), slopes="\n".join(rows))
    out = os.path.join(HERE, "smi.html")
    open(out, "w", encoding="utf-8").write(page)
    print(f"wrote smi/smi.html ({len(page) / 1024:.1f} KB) and {len(frames)} frames in smi/frames/")


if __name__ == "__main__":
    main()
