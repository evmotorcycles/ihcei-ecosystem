// helm-core-v2.mjs — HELM v2. Density-weighted evidence.
// ============================================================================
// WHY THIS EXISTS, AND WHAT IT IS *NOT* BASED ON.
//
// The DES run (spec 25c7dffc) measured HELM v1 at G = 0.1612 and 8 distinct
// verdicts across 96 evaluations — and then its own DCM self-audit VOIDED the
// run. Those numbers are therefore NOT licensed conclusions and this file does
// not rest on them.
//
// It rests on two facts visible by reading v1's source, independent of any run:
//
//   1. `count()` returns an INTEGER and `eff = Math.min(hits, cap)` keeps it an
//      integer, so the LLR sum lands on a small lattice and the posterior mean
//      inherits that lattice. The output grid is coarse BY CONSTRUCTION.
//   2. v1 computes `words` but uses it only for the methodology term `T`. Every
//      pressure and mechanism term ignores text length, so one urgency clause
//      weighs the same in a 12-word message as in a 400-word document.
//
// (2) is the defect; (1) is a consequence of it. The fix is the standard
// correction any evidence-accumulation system needs: weight evidence by
// DENSITY, saturating smoothly rather than clipping at an integer cap.
//
//      eff = cap * (1 - exp(-hits / (words * RATE)))
//
// RATE = 0.05 is chosen on principle and declared BEFORE measurement: one hit
// per 20 words is one time-constant, so a text at that density carries ~63% of
// the gate's cap. It is not fitted to any threshold.
//
// WHAT IS DELIBERATELY UNCHANGED: the gate set, every regex, every LLR prior,
// the corroboration gate, the band thresholds, the epistemic floor and the
// seed. v2 must not buy responsiveness by loosening the shield, so the shield
// surface is left exactly as it was. v1 is untouched and still ships.

import { clip, extractEvidence, band } from "./helm-core.mjs";

const RATE = 0.05;                       // one hit per 20 words = one time-constant
const EPS = 0.01;
const logit = p => { p = clip(p); return Math.log(p / (1 - p)); };
const sigmoid = x => clip(1 / (1 + Math.exp(-x)));

// Same priors as v1. Copied rather than imported because v1 does not export them;
// any divergence here would be a silent change to the shield surface.
const GATES = {
  1: { name: "Adornments", llr: 0.45, sd: 0.25, perHit: true, cap: 3 },
  2: { name: "Groupthink", llr: 0.80, sd: 0.30, perHit: true, cap: 3 },
  3: { name: "Methodology Opacity", llr: 2.10, sd: 0.55, perHit: false, cap: 1 },
  4: { name: "Verification Bypass", llr: 1.60, sd: 0.40, perHit: true, cap: 2 },
  5: { name: "Unverifiable Authority", llr: 1.20, sd: 0.35, perHit: true, cap: 2 },
  6: { name: "Distraction", llr: 0.70, sd: 0.30, perHit: true, cap: 2 },
  7: { name: "Benevolent Tyranny", llr: 2.10, sd: 0.55, perHit: false, cap: 1 },
};
const EXTRA = {
  urgency: { llr: 1.10, sd: 0.35, cap: 3, pressure: true },
  fear: { llr: 1.00, sd: 0.35, cap: 2, pressure: true },
  imperatives: { llr: 0.45, sd: 0.20, cap: 4, pressure: true },
  options: { llr: -0.55, sd: 0.20, cap: 4 },
  methodology: { llr: -0.50, sd: 0.20, cap: 5 },
  secrecy: { llr: 1.70, sd: 0.45, cap: 2 },
  payment: { llr: 1.50, sd: 0.45, cap: 2 },
  impersonation: { llr: 1.30, sd: 0.40, cap: 2 },
  scarcity: { llr: 1.10, sd: 0.40, cap: 2 },
};

function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a |= 0; a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
function gauss(r) {
  let u = 0, v = 0;
  while (!u) u = r(); while (!v) v = r();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}

// THE ONE CHANGE. Continuous, saturating, monotone in hits, decreasing in length.
// At hits = 0 it returns exactly 0, so a text with no evidence is unchanged from v1.
export function densityEff(hits, cap, words) {
  if (hits <= 0) return 0;
  return cap * (1 - Math.exp(-hits / Math.max(words * RATE, 1e-9)));
}

function mechanismPresent(ev) {
  return (ev.hits[2] > 0) || (ev.hits[4] > 0) || (ev.hits[5] > 0) ||
    (ev.secrecy > 0) || (ev.payment > 0) || (ev.impersonation > 0) || (ev.scarcity > 0);
}

export function posteriorV2(ev, words, { priorP = 0.10, nMc = 3000, seed = 7,
                                         corroborationGate = true } = {}) {
  const mech = mechanismPresent(ev);
  const disc = (corroborationGate && !mech) ? 0.15 : 1.0;
  const terms = [], evidence = [];

  for (const [gid, g] of Object.entries(GATES)) {
    const id = Number(gid); let contrib = 0, sd = 0;
    const hits = ev.hits[id] || 0;
    if (id === 3) { contrib = g.llr * ev.g3s * disc; sd = g.sd * Math.max(ev.g3s, 0.2); }
    else if (id === 7) {
      const on = ev.g7s > 0.30;
      contrib = on ? g.llr * ev.g7s * disc : 0; sd = on ? g.sd * Math.max(ev.g7s, 0.2) : 0;
    } else {
      const eff = g.perHit ? densityEff(hits, g.cap, words) : (hits ? 1 : 0);
      contrib = g.llr * eff; sd = eff ? g.sd * Math.sqrt(eff) : 0;
    }
    if (contrib !== 0) {
      terms.push([contrib, sd]);
      evidence.push({ gate: g.name, hits, llr: +contrib.toFixed(4) });
    }
  }
  const extras = [["urgency", ev.urg], ["fear", ev.fear], ["imperatives", ev.imp],
                  ["options", ev.opt], ["methodology", ev.meth], ["secrecy", ev.secrecy],
                  ["payment", ev.payment], ["impersonation", ev.impersonation],
                  ["scarcity", ev.scarcity]];
  for (const [k, c] of extras) {
    const s = EXTRA[k];
    const eff = densityEff(c, s.cap, words);
    if (eff > 0) {
      const scale = s.llr > 0 ? eff : Math.sqrt(eff);
      let m = s.llr * scale;
      if (s.pressure) m *= disc;
      terms.push([m, s.sd * Math.sqrt(eff)]);
      evidence.push({ gate: k, hits: c, llr: +m.toFixed(4) });
    }
  }
  const r = rng(seed), lo0 = logit(priorP), draws = new Array(nMc);
  for (let i = 0; i < nMc; i++) {
    let s = lo0;
    for (const [m, sd] of terms) s += m + sd * gauss(r);
    draws[i] = sigmoid(s);
  }
  draws.sort((a, b) => a - b);
  const mean = clip(draws.reduce((a, b) => a + b, 0) / nMc);
  return { mean, ci: [clip(draws[Math.floor(0.025 * nMc)]),
                      clip(draws[Math.floor(0.975 * nMc)])],
           evidence, mechanismPresent: mech };
}

export function auditV2(text, opts = {}) {
  const words = Math.max(text.split(/\s+/).length, 1);
  const ev = extractEvidence(text);
  const { mean, ci, evidence, mechanismPresent: mp } = posteriorV2(ev, words, opts);
  const b = band(mean, ci, opts);
  return { ...b, p_manipulative: +mean.toFixed(6), ci95: [+ci[0].toFixed(4), +ci[1].toFixed(4)],
           mechanismPresent: mp, evidence, words, engine: "helm-density-v2", rate: RATE };
}
