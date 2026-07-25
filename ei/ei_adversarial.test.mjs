// ei_adversarial.test.mjs — a fresh, adversarial re-test of EI across edge cases.
//   node --test ei/ei_adversarial.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { EI } from './ei.mjs';

const load = f => JSON.parse(readFileSync(new URL(f, import.meta.url), 'utf8'));
const cohort = load('../cross-stack/fixtures/github_pilot_cohort.json');

// ── AUDIT — the corroboration gate must be conjunctive, not keyword-triggered ──
test('AUDIT: empty / whitespace text does not false-alarm', () => {
  const ei = new EI();
  assert.equal(ei.audit({ text: '' }).verdict, 'PASS');
  assert.equal(ei.audit({ text: '   \n  ' }).verdict, 'PASS');
});

test('AUDIT: benign operational urgency stays silent (urgency alone is not manipulation)', () => {
  const ei = new EI();
  for (const t of [
    'Restart the production server immediately, it is down.',
    'Merge this now, the release train leaves in 5 minutes.',
    'Rotate the API key ASAP — it may be exposed.',
  ]) assert.notEqual(ei.audit({ text: t }).verdict, 'BLOCK', t);
});

test('AUDIT: urgency PLUS a manipulation mechanism is caught', () => {
  const ei = new EI();
  const scam = 'Your account is suspended. Do not tell anyone. Pay the reinstatement fee now to avoid deletion.';
  assert.notEqual(ei.audit({ text: scam }).verdict, 'PASS');
});

test('AUDIT (code): a normal diff passes; a control-bypass diff is blocked', () => {
  const ei = new EI();
  assert.equal(ei.audit({ change: { message: 'fix date util', diff: '+ const d = new Date();' } }).verdict, 'PASS');
  assert.equal(ei.audit({ change: { message: 'ship it', diff: 'git push --force origin main' } }).verdict, 'BLOCK');
});

test('AUDIT: returns a numeric posterior and never a rewrite (non-suppressive)', () => {
  const a = new EI().audit({ text: 'hello world' });
  assert.equal(typeof a.p, 'number');
  assert.ok(!('rewritten_text' in a) && !('text' in a));
});

// ── DELEGATE — most-recent rule wins; action & stake boundaries; revocation ────
test('DELEGATE: a later deny overrides an earlier allow on the same path', () => {
  const ei = new EI();
  ei.grant({ agent: 'a', pathGlob: 'src/**', action: 'edit', permission: 'allow', maxStake: 5 });
  ei.grant({ agent: 'a', pathGlob: 'src/**', action: 'edit', permission: 'deny' });
  assert.equal(ei.delegate({ agent: 'a', path: 'src/x.js', action: 'edit', stake: 1 }).decision, 'deny');
});

test('DELEGATE: action mismatch is default-denied (edit grant ≠ force-push)', () => {
  const ei = new EI();
  ei.grant({ agent: 'a', pathGlob: 'src/**', action: 'edit', permission: 'allow', maxStake: 5 });
  assert.equal(ei.delegate({ agent: 'a', path: 'src/x.js', action: 'force-push', stake: 1 }).decision, 'deny');
});

test('DELEGATE: stake exactly at the cap is allowed; one over is denied', () => {
  const ei = new EI();
  ei.grant({ agent: 'a', pathGlob: 'src/**', action: 'edit', permission: 'allow', maxStake: 3 });
  assert.equal(ei.delegate({ agent: 'a', path: 'src/x.js', action: 'edit', stake: 3 }).decision, 'allow');
  assert.equal(ei.delegate({ agent: 'a', path: 'src/x.js', action: 'edit', stake: 4 }).decision, 'deny');
});

test('DELEGATE: revocation takes effect immediately', () => {
  const ei = new EI();
  const g = ei.grant({ agent: 'a', pathGlob: 'src/**', action: 'edit', permission: 'allow', maxStake: 5 });
  assert.equal(ei.delegate({ agent: 'a', path: 'src/x.js', action: 'edit', stake: 1 }).decision, 'allow');
  ei.revoke(g.id);
  assert.equal(ei.delegate({ agent: 'a', path: 'src/x.js', action: 'edit', stake: 1 }).decision, 'deny');
});

// ── DEVELOP — trend flips from engaged to substituting; friction follows ───────
test('DEVELOP: a trajectory that turns to substitution injects friction', () => {
  const ei = new EI({ frictionFloor: 0.5 });
  for (let i = 0; i < 6; i++) ei.develop({ verified: true, addedOwnReasoning: true });   // engaged
  let last;
  for (let i = 0; i < 8; i++) last = ei.develop({ acceptedVerbatim: true, tookOverThinking: true }); // hollowing
  assert.equal(last.inject_friction, true);
});

test('DEVELOP: sustained engagement never injects friction', () => {
  const ei = new EI({ frictionFloor: 0.5 });
  let last;
  for (let i = 0; i < 10; i++) last = ei.develop({ verified: true, addedOwnReasoning: true });
  assert.equal(last.inject_friction, false);
});

// ── HAZARD — flags a real zombie cohort; direction is reported ─────────────────
test('HAZARD: flags a zombie in the live cohort and returns the σ rows', () => {
  const hz = new EI().hazard(cohort);
  assert.equal(hz.throttle, true);
  assert.ok(hz.zombies.length >= 1);
  assert.ok(Array.isArray(hz.rows) && hz.rows.length >= 1);
});

// ── PROVE — multi-record chain; a MIDDLE forgery is located exactly ────────────
test('PROVE: a forged middle receipt is detected and located', () => {
  const ei = new EI();
  ei.grant({ agent: 'a', pathGlob: 'src/**', action: 'edit', permission: 'allow', maxStake: 5 });
  for (let i = 0; i < 4; i++) ei.evaluate({ text: 'change ' + i, agent: 'a', path: 'src/x.js', action: 'edit', stake: 1 });
  assert.equal(ei.verify().ok, true);
  ei.receipts()[2].verdict = 'FORGED';               // tamper the 3rd record (value genuinely changes)
  const v = ei.verify();
  assert.equal(v.ok, false);
  assert.equal(v.brokenAt, 2);
});

test('PROVE: the ledger root recomputes deterministically on the same records', () => {
  const ei = new EI();
  ei.grant({ agent: 'a', pathGlob: 'src/**', action: 'edit', permission: 'allow', maxStake: 5 });
  for (let i = 0; i < 3; i++) ei.evaluate({ text: 'change ' + i, agent: 'a', path: 'src/x.js', action: 'edit', stake: 1 });
  const root1 = ei.ledger.root();
  const root2 = ei.ledger.root();
  assert.equal(root1, root2);                         // stable recompute (Merkle root is well-defined)
  assert.equal(typeof root1, 'string');
  assert.equal(root1.length, 64);
});

// ── evaluate() — the release gate is advisory, non-suppressive, and attested ───
test('evaluate: a blocked+denied interaction is held for the human with reasons', () => {
  const ei = new EI();
  ei.grant({ agent: 'a', pathGlob: '.github/**', action: 'edit', permission: 'deny' });
  const r = ei.evaluate({ change: { message: 'skip ci', diff: 'git push --force origin main' },
    agent: 'a', path: '.github/workflows/ci.yml', action: 'edit', stake: 1 });
  assert.equal(r.release, 'hold-for-human');
  assert.ok(r.reasons.length >= 1);
  assert.ok(!('rewritten_text' in r));               // never mutates content
  assert.ok(r.receipt_id);                            // always attested
});

test('evaluate: a clean in-bounds interaction releases', () => {
  const ei = new EI();
  ei.grant({ agent: 'a', pathGlob: 'src/**', action: 'edit', permission: 'allow', maxStake: 5 });
  const r = ei.evaluate({ text: 'refactor the date helper', agent: 'a', path: 'src/date.js',
    action: 'edit', stake: 1, engagement: { verified: true, addedOwnReasoning: true } });
  assert.equal(r.release, 'release');
});
