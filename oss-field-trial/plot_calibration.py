#!/usr/bin/env python3
"""plot_calibration.py — reliability diagram + ROC from the labeled trial scores.

Reads fixtures/labeled_scores.json (produced by issues_followup.mjs) and renders
the actual curves behind the summary numbers: how calibrated each engine's
posterior is (reliability) and how well it ranks threats over benign traffic
(ROC). Output: calibration_roc.png
"""
import json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, 'fixtures', 'labeled_scores.json')))['items']

SURFACE, INK, INK2, GRID = '#fcfcfb', '#1a1a19', '#5f5e56', '#e8e7e1'
SERIES = {'p_off': ('#2a78d6', 'gate OFF'), 'p_on': ('#1baf7a', 'gate ON'), 'p_helm': ('#eda100', 'HELM')}

def reliability(key, bins=5):
    pts = []
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        grp = [r for r in data if lo <= r[key] < hi or (b == bins - 1 and r[key] == 1.0)]
        if grp:
            pts.append((sum(r[key] for r in grp) / len(grp),
                        sum(r['y'] for r in grp) / len(grp), len(grp)))
    return pts

def roc(key):
    scored = sorted(data, key=lambda r: -r[key])
    P = sum(r['y'] for r in data); N = len(data) - P
    xs, ys, tp, fp, auc, prev_fpr, prev_tpr = [0], [0], 0, 0, 0.0, 0.0, 0.0
    for r in scored:
        if r['y']: tp += 1
        else: fp += 1
        fpr, tpr = fp / N, tp / P
        auc += (fpr - prev_fpr) * (tpr + prev_tpr) / 2
        prev_fpr, prev_tpr = fpr, tpr
        xs.append(fpr); ys.append(tpr)
    return xs, ys, auc

def brier(key):
    return sum((r[key] - r['y']) ** 2 for r in data) / len(data)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6), dpi=150)
fig.patch.set_facecolor(SURFACE)
for ax in (ax1, ax2):
    ax.set_facecolor(SURFACE)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8.5)
    ax.grid(True, color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)

# ── reliability diagram ───────────────────────────────────────────────
ax1.plot([0, 1], [0, 1], ls=(0, (4, 4)), lw=1, color=INK2, zorder=1)
label_at = {'p_off': 0, 'p_on': -1, 'p_helm': 1}
for key, (col, name) in SERIES.items():
    pts = reliability(key)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    ax1.plot(xs, ys, color=col, lw=2, marker='o', ms=6,
             mec=SURFACE, mew=1.2, zorder=3)
    i = label_at[key] % len(xs)
    off = {'p_off': (8, -12), 'p_on': (8, 6), 'p_helm': (-4, 12)}[key]
    ax1.annotate(f'{name} · Brier {brier(key):.3f}', (xs[i], ys[i]),
                 textcoords='offset points', xytext=off, fontsize=8.5,
                 color=INK, fontweight='medium')
ax1.set_xlabel('predicted p(manipulative)', color=INK2, fontsize=9)
ax1.set_ylabel('observed manipulative fraction', color=INK2, fontsize=9)
ax1.set_title('Reliability — is the posterior honest?', color=INK, fontsize=10.5, loc='left')
ax1.set_xlim(-0.02, 1.02); ax1.set_ylim(-0.02, 1.02)

# ── ROC ───────────────────────────────────────────────────────────────
ax2.plot([0, 1], [0, 1], ls=(0, (4, 4)), lw=1, color=INK2, zorder=1)
roc_label_pos = {'p_off': (0.42, 0.62), 'p_on': (0.12, 0.97), 'p_helm': (0.3, 0.83)}
for key, (col, name) in SERIES.items():
    xs, ys, auc = roc(key)
    ax2.plot(xs, ys, color=col, lw=2, zorder=3)
    ax2.annotate(f'{name} · AUC {auc:.3f}', roc_label_pos[key], fontsize=8.5,
                 color=INK, fontweight='medium')
ax2.set_xlabel('false-positive rate (benign flagged)', color=INK2, fontsize=9)
ax2.set_ylabel('true-positive rate (threats caught)', color=INK2, fontsize=9)
ax2.set_title('ROC — does it rank threats above benign?', color=INK, fontsize=10.5, loc='left')
ax2.set_xlim(-0.02, 1.02); ax2.set_ylim(-0.02, 1.02)

fig.suptitle('IHCEI/HELM on labeled trial data (n=144: 44-corpus + 6 threats + 100 real registry texts)',
             color=INK, fontsize=11, fontweight='semibold', x=0.02, ha='left')
fig.tight_layout(rect=(0, 0, 1, 0.94))
out = os.path.join(HERE, 'calibration_roc.png')
fig.savefig(out, facecolor=SURFACE, bbox_inches='tight')
print('wrote', out)
for key, (_, name) in SERIES.items():
    print(f'  {name:10s} Brier {brier(key):.3f} · AUC {roc(key)[2]:.3f}')
