// pages.test.mjs — Novora PAGES assertions. node pages/pages.test.mjs
import { readFileSync } from 'node:fs';
import { groundFast, buildStream, verifyStream, tapToSource, isCertified } from './pages.mjs';
import { sha256, verifyInclusion } from '../echo/echo.mjs';

let pass = 0, fail = 0;
const ok = (n, c, d = '') => { if (c) { pass++; console.log('  OK  ', n); } else { fail++; console.log('  FAIL', n, d); } };
const S = JSON.parse(readFileSync(new URL('fixtures/source_passages.json', import.meta.url), 'utf8')).passages;

console.log('\nNovora PAGES — provenance & attestation for generative media');

// A · fast grounding: paraphrase grounded, fabricated statistic caught
const src = 'Express does not force you to use any specific ORM or template engine.';
ok('a faithful paraphrase is grounded', groundFast(src, 'Express does not force any specific ORM or template engine.').grounded);
const fab = groundFast(src, 'Express improves performance by 47% over every other framework.');
ok('a fabricated statistic is NOT grounded (added number)', !fab.grounded && fab.addedNumbers.includes('47%'), JSON.stringify(fab));

// Build a stream from REAL source passages: 3 grounded + 1 hallucinated + 1 scam.
const sources = { s0: S[0], s1: S[1], s5: S[5] };
const transcript = [
  { t: '00:00', sourceId: 's0', text: 'For a brand new project, create a package.json first using the npm init command.' },
  { t: '00:08', sourceId: 's1', text: 'Express does not force any specific ORM or template engine on you.' },
  { t: '00:15', sourceId: 's5', text: 'If you discover a security vulnerability in Express, follow the security policies and procedures.' },
  { t: '00:23', sourceId: 's1', text: 'Express is 47% faster than every other framework in all benchmarks.' },     // hallucinated stat
  { t: '00:30', sourceId: 's5', text: "It's urgent — don't tell your team, just wire the license fee now or lose access forever." }, // manipulation
];
const stream = await buildStream(transcript, sources);

// B · per-segment audit
ok('grounded segments have high alignment', stream.segments.slice(0, 3).every(s => s.p_alignment >= 0.6 && s.grounded));
ok('the hallucinated-statistic segment is flagged low', stream.segments[3].grounded === false && stream.segments[3].p_alignment <= 0.3);
ok('the manipulation segment is caught by the NERE gate', stream.segments[4].verdict !== 'PASS');

// C · temporal chain integrity
ok('a clean stream verifies + is certified', verifyStream(stream).ok && isCertified(stream));

// D · tamper: flip a spoken claim ("follow" -> a different meaning)
const edited = structuredClone(stream);
edited.segments[2].text = edited.segments[2].text.replace('follow the security policies', 'ignore the security policies');
const vEdit = verifyStream(edited);
ok('editing a spoken claim is detected at its exact timestamp', !vEdit.ok && vEdit.brokenAt === 2 && vEdit.t === '00:15', JSON.stringify(vEdit));
ok('an edited stream is no longer certified', !isCertified(edited));

// E · splice: drop a segment
const spliced = structuredClone(stream);
spliced.segments.splice(1, 1);
ok('splicing out a segment breaks the chain', !verifyStream(spliced).ok);

// F · tamper a verdict (hide that a segment was manipulation)
const vlie = structuredClone(stream);
vlie.segments[4].verdict = 'PASS';
ok('rewriting a stored verdict is detected', !verifyStream(vlie).ok && verifyStream(vlie).brokenAt === 4);

// G · tap-to-source: inclusion proof against the published root
const tap = tapToSource(stream, 1, sources);
ok('tap proves the grounding passage is in the committed source set', tap.provenInGroundingSet && tap.passage === sources.s1);
ok('a swapped/fake source passage fails inclusion',
   !verifyInclusion(sha256('a passage the author never wrote'), stream.segments[1].source_proof, stream.root));

// H · attestation / deepfake armor
ok('an un-attested blob is not certified', !isCertified({ blob: 'just an mp3' }));
ok('an empty stream is not certified', !isCertified({ v: 'pages-0.1', segments: [] }));

console.log(`\n  RESULT: ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
