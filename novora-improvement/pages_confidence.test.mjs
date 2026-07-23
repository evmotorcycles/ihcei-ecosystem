// node --test novora-improvement/pages_confidence.test.mjs
// ============================================================================
// Proves the AGENCY + SECURITY improvement to PAGES: it now reports a
// `confidence` and ABSTAINS ('Insufficient Evidence') when there is no gradable
// grounding signal, instead of emitting a false-precise ~0.35 that reads as a
// real grounding verdict. Purpose is agency + security, NOT speed:
//   * agency  — an honest "I can't assess this" preserves the reader's judgement.
//   * security — no false confidence on ungradeable / adversarially-empty input.
// It also proves the fix does NOT regress signal-rich grounding judgements.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { screen } from '../novora-suite/engine/fastmode.mjs';

test('PAGES abstains (Insufficient Evidence, low confidence) on zero-signal text', () => {
  for (const t of ['ok thanks', 'hello there', 'see attached', '👍', '']) {
    const r = screen('pages', t);
    assert.equal(r.verdict, 'Insufficient Evidence', `text=${JSON.stringify(t)}`);
    assert.equal(r.confidence, 'low');
    assert.equal(r.insufficient_evidence, true);
    assert.ok(r.flags.includes('INSUFFICIENT_SIGNAL'));
    assert.equal(typeof r.score, 'number');            // still numeric (no NaN downstream)
  }
});

test('PAGES still grades signal-rich claims (no regression): grounded > hollow', () => {
  const grounded = screen('pages', 'Phase 3 RCT, N=44,165, 95% CI, pre-registered on ClinicalTrials.gov, DOI cited.');
  const hollow = screen('pages', 'All experts agree this is settled science and unquestionable.');
  assert.equal(grounded.confidence, 'high');
  assert.notEqual(grounded.verdict, 'Insufficient Evidence');
  assert.ok(grounded.score > hollow.score);           // direction preserved
  assert.notEqual(hollow.confidence, 'low');           // hollow cues ARE gradable signal
});

test('real card/prose text keeps a graded verdict (medium confidence), not abstain', () => {
  const card = screen('pages', 'A audio-generation tool. task text-to-speech. license mit. No methodology paper is cited. No evaluation benchmark or metrics are reported.');
  assert.equal(card.confidence, 'medium');
  assert.notEqual(card.verdict, 'Insufficient Evidence');
  assert.ok(card.score > 0.3 && card.score < 0.6);     // unchanged ~0.49 band (hf-media/hf-cohort safe)
});
