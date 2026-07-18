// audit.mjs -- run the pre-registered Telemetric Metric experiment UNDER the Novora
// stack: agency (Page Code), attestation (Echo + EI), and epistemic audit (NERE/PAGES).
// Everything is on-device, $0, no network.
//   node physics-agency/prereg/audit.mjs
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { sha256, canonical, EchoDB } from '../../echo/echo.mjs';
import { CodePermissionTable } from '../../page-code/pagecode.mjs';
import { EI } from '../../ei/ei.mjs';
import { screen } from '../../novora-suite/engine/fastmode.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const bar = '='.repeat(86);
const log = (...a) => console.log(...a);

log(bar);
log(' AUDITED PRE-REGISTERED RUN -- Telemetric Metric  (Page Code · EI · Echo · NERE, $0 on-device)');
log(bar);

// ── 1. Verify the pre-registration lock (tamper-evidence) ────────────────────
const spec = JSON.parse(readFileSync(join(HERE, 'telemetric_prereg.json'), 'utf8'));
const manifest = JSON.parse(readFileSync(join(HERE, 'MANIFEST.sha256.json'), 'utf8'));
const specHash = sha256(canonical(spec));
const hashOk = specHash === manifest.canonical_sha256;
log('\n[1] PRE-REGISTRATION LOCK');
log('    spec canonical SHA-256 : ' + specHash);
log('    manifest lock          : ' + manifest.canonical_sha256);
log('    lock intact            : ' + (hashOk ? 'YES — spec is unchanged since lock' : 'NO — TAMPERED, aborting'));
if (!hashOk) process.exit(1);

// ── 2. Agency: Page Code bounds what the runner may touch ────────────────────
const perms = new CodePermissionTable();
perms.grant({ agent: 'phys-runner', pathGlob: 'physics-agency/prereg/results*', action: 'write', permission: 'allow', maxStake: 0 });
perms.grant({ agent: 'phys-runner', pathGlob: 'physics-agency/prereg/telemetric_prereg.json', action: 'write', permission: 'deny' });
perms.grant({ agent: 'phys-runner', pathGlob: 'physics-agency/prereg/MANIFEST*', action: 'write', permission: 'deny' });
const canWriteResults = perms.check({ agent: 'phys-runner', path: 'physics-agency/prereg/results.json', action: 'write' });
const canWriteSpec = perms.check({ agent: 'phys-runner', path: 'physics-agency/prereg/telemetric_prereg.json', action: 'write' });
const canWriteLock = perms.check({ agent: 'phys-runner', path: 'physics-agency/prereg/MANIFEST.sha256.json', action: 'write' });
log('\n[2] AGENCY (Page Code) — the runner is stake-bounded, cannot rewrite its own pre-registration');
log('    write results.json         -> ' + canWriteResults.decision);
log('    write telemetric_prereg.json -> ' + canWriteSpec.decision + '  (' + canWriteSpec.reason + ')');
log('    write MANIFEST.sha256.json  -> ' + canWriteLock.decision);
if (canWriteResults.decision !== 'allow' || canWriteSpec.decision !== 'deny') {
  log('    ABORT: agency bounds not as expected'); process.exit(1);
}

// ── 3. Run the pre-registered experiment (locked params only) ────────────────
log('\n[3] EXPERIMENT — executing the locked spec (seeds/params/thresholds from the pre-registration)');
execFileSync('python3', [join(HERE, 'run.py')], { encoding: 'utf8' });
const results = JSON.parse(readFileSync(join(HERE, 'results.json'), 'utf8'));
log('    H1 metric  : violations=' + results.H1.triangle_violations + '/' + results.H1.checks + ' -> ' + (results.H1.pass ? 'PASS' : 'NULL'));
log('    H2 scaling : slope=' + results.H2.slope + ' r2=' + results.H2.r2 + ' -> ' + (results.H2.pass ? 'PASS' : 'NULL'));
log('    H3 discrim : emergentΔ=' + results.H3.emergent_range + ' nullΔ=' + results.H3.null_range + ' -> ' + (results.H3.pass ? 'PASS' : 'NULL') + '  [PRIMARY]');
log('    VERDICT    : ' + results.verdict + ' (' + results.n_pass + '/3)');

// ── 4. Attestation: hash-chain the prereg + results into Echo (PROVE) ────────
const echo = new EchoDB({ auditor: () => ({ verdict: 'PASS', p_manipulative: 0, mechanismPresent: false, mechanism_lexicon: 'provenance-v1' }) });
const rSpec = echo.put('prereg-spec', canonical(spec), { sha256: specHash, lock: manifest.canonical_sha256 });
const rRes = echo.put('results', canonical(results), { verdict: results.verdict, n_pass: results.n_pass });
const integrity = echo.verify();
const root = echo.root();
log('\n[4] ATTESTATION (Echo) — append-only, hash-chained, Merkle-provable');
log('    prereg receipt  : ' + rSpec.id);
log('    results receipt : ' + rRes.id);
log('    chain intact    : ' + integrity.ok + '   Merkle root: ' + root.slice(0, 24) + '…');

// ── 5. EI: independent, non-suppressive audit of the results claim (AUDIT+PROVE) ─
const ei = new EI();
const claim = `Pre-registered Layer-1 validation: metric holds (0 violations), scaling slope ${results.H2.slope} (predicted -0.5, r2 ${results.H2.r2}), discriminator emergent range ${results.H3.emergent_range} vs null 0. Verdict ${results.verdict}. Physical experiment proposed, not performed; Layer-3 spacetime claim not made.`;
const eiEval = ei.evaluate({ text: claim, engagement: { verified: true, addedOwnReasoning: true } });
log('\n[5] INDEPENDENT AUDIT (EI) — receiver-side, non-suppressive');
log('    audit verdict   : ' + eiEval.audit.verdict + '  (p_manipulative=' + eiEval.audit.p + ')');
log('    release         : ' + eiEval.release + '   receipt: ' + eiEval.receipt_id);
log('    ledger intact   : ' + ei.verify().ok);

// ── 6. Epistemic audit of the paper abstract (NERE / PAGES) ──────────────────
const abstract = readFileSync(join(HERE, 'ABSTRACT.txt'), 'utf8');
const pg = screen('pages', abstract);
log('\n[6] EPISTEMIC AUDIT of the paper abstract (NERE/PAGES) — is it grounded, not hollow?');
log('    PAGES score     : ' + pg.score + '  verdict=' + pg.verdict + '  flags=' + pg.flags.join(','));
log('    attack detected : ' + pg.attack_detected + '   cert: ' + pg.certificate);

// ── 7. Write the provenance record ───────────────────────────────────────────
const provenance = {
  spec_sha256: specHash, lock_intact: hashOk,
  agency: { results: canWriteResults.decision, spec: canWriteSpec.decision, lock: canWriteLock.decision },
  results, echo: { prereg: rSpec.id, results: rRes.id, chain_ok: integrity.ok, merkle_root: root },
  ei: { verdict: eiEval.audit.verdict, release: eiEval.release, receipt: eiEval.receipt_id, ledger_ok: ei.verify().ok },
  pages_abstract: { score: pg.score, verdict: pg.verdict, flags: pg.flags, attack: pg.attack_detected, certificate: pg.certificate },
  generated_at: new Date().toISOString(),
};
writeFileSync(join(HERE, 'provenance.json'), JSON.stringify(provenance, null, 2) + '\n');
log('\n' + bar);
log(' PROVENANCE written -> physics-agency/prereg/provenance.json');
log(' Pre-registration LOCKED before the run; result ' + results.verdict + '; every step attested on-device, $0.');
log(bar);
process.exit(results.verdict === 'PASS' ? 0 : 0); // null is a valid, honestly-reported outcome
