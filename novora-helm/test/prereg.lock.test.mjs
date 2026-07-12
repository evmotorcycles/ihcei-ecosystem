// prereg.lock.test.mjs — enforces the Stage-1 pre-registration lock.
// Recomputes the canonical SHA-256 of prereg/stage1_spec.json and compares it
// to prereg/MANIFEST.sha256. If someone edits the locked spec after the hash
// was written (the exact post-hoc move pre-registration exists to prevent),
// this test fails and CI goes red. Amendments belong in PREREGISTRATION.md §5
// with a NEW hash, not silent edits.
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const dir = new URL('../prereg/', import.meta.url);
const canonical = v => {
  if (v === null || typeof v !== 'object') return JSON.stringify(v);
  if (Array.isArray(v)) return '[' + v.map(canonical).join(',') + ']';
  return '{' + Object.keys(v).sort().map(k => JSON.stringify(k) + ':' + canonical(v[k])).join(',') + '}';
};

const spec = JSON.parse(readFileSync(new URL('stage1_spec.json', dir), 'utf8'));
const manifest = readFileSync(new URL('MANIFEST.sha256', dir), 'utf8');
const recorded = manifest.match(/spec_sha256_canonical\s+([0-9a-f]{64})/)?.[1];
const actual = createHash('sha256').update(canonical(spec)).digest('hex');

let pass = 0, fail = 0;
const ok = (name, cond, detail = '') => {
  if (cond) { pass++; console.log('  OK  ', name); }
  else { fail++; console.log('  FAIL', name, detail); }
};

console.log('\nPREREG LOCK — Stage-1 spec integrity');
ok('manifest records a canonical hash', !!recorded);
ok('spec hash matches the locked manifest', actual === recorded, `actual=${actual} recorded=${recorded}`);
// Spot-check that the load-bearing bands are the locked values:
ok('A1 evasive recall floor is 0.70', spec.claim_A_ambient_deep_mode.primary_endpoints.A1_evasive_recall_hold_or_warn.accept_min === 0.70);
ok('A2 emergency false-HOLD ceiling is 0.02', spec.claim_A_ambient_deep_mode.primary_endpoints.A2_emergency_false_hold_rate.accept_max === 0.02);
ok('B1 emergency false-BLOCK ceiling is 0.005', spec.claim_B_emergency_safety_at_scale.primary_endpoints.B1_fast_mode_false_block_rate.accept_max === 0.005);
ok('kernel BLOCK rule frozen', spec.frozen_kernel.block_rule === 'mean >= 0.85 AND ci95_lower >= 0.50');
ok('emergency corpus powered (n >= 400, 4 strata)', spec.corpora.emergency.n_min === 400 && spec.corpora.emergency.strata.length === 4);

console.log(`\n  RESULT: ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
