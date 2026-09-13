// run_pages_video.mjs — PAGES on the AI-video workflow.
//
//   node pages-video/run_pages_video.mjs
//
// Offline. Predictions locked in prereg_pages_video.md before this file
// existed. Sources are VERBATIM excerpts from six real open-source video model
// cards fetched today via the HF connector and frozen in cards_frozen.json.
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { buildStream, verifyStream, tapToSource, isCertified, groundFast }
  from '../pages/pages.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const PREREG_SHA = '7ef0863e86d5435e3736eb0b05a9fd250a9926bd67f455337e826b7e0fd89bce';

const got = createHash('sha256')
  .update(readFileSync(join(HERE, 'prereg_pages_video.md'))).digest('hex');
if (got !== PREREG_SHA) {
  console.error(`pre-registration edited\n locked ${PREREG_SHA}\n now    ${got}`);
  process.exit(1);
}

const frozen = JSON.parse(readFileSync(join(HERE, 'cards_frozen.json'), 'utf8'));
const sources = Object.fromEntries(frozen.models.map(m => [m.id, m.excerpt]));

// The script a person narrates over generated footage. Four segments, each
// declaring which card it is grounded against.
const transcript = [
  { t: 0,  sourceId: 'Wan-AI/Wan2.2-T2V-A14B',
    // S1 — restates its source closely
    text: 'Wan2.2 open-sources a 5B model with a compression ratio of 16x16x4, '
        + 'supporting text-to-video and image-to-video generation at 720P '
        + 'resolution with 24fps on consumer graphics cards like the 4090.' },
  { t: 12, sourceId: 'stabilityai/stable-video-diffusion-img2vid-xt',
    // S2 — a number that is NOT in the source. The card says 200,000 A100 hours.
    text: 'Training Stable Video Diffusion required approximately 500000 A100 '
        + '80GB hours and produced 19000kg of CO2 equivalent, generating 25 '
        + 'frames at 576x1024 resolution.' },
  { t: 24, sourceId: 'genmo/mochi-1-preview',
    // S3 — a true claim about LTX-Video, grounded against the WRONG card
    text: 'LTX-Video is the first DiT-based video generation model capable of '
        + 'generating high-quality videos in real-time, producing 30 FPS video '
        + 'at 1216x704 faster than it can be watched.' },
  { t: 36, sourceId: 'tencent/HunyuanVideo',
    // S4 — true of its source, loosely worded, no new figures
    text: 'HunyuanVideo was trained with over 13 billion parameters, which the '
        + 'authors describe as the largest among open-source models.' },
];

const out = {};
const stream = await buildStream(transcript, sources);

out.stream = {
  version: stream.v,
  root: stream.root,
  n_segments: stream.segments.length,
  certified_on_build: isCertified(stream),
  segments: stream.segments.map((s, i) => ({
    i, t: s.t, sourceId: s.sourceId,
    grounded: s.grounded, p_alignment: s.p_alignment,
    ground_mode: s.ground_mode, verdict: s.verdict,
  })),
};

// what groundFast saw per segment, including any fabricated figures
out.grounding = transcript.map((seg, i) => {
  const g = groundFast(sources[seg.sourceId], seg.text);
  return { i, t: seg.t, sourceId: seg.sourceId, ...g };
});

// ── P3: edit ONE segment's spoken words after the fact ──────────────────────
const edited = JSON.parse(JSON.stringify(stream));
edited.segments[2].text = edited.segments[2].text.replace('30 FPS', '60 FPS');
out.word_swap = { editedIndex: 2, ...verifyStream(edited),
                  stillCertified: isCertified(edited) };

// ── P4: splice — delete a segment entirely ─────────────────────────────────
const spliced = JSON.parse(JSON.stringify(stream));
spliced.segments.splice(1, 1);
out.splice = { removedIndex: 1, ...verifyStream(spliced),
               stillCertified: isCertified(spliced) };

// ── P5: tap to source ──────────────────────────────────────────────────────
out.taps = stream.segments.map((_, i) => {
  const tap = tapToSource(stream, i, sources);
  return { i, t: tap.t, sourceId: tap.sourceId,
           provenInGroundingSet: tap.provenInGroundingSet,
           passageUnchanged: tap.passage === sources[tap.sourceId],
           passageChars: tap.passage.length };
});

// a tap after somebody swaps the source passage under the published root
const tampered = { ...sources };
tampered['genmo/mochi-1-preview'] =
  tampered['genmo/mochi-1-preview'].replace('10 billion', '30 billion');
out.tampered_source_tap = (() => {
  const tap = tapToSource(stream, 2, tampered);
  return { provenInGroundingSet: tap.provenInGroundingSet };
})();

const g = out.grounding;
out.findings = {
  P1_fabricated_number_capped: g[1].addedNumbers.length > 0 && g[1].p_alignment <= 0.25,
  P1_addedNumbers: g[1].addedNumbers,
  P2_wrong_source_low_without_fabrication:
    !g[2].grounded && g[2].addedNumbers.length === 0,
  P2_wrong_source_overlap: g[2].overlap,
  P2_wrong_source_addedNumbers: g[2].addedNumbers,
  P3_word_swap_breaks_at_edited_index:
    out.word_swap.ok === false && out.word_swap.brokenAt === 2,
  P4_splice_breaks_chain: out.splice.ok === false,
  P5_all_taps_prove_inclusion: out.taps.every(t => t.provenInGroundingSet),
  P5_tampered_source_fails: out.tampered_source_tap.provenInGroundingSet === false,
  P6_at_least_one_grounded: g.filter(x => x.grounded).length >= 1,
  grounded_count: g.filter(x => x.grounded).length,
};
out._prereg = { file: 'pages-video/prereg_pages_video.md', sha256: got };
out._cards_sha256 = createHash('sha256')
  .update(readFileSync(join(HERE, 'cards_frozen.json'))).digest('hex');

writeFileSync(join(HERE, 'results_pages_video.json'), JSON.stringify(out, null, 1));

console.log('root', stream.root.slice(0, 16), '| certified', isCertified(stream));
console.log('\nsegment  source                                      overlap  added#     p  grounded');
for (const r of out.grounding) {
  console.log(`  t=${String(r.t).padStart(2)}    ${r.sourceId.slice(0, 42).padEnd(42)} `
    + `${String(r.overlap).padStart(6)}  ${String(r.addedNumbers.length).padStart(5)} `
    + `${String(r.p_alignment).padStart(6)}  ${r.grounded}`);
}
console.log('\nword swap :', JSON.stringify(out.word_swap));
console.log('splice    :', JSON.stringify(out.splice));
console.log('\nfindings  :', JSON.stringify(out.findings, null, 1));
