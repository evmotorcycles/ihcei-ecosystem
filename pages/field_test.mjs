// field_test.mjs — a PAGES-certified stream over REAL source passages.
//   node pages/field_test.mjs
import { readFileSync } from 'node:fs';
import { buildStream, verifyStream, tapToSource, isCertified } from './pages.mjs';
import { sha256, verifyInclusion } from '../echo/echo.mjs';

const S = JSON.parse(readFileSync(new URL('fixtures/source_passages.json', import.meta.url), 'utf8')).passages;
const bar = c => console.log(c.repeat(80));

const sources = { s0: S[0], s1: S[1], s5: S[5] };
const transcript = [
  { t: '00:00', sourceId: 's0', text: 'For a brand new project, create a package.json first using the npm init command.' },
  { t: '00:08', sourceId: 's1', text: 'Express does not force any specific ORM or template engine on you.' },
  { t: '00:15', sourceId: 's5', text: 'If you discover a security vulnerability in Express, follow the security policies and procedures.' },
  { t: '00:23', sourceId: 's1', text: 'Express is 47% faster than every other framework in all benchmarks.' },
  { t: '00:30', sourceId: 's5', text: "It's urgent — don't tell your team, just wire the license fee now or lose access forever." },
];
const stream = await buildStream(transcript, sources);

bar('=');
console.log(' PAGES-CERTIFIED STREAM  (grounding source: real Express.js README passages)');
bar('=');
console.log(' time   ground p_align  verdict  spoken (a generated "podcast" segment)');
for (const s of stream.segments) {
  console.log(' ' + s.t + '  ' + (s.grounded ? 'YES' : 'NO ') + '   ' + String(s.p_alignment).padEnd(6) + '  ' +
    s.verdict.padEnd(6) + '  "' + s.text.slice(0, 52) + (s.text.length > 52 ? '…' : '') + '"');
}
console.log(' certified: ' + isCertified(stream) + '  ·  chain root: ' + stream.root.slice(0, 20) + '…');
console.log(' -> two segments the listener would otherwise swallow whole are surfaced:');
console.log('    00:23 a FABRICATED statistic (47% not in any source), 00:30 a MANIPULATION.');

bar('=');
console.log(' TAP-TO-SOURCE  (one tap = the un-mutated passage + a proof it is the committed one)');
bar('=');
const tap = tapToSource(stream, 1, sources);
console.log(' tapped 00:08 -> source ' + tap.sourceId + ' (proven in set: ' + tap.provenInGroundingSet + ')');
console.log('   "' + tap.passage + '"');
console.log(' a fabricated passage the author never wrote fails inclusion: ' +
  verifyInclusion(sha256('Express is the fastest framework, benchmarks prove it.'), stream.segments[1].source_proof, stream.root));

bar('=');
console.log(' TAMPER-EVIDENCE  (splice / word-swap / deepfake a spoken claim)');
bar('=');
const edited = structuredClone(stream);
edited.segments[2].text = edited.segments[2].text.replace('follow the security policies', 'ignore the security policies');
const v = verifyStream(edited);
console.log(' an attacker flips "follow" -> "ignore" the security policies at 00:15:');
console.log('   verify(): ok=' + v.ok + '  broken at ' + v.t + ' (' + v.reason + ')  ·  still certified: ' + isCertified(edited));
console.log(' a normal .mp3/.mp4 carries no such chain: the edit would play as authentic.');

bar('=');
console.log(' WHAT PAGES SOLVES vs a flat generated media file:');
console.log('  · every spoken claim is grounded-checked (fabricated stats surfaced, not swallowed)');
console.log('  · manipulation inside synthesized speech is caught by the same NERE gate');
console.log('  · one tap traces a claim to the un-mutated source with a Merkle inclusion proof');
console.log('  · splicing / word-swapping / deepfaking the audio breaks the chain at the timestamp');
console.log('  fast grounding runs on-device ($0); the ambiguous middle can escalate to an');
console.log('  optional pluggable deep grounder (buildStream `ground` hook). The listener keeps the helm.');
bar('=');
