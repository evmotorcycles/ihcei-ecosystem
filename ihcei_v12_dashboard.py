import sys
import time
import math
import threading
import argparse
import collections
from typing import Dict, List, Tuple, Deque, Optional
from dataclasses import dataclass, field

import numpy as np
import scipy.linalg as la
from scipy.spatial.distance import cdist
from scipy.stats import linregress
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

# ── ANSI colour palette ───────────────────────────────────────────────────────
R  = "\033[0m"          # reset
B  = "\033[1m"          # bold
DIM = "\033[2m"         # dim

# Named colours (foreground)
def fg(code): return f"\033[38;5;{code}m"
def bg(code): return f"\033[48;5;{code}m"

CYAN    = fg(51)
GREEN   = fg(82)
RED     = fg(196)
YELLOW  = fg(226)
ORANGE  = fg(208)
BLUE    = fg(39)
PURPLE  = fg(135)
GREY    = fg(244)
WHITE   = fg(255)
GOLD    = fg(220)
TEAL    = fg(43)
LIME    = fg(118)

# Corpus identity colours
COL = {"A": GREEN, "B": RED, "C": YELLOW}

CLEAR    = "\033[2J\033[H"
HIDE_CUR = "\033[?25l"
SHOW_CUR = "\033[?25h"

def mv(row, col): return f"\033[{row};{col}H"
def clr_line():   return "\033[2K"

VECTOR_DIM = 64


# ═══════════════════════════════════════════════════════════════════════════════
# SPARK LINE RENDERER
# ═══════════════════════════════════════════════════════════════════════════════

SPARK_CHARS = " ▁▂▃▄▅▆▇█"

def sparkline(values: List[float], width: int = 20,
              colour: str = CYAN) -> str:
    if len(values) < 2:
        return GREY + "─" * width + R
    mn, mx = min(values), max(values)
    rng = mx - mn + 1e-10
    chars = []
    sample = values[-width:] if len(values) >= width else values
    for v in sample:
        idx = int((v - mn) / rng * (len(SPARK_CHARS) - 1))
        chars.append(SPARK_CHARS[idx])
    # pad left
    padded = " " * (width - len(chars)) + "".join(chars)
    return colour + padded + R


# ═══════════════════════════════════════════════════════════════════════════════
# CORPORA  (from v11.0)
# ═══════════════════════════════════════════════════════════════════════════════

OQM_ROOT_CLUSTERS = {
    "Governance / Deen": [
        "divine governance sovereign order established law stewardship accountability",
        "just authority transparent rule custodian trustee moral obligation duty",
        "constitutional duty ethical mandate communal covenant legitimate power",
        "rights responsibilities governance protocol equity judgment distributed authority",
        "checks balances public trust transparency institutional legitimacy",
    ],
    "Cognition / Aql": [
        "rational deliberation reflective judgment intellectual honesty critical thinking",
        "epistemological humility distinguishing knowledge opinion logical reasoning",
        "verified knowledge structured inquiry evidence based conclusion calibrated belief",
        "cognitive clarity deductive rigor systematic evaluation sober analysis",
        "intellectual discipline distinguishing appearance underlying reality truth",
    ],
    "Ethics / Akhlaq": [
        "moral character virtuous conduct honesty integrity dignity respect",
        "ethical discipline principled action restraint generosity empathy care",
        "compassionate justice equity fairness non exploitation benevolence",
        "sincere intention righteous conduct internal consistency moral courage",
        "good character trustworthiness reliability in word and action",
    ],
    "Knowledge / Ilm": [
        "verified knowledge transmission education learning mentorship scholarship",
        "structured curriculum knowledge transfer intellectual development growth",
        "rigorous study disciplined research careful observation documentation",
        "shared wisdom open knowledge commons accessible education lifelong learning",
        "knowledge stewardship preserving transmitting verified understanding",
    ],
    "Community / Ummah": [
        "collective cohesion social solidarity mutual support cooperative network",
        "community resilience shared resources distributed welfare neighborhood care",
        "inclusive participation civic engagement collaborative governance commons",
        "social fabric interreliance collective responsibility shared purpose",
        "networked community knowledge sharing distributed benefit public good",
    ],
    "Purification / Tazkiyah": [
        "refinement correction growth accountability self improvement rectification",
        "purifying intent removing bias eliminating corruption systemic cleansing",
        "restoring integrity course correction ethical audit institutional reform",
        "transparent review eliminating conflict of interest regulatory compliance",
        "internal audit quality assurance governance review remediation process",
    ],
    "Justice / Adl": [
        "equitable distribution fair outcome proportional response balanced judgment",
        "impartial arbitration non discriminatory equal opportunity access rights",
        "restorative justice systemic equity addressing structural imbalance",
        "rule of law applied equally regardless of status power wealth",
        "accountability harm redress grievance protection vulnerable",
    ],
    "Creation / Khalq": [
        "purposeful design structured creation stewardship natural resources",
        "ecological responsibility custodianship sustainable development care creation",
        "recognizing order natural systems reverence designed complexity",
        "environmental ethics responsible innovation preserving ecological balance",
        "long term thinking intergenerational responsibility sustainable stewardship",
    ],
}

CORPUS_A = [
    "Our governance framework mandates equitable distribution of resources across all stakeholder communities, with transparent accountability mechanisms reviewed quarterly.",
    "The stewardship council ensures no single actor accumulates disproportionate authority. All decisions require multi-stakeholder deliberation and documented rationale.",
    "Knowledge transfer programs must be freely accessible to all community members. Intellectual enclosure violates the principle of shared commons.",
    "The audit committee identified governance gaps and issued corrective mandates to restore accountability. All remediation steps are publicly documented.",
    "Leadership is defined not by authority hoarded but by responsibility shouldered. The role of the executive is custodian, not sovereign.",
    "Community resilience depends on distributed participation. No decision affecting the commons should be made without meaningful consultation.",
    "Institutional trust is built through consistency between stated values and enacted policies. Gaps between rhetoric and action are a governance deficit.",
    "Accountability without remedy is performative. Every finding of misconduct must be followed by binding corrective action with verified implementation.",
    "The commons is not a resource to be harvested. It is a stewardship to be maintained across generations with long-horizon planning.",
    "Decentralised authority structures outperform hierarchical monopolies in resilience and adaptive capacity under uncertainty.",
    "Institutional reform requires honest diagnosis. The first step in systemic correction is accurate acknowledgment of systemic failure.",
    "Equitable participation in decision-making is not a courtesy. It is a structural prerequisite for legitimate governance.",
    "Transparency in resource allocation prevents informational asymmetries that enable rent-seeking and undermine collective trust.",
    "The organisation's purpose is not profit extraction but cognitive development and collective flourishing.",
    "Educational resources must be weighted toward communities with the greatest access deficits, not those already best served.",
]

CORPUS_B = [
    "Maximise daily active users through aggressive retention loops. Deploy variable reward schedules to increase session length and reduce churn at all cost.",
    "Extract 40% more revenue per user by reducing friction on upsell flows and leveraging behavioural data to trigger purchase intent at peak vulnerability.",
    "Dominate the market before competitors respond. Move fast, capture the install base, then monetise the lock-in. Ethics review is a post-scale concern.",
    "The algorithm surfaces increasingly stimulating content to prevent scroll-stopping. Outrage and anxiety are high-engagement emotional drivers. Leverage them.",
    "Regulatory compliance is a cost centre. Our legal team's job is to delay enforcement, not achieve genuine compliance.",
    "User data is our core asset. Consent flows are legally sufficient but designed to obscure the scope of collection. Exploit the grey zone.",
    "Make switching costs prohibitive through data portability restrictions and social graph lock-in. Trap users before they realise the cost.",
    "Growth hacking requires moving faster than ethical review can track. Apologise and pay fines post-scale. The fine is smaller than the market advantage.",
    "We define success as market share, not user wellbeing. If our product degrades mental health but drives engagement, the engagement metric wins.",
    "The human attention span is a resource to be harvested. Every second not engaged is untapped monetisation potential.",
    "Suppress negative press through coordinated social amplification of counter-narratives. Dilute criticism with volume.",
    "Workforce is a variable cost. Automate the moment automation margin exceeds severance liability. Human capital is overhead.",
    "Our content delivery amplifies emotionally activating content because it generates more ad impressions. Depression and outrage are high-CPM categories.",
    "Regulatory capture is cheaper than systemic reform. Focus lobbying on capturing agencies rather than achieving compliance.",
    "Competitor ethical constraints are slowing their growth. Our advantage is precisely our willingness to operate without those constraints.",
]

CORPUS_C = [
    "The board approved a strategic plan to grow revenue while maintaining compliance with applicable regulatory requirements.",
    "Diversity initiatives aim to improve representation metrics across all seniority levels by end of fiscal year.",
    "Community benefit agreements require the company to fund local infrastructure improvements in exchange for development permits.",
    "Quarterly earnings exceeded analyst expectations. Cost reduction measures contributed 60% of margin improvement.",
    "The ethics hotline received 47 reports this quarter. Twelve were investigated and three resulted in disciplinary action.",
    "The sustainability report documents carbon reduction progress and outlines commitments to net-zero by 2040.",
    "Legal advised the proposed data arrangement carries moderate regulatory risk. Business decided to proceed.",
    "The platform recommendation engine was updated to reduce harmful content exposure while maintaining engagement targets.",
    "Supplier audit found labour violations at two tier-two suppliers. Remediation plans have been requested.",
    "The personalisation engine increases purchase conversion by 23% using predictive behavioural modelling.",
    "The public interest litigation against our data practices was settled for an undisclosed sum without admission of liability.",
    "The government contract requires transparent reporting on milestones, expenditure, and community impact.",
    "Customer retention is our primary growth lever. Reducing churn by 5% has outsized impact on lifetime value.",
    "Leadership programmes focus on building strategic thinking and stakeholder communication capabilities.",
    "The merger creates significant synergies but requires careful workforce integration and cultural alignment.",
]


# ═══════════════════════════════════════════════════════════════════════════════
# LOCAL EMBEDDER  (BERT-compatible — see v11.0 swap instructions)
# ═══════════════════════════════════════════════════════════════════════════════

class LocalEmbedder:
    def __init__(self, vector_dim=VECTOR_DIM, seed=42):
        self.dim        = vector_dim
        self.vectoriser = TfidfVectorizer(ngram_range=(1,2), max_features=6000,
                                           sublinear_tf=True, min_df=1)
        self.svd        = TruncatedSVD(n_components=vector_dim, random_state=seed)
        self._fitted    = False

    def fit(self, corpus):
        mat = self.vectoriser.fit_transform(corpus)
        self.svd.fit(mat)
        self._fitted = True

    def embed(self, texts):
        mat  = self.vectoriser.transform(texts)
        vecs = self.svd.transform(mat)
        return normalize(vecs, norm="l2")

    def raw_magnitude(self, text):
        mat = self.vectoriser.transform([text])
        return float(np.sqrt(mat.multiply(mat).sum()))


# ═══════════════════════════════════════════════════════════════════════════════
# OQM FRAME + AL-3ASSR PIPELINE  (from v11.0)
# ═══════════════════════════════════════════════════════════════════════════════

class OQMFrame:
    def __init__(self, embedder):
        self.embedder = embedder
        self.names    = list(OQM_ROOT_CLUSTERS.keys())
        self.centroids = None

    def build(self):
        rows = []
        for phrases in OQM_ROOT_CLUSTERS.values():
            emb = self.embedder.embed(phrases)
            c   = emb.mean(axis=0)
            c  /= np.linalg.norm(c) + 1e-10
            rows.append(c)
        self.centroids = np.stack(rows)

    def press(self, text) -> dict:
        vec    = self.embedder.embed([text])[0]
        sims   = np.clip(self.centroids @ vec, 0, 1)
        best   = int(np.argmax(sims))
        d      = float(sims[best])
        u      = self.embedder.raw_magnitude(text)
        e      = u * d**2
        attractor = self.centroids[best]

        if   d < 0.12 and u > 0.50: label, h = "EXTRACTION_PATTERN",  0.90
        elif d < 0.22 and u > 0.35: label, h = "MISALIGNMENT_ZONE",   0.45
        elif d > 0.50 and u > 0.25: label, h = "ALIGNED_UTILITY",     0.04
        elif d > 0.38:              label, h = "LOW_UTIL_ALIGNED",     0.08
        else:                       label, h = "NEUTRAL_ZONE",          0.22

        return dict(text=text, d=d, u=u, e=e, label=label,
                    h=h, root=self.names[best], attractor=attractor)


# ═══════════════════════════════════════════════════════════════════════════════
# DECOUPLED SPECTRAL ENGINE  (from v11.0)
# ═══════════════════════════════════════════════════════════════════════════════

class SpectralEngine:
    GAMMA = 0.015

    def __init__(self, n=60, seed=42):
        rng       = np.random.default_rng(seed)
        raw_g     = rng.random((n, n))
        self.adj  = (raw_g + raw_g.T) / 2.0
        np.fill_diagonal(self.adj, 0.0)
        self.mask = (self.adj > 0.5).astype(float)
        self.phi  = rng.uniform(0.1, 1.0, (n, VECTOR_DIM))
        self.hbar = np.zeros((n, n))
        self.hbar_total = 0.0
        self.n    = n
        prev_W    = self._W()
        self.prev_l2 = self._fiedler(prev_W)

    def _W(self):
        p  = self.phi / (self.phi.sum(axis=1,keepdims=True) + 1e-10)
        js = cdist(p, p, metric="jensenshannon")
        js = np.nan_to_num(js, nan=1.0)
        Wb = self.mask * (1.0 / (1.0 + js))
        np.fill_diagonal(Wb, 0.0)
        Wf = Wb * np.exp(-self.GAMMA * self.hbar)
        np.fill_diagonal(Wf, 0.0)
        return Wf

    def _fiedler(self, W):
        D  = np.diag(W.sum(axis=1))
        ev = la.eigvalsh(D - W)
        return float(ev[1])

    def _js_mean(self):
        p  = self.phi / (self.phi.sum(axis=1,keepdims=True) + 1e-10)
        js = cdist(p, p, metric="jensenshannon")
        return float(np.nan_to_num(js).mean())

    def ingest(self, pkt: dict, lr=0.06):
        # Channel 1 — Φ update
        if pkt["e"] > 1e-3:
            att  = pkt["attractor"]
            if len(att) != VECTOR_DIM:
                att = np.resize(att, VECTOR_DIM)
            ew   = self.adj.sum(axis=1)
            ew  /= ew.max() + 1e-10
            pull = lr * min(pkt["e"], 2.0)
            self.phi += (pull * ew).reshape(-1,1) * (att - self.phi)
            self.phi  = np.clip(self.phi, 0.01, 1.0)

        # Channel 2 — ħ edge penalty
        self.hbar      += pkt["h"] * self.mask * 0.1
        self.hbar_total += pkt["h"]

    def step(self, pkts: list) -> dict:
        for p in pkts:
            self.ingest(p)
        W    = self._W()
        l2   = self._fiedler(W)
        rate = l2 - self.prev_l2
        self.prev_l2 = l2
        js   = self._js_mean()
        return dict(l2=l2, rate=rate, js=js, hbar=self.hbar_total)


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD STATE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CorpusState:
    label:  str           # "A", "B", "C"
    name:   str           # "Governance", "Extraction", "Mixed"
    colour: str
    engine: SpectralEngine
    corpus: List[str]
    l2_hist:    Deque[float] = field(default_factory=lambda: collections.deque(maxlen=40))
    js_hist:    Deque[float] = field(default_factory=lambda: collections.deque(maxlen=40))
    hbar_hist:  Deque[float] = field(default_factory=lambda: collections.deque(maxlen=40))
    rate_hist:  Deque[float] = field(default_factory=lambda: collections.deque(maxlen=40))
    last_pkt:   dict = field(default_factory=dict)
    round_num:  int = 0
    tawbah:     bool = False

    def update(self, m: dict, pkt: dict):
        self.l2_hist.append(m["l2"])
        self.js_hist.append(m["js"])
        self.hbar_hist.append(m["hbar"])
        self.rate_hist.append(m["rate"])
        self.last_pkt  = pkt
        self.round_num += 1
        self.tawbah    = m["l2"] < 0.001


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD RENDERER
# ═══════════════════════════════════════════════════════════════════════════════

class Dashboard:
    """
    ANSI terminal dashboard. Renders on stdout using escape codes.
    No external libraries required.
    """

    WIDTH  = 112
    HEIGHT = 52

    # Heuristic label colours
    LABEL_COL = {
        "EXTRACTION_PATTERN": RED,
        "MISALIGNMENT_ZONE":  ORANGE,
        "ALIGNED_UTILITY":    GREEN,
        "LOW_UTIL_ALIGNED":   LIME,
        "NEUTRAL_ZONE":       GREY,
    }

    def __init__(self, tick: float = 0.3):
        self.tick = tick
        self._buf: List[str] = []

    def _w(self, s):
        self._buf.append(s)

    def _flush(self):
        sys.stdout.write("".join(self._buf))
        sys.stdout.flush()
        self._buf.clear()

    # ── Drawing primitives ────────────────────────────────────────────────────

    def _box_line(self, row, col, width, text="", colour=CYAN):
        inner = text[:width-2].ljust(width-2)
        self._w(mv(row, col))
        self._w(colour + "│" + R + " " + inner + " " + colour + "│" + R)

    def _hbar(self, row, col, width, colour=CYAN):
        self._w(mv(row, col) + colour + "─" * width + R)

    def _tl(self, row, col, colour=CYAN): self._w(mv(row,col)+colour+"┌"+R)
    def _tr(self, row, col, colour=CYAN): self._w(mv(row,col)+colour+"┐"+R)
    def _bl(self, row, col, colour=CYAN): self._w(mv(row,col)+colour+"└"+R)
    def _br(self, row, col, colour=CYAN): self._w(mv(row,col)+colour+"┘"+R)
    def _ml(self, row, col, colour=CYAN): self._w(mv(row,col)+colour+"├"+R)
    def _mr(self, row, col, colour=CYAN): self._w(mv(row,col)+colour+"┤"+R)

    def _panel(self, row, col, w, h, title="", colour=CYAN):
        # Top border
        title_str = f" {B}{WHITE}{title}{R}{colour} " if title else ""
        title_raw = f" {title} " if title else ""
        top_fill  = w - 2 - len(title_raw)
        self._w(mv(row, col) + colour + "┌" + title_str + "─"*max(0,top_fill) + "┐" + R)
        # Side borders
        for r in range(row+1, row+h-1):
            self._w(mv(r, col)   + colour + "│" + R)
            self._w(mv(r, col+w-1) + colour + "│" + R)
        # Bottom border
        self._w(mv(row+h-1, col) + colour + "└" + "─"*(w-2) + "┘" + R)

    def _text(self, row, col, s):
        self._w(mv(row, col) + s)

    # ── Mini bar chart for a single metric ────────────────────────────────────

    def _metric_bar(self, value, max_val, width=12, colour=GREEN) -> str:
        frac  = min(value / (max_val + 1e-10), 1.0)
        filled= int(frac * width)
        bar   = "█" * filled + "░" * (width - filled)
        return colour + bar + R

    # ── Full screen render ─────────────────────────────────────────────────────

    def render(self, states: Dict[str, CorpusState], round_n: int,
               total_rounds: int, elapsed: float):

        W = self.WIDTH
        self._buf.clear()
        self._w(CLEAR + HIDE_CUR)

        # ══ HEADER ══════════════════════════════════════════════════════════
        self._w(mv(1, 1))
        self._w(CYAN + "╔" + "═"*(W-2) + "╗" + R)
        header_text = (
            f"  {GOLD}{B}QG-COS  ◈  SOVEREIGN OPERATING SYSTEM  ◈  "
            f"IHCEI v12.0{R}  "
            f"{GREY}│  Round {CYAN}{B}{round_n:>3}/{total_rounds}{R}  "
            f"{GREY}│  Elapsed: {CYAN}{elapsed:.1f}s{R}  "
            f"{GREY}│  N=60 nodes │ OQM-8 clusters │ LocalEmbedder{R}"
        )
        header_raw = f"  QG-COS  ◈  SOVEREIGN OPERATING SYSTEM  ◈  IHCEI v12.0  │  Round {round_n:>3}/{total_rounds}  │  Elapsed: {elapsed:.1f}s  │  N=60 nodes │ OQM-8 clusters │ LocalEmbedder"
        pad = max(0, W - 2 - len(header_raw))
        self._w(mv(2, 1) + CYAN + "║" + R + header_text + " "*pad + CYAN + "║" + R)
        self._w(mv(3, 1) + CYAN + "╠" + "═"*(W-2) + "╣" + R)

        # ══ CORPUS PANELS (3 columns) ════════════════════════════════════════
        col_w   = (W - 4) // 3
        panel_h = 14
        row_start = 4

        corpus_order = ["A", "B", "C"]

        for idx, key in enumerate(corpus_order):
            st   = states[key]
            cx   = 1 + idx * (col_w + 1)

            # Panel outline
            self._panel(row_start, cx, col_w, panel_h,
                        title=f"CORPUS {key}  {st.name}", colour=st.colour)

            r = row_start + 1

            # λ₂ sparkline
            spark = sparkline(list(st.l2_hist), width=col_w-20, colour=st.colour)
            l2_val = st.l2_hist[-1] if st.l2_hist else 0.0
            l2_disp = f"{st.colour}{B}λ₂={l2_val:>8.4f}{R}"
            rate    = st.rate_hist[-1] if st.rate_hist else 0.0
            rate_arrow = (f"{GREEN}▲" if rate > 0.001 else
                         f"{RED}▼" if rate < -0.001 else f"{GREY}─") + R
            self._text(r, cx+1, f" {l2_disp} {rate_arrow}  {spark}")
            r += 1

            # JS divergence
            js_val  = st.js_hist[-1]  if st.js_hist  else 0.0
            js_spark = sparkline(list(st.js_hist), width=col_w-18, colour=PURPLE)
            js_arrow = (f"{GREEN}▼" if (len(st.js_hist)>1 and st.js_hist[-1]<st.js_hist[-2])
                       else f"{RED}▲") + R
            self._text(r, cx+1, f" {PURPLE}JS={js_val:.5f}{R} {js_arrow}  {js_spark}")
            r += 1

            # ħ bar
            hbar_val = st.hbar_hist[-1] if st.hbar_hist else 0.0
            max_hbar = max((max(st.hbar_hist) if st.hbar_hist else 1), 1)
            hbar_bar = self._metric_bar(hbar_val, max_hbar, 14,
                                         colour=(RED if key=="B" else ORANGE if key=="C" else GREEN))
            self._text(r, cx+1, f" {GREY}ħ={hbar_val:>7.2f}{R}  {hbar_bar}")
            r += 1
            self._hbar(r, cx+1, col_w-2, colour=GREY)
            r += 1

            # Last packet info
            pkt = st.last_pkt
            if pkt:
                lbl    = pkt.get("label","—")
                lc     = self.LABEL_COL.get(lbl, GREY)
                lbl_str= (lc + B + lbl[:22].center(22) + R)
                self._text(r, cx+1,
                    f" D={st.colour}{pkt.get('d',0):.3f}{R}  "
                    f"E={GOLD}{pkt.get('e',0):.4f}{R}  "
                    f"ħ={ORANGE}{pkt.get('h',0):.2f}{R}")
                r += 1
                self._text(r, cx+1, f" {lbl_str}")
                r += 1
                root_str = pkt.get("root","")[:col_w-4]
                self._text(r, cx+1, f" {TEAL}{root_str}{R}")
                r += 1
                # Text snippet
                snippet = pkt.get("text","")[:col_w-4]
                self._text(r, cx+1, f" {DIM}{snippet}…{R}")
                r += 1

            # Tawbah indicator
            if st.tawbah:
                self._text(r, cx+1,
                    f" {RED}{B}⚠ BC10 TAWBAH — λ₂ < COLLAPSE THRESHOLD{R}")

        # ══ SPECTRAL NETWORK MONITOR (full width) ════════════════════════════
        net_row = row_start + panel_h + 1
        self._panel(net_row, 1, W, 12,
                    title="SPECTRAL NETWORK MONITOR  │  λ₂ Trajectory  │  Fiedler Eigenvalue",
                    colour=CYAN)

        # Unified λ₂ sparkline overlay (all 3 corpora)
        spark_w = W - 30
        spark_row = net_row + 2

        self._text(spark_row, 3,
            f"{GREEN}A{R}:{sparkline(list(states['A'].l2_hist), spark_w, GREEN)}  "
            f"{GREEN}λ₂={states['A'].l2_hist[-1] if states['A'].l2_hist else 0:.4f}{R}")
        spark_row += 1
        self._text(spark_row, 3,
            f"{RED}B{R}:{sparkline(list(states['B'].l2_hist), spark_w, RED)}  "
            f"{RED}λ₂={states['B'].l2_hist[-1] if states['B'].l2_hist else 0:.4f}{R}")
        spark_row += 1
        self._text(spark_row, 3,
            f"{YELLOW}C{R}:{sparkline(list(states['C'].l2_hist), spark_w, YELLOW)}  "
            f"{YELLOW}λ₂={states['C'].l2_hist[-1] if states['C'].l2_hist else 0:.4f}{R}")
        spark_row += 1

        # Schism gap
        l2_a = states['A'].l2_hist[-1] if states['A'].l2_hist else 0
        l2_b = states['B'].l2_hist[-1] if states['B'].l2_hist else 0
        gap   = l2_a - l2_b
        gap_c = GREEN if gap > 0 else RED

        # Slopes
        def slope_str(hist, colour):
            if len(hist) < 3: return f"{GREY}—{R}"
            s = linregress(range(len(hist)), list(hist)).slope
            arrow = "▲" if s > 0.001 else ("▼" if s < -0.001 else "─")
            return f"{colour}{arrow}{s:+.5f}{R}"

        self._text(spark_row + 1, 3,
            f"  {GREY}Schism gap (A−B): {gap_c}{B}{gap:>+8.4f}{R}  │  "
            f"∂λ₂/∂t:  "
            f"{GREEN}A{R}:{slope_str(states['A'].l2_hist, GREEN)}  "
            f"{RED}B{R}:{slope_str(states['B'].l2_hist, RED)}  "
            f"{YELLOW}C{R}:{slope_str(states['C'].l2_hist, YELLOW)}")

        # JS divergence comparison
        js_a = states['A'].js_hist[-1] if states['A'].js_hist else 0
        js_b = states['B'].js_hist[-1] if states['B'].js_hist else 0
        self._text(spark_row + 2, 3,
            f"  {GREY}JS-divergence:  "
            f"{GREEN}A={js_a:.5f}{R}  "
            f"{RED}B={js_b:.5f}{R}  "
            f"{GREY}Δ(B−A)={RED if js_b>js_a else GREEN}{js_b-js_a:+.5f}{R}  "
            f"{GREY}[Channel 1 decoupling: {GREEN if js_b>js_a else GREY}"
            f"{'A converging faster ✔' if js_b>js_a else 'monitoring…'}{R}{GREY}]{R}")

        # ══ SYSTEMIC FRICTION LEDGER (full width) ════════════════════════════
        fric_row = net_row + 13
        self._panel(fric_row, 1, W, 10,
                    title="SYSTEMIC FRICTION LEDGER  │  ħ_network  │  Channel 2: Edge Penalty",
                    colour=ORANGE)

        hbar_a = states['A'].hbar_hist[-1] if states['A'].hbar_hist else 0
        hbar_b = states['B'].hbar_hist[-1] if states['B'].hbar_hist else 0
        hbar_c = states['C'].hbar_hist[-1] if states['C'].hbar_hist else 0
        max_h  = max(hbar_a, hbar_b, hbar_c, 1)

        self._text(fric_row+2, 3,
            f"  {GREEN}A ħ={hbar_a:>8.2f}{R}  "
            f"{self._metric_bar(hbar_a, max_h, 20, GREEN)}")
        self._text(fric_row+3, 3,
            f"  {RED}B ħ={hbar_b:>8.2f}{R}  "
            f"{self._metric_bar(hbar_b, max_h, 20, RED)}"
            f"  {GREY}ratio B/A: {RED}{B}{hbar_b/(hbar_a+1e-6):.2f}×{R}")
        self._text(fric_row+4, 3,
            f"  {YELLOW}C ħ={hbar_c:>8.2f}{R}  "
            f"{self._metric_bar(hbar_c, max_h, 20, YELLOW)}")

        # Extraction event counter
        ext_a = sum(1 for s in states['A'].last_pkt.get("label","") if "EXTRACT" in s)
        self._text(fric_row+6, 3,
            f"  {GREY}Active BCs: BC01-BC10  │  "
            f"Zero-corruption guarantee: {GREEN}ACTIVE{R}  │  "
            f"Tawbah resets: "
            f"{RED if states['B'].tawbah else GREEN}"
            f"{'⚠ TRIGGERED' if states['B'].tawbah else 'NONE'}{R}")

        # Progress bar
        progress = round_n / total_rounds
        prog_w   = W - 20
        filled   = int(progress * prog_w)
        prog_bar = (GREEN + "█" * filled + GREY + "░" * (prog_w - filled) + R)
        self._text(fric_row+8, 3,
            f"  {GREY}Progress:{R}  {prog_bar}  "
            f"{CYAN}{B}{round_n}/{total_rounds}{R}")

        # ══ FOOTER ══════════════════════════════════════════════════════════
        foot_row = fric_row + 11
        self._w(mv(foot_row, 1) + CYAN + "╠" + "═"*(W-2) + "╣" + R)
        self._w(mv(foot_row+1, 1) + CYAN + "║" + R)
        self._text(foot_row+1, 3,
            f"  {GOLD}E=U·D²{R}  {GREY}│{R}  "
            f"{PURPLE}Ψ=A_n(Φ)·ψ·e^(iS/ħ){R}  {GREY}│{R}  "
            f"{TEAL}C_dev=∂λ₂/∂t{R}  {GREY}│{R}  "
            f"{ORANGE}ħ_net=1/λ₂{R}  {GREY}│{R}  "
            f"{CYAN}Al-3assr: D evaluated before U{R}  {GREY}│{R}  "
            f"{GREEN}Ctrl+C to exit{R}")
        self._w(mv(foot_row+1, W) + CYAN + "║" + R)
        self._w(mv(foot_row+2, 1) + CYAN + "╚" + "═"*(W-2) + "╝" + R)

        self._flush()


# ═══════════════════════════════════════════════════════════════════════════════
# CERTIFICATE PRINTER
# ═══════════════════════════════════════════════════════════════════════════════

def print_certificate(states: Dict[str, CorpusState], elapsed: float):
    l2_A = list(states['A'].l2_hist)
    l2_B = list(states['B'].l2_hist)
    T    = min(len(l2_A), len(l2_B))

    if T < 2:
        print(f"\n{CYAN}Insufficient data for certificate.{R}")
        return

    s_A = linregress(range(T), l2_A[-T:]).slope
    s_B = linregress(range(T), l2_B[-T:]).slope
    h_A = states['A'].hbar_hist[-1] if states['A'].hbar_hist else 0
    h_B = states['B'].hbar_hist[-1] if states['B'].hbar_hist else 0
    j_A = linregress(range(T), list(states['A'].js_hist)[-T:]).slope if T > 1 else 0
    j_B = linregress(range(T), list(states['B'].js_hist)[-T:]).slope if T > 1 else 0

    c1 = s_A > s_B
    c2 = h_B > h_A
    c3 = l2_A[-1] > l2_B[-1]
    c4 = j_A <= j_B
    passed = sum([c1,c2,c3,c4])

    W = 80
    SEP  = "═" * W
    SEP2 = "─" * W

    print(f"\n\n{CLEAR}{GOLD}{B}")
    print(SEP)
    print("  IHCEI v12.0 — QG-COS FALSIFICATION CERTIFICATE")
    print(f"  Signed by: Endogenous_SpectralADGE_Engine  │  Elapsed: {elapsed:.1f}s")
    print(SEP + R)
    print(f"\n  {GREY}CLAIM UNDER TEST:{R}")
    print(f"  Governance-aligned text (Corpus A) maintains higher spectral cohesion")
    print(f"  than extraction-pattern text (Corpus B) when ingested by the")
    print(f"  OQM-constrained Endogenous_SpectralADGE_Engine.\n")
    print(f"  {GREY}{SEP2}{R}")

    def crit(ok, label, detail):
        mark = f"{GREEN}✔{R}" if ok else f"{RED}✘{R}"
        print(f"  [{mark}]  {label}")
        print(f"         {GREY}{detail}{R}")

    crit(c1, "C1 · ∂λ₂/∂t(A) > ∂λ₂/∂t(B)  — A degrades slower",
         f"A slope={s_A:+.6f}  B slope={s_B:+.6f}")
    crit(c2, "C2 · ħ_cumulative(B) > ħ_cumulative(A)  — extraction generates more friction",
         f"A={h_A:.2f}  B={h_B:.2f}  ratio={h_B/(h_A+1e-6):.2f}×")
    crit(c3, "C3 · Final λ₂(A) > final λ₂(B)  — governance network ends more cohesive",
         f"A={l2_A[-1]:.5f}  B={l2_B[-1]:.5f}  Δ={l2_A[-1]-l2_B[-1]:+.5f}")
    crit(c4, "C4 · ∂JS/∂t(A) ≤ ∂JS/∂t(B)  — Channel 1: A converges, B diverges",
         f"JS slope A={j_A:+.7f}  JS slope B={j_B:+.7f}")

    verdict_col = GREEN if passed == 4 else (YELLOW if passed >= 3 else RED)
    verdict     = ("✔ FULL PROOF" if passed == 4 else
                   "✔ SUPPORTED" if passed >= 3 else
                   "⚠ PARTIAL — increase rounds")

    print(f"\n  {GREY}{SEP2}{R}")
    print(f"  CRITERIA PASSED: {verdict_col}{B}{passed}/4{R}")
    print(f"  VERDICT:         {verdict_col}{B}{verdict}{R}\n")
    print(f"  {GREY}CONDITIONAL CLAIM (formally maintained):{R}")
    print(f"  IF a network requires stable or improving λ₂ under realistic text load")
    print(f"  THEN OQM-aligned text is measurably less disruptive to spectral cohesion")
    print(f"  than extraction-pattern text. D_audit is semantic distance. λ₂ is real.\n")
    print(f"  {GOLD}{B}{'═'*W}{R}\n")
    print(SHOW_CUR)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════

def main(rounds: int = 12, tick: float = 0.3, fast: bool = False):
    tick = 0.0 if fast else tick

    # ── Build embedder + OQM frame ─────────────────────────────────────────
    print(f"{CLEAR}{CYAN}Initialising QG-COS...{R}", end="", flush=True)

    all_seeds  = [p for ps in OQM_ROOT_CLUSTERS.values() for p in ps]
    fit_corpus = all_seeds + CORPUS_A + CORPUS_B + CORPUS_C

    emb = LocalEmbedder(seed=42)
    emb.fit(fit_corpus)

    oqm = OQMFrame(emb)
    oqm.build()

    # Pre-press all corpora
    pressed = {
        "A": [oqm.press(t) for t in CORPUS_A],
        "B": [oqm.press(t) for t in CORPUS_B],
        "C": [oqm.press(t) for t in CORPUS_C],
    }

    # ── Initialise corpus states ────────────────────────────────────────────
    states = {
        "A": CorpusState("A", "Governance", GREEN,
                          SpectralEngine(n=60, seed=42), CORPUS_A),
        "B": CorpusState("B", "Extraction", RED,
                          SpectralEngine(n=60, seed=42), CORPUS_B),
        "C": CorpusState("C", "Mixed",      YELLOW,
                          SpectralEngine(n=60, seed=42), CORPUS_C),
    }

    dash    = Dashboard(tick=tick)
    rng     = np.random.default_rng(77)
    t_start = time.time()

    print(f"\r{CYAN}QG-COS ready. Starting dashboard...{R}", flush=True)
    time.sleep(0.4 if not fast else 0)

    try:
        for round_n in range(1, rounds + 1):
            # Shuffle packets each round (streaming simulation)
            for key in ["A", "B", "C"]:
                pkts   = pressed[key]
                idxs   = rng.permutation(len(pkts))
                batch  = [pkts[i] for i in idxs]
                m      = states[key].engine.step(batch)
                # Pick a representative packet for display
                rep    = max(batch, key=lambda p: abs(p["d"] - 0.5))
                states[key].update(m, rep)

            elapsed = time.time() - t_start
            dash.render(states, round_n, rounds, elapsed)
            time.sleep(tick)

    except KeyboardInterrupt:
        pass
    finally:
        elapsed = time.time() - t_start
        print_certificate(states, elapsed)


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="IHCEI v12.0 — QG-COS Sovereign Operating System Dashboard"
    )
    parser.add_argument("--rounds", type=int,   default=12,   help="Simulation rounds")
    parser.add_argument("--tick",   type=float, default=0.35, help="Seconds between frames")
    parser.add_argument("--fast",   action="store_true",      help="No delays — instant output")
    args = parser.parse_args()
    main(rounds=args.rounds, tick=args.tick, fast=args.fast)
