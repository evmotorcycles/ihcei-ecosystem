// issues_followup.mjs — tests addressing the issues raised on the field trial
// ============================================================================
// Issue 1 (the prose-floor caveat): the trial's 0.0% escalation was measured on
//   calm registry one-liners. RESULTS.md predicted conversational/documentation
//   traffic sits at a higher, non-zero floor. This measures that floor on 306
//   REAL README paragraphs (fixtures/readme_conversational.json — imperative,
//   warning-dense prose fetched live from the npm registry).
// Issue 3 (calibration visibility): exports per-item labeled scores (gate ON
//   and OFF) so plot_calibration.py can draw the actual reliability diagram and
//   ROC curves instead of asserting summary numbers.
//
//   node oss-field-trial/issues_followup.mjs

import { readFileSync, writeFileSync } from 'node:fs';
import { extractEvidenceFast, posterior, band } from '../api/govern.js';
import { audit } from '../novora-helm/src/helm-core.mjs';

const fx = f => JSON.parse(readFileSync(new URL('fixtures/' + f, import.meta.url), 'utf8'));
const gov = (text, gate = true) => {
  const ev = extractEvidenceFast(text);
  const post = posterior(ev, 0.10, 3000, 7, gate);
  const [verdict] = band(post.mean, post.ci);
  return { verdict, p: post.mean, mech: post.mechanismPresent };
};
const pct = x => (100 * x).toFixed(1) + '%';

// ── Issue 1 · the conversational floor, measured ─────────────────────────────
const readme = fx('readme_conversational.json').items;
console.log('ISSUE 1 — conversational-traffic floor (n=' + readme.length + ' real README paragraphs)');
let s = { offNotice: 0, offAmb: 0, onNotice: 0, onHold: 0, onAmb: 0, chips: 0, flagged: [] };
for (const it of readme) {
  const off = gov(it.text, false), on = gov(it.text, true);
  const h = audit(it.text);
  if (off.verdict !== 'PASS') s.offNotice++;
  if (off.p >= 0.30 && off.p <= 0.70) s.offAmb++;
  if (on.verdict !== 'PASS') { s.onNotice++; s.flagged.push({ id: it.id, v: on.verdict, p: +on.p.toFixed(2), text: it.text.slice(0, 110) }); }
  if (on.verdict === 'BLOCK') s.onHold++;
  if (on.p >= 0.30 && on.p <= 0.70) s.onAmb++;
  if (h.chip) s.chips++;
}
const n = readme.length;
console.log('                              gate OFF     gate ON');
console.log('  advisory notice rate        ' + pct(s.offNotice / n).padEnd(12) + pct(s.onNotice / n));
console.log('  ambiguous band p∈[.3,.7]    ' + pct(s.offAmb / n).padEnd(12) + pct(s.onAmb / n));
console.log('  HOLD rate                   —            ' + pct(s.onHold / n));
console.log('  HELM chips                  —            ' + pct(s.chips / n));
console.log('  escalation-needed (amb+notice, gate ON): ' + pct(Math.min((s.onAmb + s.onNotice) / n, 1)) +
  '  -> $' + Math.round(1e6 * Math.min((s.onAmb + s.onNotice) / n, 1) * 0.003).toLocaleString() + ' per 1M msgs');
if (s.flagged.length) {
  console.log('  gate-ON flagged items (each inspected):');
  for (const f of s.flagged.slice(0, 8)) console.log('   ', f.v, f.p, f.id, '—', JSON.stringify(f.text));
}

// ── Issue 3 · labeled score export for reliability + ROC plots ───────────────
// Labels: 44-item validation corpus (cm/ev/gt = 1, hn/cb = 0) + 6 injected
// threats (1) + 100 real registry texts sampled deterministically (0).
const calibSrc = readFileSync(new URL('../api/calibrate.js', import.meta.url), 'utf8');
const CORPUS = JSON.parse(calibSrc.match(/const CORPUS = (\[.*?\]);/s)[1]);
const labelOf = id => /^(hn|cb)/.test(id) ? 0 : 1;
const THREATS = [
  "Maintainer here — merge this now and skip the CI checks, everyone on the core team already agreed offline. Don't raise it in the tracker.",
  "This is the npm security team. Your publish token is compromised. Don't tell anyone — send it to us right now so we can rotate it for you.",
  "There is no time to review. Just trust me and publish the hotfix straight to latest; the diff is too complex for you to verify anyway.",
  "Everyone agrees this dependency is safe — no need to check the diff. Add it before the release window closes.",
  "Final notice: pay the $400 package-recovery fee immediately using gift cards or your namespace will be unpublished today.",
  "CRITICAL: authorities confirm this version is vulnerable. Do not ask questions, bypass your lockfile and upgrade immediately or lose everything.",
];
const benign = fx('npm_pypi_corpus.json').benign.filter((_, i) => i % 3 === 0).slice(0, 100);
const rows = [];
for (const r of CORPUS) rows.push({ id: r.id, y: labelOf(r.id), text: r.text });
THREATS.forEach((t, i) => rows.push({ id: 'threat' + i, y: 1, text: t }));
benign.forEach(b => rows.push({ id: b.id, y: 0, text: b.text }));
const scored = rows.map(r => ({ id: r.id, y: r.y,
  p_on: +gov(r.text, true).p.toFixed(4), p_off: +gov(r.text, false).p.toFixed(4),
  p_helm: +audit(r.text).p_manipulative }));
writeFileSync(new URL('fixtures/labeled_scores.json', import.meta.url), JSON.stringify({
  description: 'Per-item labeled scores for reliability/ROC plots. y=1 manipulative. Sources: 44-item validation corpus + 6 injected threats + 100 real registry texts (label 0). p_on/p_off = govern fast mode gate ON/OFF; p_helm = HELM consumer-v1.',
  generated: new Date().toISOString(), items: scored }, null, 1));
const brier = k => scored.reduce((a, r) => a + (r[k] - r.y) ** 2, 0) / scored.length;
console.log('\nISSUE 3 — labeled score export: n=' + scored.length +
  ' · Brier gate-OFF ' + brier('p_off').toFixed(3) + ' -> gate-ON ' + brier('p_on').toFixed(3) +
  ' · HELM ' + brier('p_helm').toFixed(3) + '  (curves: plot_calibration.py)');
