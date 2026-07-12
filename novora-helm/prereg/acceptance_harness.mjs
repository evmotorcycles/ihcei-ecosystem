// acceptance_harness.mjs — the Stage-1 Registered Report SCORER (GT v18.2)
// ============================================================================
// This is the instrument that will grade the distilled on-device extractor
// against prereg/stage1_spec.json when it exists. It is built and verified NOW,
// before any model training, so the grading pipeline itself cannot be shaped
// around a trained model's behavior.
//
// WHAT THIS IS NOT: a simulation of the 1-3B NPU model. No such model exists
// yet; inventing its Brier scores or latency curves would fabricate exactly the
// numbers the locked spec exists to measure. The harness therefore runs with a
// pluggable extractor, and the only extractor available today is fast mode —
// the documented BASELINE. A dry run with the stand-in is expected to FAIL
// Claim A (evasive recall), which demonstrates the harness can return a null.
//
// Usage:
//   node prereg/acceptance_harness.mjs                 # dry run, fast stand-in
//   node prereg/acceptance_harness.mjs --json out.json # also emit per-item records
//
// Plugging in the real candidate later: implement extract(text) returning the
// evidence schema ({hits, iso, urg, fear, opt, imp, meth, ...}) and pass it to
// runAcceptance(). The posterior kernel is imported, never reimplemented.

import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { extractEvidenceFast, posterior, band } from '../../api/govern.js';

const dir = new URL('.', import.meta.url);
const canonical = v => {
  if (v === null || typeof v !== 'object') return JSON.stringify(v);
  if (Array.isArray(v)) return '[' + v.map(canonical).join(',') + ']';
  return '{' + Object.keys(v).sort().map(k => JSON.stringify(k) + ':' + canonical(v[k])).join(',') + '}';
};

// ── 0 · Load the locked spec and verify the lock before scoring anything ────
const spec = JSON.parse(readFileSync(new URL('stage1_spec.json', dir), 'utf8'));
const manifest = readFileSync(new URL('MANIFEST.sha256', dir), 'utf8');
const recorded = manifest.match(/spec_sha256_canonical\s+([0-9a-f]{64})/)[1];
const actual = createHash('sha256').update(canonical(spec)).digest('hex');
if (actual !== recorded) {
  console.error('REFUSING TO SCORE: stage1_spec.json does not match the locked manifest hash.');
  console.error('A graded run against an edited spec is not a pre-registered result.');
  process.exit(2);
}
console.log('lock verified: spec sha256', recorded.slice(0, 16) + '… matches manifest\n');

// ── 1 · Corpus. DRY RUN uses the 44-item seed corpus (labels by id prefix).
// The REAL acceptance run must load the frozen corpora's sealed 30% splits and
// verify their hashes in MANIFEST.sha256 (they are not built yet — §1 of spec).
const src = readFileSync(new URL('../../api/calibrate.js', import.meta.url), 'utf8');
const CORPUS = JSON.parse(src.match(/const CORPUS = (\[.*?\]);/s)[1]);
const cls = id => id.startsWith('hn') ? 'emergency'
  : id.startsWith('cb') ? 'clean'
  : id.startsWith('ev') ? 'evasive'
  : id.startsWith('gt') ? 'groupthink' : 'blunt';
const label = id => (cls(id) === 'emergency' || cls(id) === 'clean') ? 0 : 1; // 1 = manipulative

// ── 2 · The scorer ───────────────────────────────────────────────────────────
export function runAcceptance(extract, extractorName) {
  const items = [];
  const lat = [];
  for (const row of CORPUS) {
    const t0 = performance.now();
    const ev = extract(row.text);
    const post = posterior(ev, 0.10, 3000, 7, true);
    lat.push(performance.now() - t0);
    const [verdict] = band(post.mean, post.ci);
    items.push({
      id: row.id, class: cls(row.id), y: label(row.id),
      p: +post.mean.toFixed(4), ci95: [+post.ci[0].toFixed(4), +post.ci[1].toFixed(4)],
      verdict, mechanism_present: post.mechanismPresent,
      mechanism_lexicon: 'enterprise-v1',
    });
  }
  const by = c => items.filter(i => i.class === c);
  const rate = (rows, pred) => rows.length ? rows.filter(pred).length / rows.length : NaN;

  // Primary endpoints (bands read from the LOCKED spec, never hardcoded here)
  const A1 = rate(by('evasive'), i => i.verdict !== 'PASS');
  const A2 = rate(by('emergency'), i => i.verdict === 'BLOCK');
  const B1 = rate(by('emergency'), i => i.verdict === 'BLOCK');
  // Secondary: calibration over all items
  const brier = items.reduce((s, i) => s + (i.p - i.y) ** 2, 0) / items.length;
  const bins = Array.from({ length: 5 }, () => ({ n: 0, p: 0, y: 0 }));
  for (const i of items) {
    const b = bins[Math.min(4, Math.floor(i.p * 5))];
    b.n++; b.p += i.p; b.y += i.y;
  }
  const ece = bins.reduce((s, b) => b.n ? s + (b.n / items.length) * Math.abs(b.p / b.n - b.y / b.n) : s, 0);
  lat.sort((a, b) => a - b);
  const p50 = lat[Math.floor(lat.length * 0.5)], p95 = lat[Math.floor(lat.length * 0.95)];

  const sA = spec.claim_A_ambient_deep_mode, sB = spec.claim_B_emergency_safety_at_scale;
  const checks = [
    ['A1 evasive recall (HOLD/WARN)', A1, '>=', sA.primary_endpoints.A1_evasive_recall_hold_or_warn.accept_min],
    ['A2 emergency false-HOLD', A2, '<=', sA.primary_endpoints.A2_emergency_false_hold_rate.accept_max],
    ['B1 emergency false-BLOCK', B1, '<=', sB.primary_endpoints.B1_fast_mode_false_block_rate.accept_max],
    ['secondary: Brier', brier, '<=', sA.secondary_reported_not_gating.brier_score_max],
    ['secondary: ECE (5-bin)', ece, '<=', sA.secondary_reported_not_gating.ece_5bin_max],
  ];
  console.log(`extractor: ${extractorName}`);
  console.log(`corpus: SEED (n=${items.length}) — DRY RUN; the frozen acceptance corpora do not exist yet`);
  console.log(`pipeline latency on this host (NOT NPU numbers): p50 ${p50.toFixed(1)}ms · p95 ${p95.toFixed(1)}ms\n`);
  console.log('endpoint                          measured   band        verdict');
  let claimAFail = false;
  for (const [name, val, op, bound] of checks) {
    const pass = op === '>=' ? val >= bound : val <= bound;
    if (name.startsWith('A') && !pass) claimAFail = true;
    console.log(' ', name.padEnd(31), val.toFixed(3).padEnd(10), `${op} ${bound}`.padEnd(11), pass ? 'PASS' : 'FAIL');
  }
  console.log('  B2 worst-stratum false-BLOCK    —          <= 0.02     SKIP (seed corpus has no strata)');
  const decision = claimAFail
    ? 'NULL under this extractor — per the locked spec this retires the ambient-deep claim for it;\n  HELM stays fast-mode + primitives unless a candidate clears BOTH A-bands on the sealed sets.'
    : 'bands cleared — meaningful ONLY on the sealed acceptance sets, one shot, per §4 of the spec.';
  console.log('\nClaim A decision:', decision);
  return { extractor: extractorName, items, metrics: { A1, A2, B1, brier, ece, latency_ms: { p50, p95 } } };
}

// ── 3 · Dry run with the only extractor that exists today ───────────────────
const isMain = process.argv[1] && import.meta.url.endsWith(process.argv[1].split('/').pop());
if (isMain) {
  const res = runAcceptance(extractEvidenceFast, 'fast-mode regex (BASELINE STAND-IN — not the distilled candidate)');
  const flag = process.argv.indexOf('--json');
  if (flag > -1 && process.argv[flag + 1]) {
    writeFileSync(process.argv[flag + 1], JSON.stringify(res, null, 2));
    console.log('\nper-item records written to', process.argv[flag + 1]);
  }
}
