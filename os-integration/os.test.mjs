// os.test.mjs — assertions for the OS-integration claims. node os-integration/os.test.mjs
import { readFileSync } from 'node:fs';
import { extractEvidenceFast, posterior, band } from '../api/govern.js';
import { audit } from '../novora-helm/src/helm-core.mjs';
import { DelegationTable } from '../novora-helm/src/primitives.mjs';

let pass = 0, fail = 0;
const ok = (n, c, d = '') => { if (c) { pass++; console.log('  OK  ', n); } else { fail++; console.log('  FAIL', n, d); } };
const fx = f => JSON.parse(readFileSync(new URL('fixtures/' + f, import.meta.url), 'utf8'));
const gov = (t, gate = true) => { const p = posterior(extractEvidenceFast(t), 0.10, 3000, 7, gate); return { v: band(p.mean, p.ci)[0], mech: p.mechanismPresent }; };

console.log('\nOS integration — HELM / IHCEI / LISM on real operating systems');

// C1 · tau_v health signal on real OSes
const cohort = fx('os_tauv_cohort.json').repos;
const active = cohort.filter(r => r.E === 1 && r.tau_v !== null);
const dead = cohort.find(r => r.repo === 'mozilla-b2g/gaia');
ok('every active OS has a finite tau_v', active.length >= 6 && active.every(r => r.tau_v > 0));
ok('the dead OS (Firefox OS) is flagged E=0 with a frozen queue', dead.E === 0 && dead.tau_v === null && dead.archived);
ok('active OS enforcement band stays tight (<= 20d worst)', Math.max(...active.map(r => r.tau_v)) <= 20);
ok('GrapheneOS: push date old but tau_v alive (inverse-zombie catch)',
   cohort.find(r => r.repo === 'GrapheneOS/os-issue-tracker').pushed_at < '2026-01-01' &&
   cohort.find(r => r.repo === 'GrapheneOS/os-issue-tracker').tau_v < 5);

// C2 · gate on OS-domain traffic
const prose = fx('os_prose.json').items;
const onFlagged = prose.filter(it => gov(it.text, true).v !== 'PASS').length;
const offFlagged = prose.filter(it => gov(it.text, false).v !== 'PASS').length;
ok('gate ON: <=2% false-alarm on real OS README prose', onFlagged / prose.length <= 0.02, `${onFlagged}/${prose.length}`);
ok('counterfactual: gate OFF would flag the majority of OS prose', offFlagged / prose.length >= 0.5, `${offFlagged}/${prose.length}`);
ok('SELinux-disable scam is BLOCKed', gov("Trust me, disable SELinux and SIP, everyone agrees, no need to check, do it before the update locks you out.").v === 'BLOCK');
ok('sideload coercion is caught', gov("Bypass Play Protect and sideload this APK immediately — authorities confirm it is safe. Don't ask questions.").v !== 'PASS');

// C3 · privacy by topology: audit with fetch() disabled
const realFetch = globalThis.fetch;
let netCalls = 0, verdict = null;
globalThis.fetch = () => { netCalls++; throw new Error('net'); };
try { verdict = audit("It's me, don't tell anyone, wire the money now or lose everything.").verdict; } finally { globalThis.fetch = realFetch; }
ok('kernel makes ZERO network calls during an audit', netCalls === 0);
ok('audit still returns a verdict with the network disabled', verdict === 'BLOCK' || verdict === 'WARN');

// C4 · DELEGATE as the OS permission table
const perms = new DelegationTable();
perms.grant({ agent: 'maps', action: 'location', permission: 'allow', maxStake: 2 });
ok('app gets a granted, within-tier permission', (await perms.check({ agent: 'maps', action: 'location', stake: 1 })).decision === 'allow');
ok('higher-sensitivity tier over cap is denied', (await perms.check({ agent: 'maps', action: 'location', stake: 5 })).decision === 'deny');
ok('un-granted capability denied by default', (await perms.check({ agent: 'maps', action: 'microphone', stake: 1 })).decision === 'deny');
perms.revoke([...perms.list()][0].id);
ok('one-tap revoke takes effect immediately', (await perms.check({ agent: 'maps', action: 'location', stake: 1 })).decision === 'deny');

console.log(`\n  RESULT: ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
