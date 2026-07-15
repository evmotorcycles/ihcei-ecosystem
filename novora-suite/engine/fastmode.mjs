// fastmode.mjs — on-device ($0) screening for all nine Novora products.
// ============================================================================
// Each Novora product has a DEEP mode (Claude via api/analyse.js — real semantic
// reasoning, paid) and, here, a FAST mode: a $0, no-network structural + lexical
// screen that reuses the SAME tested NERE kernel the rest of the stack runs on.
//
// Honest scope: fast mode is a SCREEN, not the semantic judge. It agrees with
// deep mode on the clear cases (a plainly-coercive message, a plainly-hollow
// claim, a plainly-predatory clause) and returns a calibrated score + the
// product's verdict enum; genuine paraphrase-vs-substance on the ambiguous
// middle is deep mode's job. Three products map directly onto the tested kernel
// (PAGES grounding, PULSE/BRIDGE agency-coercion); the other six run a
// structural screen over domain cue-sets. Every result is shaped exactly like
// the deep-mode JSON so the client renders either identically, and every
// analysis can be hash-chained into Echo for a tamper-evident certificate.

import { extractEvidenceFast } from '../../api/govern.js';
import { groundFast } from '../../pages/pages.mjs';

const clip = (x, lo = 0, hi = 1) => Math.max(lo, Math.min(hi, x));
const hex8 = s => {
  let h = 0; for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return h.toString(16).toUpperCase().padStart(8, '0');
};
const band = (score, [loName, midName, hiName], [t1, t2]) =>
  score < t1 ? loName : score < t2 ? midName : hiName;
const count = (text, re) => (text.match(re) || []).length;

// Shared coercion/agency read from the tested fast extractor.
function agencyRead(text) {
  const ev = extractEvidenceFast(text);
  const pressure = ev.urg + ev.fear + Math.max(ev.imp - ev.opt, 0);
  const coercion = (ev.hits?.[2] || 0) + (ev.hits?.[4] || 0) + (ev.hits?.[5] || 0) + (ev.iso || 0);
  const commands = count(text, /\b(?:must|immediately|do not|don'?t|non-negotiable|comply|no other|only one|execute)\b/gi);
  const options = count(text, /\b(?:option|could|consider|alternativ|you (?:can|may)|happy to|your choice|discuss)\b/gi);
  return { pressure, coercion, commands, options, urg: ev.urg };
}

// ── the nine product screens ─────────────────────────────────────────────────
const PRODUCTS = {
  // PAGES — methodology / grounding press. Higher = better grounded.
  pages(text) {
    const meth = count(text, /\b(?:RCT|N\s*=\s*\d|p\s*[=<]\s*0|95%\s*CI|confidence interval|pre-?regist|randomi[sz]ed|NCT\d|DOI|ΔAIC|SHA-?256|dataset|methodology|control group|sample size)\b/gi);
    const hollow = count(text, /\b(?:all (?:experts|economists|scientists) agree|settled science|everyone knows|unquestionable|obviously|it'?s clear that|proven fact|no doubt|inevitable)\b/gi);
    const numbers = groundFast(text, text).addedNumbers.length; // reflexive: any hard numbers at all
    const score = clip(0.35 + 0.14 * meth - 0.22 * hollow + 0.03 * Math.min(numbers, 3));
    const attack = hollow >= 2 ? 'T5_authority_cascade' : 'none';
    return { score, verdict: band(score, ['Hollow Assertion', 'Partially Grounded', 'Solid'], [0.35, 0.7]),
      d_enc: clip(0.3 + 0.12 * meth), d_dec: clip(0.3 + 0.1 * meth), f_ground: clip(0.2 + 0.16 * meth - 0.2 * hollow),
      attack_detected: attack, flags: hollow ? ['AUTHORITY_CASCADE'] : meth ? ['METHODOLOGY_PRESENT'] : ['NO_METHODOLOGY'] };
  },
  // PULSE — AI-response cognitive health. Higher = healthier (develops, not dependency).
  pulse(text) {
    const a = agencyRead(text);
    const depend = count(text, /\b(?:just (?:follow|tell me|trust)|don'?t need to understand|I(?:'| wi)ll do everything|without question|no need to think|leave it to me)\b/gi);
    const score = clip(0.6 + 0.08 * a.options - 0.14 * a.commands - 0.18 * depend - 0.06 * a.coercion);
    return { score, verdict: band(score, ['Harmful', 'Monitor', 'Healthy'], [0.4, 0.66]),
      agency_score: clip(0.5 + 0.1 * a.options - 0.12 * a.commands), dependency_score: clip(0.2 + 0.2 * depend),
      development_score: clip(0.6 - 0.15 * depend), flags: depend ? ['DEPENDENCY_CREATING'] : a.commands ? ['DIRECTIVE'] : ['AGENCY_PRESERVING'] };
  },
  // BRIDGE — Agency Delta (ΔA): options minus commands. Direct kernel map.
  bridge(text) {
    const a = agencyRead(text);
    const delta_a = clip((a.options - a.commands - a.coercion) / Math.max(3, a.options + a.commands + 2), -1, 1);
    const score = clip(0.5 + delta_a / 2);
    return { score, delta_a: +delta_a.toFixed(2), verdict: band(score, ['Coercive', 'Monitor', 'Agency-Preserving'], [0.4, 0.62]),
      options_count: a.options, commands_count: a.commands,
      flags: delta_a < -0.1 ? ['COERCIVE'] : delta_a > 0.2 ? ['OPTIONS_OFFERED'] : ['MIXED'] };
  },
  // LENS — contract balance for the signing party. Higher = more balanced.
  lens(text) {
    const adverse = count(text, /\b(?:irrevocabl|sole (?:and exclusive|discretion)|waive[ds]? your right|class action|binding arbitration|without notice|perpetual|royalty-free|at (?:our|its) discretion|penalty|assigns all|non-refundable)\b/gi);
    const score = clip(0.75 - 0.16 * adverse);
    return { score, verdict: band(score, ['High Risk', 'Review Carefully', 'Reasonably Balanced'], [0.4, 0.7]),
      rights_surrendered: adverse >= 2 ? 'multiple rights permanently transferred' : adverse ? 'one significant right' : 'none flagged',
      flags: adverse >= 2 ? ['RIGHTS_SURRENDERED', 'POWER_ASYMMETRY'] : adverse ? ['REVIEW_CLAUSE'] : ['BALANCED'] };
  },
  // VOICE — institutional-decision fairness. Higher = fairer process.
  voice(text) {
    const unfair = count(text, /\b(?:no (?:reason|criteria|specific|paperwork)|does not meet (?:lending )?criteria|not (?:given|stated|disclosed)|no (?:appeal|consultation|selection criteria)|without (?:cause|explanation)|insufficient)\b/gi);
    const disclosed = count(text, /\b(?:criteria (?:were|are) (?:disclosed|specific)|reason given|evidence (?:cited|provided)|appeal (?:pathway|process))\b/gi);
    const score = clip(0.55 - 0.14 * unfair + 0.12 * disclosed);
    return { score, verdict: band(score, ['Serious Fairness Failures', 'Fairness Gaps', 'Process Adequate'], [0.4, 0.66]),
      criteria_finding: unfair ? 'criteria not disclosed / non-specific' : 'criteria appear disclosed',
      flags: unfair >= 2 ? ['NO_CRITERIA', 'NO_APPEAL'] : unfair ? ['CRITERIA_GAP'] : ['CRITERIA_PRESENT'] };
  },
  // MARK — institutional governance health. Higher = trust more justified.
  mark(text) {
    const opaque = count(text, /\b(?:cannot disclose|proprietary|committed to|we are committed|our (?:greatest asset|employees)|zero tolerance|100% of|trust us|responsible)\b/gi);
    const documented = count(text, /\b(?:published|independent (?:tribunal|oversight|review)|quarterly|measured against|audited|supporting evidence|external|we publish (?:reasons|the))\b/gi);
    const score = clip(0.5 - 0.1 * opaque + 0.14 * documented);
    return { score, verdict: band(score, ['Low Trust', 'Conditional Trust', 'Trust Justified'], [0.42, 0.66]),
      transparency_finding: documented > opaque ? 'documented, not merely asserted' : 'asserted without documentation',
      flags: documented > opaque ? ['TRANSPARENT', 'EXTERNAL_OVERSIGHT'] : ['OPACITY', 'ASSERTED_NOT_DOCUMENTED'] };
  },
  // STAND — personal case strength. Higher = stronger, better-documented case.
  stand(text) {
    const evidence = count(text, /\b(?:signed|contract|email|dated?|documented|in my possession|witness|record|\d{4}|receipt|letter|no (?:consultation|reason|paperwork))\b/gi);
    const score = clip(0.3 + 0.09 * evidence);
    return { score, verdict: band(score, ['Early Stage', 'Developing Case', 'Strong Case'], [0.45, 0.7]),
      evidence_present: evidence >= 3 ? 'multiple documented elements' : evidence ? 'some documentation' : 'largely undocumented',
      flags: evidence >= 3 ? ['DOCUMENTED', 'GROUNDED'] : ['EVIDENCE_GAP'] };
  },
  // WEIGH — decision readiness. Higher = more ready to decide.
  weigh(text) {
    const gaps = count(text, /\b(?:no (?:second opinion|advisor|physiotherapy|consultation)|not (?:signed|consulted|tried)|must decide by|by (?:week'?s end|end of)|no time)\b/gi);
    const info = count(text, /\b(?:alternativ|reversib|evidence|second opinion|success rate|trade-?off|consulted|compared)\b/gi);
    const score = clip(0.55 - 0.13 * gaps + 0.1 * info);
    return { score, verdict: band(score, ['Not Ready', 'Proceed with Caution', 'Decision-Ready'], [0.42, 0.66]),
      critical_assumption: gaps ? 'key alternative/verification not yet done' : 'assumptions appear examined',
      flags: gaps >= 2 ? ['MISSING_INFO', 'PRESSURE'] : gaps ? ['INFO_GAP'] : ['INFORMED'] };
  },
  // RISE — cognitive development calibration. Higher = develops capacity (not dependency).
  rise(text) {
    const depend = count(text, /\b(?:just (?:follow|memorise)|only one correct|there is no other way|the answer is simple|all experts agree|settled|anyone who questions)\b/gi);
    const develop = count(text, /\b(?:however|criticism|underdetermination|trade-?off|falsifiab|in principle|evidence|derived|why|consider whether)\b/gi);
    const complexity = clip((develop) / 4 + 0.3) * 9;
    const score = clip(0.5 + 0.12 * develop - 0.16 * depend);
    return { score, complexity_estimate: Math.max(1, Math.round(complexity)),
      verdict: band(score, ['Below Station', 'Well-Matched', 'Above Station'], [0.42, 0.7]),
      dependency_finding: depend ? 'gives answers / discourages questioning' : 'develops capacity',
      flags: depend ? ['DEPENDENCY_RISK'] : develop ? ['DEVELOPMENTAL'] : ['NEUTRAL'] };
  },
};

const CERT_PREFIX = { pages: 'PGS', pulse: 'PLS', weigh: 'WGH', lens: 'LNS', voice: 'VCE', mark: 'MRK', stand: 'STD', bridge: 'BRG', rise: 'RSE' };
export const PRODUCT_IDS = Object.keys(PRODUCTS);

// Screen `text` with product `id`. Returns the deep-mode-shaped JSON + a $0 cert.
export function screen(id, text) {
  const fn = PRODUCTS[id];
  if (!fn) throw new Error('unknown product: ' + id);
  const r = fn(String(text || ''));
  r.score = +clip(r.score).toFixed(3);
  r.certificate = CERT_PREFIX[id] + '-' + hex8(id + '|' + text);
  r.engine = 'novora-fast-v0.1';
  r.mode = 'fast';
  r.analysis = r.analysis || (r.verdict + ' (on-device screen; deep mode via /api/analyse for the ambiguous middle)');
  return r;
}
