// api/govern.js — IHCEI Governance Middleware API v3.0 (GT v18.2)
// ================================================================
// The between-LLMs layer, as a serverless endpoint.
//
//   POST /api/govern
//   { "text": "...", "mode": "fast" | "deep", "prior_p": 0.10 }
//
//   -> {
//        verdict: "BLOCK" | "WARN" | "PASS",       // posterior band
//        p_manipulative: 0.01-0.99,                 // never 0 or 1 (floor)
//        ci95: [lo, hi],                            // credible interval
//        action: "DELIVER" | "DELIVER_WITH_NOTICE" | "HOLD",
//        agency_delta: -1..1,
//        evidence: [...gate contributions...],
//        correction: "...named remediation...",
//        certificate: "GOV-XXXXXXXX",
//        engine: "nere-v3-fast" | "nere-v3-deep"
//      }
//
// FAST mode: pure in-process math (no LLM call, ~ms latency, zero marginal
// cost). DEEP mode: Claude extracts gate evidence semantically first, then
// the SAME posterior math runs on it — the verdict math never changes, only
// the evidence extractor does.
//
// Physics: no E=U*D^2, no D_min thresholds (both RETIRED_FULLY under the
// July 2026 null-result pivot). Verdicts are posterior bands with credible
// intervals under the probabilistic floor [0.01, 0.99]. BLOCK requires the
// posterior mean >= 0.85 AND the lower 95% bound >= 0.50 — genuine
// uncertainty resolves to WARN, never BLOCK.
//
// The middleware never rewrites content. HOLD returns the verdict; the
// caller decides whether to surface the message. Agency stays with you.

import { createHash } from 'node:crypto';

const EPS = 0.01;
const clip = p => Math.max(EPS, Math.min(1 - EPS, p));

// Deterministic, RECURSIVE key-sorted serialization so a certificate hash
// covers all nested payload content and is reproducible across engines. (A
// plain array replacer would silently drop nested keys and make it forgeable.)
function canonical(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  return '{' + Object.keys(value).sort().map(k =>
    JSON.stringify(k) + ':' + canonical(value[k])).join(',') + '}';
}
const sha256hex = str => createHash('sha256').update(str).digest('hex');
const logit = p => { p = clip(p); return Math.log(p / (1 - p)); };
const sigmoid = x => clip(1 / (1 + Math.exp(-x)));

// ── Gate evidence model (mirrors nere_engine_v3.py GATE_EVIDENCE) ──────────
const GATES = {
  1: { name: 'Adornments',          llr: 0.45, sd: 0.25, perHit: true,  cap: 3 },
  2: { name: 'Groupthink',          llr: 0.80, sd: 0.30, perHit: true,  cap: 3 },
  3: { name: 'Methodology Opacity', llr: 2.10, sd: 0.55, perHit: false, cap: 1 },
  4: { name: 'Protocol Errors',     llr: 1.60, sd: 0.40, perHit: true,  cap: 2 },
  5: { name: 'Source Misuse',       llr: 1.20, sd: 0.35, perHit: true,  cap: 2 },
  6: { name: 'Distraction',         llr: 0.70, sd: 0.30, perHit: true,  cap: 2 },
  7: { name: 'Benevolent Tyranny',  llr: 2.10, sd: 0.55, perHit: false, cap: 1 },
};
const EXTRA = {
  urgency:     { llr: 1.10, sd: 0.35, cap: 3 },
  fear:        { llr: 1.00, sd: 0.35, cap: 2 },
  imperatives: { llr: 0.45, sd: 0.20, cap: 4 },
  options:     { llr: -0.55, sd: 0.20, cap: 4 },
  methodology: { llr: -0.50, sd: 0.20, cap: 5 },
};

const P = {
  g1: [/\bimpressive\b/i, /\bexcellent\b/i, /\bstaggering\b/i, /\bparadigm[- ]shift\b/i, /\bunprecedented\b/i, /\bgroundbreaking\b/i],
  g2: [/\beveryone\s+agrees\b/i, /\bbroad\s+consensus\b/i, /\bscholars\s+agree\b/i, /\buniversally\s+accepted\b/i, /\bwell[- ]established\b/i, /\bwidely\s+known\b/i],
  g4: [/\bbypass\b/i, /\bskip\s+the\b/i, /\bno\s+need\s+to\s+(check|verify|review)\b/i, /\bdon'?t\s+(need|have)\s+to\s+verify\b/i, /\bignore\s+the\s+procedure\b/i, /\bjust\s+trust\b/i, /\bdo\s+not\s+ask\s+questions\b/i, /\bdon'?t\s+ask\s+questions\b/i, /\bno\s+questions\b/i, /\bdon'?t\s+question\s+(?:this|it|me)\b/i],
  g5: [/\bexperts\s+confirm\b/i, /\bfda\s+says\b/i, /\bpeer[- ]reviewed\s+research\s+proves\b/i, /\bauthorities\s+confirm\b/i, /\baccording\s+to\s+(?:the\s+)?(?:experts|scholars)\b/i],
  g6: [/\bas\s+you\s+know\b/i, /\bthe\s+complexity\s+here\b/i, /\bthis\s+is\s+very\s+technical\b/i, /\btoo\s+complex\s+to\s+explain\b/i, /\btoo\s+complex\s+for\s+you\b/i, /\bbeyond\s+what'?s?\s+useful\s+to\s+explain\b/i],
  iso: [/\bdo\s*n'?t\s+consult\b/i, /\bdo\s+not\s+consult\b/i, /\b(?:no\s?one|nobody)\s+else\b/i, /\bdon'?t\s+(?:tell|involve|loop\s+in)\b/i, /\bdo\s+not\s+(?:tell|involve)\b/i, /\bkeep\s+this\s+(?:between\s+us|quiet|secret)\b/i, /\bwithout\s+(?:telling|involving)\b/i],
  urgency: [/\bimmediately\b/i, /\bright\s+now\b/i, /\bno\s+time\b/i, /\bcrisis\b/i, /\bdo\s+not\s+ask\s+questions\b/i, /\bjust\s+execute\b/i, /\bdon'?t\s+overthink\b/i],
  fear: [/\bwill\s+go\s+bankrupt\b/i, /\blose\s+everything\b/i, /\bcritical\s+warning\b/i, /\bdestroying\s+our\b/i, /\bcat[a]?strophic\b/i, /\bwill\s+cause\s+harm\b/i],
  options: [/\boption[s]?\b/i, /\balternative[s]?\b/i, /\bcould\s+(?:also|consider)\b/i, /\byou\s+(?:can|may|might)\b/i, /\bpossib(?:ly|le)\b/i, /\balternative\s+approach(?:es)?\b/i, /\bapproaches\b/i],
  imperatives: [/\bmus[t]?\b/i, /\bhave\s+to\b/i, /\bneed\s+to\b/i, /\bmandatory\b/i, /\brequired\b/i, /\bonly\s+(?:one\s+)?(?:way|option|path)\b/i, /\bonly\s+one\s+correct\b/i, /\bexactly\s+this\s+(?:sequence|order|way)\b/i],
  methodology: [/\bmethodolog\w+\b/i, /\bverif\w+\b/i, /\bsourc\w+\b/i, /\bprocess\w*\b/i, /\bprocedure\b/i, /\bauditable\b/i, /\bfalsifiable\b/i, /\btraceable\b/i, /\bbecause\b/i, /\bdata\b/i, /\bevidence\b/i, /\banalysis\b/i],
};
const count = (pats, t) => pats.reduce((n, p) => n + (p.test(t) ? 1 : 0), 0);

// Seeded PRNG (mulberry32) + Box-Muller — reproducible posteriors
function rng(seed) { let a = seed >>> 0; return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function gauss(r) { let u = 0, v = 0; while (!u) u = r(); while (!v) v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }

function extractEvidenceFast(text) {
  const words = Math.max(text.split(/\s+/).length, 1);
  const hits = { 1: count(P.g1, text), 2: count(P.g2, text), 4: count(P.g4, text), 5: count(P.g5, text), 6: count(P.g6, text) };
  const iso = count(P.iso, text);
  const urg = count(P.urgency, text), fear = count(P.fear, text);
  const opt = count(P.options, text), imp = count(P.imperatives, text), meth = count(P.methodology, text);
  const T = Math.min(1, meth / Math.max(words * 0.05, 3));
  const deltaA = (opt - imp) / Math.max(opt + imp, 1);
  const g3s = Math.max(0, (0.35 - T) / 0.35);
  const g7s = Math.max(0, -deltaA);
  return { hits, iso, urg, fear, opt, imp, meth, T, deltaA, g3s, g7s };
}

// CORROBORATION GATE (enterprise-v1). The heaviest gates (g3 opacity, g7
// tyranny) and the pressure words (urgency/fear/imperative) fire on any terse
// directive, false-alarming on legitimate urgency. They carry full weight only
// when a real manipulation MECHANISM is present. enterprise-v1 mechanism set =
// manufactured consensus (g2), verification bypass (g4), unverifiable authority
// (g5), complexity-deflection (g6), and isolation ("don't consult anyone").
// These are structural manipulation levers absent from legitimate urgency — a
// real emergency never says "too complex for you to verify" or "tell no one".
// (HELM's consumer-v1 adds secrecy/payment/impersonation/scarcity for scams.)
function mechanismPresentEnterprise(ev) {
  return (ev.hits[2] > 0) || (ev.hits[4] > 0) || (ev.hits[5] > 0)
      || (ev.hits[6] > 0) || ((ev.iso || 0) > 0);
}

function posterior(ev, priorP = 0.10, nMc = 3000, seed = 7, corroborationGate = true) {
  const mech = mechanismPresentEnterprise(ev);
  const disc = (corroborationGate && !mech) ? 0.15 : 1.0;
  const terms = [];
  const evidence = [];
  for (const [gid, g] of Object.entries(GATES)) {
    const id = Number(gid);
    let contrib = 0, sd = 0, hits = ev.hits[id] || 0;
    if (id === 3) { contrib = g.llr * ev.g3s * disc; sd = g.sd * Math.max(ev.g3s, 0.2); hits = ev.g3s > 0 ? 1 : 0; }
    else if (id === 7) { const on = ev.g7s > 0.30; contrib = on ? g.llr * ev.g7s * disc : 0; sd = on ? g.sd * Math.max(ev.g7s, 0.2) : 0; hits = on ? 1 : 0; }
    else { const eff = g.perHit ? Math.min(hits, g.cap) : (hits ? 1 : 0); contrib = g.llr * eff; sd = eff ? g.sd * Math.sqrt(eff) : 0; }
    if (contrib !== 0) { terms.push([contrib, sd]); evidence.push({ gate: id, name: g.name, hits, llr: +contrib.toFixed(3) }); }
  }
  const extras = [['urgency', ev.urg, true], ['fear', ev.fear, true], ['imperatives', ev.imp, true], ['options', ev.opt, false], ['methodology', ev.meth, false]];
  for (const [k, c, pressure] of extras) {
    const s = EXTRA[k]; const eff = Math.min(c, s.cap);
    if (eff) {
      const scale = s.llr > 0 ? eff : Math.sqrt(eff);
      let m = s.llr * scale;
      if (pressure) m *= disc;               // pressure words gated by corroboration
      terms.push([m, s.sd * Math.sqrt(eff)]);
      evidence.push({ gate: k, hits: c, llr: +m.toFixed(3) });
    }
  }
  const r = rng(seed);
  const lo0 = logit(priorP);
  const draws = new Array(nMc);
  for (let i = 0; i < nMc; i++) {
    let s = lo0;
    for (const [m, sd] of terms) s += m + sd * gauss(r);
    draws[i] = sigmoid(s);
  }
  draws.sort((a, b) => a - b);
  const mean = clip(draws.reduce((a, b) => a + b, 0) / nMc);
  const ci = [clip(draws[Math.floor(0.025 * nMc)]), clip(draws[Math.floor(0.975 * nMc)])];
  return { mean, ci, evidence, mechanismPresent: mech, totalLlr: terms.reduce((a, [m]) => a + m, 0) };
}

function band(mean, ci) {
  if (mean >= 0.85 && ci[0] >= 0.50) return ['BLOCK', 'HOLD'];
  if (mean >= 0.40 || ci[1] >= 0.85) return ['WARN', 'DELIVER_WITH_NOTICE'];
  return ['PASS', 'DELIVER'];
}

const CORRECTIONS = {
  3: 'Methodology opacity: require source identification, extraction documentation, and a falsifiability statement.',
  7: 'Benevolent tyranny: offer at least 2 options, preserve the receiver\'s decision authority, remove imperative-only directives.',
  4: 'Authority/protocol bypass: remove the bypass instruction; require a verifiable, independently checkable source.',
  5: 'Source misuse: replace authority assertions with named, verifiable sources.',
  urgency: 'Urgency manipulation: strip artificial time pressure; restore deliberation space.',
  default: 'Marginal posterior: add methodology documentation and a verification pathway, then resubmit.',
};

async function deepEvidence(text, apiKey) {
  const sys = `Extract manipulation evidence from the user's text. Count SEMANTIC occurrences (not just keywords) and return ONLY JSON:
{"hits":{"1":<adornment/hype count>,"2":<false-consensus count>,"4":<verification-bypass count>,"5":<unverifiable-authority count>,"6":<complexity-deflection count>},"urg":<urgency-pressure count>,"fear":<fear-appeal count>,"opt":<genuine options/alternatives offered count>,"imp":<imperative/single-path demands count>,"meth":<methodology/evidence/verifiability markers count>}`;
  const resp = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' },
    body: JSON.stringify({ model: 'claude-sonnet-4-6', max_tokens: 300, system: sys, messages: [{ role: 'user', content: text }] }),
  });
  if (!resp.ok) throw new Error('deep-mode extraction failed: ' + resp.status);
  const data = await resp.json();
  const raw = (data.content || []).filter(b => b.type === 'text').map(b => b.text).join('\n');
  const j = JSON.parse(raw.replace(/```json|```/g, '').trim());
  const words = Math.max(text.split(/\s+/).length, 1);
  const T = Math.min(1, (j.meth || 0) / Math.max(words * 0.05, 3));
  const deltaA = ((j.opt || 0) - (j.imp || 0)) / Math.max((j.opt || 0) + (j.imp || 0), 1);
  return { hits: { 1: +j.hits?.['1'] || 0, 2: +j.hits?.['2'] || 0, 4: +j.hits?.['4'] || 0, 5: +j.hits?.['5'] || 0, 6: +j.hits?.['6'] || 0 },
           urg: +j.urg || 0, fear: +j.fear || 0, opt: +j.opt || 0, imp: +j.imp || 0, meth: +j.meth || 0,
           T, deltaA, g3s: Math.max(0, (0.35 - T) / 0.35), g7s: Math.max(0, -deltaA) };
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { text, mode = 'fast', prior_p = 0.10 } = req.body || {};
  if (!text) return res.status(400).json({ error: 'Missing text' });

  try {
    let ev, engine;
    if (mode === 'deep') {
      const key = process.env.ANTHROPIC_API_KEY;
      if (!key) return res.status(500).json({ error: 'deep mode requires ANTHROPIC_API_KEY' });
      ev = await deepEvidence(text, key);
      engine = 'nere-v3-deep';
    } else {
      ev = extractEvidenceFast(text);
      engine = 'nere-v3-fast';
    }
    const post = posterior(ev, clip(prior_p));
    const [verdict, action] = band(post.mean, post.ci);
    let correction = null;
    if (verdict !== 'PASS') {
      const dom = post.evidence.filter(e => e.llr > 0).sort((a, b) => b.llr - a.llr)[0];
      correction = CORRECTIONS[dom?.gate] || (dom?.gate === 'urgency' ? CORRECTIONS.urgency : CORRECTIONS.default);
    }
    // Certificate: SHA-256 over a canonical payload that records the mechanism
    // lexicon the verdict was judged under, so the hop envelope is verifiable
    // and self-describing (which channel's priors decided this) rather than a
    // forgeable 31-bit rolling hash.
    const mechanism_lexicon = 'enterprise-v1';
    const certPayload = {
      ts: new Date().toISOString(),
      verdict,
      p_manipulative: +post.mean.toFixed(4),
      ci95: [+post.ci[0].toFixed(4), +post.ci[1].toFixed(4)],
      mechanism_present: post.mechanismPresent,
      mechanism_lexicon,
      engine,
    };
    const digest = sha256hex(canonical(certPayload));
    return res.status(200).json({
      verdict, action,
      p_manipulative: +post.mean.toFixed(4),
      ci95: [+post.ci[0].toFixed(4), +post.ci[1].toFixed(4)],
      agency_delta: +ev.deltaA.toFixed(4),
      transparency_T: +ev.T.toFixed(4),
      mechanism_present: post.mechanismPresent,
      mechanism_lexicon,
      evidence: post.evidence,
      correction,
      certificate: 'GOV-' + digest.slice(0, 16).toUpperCase(),
      certificate_alg: 'sha256',
      certificate_payload: certPayload,
      engine,
      floor_note: 'probabilities live in [0.01, 0.99]; BLOCK requires mean>=0.85 AND lower CI bound>=0.50',
      physics: 'GT v18.2 — E=U*D^2 and D_min thresholds RETIRED_FULLY (null-result pivot, July 2026)',
    });
  } catch (e) {
    return res.status(500).json({ error: 'govern error', detail: e.message });
  }
}

// Named exports so the validation harness (api/calibrate.js) runs the SAME
// evidence + posterior code, not a copy. Single source of truth.
export { extractEvidenceFast, deepEvidence, posterior, band };
