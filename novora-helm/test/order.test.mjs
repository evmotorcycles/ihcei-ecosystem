// order.test.mjs — the hierarchy, and whether it can actually refuse anything.
// ============================================================================
// A hierarchy that cannot turn anything away is a diagram. These tests exist to
// find out whether this one is load-bearing.
import { strict as A } from 'node:assert';
import {
  LAYERS, layer, escalation, STAGES, GOVERNANCE, REASONING,
  TEN, SOPS, LIMITS, GO_CHECK, settled,
} from '../src/order.mjs';

let pass = 0, fail = 0;
const t = (name, fn) => {
  try { fn(); console.log('  OK  ', name); pass++; }
  catch (e) { console.log('  FAIL', name, '\n        ' + e.message); fail++; }
};

console.log('\nTHE HIERARCHY');

t('three layers, strictly nested, in order', () => {
  A.equal(LAYERS.length, 3);
  A.deepEqual(LAYERS.map(l => l.id), ['reach', 'order', 'domain']);
  A.deepEqual(LAYERS.map(l => l.n), [1, 2, 3]);
});

t('a reading answering its own layer is fine', () => {
  const r = escalation({ measuredAt: 'reach', answers: 'reach', where: 'this test' });
  A.equal(r.ok, true);
  A.equal(r.gap, 0);
});

t('a reading answering INWARD is fine — that is what narrowing a question is', () => {
  const r = escalation({ measuredAt: 'order', answers: 'reach', where: 'this test' });
  A.equal(r.ok, true);
  A.equal(r.gap, -1);
});

t('THE ONE THAT MATTERS: a word count cannot settle whether someone is lying', () => {
  // This is HELM's own readout being pushed one layer too far, which is the
  // single most likely way this product gets misused.
  const r = escalation({ measuredAt: 'reach', answers: 'domain', where: 'helm audit readout' });
  A.equal(r.ok, false);
  A.equal(r.gap, 2);
  A.match(r.why, /bigger than the instrument/);
});

t('one layer out is refused too, not just two', () => {
  const r = escalation({ measuredAt: 'reach', answers: 'order', where: 'this test' });
  A.equal(r.ok, false);
  A.equal(r.gap, 1);
  A.match(r.why, /1 layer,? /);
});

t('a placement with no `where` is refused — same rule as the rest of the repo', () => {
  const r = escalation({ measuredAt: 'reach', answers: 'reach' });
  A.equal(r.ok, false);
  A.match(r.why, /where/);
});

t('an unknown layer is refused rather than ranked', () => {
  A.equal(escalation({ measuredAt: 'vibes', answers: 'reach', where: 'x' }).ok, false);
  A.equal(escalation({ measuredAt: 'reach', answers: 'vibes', where: 'x' }).ok, false);
});

t('layer() returns null for something that is not a layer', () => {
  A.equal(layer('nope'), null);
  A.equal(layer('reach').n, 1);
});

console.log('\nGOVERNANCE AND REASONING');

t('six stages: four governance, two reasoning, numbered 1..6', () => {
  A.equal(STAGES.length, 6);
  A.equal(GOVERNANCE.length, 4);
  A.equal(REASONING.length, 2);
  A.deepEqual(STAGES.map(s => s.n), [1, 2, 3, 4, 5, 6]);
  A.deepEqual(GOVERNANCE.map(s => s.n), [1, 2, 3, 4]);
  A.deepEqual(REASONING.map(s => s.n), [5, 6]);
});

t('every stage names what it refuses — a stage that refuses nothing is a heading', () => {
  for (const s of STAGES) {
    A.ok(s.refuses && s.refuses.trim().length > 10, `stage ${s.n} refuses nothing`);
    A.ok(s.asks && s.asks.trim().endsWith('?'), `stage ${s.n} does not ask anything`);
  }
});

t('every procedure ends in something a person does OUTSIDE the screen', () => {
  A.equal(SOPS.length, 6);
  for (const s of SOPS) {
    A.ok(s.does && s.does.trim(), `SOP ${s.n} has no action`);
    A.ok(s.refuse && s.refuse.trim(), `SOP ${s.n} refuses nothing, so it is advice`);
    A.ok(s.check && s.check.trim(), `SOP ${s.n} sends the reader nowhere`);
  }
});

console.log('\nSTAGE 3 — THE TEN');

t('ten elements, each asking something', () => {
  A.equal(TEN.length, 10);
  A.equal(new Set(TEN.map(e => e.id)).size, 10);
  // contains, not endsWith: two of the ten ask and then qualify ("Who does
  // what? Named, not implied."). endsWith would have forced worse copy to
  // satisfy a test, which is the tail wagging the product.
  for (const e of TEN) A.ok(e.asks.includes('?'), `${e.id} asks nothing`);
});

t('nothing filled means ten open, not a score of zero', () => {
  const r = settled({});
  A.equal(r.openCount, 10);
  A.equal(r.filled, 0);
  A.equal(r.open.length, 10);
});

t('A BLANK FIELD STAYS BLANK: whitespace is not a fill', () => {
  // The repo has this defect on record: a blank "amount paid" silently reading
  // 0 reported a credit of -62084. A whitespace-only answer is a blank answer.
  const r = settled({ terms: '   ', roles: '\n\t', dues: 'the tenant pays rent monthly' });
  A.deepEqual(r.openCount, 9);
  A.ok(r.open.includes('terms'));
  A.ok(r.open.includes('roles'));
  A.ok(!r.open.includes('dues'));
});

t('the readout names the blanks and carries NO percentage', () => {
  const r = settled({ terms: 'x' });
  A.ok(Array.isArray(r.open));
  // "never put a grade on the first screen" — the count of open questions is an
  // errand list; a percentage of completeness would be a mark.
  A.equal('score' in r, false);
  A.equal('percent' in r, false);
  A.equal('grade' in r, false);
});

t('a non-object is treated as nothing filled rather than throwing', () => {
  A.equal(settled(null).openCount, 10);
  A.equal(settled(undefined).openCount, 10);
  A.equal(settled('terms').openCount, 10);
});

console.log('\nWHAT IT SAYS ABOUT ITSELF');

t('the limits are stated and the last one is the one people misread', () => {
  A.ok(LIMITS.length >= 4);
  A.ok(LIMITS.some(l => /does not understand/i.test(l)));
  A.ok(LIMITS.some(l => /Saying nothing.*does not mean.*safe/i.test(l)),
    'the silence-is-not-a-clearance limit must be stated');
});

t('every limit and every next step is a full sentence, not a label', () => {
  for (const s of LIMITS.concat(GO_CHECK)) {
    A.ok(s.length > 25 && /[.!?]$/.test(s), `not a sentence: ${s}`);
  }
});

console.log(`\n  RESULT: ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
