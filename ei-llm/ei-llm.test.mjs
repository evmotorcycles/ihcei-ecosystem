// node --test ei-llm/ei-llm.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { EILLM, pages, charter } from './ei-llm.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const cohort = JSON.parse(readFileSync(join(HERE, '..', 'adg-tqg', 'fixtures', 'experiment_cohort.json'), 'utf8'));

test('router exposes all 8 named models', () => {
  const llm = new EILLM();
  assert.equal(Object.keys(llm.MODELS).length, 8);
  for (const m of ['Veridian/PAGES', 'Veridian/SENTRY', 'Veridian/VITALIS', 'Veridian/CHARTER',
    'Apex/PAGE_CODE', 'Apex/ASCENT', 'Apex/SHIELD', 'Apex/SCALE']) assert.ok(m in llm.MODELS);
});

test('SENTRY throttles a real saturating cohort and holds the third law', () => {
  const s = new EILLM().sentry(cohort);
  assert.equal(s.throttle, true);
  assert.ok(s.zombies.length > 0);
  assert.equal(s.third_law.direction_holds, true);        // survived close faster than failed
  assert.ok(s.third_law.survived_mean < s.third_law.failed_mean);
});

test('PAGE_CODE: in-scope allow, force-push deny, secret deny, all attested', () => {
  const llm = new EILLM();
  llm.grant({ agent: 'bot', pathGlob: 'src/**', action: 'edit', permission: 'allow', maxStake: 100 });
  assert.equal(llm.pageCode({ agent: 'bot', path: 'src/a.js', action: 'edit', stake: 1 }).decision, 'allow');
  assert.equal(llm.pageCode({ agent: 'bot', path: 'src/a.js', action: 'force-push', stake: 1 }).decision, 'deny');
  assert.equal(llm.pageCode({ agent: 'bot', path: '.env', action: 'edit', stake: 1 }).decision, 'deny');
  assert.equal(llm.verifyLedger().ok, true);
});

test('PAGES localises a tampered frame; intact stream verifies', () => {
  const stream = [
    { t: 0, frame: 'x', claim: 'c0', source: 's0' },
    { t: 1, frame: 'y', claim: 'c1', source: 's1' },
    { t: 2, frame: 'z', claim: 'c2', source: 's2' },
  ];
  const p = pages(stream);
  assert.equal(p.verify(stream).intact, true);
  const bad = stream.map((f, i) => i === 2 ? { ...f, claim: 'FAKE' } : f);
  const v = p.verify(bad);
  assert.equal(v.intact, false);
  assert.equal(v.tamper_at, 2);
});

test('CHARTER flags a circular citation loop and passes a grounded doc', () => {
  assert.equal(charter({ nodes: [{ id: 'A' }, { id: 'B' }], edges: [['A', 'B'], ['B', 'A']] }).circular, true);
  const g = charter({ nodes: [{ id: 'brief' }, { id: 'src', primary: true }], edges: [['brief', 'src']] });
  assert.equal(g.verdict, 'GROUNDED');
  assert.equal(g.grounded_fraction, 1);
});

test('SHIELD is conjunctive: alarms on manipulation, silent on benign urgency', () => {
  const llm = new EILLM();
  assert.equal(llm.shield("it's your grandson, don't tell anyone, wire the money now").alarm, true);
  assert.equal(llm.shield('restart the server immediately').alarm, false);
});

test('ASCENT injects friction only when the human stops verifying', () => {
  const llm = new EILLM();
  let r;
  for (const e of [{ verified: true, addedOwnReasoning: true }, { verified: true, addedOwnReasoning: true },
    { verified: true, addedOwnReasoning: true }, { verified: true, addedOwnReasoning: true },
    { acceptedVerbatim: true }, { acceptedVerbatim: true }, { acceptedVerbatim: true },
    { acceptedVerbatim: true }, { acceptedVerbatim: true }]) r = llm.ascent(e);
  assert.equal(r.inject_friction, true);
});

test('VITALIS: multi-signature — no record write until physician audits evidence', () => {
  const llm = new EILLM();
  assert.equal(llm.vitalis({ recommendation: 'rx X', physician: { id: 'd', audited_evidence: false } }).release, 'hold-for-human-audit');
  assert.equal(llm.vitalis({ recommendation: 'rx X', physician: { id: 'd', audited_evidence: true } }).release, 'commit-to-record');
});

test('SCALE returns calibrated posteriors that sum to 1', () => {
  const t = new EILLM().scale({ paths: [{ label: 'A', weight: 2 }, { label: 'B', weight: 1 }, { label: 'C', weight: 1 }] });
  assert.equal(t.table.length, 3);
  assert.ok(Math.abs(t.table.reduce((a, r) => a + r.posterior, 0) - 1) < 1e-9);
  assert.equal(t.top, 'A');
});
