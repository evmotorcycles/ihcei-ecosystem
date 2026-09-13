// pages_video.test.mjs — PAGES on the AI-video workflow.
//
//   node pages-video/pages_video.test.mjs
//
// Predictions locked before the run:
//   sha256 7ef0863e86d5435e3736eb0b05a9fd250a9926bd67f455337e826b7e0fd89bce
//
// FIVE HELD, ONE MISSED, and the miss found a limit that belongs on the box —
// see "P2 MISSED". A formatting defect is recorded too and NOT fixed here.
import { strict as A } from 'node:assert';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { groundFast } from '../pages/pages.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const PREREG_SHA = '7ef0863e86d5435e3736eb0b05a9fd250a9926bd67f455337e826b7e0fd89bce';

execFileSync('node', [join(HERE, 'run_pages_video.mjs')], { timeout: 300000 });
const r = JSON.parse(readFileSync(join(HERE, 'results_pages_video.json'), 'utf8'));
const F = r.findings;

let pass = 0, fail = 0;
const t = (name, fn) => {
  try { fn(); console.log('  OK  ', name); pass++; }
  catch (e) { console.log('  FAIL', name, '\n        ' + e.message); fail++; }
};

t('the predictions were locked before the run', () => {
  const got = createHash('sha256')
    .update(readFileSync(join(HERE, 'prereg_pages_video.md'))).digest('hex');
  A.equal(got, PREREG_SHA);
});

t('the sources are verbatim excerpts fetched today, not written here', () => {
  const f = JSON.parse(readFileSync(join(HERE, 'cards_frozen.json'), 'utf8'));
  A.equal(f._provenance.fetched_at, '2026-09-13');
  A.equal(f.models.length, 6);
  A.match(f._provenance.note, /curl to huggingface\.co still answers 000/);
  // real download figures, not invented
  A.equal(f.models.find(m => m.id === 'Lightricks/LTX-Video').downloads, 8200000);
});

console.log('\nGROUNDING');

t('P1 — a fabricated figure is caught and the alignment is capped', () => {
  // The card says 200,000 A100 hours. The script says 500000.
  A.equal(F.P1_fabricated_number_capped, true);
  A.ok(F.P1_addedNumbers.includes('500000'));
  A.ok(r.grounding[1].p_alignment <= 0.25);
  A.equal(r.grounding[1].grounded, false);
});

t('P2 MISSED — wrong-source and invented-figure are NOT distinguishable', () => {
  // PREDICTED: the wrong-source segment would read low on overlap with NO
  // fabricated numbers, so a creator could tell "you cited the wrong card"
  // apart from "you made a number up".
  //
  // MEASURED: overlap 0.29 and addedNumbers ["30","1216","704"] — the LTX
  // figures are real, and they are absent from the Mochi card only because the
  // card is the wrong one. The engine reports misattribution AS fabrication.
  //
  // Those need different fixes. "Check your figure" sends a person to verify a
  // number that is already correct; "you attached the wrong source" is the
  // actual errand. PAGES cannot currently say which, and that limit belongs on
  // the box rather than in a footnote.
  A.equal(F.P2_wrong_source_low_without_fabrication, false);
  A.equal(F.P2_wrong_source_overlap, 0.29);
  A.deepEqual(F.P2_wrong_source_addedNumbers, ['30', '1216', '704']);
  A.equal(r.grounding[2].grounded, false);
});

t('P6 — it is strict, not merely refusing everything', () => {
  A.equal(F.P6_at_least_one_grounded, true);
  A.equal(F.grounded_count, 2);
  A.equal(r.grounding[0].grounded, true);   // Wan2.2, overlap 0.95
  A.equal(r.grounding[3].grounded, true);   // HunyuanVideo, overlap 0.77
});

console.log('\nTHE TEMPORAL CHAIN');

t('P3 — swapping two words breaks the chain at exactly that segment', () => {
  A.equal(F.P3_word_swap_breaks_at_edited_index, true);
  A.equal(r.word_swap.brokenAt, 2);
  A.equal(r.word_swap.t, 24);
  A.equal(r.word_swap.reason, 'spoken text altered');
  A.equal(r.word_swap.stillCertified, false);
});

t('P4 — deleting a segment breaks the chain as a splice', () => {
  A.equal(F.P4_splice_breaks_chain, true);
  A.equal(r.splice.brokenAt, 1);
  A.equal(r.splice.reason, 'prev-link mismatch (splice)');
  A.equal(r.splice.stillCertified, false);
});

t('an untouched stream certifies', () => {
  A.equal(r.stream.certified_on_build, true);
  A.equal(r.stream.n_segments, 4);
});

console.log('\nTAP TO SOURCE');

t('P5 — every tap proves its passage is the one committed in the root', () => {
  A.equal(F.P5_all_taps_prove_inclusion, true);
  for (const tap of r.taps) {
    A.equal(tap.provenInGroundingSet, true);
    A.equal(tap.passageUnchanged, true);
    A.ok(tap.passageChars > 100);
  }
});

t('swapping the source passage under the published root fails the proof', () => {
  // somebody edits "10 billion" to "30 billion" in the cited passage
  A.equal(F.P5_tampered_source_fails, true);
});

console.log('\nTHE DEFECT THIS RUN FOUND');

t('a thousands separator reads as a fabricated number', () => {
  // The SVD card writes "~19,000kg CO2 eq."; the script writes "19000kg".
  // groundFast's number regex splits "19,000" into "19" and "000", so the
  // script's "19000" has no match and is reported as invented. It is not.
  //
  // Every creator writing "1,000 hours" in a source and "1000" in a script hits
  // this. NOT FIXED HERE: changing the number extractor changes a shipped
  // grounding engine and every reading in this directory, which is a decision
  // to take deliberately. Asserted as CURRENT BEHAVIOUR so a fix changes this
  // test in the same commit.
  const src = 'The resulting CO2 emission is ~19,000kg CO2 eq.';
  const claim = 'It produced 19000kg of CO2.';
  const g = groundFast(src, claim);
  A.ok(g.addedNumbers.includes('19000'),
    'if this now passes, the separator handling was changed');
  A.ok(F.P1_addedNumbers.includes('19000'));
});

t('PAGES proves no edit AFTER the build, never that the build was true', () => {
  // NULL-P2, asserted rather than trusted: a stream whose every segment is
  // ungrounded still certifies, because the chain is about tampering, not truth.
  A.equal(r.stream.certified_on_build, true);
  A.equal(F.grounded_count, 2);   // two of four ungrounded, and it still certifies
  const txt = readFileSync(join(HERE, 'prereg_pages_video.md'), 'utf8')
    .replace(/\s+/g, ' ');
  A.ok(txt.includes('says nothing about whether the transcript was true'));
  A.ok(txt.includes('A liar who commits their lie at t=0 gets a chain that verifies perfectly'));
});

console.log(`\n  RESULT: ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
