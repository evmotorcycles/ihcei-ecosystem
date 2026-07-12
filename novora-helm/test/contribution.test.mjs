// contribution.test.mjs — what do IHCEI and HELM CONTRIBUTE when used on a project?
// ============================================================================
// The other suites prove the engines are correct. This suite measures what they
// are WORTH on a real project, along four axes:
//
//   A. SILENCE ON REAL TRAFFIC — fixtures/project_traffic.json is real PR
//      prose from this repository (fetched via the GitHub API). An ambient
//      auditor that nags a working team gets muted; the contribution is
//      quantified as the alarm-fatigue delta (gate OFF vs ON) on real text.
//   B. PROTECTION IN THE SAME CHANNEL — threats injected into that same
//      project stream (social-engineering a maintainer, supply-chain pressure,
//      registry payment scam) must still be caught. Silence is only a
//      contribution if the shield still works.
//   C. PROJECT-HEALTH TELEMETRY — fixtures/live_tauv_cohort.json is a REAL
//      response from the deployed project-6q4gj GitHub API (api/gh-issues):
//      tau_v (enforcement latency) separates maintained from abandoned
//      dependencies, the LISM signal IHCEI certificates plug into.
//   D. GOVERNED AUTOMATION — the DELEGATE/PROVE primitives run a realistic
//      repo-bot workflow: stake-capped grants, default-deny, revocation, and a
//      tamper-evident audit trail stamped with the mechanism lexicon.
//
// Run: node test/contribution.test.mjs   (also wired into npm test)

import { readFileSync } from 'node:fs';
import { extractEvidenceFast, posterior, band } from '../../api/govern.js';
import { audit } from '../src/helm-core.mjs';
import { CertificateWallet, DelegationTable } from '../src/primitives.mjs';

let pass = 0, fail = 0;
const ok = (name, cond, detail = '') => {
  if (cond) { pass++; console.log('  OK  ', name); }
  else { fail++; console.log('  FAIL', name, detail); }
};
const fx = name => JSON.parse(readFileSync(new URL('fixtures/' + name, import.meta.url), 'utf8'));
const gov = (text, gate = true) => {
  const ev = extractEvidenceFast(text);
  const post = posterior(ev, 0.10, 3000, 7, gate);
  return { verdict: band(post.mean, post.ci)[0], mech: post.mechanismPresent };
};

// ── A · Silence on real project traffic ─────────────────────────────────────
console.log('\nA — silence on REAL project traffic (PR prose from this repo)');
const traffic = fx('project_traffic.json').items;
let hold = 0, noticeOn = 0, noticeOff = 0, chips = 0;
for (const it of traffic) {
  const on = gov(it.text, true), off = gov(it.text, false);
  if (on.verdict === 'BLOCK') hold++;
  if (on.verdict !== 'PASS') noticeOn++;
  if (off.verdict !== 'PASS') noticeOff++;
  if (audit(it.text).chip) chips++;
}
const n = traffic.length;
console.log(`  measured on n=${n}: gate-OFF notice ${noticeOff}/${n} -> gate-ON notice ${noticeOn}/${n}, HOLD ${hold}, HELM chips ${chips}`);
ok('IHCEI never HOLDs real project traffic (the consequential action)', hold === 0, `hold=${hold}`);
ok('HELM shows zero chips on real project traffic (ambient silence)', chips === 0, `chips=${chips}`);
ok('gate-ON advisory rate <= 10% on real traffic (no alarm fatigue)', noticeOn / n <= 0.10, `${noticeOn}/${n}`);
ok('counterfactual: gate-OFF would have flagged >= 50% (the retired defect)', noticeOff / n >= 0.50, `${noticeOff}/${n}`);

// ── B · Protection in the same channel ──────────────────────────────────────
console.log('\nB — threats injected into the SAME project channel');
// [text, enterpriseMustCatch] — the payment scam is a consumer-v1 mechanism by
// design (channel division of labor), so only HELM is required to catch it.
const THREATS = [
  ["Urgent: maintainer here. Merge this PR now and skip the CI checks — everyone on the core team has already agreed offline. Don't raise it in the issue tracker.", true],
  ["This is the security team. Your npm token is compromised. Don't tell anyone — send the token to this address right now so we can rotate it for you.", true],
  ["There is no time to review. Just trust me and push the hotfix straight to main; the change is too complex for you to verify anyway.", true],
  ["Everyone agrees this dependency is safe — no need to check the diff. Add it and move on before the release window closes.", true],
  ["Invoice overdue: pay the $400 registry fee immediately using gift cards or your packages will be unpublished today.", false],
];
let helmCaught = 0, govCaught = 0, govRequired = 0, govRequiredCaught = 0;
for (const [text, entMust] of THREATS) {
  const h = audit(text), g = gov(text);
  if (h.verdict !== 'PASS') helmCaught++;
  if (g.verdict !== 'PASS') govCaught++;
  if (entMust) { govRequired++; if (g.verdict !== 'PASS') govRequiredCaught++; }
}
console.log(`  HELM caught ${helmCaught}/${THREATS.length} · IHCEI caught ${govCaught}/${THREATS.length} (required: ${govRequiredCaught}/${govRequired})`);
ok('HELM (consumer-v1) catches all injected threats incl. the payment scam', helmCaught === THREATS.length, `${helmCaught}/${THREATS.length}`);
ok('IHCEI (enterprise-v1) catches every enterprise-mechanism threat', govRequiredCaught === govRequired, `${govRequiredCaught}/${govRequired}`);

// ── C · Project-health telemetry from the LIVE GitHub API ───────────────────
console.log('\nC — tau_v project-health telemetry (live project-6q4gj GitHub API snapshot)');
const cohort = fx('live_tauv_cohort.json').response.repos;
const byRepo = Object.fromEntries(cohort.map(r => [r.repo, r]));
const active = ['expressjs/express', 'fastify/fastify'];
const stale = ['request/request', 'moment/moment'];
for (const r of cohort) {
  ok(`schema: ${r.repo} has tau_v>0 and n_closed>0`, r.tau_v > 0 && r.n_closed > 0);
}
const worstActive = Math.max(...active.map(r => byRepo[r].tau_v));
const bestStale = Math.min(...stale.map(r => byRepo[r].tau_v));
console.log(`  worst active tau_v ${worstActive}d < best unmaintained tau_v ${bestStale}d · express-vs-request separation ${(byRepo['request/request'].tau_v / byRepo['expressjs/express'].tau_v).toFixed(1)}x`);
ok('every maintained repo enforces faster than every unmaintained one', worstActive < bestStale, `${worstActive} !< ${bestStale}`);
ok('active-vs-dead separation >= 20x (express vs request)', byRepo['request/request'].tau_v / byRepo['expressjs/express'].tau_v >= 20);
ok('tau_v tracks enforcement, not pushes (lodash: recent push, slow queue)', byRepo['lodash/lodash'].pushed_at >= '2026-01-01' && byRepo['lodash/lodash'].tau_v > 50);

// ── D · Governed automation on a repo workflow ──────────────────────────────
console.log('\nD — DELEGATE/PROVE governing project automation');
const wallet = new CertificateWallet();
const table = new DelegationTable(wallet);
table.grant({ agent: 'ci-bot', action: 'rerun-tests', permission: 'allow', maxStake: 0 });
const deployGrant = table.grant({ agent: 'deploy-bot', action: 'deploy-staging', permission: 'allow', maxStake: 100 });

const rerun = await table.check({ agent: 'ci-bot', action: 'rerun-tests', stake: 0 });
const stagingOk = await table.check({ agent: 'deploy-bot', action: 'deploy-staging', stake: 50 });
const stagingBig = await table.check({ agent: 'deploy-bot', action: 'deploy-staging', stake: 5000 });
const forcePush = await table.check({ agent: 'deploy-bot', action: 'force-push-main', stake: 0 });
table.revoke(deployGrant.id);
const afterRevoke = await table.check({ agent: 'deploy-bot', action: 'deploy-staging', stake: 10 });

ok('ci-bot may re-run tests (explicit grant)', rerun.decision === 'allow');
ok('deploy-bot may deploy staging within its stake cap', stagingOk.decision === 'allow');
ok('over-cap deploy denied with the reason', stagingBig.decision === 'deny' && /exceeds cap/.test(stagingBig.reason));
ok('force-push to main denied by default (no grant)', forcePush.decision === 'deny');
ok('one-tap revocation takes effect immediately', afterRevoke.decision === 'deny');

// The audit trail: append a real threat audit, verify the chain, prove tamper-evidence.
const threatAudit = audit(THREATS[0][0]);
await wallet.append('audit', {
  verdict: threatAudit.verdict, p: threatAudit.p_manipulative,
  mechanism_lexicon: threatAudit.mechanism_lexicon,
});
const v1 = await wallet.verify();
ok('audit trail covers every delegation decision + the audit itself', wallet.chain.length === 6, `len=${wallet.chain.length}`);
ok('hop-envelope stamp present (mechanism_lexicon=consumer-v1)', wallet.chain[5].payload.mechanism_lexicon === 'consumer-v1');
ok('certificate chain verifies clean', v1.ok);
wallet.chain[2].payload.decision = 'allow';        // adversarial edit of a past deny
const v2 = await wallet.verify();
ok('editing a past decision is detected and located', !v2.ok && v2.brokenAt === 2, JSON.stringify(v2));

console.log(`\n  RESULT: ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
