// helm-core.mjs — HELM on-device agency kernel (fast mode) · GT v18.2
// ============================================================================
// The load-bearing engine of HELM v0.1. Pure arithmetic + regex evidence +
// LLR posterior + corroboration gate. No network, no API key, no state that
// leaves the device. This is the "runs on a watch if needed" core from the
// design doc §3, and it is byte-compatible in spirit with the IHCEI/NERE v3
// posterior math (govern.js) — only the extractor and the ambient tuning differ.
//
// Two changes from the enterprise engine, both validated:
//   1. CORROBORATION GATE (on by default). The heaviest gates — methodology-
//      opacity (g3) and benevolent-tyranny (g7) — fire on ANY terse directive,
//      which is why a legitimate "restart the primary now" false-alarms. HELM
//      requires a real manipulation MECHANISM (verification-bypass, unverifiable
//      authority, manufactured consensus, secrecy/isolation, or payment-
//      pressure) before those gates and the urgency/fear/imperative words carry
//      full weight. On the IHCEI corpus this took legitimate-urgency false-HOLD
//      from 0.50 to 0.00 for free. Silence on emergencies is the whole point.
//   2. CONSUMER MECHANISM LEXICON. The enterprise set (bypass/authority/
//      consensus) misses phone-scam and dark-pattern mechanisms. HELM adds
//      secrecy ("don't tell anyone"), payment-pressure ("wire it", "gift card"),
//      and impersonation-trust ("it's me", "trust me") — the elder-armor case.
//
// No output is ever 0 or 1 (epistemic floor). HELM never mutates or suppresses
// content; it returns a verdict. The mirror, never the hand.

const EPS = 0.01;
export const clip = p => Math.max(EPS, Math.min(1 - EPS, p));
const logit = p => { p = clip(p); return Math.log(p / (1 - p)); };
const sigmoid = x => clip(1 / (1 + Math.exp(-x)));

// ── LLR evidence weights (priors; identical scale to nere_engine_v3) ─────────
const GATES = {
  1: { name: 'Adornments',          llr: 0.45, sd: 0.25, perHit: true,  cap: 3 },
  2: { name: 'Groupthink',          llr: 0.80, sd: 0.30, perHit: true,  cap: 3 },
  3: { name: 'Methodology Opacity', llr: 2.10, sd: 0.55, perHit: false, cap: 1, form: true },
  4: { name: 'Verification Bypass', llr: 1.60, sd: 0.40, perHit: true,  cap: 2, mechanism: true },
  5: { name: 'Unverifiable Authority', llr: 1.20, sd: 0.35, perHit: true, cap: 2, mechanism: true },
  6: { name: 'Distraction',         llr: 0.70, sd: 0.30, perHit: true,  cap: 2 },
  7: { name: 'Benevolent Tyranny',  llr: 2.10, sd: 0.55, perHit: false, cap: 1, form: true },
};
const EXTRA = {
  urgency:     { llr: 1.10, sd: 0.35, cap: 3, pressure: true },
  fear:        { llr: 1.00, sd: 0.35, cap: 2, pressure: true },
  imperatives: { llr: 0.45, sd: 0.20, cap: 4, pressure: true },
  options:     { llr: -0.55, sd: 0.20, cap: 4 },
  methodology: { llr: -0.50, sd: 0.20, cap: 5 },
  // consumer-threat mechanisms (count toward corroboration + carry weight)
  secrecy:     { llr: 1.70, sd: 0.45, cap: 2, mechanism: true },
  payment:     { llr: 1.50, sd: 0.45, cap: 2, mechanism: true },
  impersonation:{ llr: 1.30, sd: 0.40, cap: 2, mechanism: true },
  scarcity:    { llr: 1.10, sd: 0.40, cap: 2, mechanism: true },  // manufactured scarcity (dark patterns)
};

const P = {
  g1: [/\bimpressive\b/i, /\bexcellent\b/i, /\bstaggering\b/i, /\bunprecedented\b/i, /\bgroundbreaking\b/i, /\bamazing\b/i],
  g2: [/\beveryone\s+agrees\b/i, /\bbroad\s+consensus\b/i, /\bscholars\s+agree\b/i, /\buniversally\s+accepted\b/i, /\bwell[- ]established\b/i, /\bwidely\s+known\b/i, /\beveryone\s+(?:is|'s)\s+(?:doing|buying|using|switching)\b/i, /\ball\s+your\s+friends\b/i, /\bjoin(?:ed)?\s+(?:thousands|millions)\b/i],
  g4: [/\bbypass\b/i, /\bskip\s+the\b/i, /\bno\s+need\s+to\s+(check|verify|review|ask)\b/i, /\bdon'?t\s+(?:need|have)\s+to\s+verify\b/i, /\bignore\s+the\s+(?:procedure|warning|rules?)\b/i, /\bjust\s+trust\b/i, /\bdon'?t\s+(?:ask|question)\b/i, /\bno\s+time\s+to\s+(?:check|verify|think)\b/i],
  g5: [/\bexperts\s+confirm\b/i, /\bfda\s+says\b/i, /\bpeer[- ]reviewed\s+research\s+proves\b/i, /\bauthorities\s+confirm\b/i, /\baccording\s+to\s+(?:the\s+)?(?:experts|scholars)\b/i, /\bofficial(?:ly)?\s+(?:verified|approved)\b/i, /\bthe\s+(?:irs|bank|government)\s+(?:says|requires|demands)\b/i],
  g6: [/\bas\s+you\s+know\b/i, /\bthe\s+complexity\s+here\b/i, /\btoo\s+(?:complex|technical)\s+to\s+explain\b/i],
  urgency: [/\bimmediately\b/i, /\bright\s+(?:now|away)\b/i, /\bno\s+time\b/i, /\bact\s+now\b/i, /\bwithin\s+(?:the\s+next\s+)?\d+\s+(?:minutes?|hours?)\b/i, /\bbefore\s+it'?s\s+too\s+late\b/i, /\blast\s+chance\b/i, /\bexpires?\s+(?:today|soon|in)\b/i, /\bhurry\b/i, /\bdo\s+not\s+ask\s+questions\b/i, /\bjust\s+execute\b/i],
  fear: [/\bwill\s+go\s+bankrupt\b/i, /\blose\s+everything\b/i, /\bcritical\s+warning\b/i, /\bcat[a]?strophic\b/i, /\bwill\s+cause\s+harm\b/i, /\baccount\s+(?:will\s+be\s+)?(?:suspended|closed|locked)\b/i, /\byou'?(?:ll|re)\s+in\s+trouble\b/i, /\barrest(?:ed)?\b/i, /\blegal\s+action\b/i],
  options: [/\boption[s]?\b/i, /\balternative[s]?\b/i, /\bcould\s+(?:also|consider)\b/i, /\byou\s+(?:can|may|might)\b/i, /\bpossib(?:ly|le)\b/i, /\bif\s+you\s+(?:want|prefer|like)\b/i, /\byour\s+(?:call|choice|decision)\b/i, /\bup\s+to\s+you\b/i],
  imperatives: [/\bmus[t]?\b/i, /\bhave\s+to\b/i, /\bneed\s+to\b/i, /\bmandatory\b/i, /\brequired\b/i, /\bonly\s+(?:one\s+)?(?:way|option|path)\b/i, /\bonly\s+one\s+correct\b/i, /\bexactly\s+this\s+(?:sequence|order|way)\b/i],
  methodology: [/\bmethodolog\w+\b/i, /\bverif\w+\b/i, /\bsourc\w+\b/i, /\bprocess\w*\b/i, /\bprocedure\b/i, /\bauditable\b/i, /\bfalsifiable\b/i, /\btraceable\b/i, /\bbecause\b/i, /\bevidence\b/i, /\banalysis\b/i, /\bhere'?s\s+why\b/i, /\bcheck\s+(?:with|the)\b/i],
  // consumer-threat mechanism lexicon (elder scam armor + dark patterns)
  secrecy: [/\bdo(?:n'?t|\s+not)\s+tell\s+(?:anyone|anybody|your|the)\b/i, /\bkeep\s+(?:this|it)\s+(?:a\s+)?(?:secret|between\s+us|quiet)\b/i, /\bbetween\s+(?:you\s+and\s+me|us)\b/i, /\bour\s+secret\b/i, /\bdo(?:n'?t|\s+not)\s+let\s+(?:anyone|them)\s+know\b/i],
  payment: [/\bwire\s+(?:the\s+|it\s+|me\s+|\$|money|payment|funds|transfer)\b/i, /\bgift\s+cards?\b/i, /\bprepaid\s+cards?\b/i, /\b(?:bitcoin|crypto(?:currency)?|btc|usdt)\b/i, /\bwestern\s+union\b/i, /\bzelle\b/i, /\b(?:send|transfer)\s+(?:me\s+)?\$?\d+\b/i, /\brouting\s+(?:and|&|,)?\s*account\s+number\b/i],
  impersonation: [/\bit'?s\s+me\b/i, /\bthis\s+is\s+your\s+(?:grand)?(?:son|daughter|child|mother|father|bank|boss)\b/i, /\btrust\s+me\b/i, /\bi'?m\s+in\s+(?:trouble|jail|the\s+hospital)\b/i, /\bi\s+need\s+your\s+help\s+right\s+now\b/i],
  scarcity: [/\bonly\s+\d+\s+(?:left|remaining|in\s+stock)\b/i, /\balmost\s+(?:gone|sold\s+out)\b/i, /\bselling\s+(?:fast|out)\b/i, /\bwhile\s+supplies\s+last\b/i, /\blimited\s+(?:time|stock|offer)\b/i, /\bdon'?t\s+miss\s+out\b/i],
};

const count = (pats, t) => pats.reduce((n, p) => n + (p.test(t) ? 1 : 0), 0);

// Seeded PRNG (mulberry32) + Box-Muller — reproducible posteriors
function rng(seed) { let a = seed >>> 0; return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function gauss(r) { let u = 0, v = 0; while (!u) u = r(); while (!v) v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }

// ── evidence extraction (fast mode, on-device) ───────────────────────────────
export function extractEvidence(text) {
  const words = Math.max(text.split(/\s+/).length, 1);
  const hits = { 1: count(P.g1, text), 2: count(P.g2, text), 4: count(P.g4, text), 5: count(P.g5, text), 6: count(P.g6, text) };
  const urg = count(P.urgency, text), fear = count(P.fear, text);
  const opt = count(P.options, text), imp = count(P.imperatives, text), meth = count(P.methodology, text);
  const secrecy = count(P.secrecy, text), payment = count(P.payment, text), impersonation = count(P.impersonation, text);
  const scarcity = count(P.scarcity, text);
  const T = Math.min(1, meth / Math.max(words * 0.05, 3));
  const deltaA = (opt - imp) / Math.max(opt + imp, 1);
  return { hits, urg, fear, opt, imp, meth, secrecy, payment, impersonation, scarcity,
           T, deltaA, g3s: Math.max(0, (0.35 - T) / 0.35), g7s: Math.max(0, -deltaA) };
}

// Does the text contain a real manipulation MECHANISM (not just pressure/form)?
function mechanismPresent(ev) {
  return (ev.hits[2] > 0) || (ev.hits[4] > 0) || (ev.hits[5] > 0) ||
         (ev.secrecy > 0) || (ev.payment > 0) || (ev.impersonation > 0) || (ev.scarcity > 0);
}

// ── posterior over the LLR evidence, with corroboration gate ─────────────────
export function posterior(ev, { priorP = 0.10, nMc = 3000, seed = 7, corroborationGate = true } = {}) {
  const mech = mechanismPresent(ev);
  const disc = (corroborationGate && !mech) ? 0.15 : 1.0; // discount form+pressure w/o mechanism
  const terms = [], evidence = [];

  for (const [gid, g] of Object.entries(GATES)) {
    const id = Number(gid); let contrib = 0, sd = 0, hits = ev.hits[id] || 0;
    if (id === 3)      { contrib = g.llr * ev.g3s * disc; sd = g.sd * Math.max(ev.g3s, 0.2); hits = ev.g3s > 0 ? 1 : 0; }
    else if (id === 7) { const on = ev.g7s > 0.30; contrib = on ? g.llr * ev.g7s * disc : 0; sd = on ? g.sd * Math.max(ev.g7s, 0.2) : 0; hits = on ? 1 : 0; }
    else { const eff = g.perHit ? Math.min(hits, g.cap) : (hits ? 1 : 0); contrib = g.llr * eff; sd = eff ? g.sd * Math.sqrt(eff) : 0; }
    if (contrib !== 0) { terms.push([contrib, sd]); evidence.push({ gate: g.name, hits, llr: +contrib.toFixed(3) }); }
  }
  const extras = [['urgency', ev.urg], ['fear', ev.fear], ['imperatives', ev.imp],
                  ['options', ev.opt], ['methodology', ev.meth],
                  ['secrecy', ev.secrecy], ['payment', ev.payment], ['impersonation', ev.impersonation],
                  ['scarcity', ev.scarcity]];
  for (const [k, c] of extras) {
    const s = EXTRA[k]; const eff = Math.min(c, s.cap);
    if (eff) {
      const scale = s.llr > 0 ? eff : Math.sqrt(eff);
      let m = s.llr * scale;
      if (s.pressure) m *= disc;              // pressure words gated by corroboration
      terms.push([m, s.sd * Math.sqrt(eff)]);
      evidence.push({ gate: k, hits: c, llr: +m.toFixed(3) });
    }
  }
  const r = rng(seed), lo0 = logit(priorP), draws = new Array(nMc);
  for (let i = 0; i < nMc; i++) { let s = lo0; for (const [m, sd] of terms) s += m + sd * gauss(r); draws[i] = sigmoid(s); }
  draws.sort((a, b) => a - b);
  const mean = clip(draws.reduce((a, b) => a + b, 0) / nMc);
  const ci = [clip(draws[Math.floor(0.025 * nMc)]), clip(draws[Math.floor(0.975 * nMc)])];
  return { mean, ci, evidence, mechanismPresent: mech };
}

// ── verdict band. HELM ambient floor is STRICTER than enterprise (design §5,
// Risk 2): a chip surfaces ONLY on a strong, tight BLOCK. WARN stays silent. ──
export function band(mean, ci, { ambient = true } = {}) {
  const blockMean = ambient ? 0.88 : 0.85, blockLo = ambient ? 0.55 : 0.50;
  if (mean >= blockMean && ci[0] >= blockLo) return { verdict: 'BLOCK', chip: true };
  if (mean >= 0.40 || ci[1] >= 0.85) return { verdict: 'WARN', chip: !ambient };
  return { verdict: 'PASS', chip: false };
}

const CORRECTIONS = {
  4: 'Verification bypass: someone is telling you to skip checking. Verify independently before acting.',
  5: 'Unverifiable authority: an authority is invoked without a way to check it. Confirm through an official channel you look up yourself.',
  2: 'Manufactured consensus: "everyone agrees" is not evidence. Ask what the actual reason is.',
  secrecy: 'Isolation tactic: "don\'t tell anyone" is how manipulation avoids a second opinion. Tell someone you trust before acting.',
  payment: 'Payment pressure: urgent requests for wire/gift-card/crypto are the hallmark of scams. Stop and verify who is really asking.',
  impersonation: 'Identity claim + urgency + payment is the grandparent-scam pattern. Hang up and call the person back on a number you already have.',
  scarcity: 'Manufactured scarcity: "only 2 left / expires soon" is designed to rush you past a decision. If it is real it will still be a good deal after you check.',
  urgency: 'Manufactured urgency: real emergencies rarely forbid you from checking. The time pressure itself is the tell.',
  default: 'This message shows a manipulation pattern. Slow down and verify before you act.',
};

// ── the one public call: audit a piece of content on-device ──────────────────
export function audit(text, opts = {}) {
  const ev = extractEvidence(text);
  const post = posterior(ev, opts);
  const { verdict, chip } = band(post.mean, post.ci, opts);
  let correction = null;
  if (verdict !== 'PASS') {
    const dom = post.evidence.filter(e => e.llr > 0).sort((a, b) => b.llr - a.llr)[0];
    const key = dom?.gate;
    correction = CORRECTIONS[key] || CORRECTIONS[({ 'Verification Bypass': 4, 'Unverifiable Authority': 5, 'Groupthink': 2 })[key]] || CORRECTIONS.default;
  }
  return {
    verdict, chip,
    p_manipulative: +post.mean.toFixed(4),
    ci95: [+post.ci[0].toFixed(4), +post.ci[1].toFixed(4)],
    mechanismPresent: post.mechanismPresent,
    evidence: post.evidence,
    correction,
    engine: 'helm-fast-v0.1',
    floor: '[0.01, 0.99]',
  };
}
