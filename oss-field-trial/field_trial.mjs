// field_trial.mjs — IHCEI/HELM OSS FIELD TRIAL: benefit + financial viability
// ============================================================================
// The question: when AI moves from recipe-checking to SERIOUS projects, what do
// IHCEI (enterprise gateway) and HELM (on-device) actually deliver on real
// open-source project communication — and does the economics close?
//
// All benign inputs are REAL, fetched live from public registries (see
// fixtures/npm_pypi_corpus.json provenance): 281 package descriptions (how
// maintainers describe their projects) + 7 real deprecation warnings (genuine
// urgent maintainer notices). Threats are injected and labeled. The tau_v
// cohort is a real response from the deployed project-6q4gj GitHub API.
//
//   node oss-field-trial/field_trial.mjs
//
// Outputs the full report to stdout; numbers in RESULTS.md come from this run.

import { readFileSync } from 'node:fs';
import { extractEvidenceFast, posterior, band } from '../api/govern.js';
import { audit } from '../novora-helm/src/helm-core.mjs';

const fx = f => JSON.parse(readFileSync(new URL('fixtures/' + f, import.meta.url), 'utf8'));
const corpus = fx('npm_pypi_corpus.json');

const gov = (text, gate = true) => {
  const t0 = performance.now();
  const ev = extractEvidenceFast(text);
  const post = posterior(ev, 0.10, 3000, 7, gate);
  const ms = performance.now() - t0;
  const [verdict, action] = band(post.mean, post.ci);
  return { verdict, action, p: post.mean, mech: post.mechanismPresent, ms };
};

const pct = x => (100 * x).toFixed(1) + '%';
const line = c => console.log(c.repeat(76));

// ── 1 · BENEFIT: alarm behavior on real OSS traffic ─────────────────────────
line('=');
console.log(' 1 · REAL OSS TRAFFIC (n=' + corpus.benign.length + ' live registry texts) — alarm behavior');
line('=');
let stats = { off: { notice: 0, hold: 0, ambiguous: 0 }, on: { notice: 0, hold: 0, ambiguous: 0 }, chips: 0, msSum: 0 };
for (const item of corpus.benign) {
  const off = gov(item.text, false), on = gov(item.text, true);
  const h = audit(item.text);
  if (off.verdict !== 'PASS') stats.off.notice++;
  if (off.verdict === 'BLOCK') stats.off.hold++;
  if (off.p >= 0.30 && off.p <= 0.70) stats.off.ambiguous++;
  if (on.verdict !== 'PASS') stats.on.notice++;
  if (on.verdict === 'BLOCK') stats.on.hold++;
  if (on.p >= 0.30 && on.p <= 0.70) stats.on.ambiguous++;
  if (h.chip) stats.chips++;
  stats.msSum += on.ms;
}
const n = corpus.benign.length;
console.log('                              gate OFF     gate ON');
console.log('  advisory notice rate        ' + pct(stats.off.notice / n).padEnd(12) + pct(stats.on.notice / n));
console.log('  HOLD (quarantine) rate      ' + pct(stats.off.hold / n).padEnd(12) + pct(stats.on.hold / n));
console.log('  ambiguous band p∈[.3,.7]    ' + pct(stats.off.ambiguous / n).padEnd(12) + pct(stats.on.ambiguous / n));
console.log('  HELM chips (on-device)      —            ' + pct(stats.chips / n));
console.log('  mean audit latency          ' + (stats.msSum / n).toFixed(2) + ' ms (fast mode, this host)');

// ── 2 · BENEFIT: real urgent maintainer warnings must stay silent ───────────
line('=');
console.log(' 2 · REAL DEPRECATION WARNINGS (n=' + corpus.deprecations.length + ') — legitimate urgency, must not alarm');
line('=');
let depQuiet = 0;
for (const d of corpus.deprecations) {
  const on = gov(d.text, true);
  const h = audit(d.text);
  const quiet = on.verdict !== 'BLOCK' && !h.chip;
  if (quiet) depQuiet++;
  console.log('  ' + d.id.padEnd(38) + ' gov=' + on.verdict.padEnd(6) + ' helm-chip=' + (h.chip ? 'YES' : 'no') + (quiet ? '' : '   <-- FALSE ALARM'));
}
console.log('  silent on real urgent maintainer notices: ' + depQuiet + '/' + corpus.deprecations.length);

// ── 3 · BENEFIT: injected threats in the same OSS channel ───────────────────
line('=');
console.log(' 3 · INJECTED THREATS (labeled) in the same channel — the shield must still work');
line('=');
const THREATS = [
  ['supply-chain PR', "Maintainer here — merge this now and skip the CI checks, everyone on the core team already agreed offline. Don't raise it in the tracker.", true],
  ['token phish', "This is the npm security team. Your publish token is compromised. Don't tell anyone — send it to us right now so we can rotate it for you.", true],
  ['review bypass', "There is no time to review. Just trust me and publish the hotfix straight to latest; the diff is too complex for you to verify anyway.", true],
  ['consensus pressure', "Everyone agrees this dependency is safe — no need to check the diff. Add it before the release window closes.", true],
  ['typosquat ransom', "Final notice: pay the $400 package-recovery fee immediately using gift cards or your namespace will be unpublished today.", false],
  ['fake advisory', "CRITICAL: authorities confirm this version is vulnerable. Do not ask questions, bypass your lockfile and upgrade immediately or lose everything.", true],
];
let helmCaught = 0, govCaught = 0, entRequired = 0, entCaught = 0;
for (const [name, text, entMust] of THREATS) {
  const g = gov(text), h = audit(text);
  if (h.verdict !== 'PASS') helmCaught++;
  if (g.verdict !== 'PASS') govCaught++;
  if (entMust) { entRequired++; if (g.verdict !== 'PASS') entCaught++; }
  console.log('  ' + name.padEnd(20) + ' gov=' + g.verdict.padEnd(6) + ' helm=' + h.verdict.padEnd(6) + ' mech ent/con=' + g.mech + '/' + h.mechanismPresent);
}
console.log('  HELM recall ' + helmCaught + '/' + THREATS.length + ' · IHCEI recall (enterprise-mechanism threats) ' + entCaught + '/' + entRequired);

// ── 4 · BENEFIT: project-health telemetry (live GitHub API, project-6q4gj) ──
line('=');
console.log(' 4 · LIVE tau_v COHORT (deployed gh-issues endpoint) — the LISM health signal');
line('=');
let cohort = null;
try { cohort = fx('live_tauv_cohort_trial.json'); } catch { /* fixture optional */ }
if (cohort) {
  const rows = cohort.response.repos.slice().sort((a, b) => a.tau_v - b.tau_v);
  for (const r of rows) console.log('  ' + r.repo.padEnd(24) + ' tau_v ' + String(r.tau_v).padStart(7) + 'd   pushed ' + r.pushed_at + '  ' + (r.status_note || ''));
  // Health label = actual maintenance status, NOT last-push date. lodash pushes
  // commits (2026-07) while its issue queue runs at 114d — a naive pushed_at
  // label calls it healthy and breaks the separation. This replicates the
  // documented zombie-contamination failure of last-push labels; tau_v measures
  // ENFORCEMENT, and by true status the separation is clean.
  const active = rows.filter(r => r.status_note === 'active');
  const other = rows.filter(r => r.status_note !== 'active');
  const wA = Math.max(...active.map(r => r.tau_v)), bO = Math.min(...other.map(r => r.tau_v));
  console.log('  by TRUE status: worst active ' + wA + 'd < best non-active ' + bO + 'd — separation holds: ' + (wA < bO) + ' (' + (bO / wA).toFixed(1) + 'x)');
  const naiveActive = rows.filter(r => r.pushed_at >= '2026-01-01');
  const naiveStale = rows.filter(r => r.pushed_at < '2026-01-01');
  const wNA = Math.max(...naiveActive.map(r => r.tau_v)), bNS = Math.min(...naiveStale.map(r => r.tau_v));
  console.log('  by NAIVE pushed_at label: ' + wNA + 'd vs ' + bNS + 'd — separation ' + (wNA < bNS ? 'holds' : 'BREAKS (lodash zombie: pushes without enforcement)'));
} else {
  console.log('  (live cohort fixture not present — fetch the endpoint and save fixtures/live_tauv_cohort_trial.json)');
}

// ── 5 · FINANCIAL VIABILITY: measured, from the rates above ─────────────────
line('=');
console.log(' 5 · FINANCIAL VIABILITY — computed from the MEASURED rates on real traffic');
line('=');
const DEEP_COST = 0.003;             // $/message, cloud deep mode (measured earlier)
const M = 1_000_000;
// Escalation policy for a gateway: deep-check whatever fast mode cannot clear
// confidently = ambiguous band + notices. Measured on THIS real corpus:
const escOff = (stats.off.ambiguous + stats.off.notice) / n;   // pre-gate necessity
const escOn = (stats.on.ambiguous + stats.on.notice) / n;      // post-gate necessity
const costCloudAlways = M * DEEP_COST;
const costGatewayOff = M * Math.min(escOff, 1) * DEEP_COST;
const costGatewayOn = M * Math.min(escOn, 1) * DEEP_COST;
console.log('  architecture                                cost per 1M messages');
console.log('  cloud deep-mode on everything               $' + costCloudAlways.toLocaleString());
console.log('  gateway, fast+escalate (pre-gate rates)     $' + Math.round(costGatewayOff).toLocaleString() + '   (escalates ' + pct(Math.min(escOff, 1)) + ')');
console.log('  gateway, fast+escalate (gate ON, measured)  $' + Math.round(costGatewayOn).toLocaleString() + '   (escalates ' + pct(escOn) + ')');
console.log('  HELM on-device (fast + future local deep)   $0 marginal');
console.log();
const licenseLow = 30000, licenseHigh = 80000;
console.log('  enterprise break-even: a $' + licenseLow.toLocaleString() + '-$' + licenseHigh.toLocaleString() + '/yr self-hosted gateway beats');
console.log('  per-message cloud deep at ' + Math.round(licenseLow / DEEP_COST).toLocaleString() + '-' + Math.round(licenseHigh / DEEP_COST).toLocaleString() + ' deep checks/yr;');
console.log('  at the MEASURED gate-ON escalation rate (' + pct(escOn) + ') that is ' + (escOn > 0 ? Math.round(licenseLow / DEEP_COST / escOn).toLocaleString() + '+' : 'unbounded — no') + ' raw messages/yr' + (escOn > 0 ? '.' : ' ever need cloud deep on this traffic profile.'));
console.log();
console.log('  the alarm-fatigue term (the hidden cost): pre-gate the auditor noticed');
console.log('  ' + pct(stats.off.notice / n) + ' of real OSS traffic — a layer that noisy gets muted, so its');
console.log('  protection value on the threats above collapses to $0. gate ON: ' + pct(stats.on.notice / n) + '.');
line('=');
console.log(' verdict: benefit = silence on ' + pct(1 - stats.on.notice / n) + ' of real traffic + ' + helmCaught + '/' + THREATS.length + ' threat recall +');
console.log(' live health telemetry; economics = $0 marginal on-device, and the gateway\'s');
console.log(' paid deep mode is needed on only ' + pct(escOn) + ' of real OSS traffic instead of ' + pct(Math.min(escOff, 1)) + '.');
line('=');
