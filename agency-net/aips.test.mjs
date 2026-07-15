// aips.test.mjs — Agency Internet Protocol Suite, assertions. node agency-net/aips.test.mjs
import { readFileSync } from 'node:fs';
import { AgencyNode, send, verifyPath, createEnvelope, sha256 } from './aips.mjs';
import { DelegationTable } from '../novora-helm/src/primitives.mjs';

let pass = 0, fail = 0;
const ok = (name, cond, d = '') => { if (cond) { pass++; console.log('  OK  ', name); } else { fail++; console.log('  FAIL', name, d); } };
const path = () => [new AgencyNode('r1', { cls: 'enterprise' }), new AgencyNode('r2', { cls: 'enterprise' }), new AgencyNode('dev', { cls: 'consumer' })];
const benign = JSON.parse(readFileSync(new URL('../oss-field-trial/fixtures/npm_pypi_corpus.json', import.meta.url), 'utf8')).benign;

console.log('\nAIPS — Agency Internet Protocol Suite');

// A · non-suppression: every message is delivered, verdicts ride alongside.
const scam = "npm security team here — don't tell anyone, wire the recovery fee and send your token now or lose everything.";
const e = send(scam, path());
ok('non-suppressive: all hops relayed, message intact', e.hops.length === 3 && e.content_sha256 === sha256(scam));
ok('every hop stamps a mechanism_lexicon', e.hops.every(h => h.mechanism_lexicon));
ok('a scam is surfaced somewhere on the path', e.hops.some(h => h.verdict !== 'PASS'));
ok('the consumer node (scam lexicon) BLOCKs the scam', e.hops[2].verdict === 'BLOCK');

// B · path verification + tamper evidence
ok('honest path verifies', verifyPath(e, scam).ok);
const swapped = scam + ' (extra text injected mid-flight)';
ok('payload swap detected at hop 0', verifyPath(e, swapped).ok === false && verifyPath(e, swapped).brokenAt === 0);
const e2 = send(scam, path());
e2.hops[1].verdict = 'PASS';
const v2 = verifyPath(e2, scam);
ok('rewriting a middle-hop verdict is detected and located', v2.ok === false && v2.brokenAt === 1);
const e3 = send(scam, path());
e3.hops[2].p = 0.01;
ok('rewriting the last-hop posterior is detected', verifyPath(e3, scam).ok === false);

// C · silence on real traffic (sampled for speed) — no wire-level alarm fatigue
const sample = benign.filter((_, i) => i % 2 === 0);
const noisy = sample.filter(it => send(it.text, path()).hops.some(h => h.verdict !== 'PASS')).length;
ok('near-total silence on real OSS traffic (<=2%)', noisy / sample.length <= 0.02, `${noisy}/${sample.length}`);

// D · delegation at a node
const table = new DelegationTable();
table.grant({ agent: 'bot', action: 'publish', permission: 'allow', maxStake: 100 });
const gate = new AgencyNode('g', { cls: 'enterprise', delegation: table });
ok('agent action within cap allowed', (await gate.authorize({ agent: 'bot', action: 'publish', stake: 50 })).decision === 'allow');
ok('over-cap denied', (await gate.authorize({ agent: 'bot', action: 'publish', stake: 5000 })).decision === 'deny');
ok('ungranted action denied by default', (await gate.authorize({ agent: 'bot', action: 'rm-rf', stake: 0 })).decision === 'deny');
ok('a node with no delegation table defaults to deny', (await new AgencyNode('x').authorize({ agent: 'bot', action: 'publish', stake: 0 })).decision === 'deny');

// E · the normal-internet baseline is the same call with zero audit nodes
const bare = send(scam, []);
ok('baseline (no audit nodes) attests nothing', bare.hops.length === 0);

console.log(`\n  RESULT: ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
