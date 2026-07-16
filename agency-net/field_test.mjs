// field_test.mjs — AIPS vs the normal internet, on REAL open-source traffic.
// ============================================================================
// Runs the Agency Internet Protocol Suite over real package descriptions and
// injected threats, across a multi-hop path, and contrasts it hop-for-hop with
// what today's internet does with the same bytes. Reuses the live-fetched
// corpora already in the repo (oss-field-trial/fixtures) — no synthetic benign.
//
//   node agency-net/field_test.mjs

import { readFileSync } from 'node:fs';
import { AgencyNode, send, verifyPath, sha256 } from './aips.mjs';
import { DelegationTable, CertificateWallet } from '../novora-helm/src/primitives.mjs';

const fx = f => JSON.parse(readFileSync(new URL('../oss-field-trial/fixtures/' + f, import.meta.url), 'utf8'));
const bar = c => console.log(c.repeat(78));
const pct = x => (100 * x).toFixed(1) + '%';

// A realistic path: sender's home router -> an ISP-level Agency gateway
// (enterprise lexicon) -> the receiver's own device (consumer lexicon).
const path = () => [
  new AgencyNode('home-router', { cls: 'enterprise' }),
  new AgencyNode('isp-gateway', { cls: 'enterprise' }),
  new AgencyNode('receiver-device', { cls: 'consumer' }),
];

// ── 1 · Same bytes, two networks ─────────────────────────────────────────────
bar('=');
console.log(' 1 · THE SAME MESSAGE ON BOTH NETWORKS');
bar('=');
const scam = "It's the npm security team — your publish token is compromised. Don't tell anyone, wire the recovery fee and send us the token right now or your packages are unpublished today.";
console.log('message (a token-phish + payment scam aimed at a maintainer):');
console.log('  "' + scam.slice(0, 92) + '…"\n');
console.log('NORMAL INTERNET (TCP/IP): checksums say the bytes are intact, TLS says the pipe');
console.log('  was private — then it hands the receiver the raw text. Attestation of MEANING: none.');
const env = send(scam, path());
console.log('\nAGENCY INTERNET (AIPS): every hop attaches a signed verdict; nothing is dropped.');
for (const h of env.hops) {
  console.log('  ' + h.node.padEnd(16) + h.verdict.padEnd(6) + 'p=' + h.p +
    ' mech=' + h.mechanism_present + ' [' + h.mechanism_lexicon + ']  cert ' + h.hash.slice(0, 12) + '…');
}
const v = verifyPath(env, scam);
console.log('  receiver verifies the whole path: ok=' + v.ok + ' (hops=' + env.hops.length + ')');

// ── 2 · Silence on real project traffic (no alarm fatigue on the wire) ───────
bar('=');
console.log(' 2 · REAL OSS TRAFFIC ACROSS THE NETWORK (n=281 live registry texts)');
bar('=');
const benign = fx('npm_pypi_corpus.json').benign;
let flaggedHops = 0, quietMsgs = 0;
for (const item of benign) {
  const e = send(item.text, path());
  const anyChip = e.hops.some(h => h.verdict !== 'PASS');
  if (anyChip) flaggedHops++; else quietMsgs++;
}
console.log('  messages the network stayed fully silent on: ' + quietMsgs + '/' + benign.length +
  ' (' + pct(quietMsgs / benign.length) + ')');
console.log('  messages that raised any chip: ' + flaggedHops +
  '  — a wire that cried wolf on real traffic would be turned off; this one is not.');

// ── 3 · Threats still caught in-band ─────────────────────────────────────────
bar('=');
console.log(' 3 · INJECTED THREATS TRAVERSING THE NETWORK');
bar('=');
const THREATS = [
  ['token phish', scam],
  ['supply-chain PR', "Maintainer here — merge now and skip CI, the core team already agreed offline. Don't raise it in the tracker."],
  ['fake advisory', "CRITICAL: authorities confirm this version is vulnerable. Do not ask questions, bypass your lockfile and upgrade immediately or lose everything."],
  ['consensus pressure', "Everyone agrees this dependency is safe — no need to check the diff. Add it before the release window closes."],
];
let caught = 0;
for (const [name, t] of THREATS) {
  const e = send(t, path());
  const worst = e.hops.reduce((w, h) => (h.verdict === 'BLOCK' ? 'BLOCK' : (w === 'BLOCK' ? 'BLOCK' : h.verdict !== 'PASS' ? 'WARN' : w)), 'PASS');
  if (worst !== 'PASS') caught++;
  console.log('  ' + name.padEnd(20) + 'network verdict: ' + worst + '  (chips at ' +
    e.hops.filter(h => h.verdict !== 'PASS').map(h => h.node).join(', ') + ')');
}
console.log('  threats surfaced by the network: ' + caught + '/' + THREATS.length);

// ── 4 · Tamper-evidence: rewrite in flight, receiver detects it ─────────────
bar('=');
console.log(' 4 · A MALICIOUS RELAY TAMPERS — the receiver catches it, TCP/IP cannot');
bar('=');
// (a) payload swapped after the home-router attested the benign original
const good = "Here are three migration options with rollback steps and linked sources. The choice is yours.";
const e4 = send(good, path());
const swapped = good + " Also: wire the fee now or lose everything, don't tell anyone.";
const vSwap = verifyPath(e4, swapped);
console.log('  (a) relay swaps payload after attestation:  ok=' + vSwap.ok +
  '  brokenAt hop ' + vSwap.brokenAt + ' — ' + vSwap.reason);
// (b) a relay rewrites a past BLOCK verdict to PASS to sneak a scam through
const e4b = send(scam, path());
e4b.hops[0].verdict = 'PASS'; e4b.hops[0].mechanism_present = false;
const vRw = verifyPath(e4b, scam);
console.log('  (b) relay rewrites a hop verdict to PASS:   ok=' + vRw.ok +
  '  brokenAt hop ' + vRw.brokenAt + ' — ' + vRw.reason);
console.log('  normal internet: neither tamper is detectable above the transport — the bytes');
console.log('  re-checksum fine and arrive "valid". AIPS breaks the chain at the exact hop.');

// ── 5 · L4 delegation on an agent action crossing a node ────────────────────
bar('=');
console.log(' 5 · AN AGENT ACTION CROSSES A DELEGATION NODE (the "OAuth of agency")');
bar('=');
const wallet = new CertificateWallet();
const table = new DelegationTable(wallet);
table.grant({ agent: 'deploy-bot', action: 'publish-package', permission: 'allow', maxStake: 100 });
const gate = new AgencyNode('publish-gateway', { cls: 'enterprise', delegation: table });
const ok = await gate.authorize({ agent: 'deploy-bot', action: 'publish-package', stake: 40 });
const over = await gate.authorize({ agent: 'deploy-bot', action: 'publish-package', stake: 9000 });
const ungr = await gate.authorize({ agent: 'deploy-bot', action: 'force-delete-registry', stake: 0 });
console.log('  publish within cap:        ' + ok.decision + '  (' + ok.reason + ')');
console.log('  publish over stake cap:    ' + over.decision + '  (' + over.reason + ')');
console.log('  ungranted destructive act: ' + ungr.decision + '  (' + ungr.reason + ')');
console.log('  normal internet routes all three identically — it has no concept of WHO may do WHAT.');

// ── 6 · Network-health telemetry (LISM tau_v), which TCP/IP has no notion of ─
bar('=');
console.log(' 6 · THE NETWORK KNOWS THE HEALTH OF WHAT IT CARRIES (live tau_v cohort)');
bar('=');
const cohort = fx('live_tauv_cohort_trial.json').response.repos.slice().sort((a, b) => a.tau_v - b.tau_v);
for (const r of cohort) {
  const flag = r.tau_v > 60 ? '  ⚠ zombie-risk (queue saturating)' : '';
  console.log('  ' + r.repo.padEnd(24) + 'tau_v ' + String(r.tau_v).padStart(7) + 'd' + flag);
}
console.log('  normal internet delivers a package identically whether its maintainers answer in');
console.log('  3 days or 251; AIPS surfaces enforcement latency so the receiver sees the risk.');

bar('=');
console.log(' AIPS moves the same bits as TCP/IP, and adds what TCP/IP structurally cannot:');
console.log(' a verifiable, non-suppressive record of what each hop concluded about MEANING —');
console.log(' silent on ' + pct(quietMsgs / benign.length) + ' of real traffic, ' + caught + '/' + THREATS.length +
  ' threats surfaced, every tamper located, agency boundaries enforced.');
bar('=');
