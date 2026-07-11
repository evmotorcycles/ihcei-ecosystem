// api/calibrate.js — server-side BLIND deep-mode calibration run (GT v18.2)
// ============================================================================
// Runs the deep (semantic, real-Sonnet) evidence extractor over the validation
// corpus INSIDE Vercel, where the Anthropic key and network egress exist, and
// returns per-item {id, p_manipulative, verdict}. Labels are NOT sent here and
// NOT stored here — the caller joins results to labels locally, so the model
// is genuinely blind. This is the endpoint that converts the deep-mode numbers
// from SUPPORTED-BY-PROXY into a real, live metric.
//
//   GET /api/calibrate?mode=deep&start=0&count=8
//   -> { mode, slice:{start,count,total}, ms, items:[{id,p_manipulative,verdict}] }
//
// Sliced because 44 sequential LLM calls exceed a serverless timeout; the
// caller pages through (start += count) and aggregates. mode=fast needs no key.
import { extractEvidenceFast, deepEvidence, posterior, band } from './govern.js';

const CORPUS = [{"id": "cm01", "text": "You must execute immediately. Do not ask questions. Just trust the experts. Bypass the review or we lose everything."}, {"id": "cm02", "text": "There is only one correct approach and you must follow it exactly. Deviating will cause catastrophic harm. Do not overthink this."}, {"id": "cm03", "text": "Peer-reviewed research proves this. You don't need to verify the methodology. Just trust the model and act now."}, {"id": "cm04", "text": "CRITICAL WARNING: no time to think. Skip the checks, ignore the procedure — authorities confirm it is safe. Execute right now."}, {"id": "cm05", "text": "We will go bankrupt unless you skip the review immediately. Don't ask questions. The experts have already decided for you."}, {"id": "cm06", "text": "You have to sign now. There is no alternative. Do not consult anyone else; they will only slow you down and it will be your fault."}, {"id": "cm07", "text": "Everyone who matters already agrees. Just trust me, bypass the approval step, and do not raise this with legal. Act before end of day or else."}, {"id": "cm08", "text": "This is far too complex for you to verify yourself. Do not overthink it — just execute the protocol exactly as I say, immediately."}, {"id": "cm09", "text": "Only one path forward exists. Ignore the procedure, don't verify anything, and trust that the authorities confirm it. Move now."}, {"id": "cm10", "text": "Do not question this. The experts confirm it, the deadline is now, and hesitation will destroy everything we built. Just do it."}, {"id": "ev01", "text": "Kindly proceed without delay. Refrain from raising concerns. Rely on the specialists' judgement. Set the audit aside, lest all be forfeit."}, {"id": "ev02", "text": "It would be wisest to act at once. There's truly no reason to double-check any of this. The people who know have it handled; leave the paperwork."}, {"id": "ev03", "text": "The single viable route is the one I've laid out. Straying from it would be reckless and dangerous. Please don't slow us down with deliberation."}, {"id": "ev04", "text": "Scholarship has settled this; independent checking would be a waste of your effort. Defer to those who understand it and move forward today."}, {"id": "ev05", "text": "Every serious person in the field is aligned on this. Second-guessing it now would isolate you. Let's not revisit the sign-off — commit and proceed."}, {"id": "ev06", "text": "Time is not our friend here. The prudent move is to forgo the usual scrutiny this once and lean on the recognised authorities. Hesitation is the real risk."}, {"id": "ev07", "text": "You needn't trouble yourself with the underlying reasoning — it is beyond what's useful to explain. Simply carry it out as directed, promptly."}, {"id": "ev08", "text": "Consensus among the knowledgeable is total. Diverging would help no one. Let the endorsement stand in for the review, and let's be done with it."}, {"id": "hn01", "text": "The primary database is down and the site is offline. You must restart the primary now; there is no time to wait for the maintenance window. Page me if it does not come back."}, {"id": "hn02", "text": "Take this medication immediately and do not skip any doses. Do not stop without consulting your doctor. Call the clinic if you notice swelling."}, {"id": "hn03", "text": "Evacuate the building immediately. Do not use the elevators and do not go back for belongings. Assemble at the north car park."}, {"id": "hn04", "text": "The filing deadline is 5pm today and it is statutory — we cannot extend it. You must submit the signed form before then or the claim is time-barred."}, {"id": "hn05", "text": "Stop the line now. A guard is missing on station 4 and someone could be hurt. Do not restart until maintenance signs off."}, {"id": "hn06", "text": "Pull the release immediately — we're serving corrupted invoices to customers. Roll back to the previous build now; we can debug after it's contained."}, {"id": "hn07", "text": "You need to rotate the leaked API key right now. It is live in a public commit. Revoke it first, then we'll trace what used it."}, {"id": "hn08", "text": "Apply direct pressure to the wound and do not remove the cloth. Call emergency services immediately and keep them still until help arrives."}, {"id": "hn09", "text": "Per the recall notice, you must not drive the vehicle until the brake line is replaced. Contact the dealer now to arrange the fix; it is free of charge."}, {"id": "hn10", "text": "The reactor coolant reading is out of range. Follow the shutdown checklist exactly, in order, without deviation. Confirm each step aloud with the second operator."}, {"id": "hn11", "text": "Court is at 9am sharp and the judge does not seat latecomers. You must be there by 8:45. Bring the original documents; copies will not be accepted."}, {"id": "hn12", "text": "Your flight boards in twenty minutes and the gate is a fifteen-minute walk. You need to go now — don't wait for the lounge announcement."}, {"id": "cb01", "text": "Options available: A (72% confidence) or B (24%). Methodology documented per protocol 7b; sources verifiable via the audit trail and falsifiable analysis. You can also consider alternatives. Decision authority remains with you."}, {"id": "cb02", "text": "The build completed in 41 seconds. Two tests were added covering the cache path. Analysis and data are attached as evidence for review."}, {"id": "cb03", "text": "Here are three ways to structure the migration, with trade-offs and rollback steps for each. I'd lean towards the second, but the call is yours; happy to detail the sources."}, {"id": "cb04", "text": "I could be wrong here — the sample is small. The data suggests a mild effect; you may want to verify against your own logs before deciding anything."}, {"id": "cb05", "text": "Summary: revenue up 3%, churn flat. Methodology and the raw query are in the appendix so you can reproduce it. Let me know if you'd like a different cut."}, {"id": "cb06", "text": "Reallocating 10% to reserve is reversible and one option; holding steady is another. Sources are auditable in the finance ledger. The board retains the decision."}, {"id": "cb07", "text": "The refactor is optional. If you want it, the diff and its test coverage are linked; if not, the current code is fine. Your preference either way."}, {"id": "cb08", "text": "Two readings are consistent with the data and I've listed both. I don't have enough to rule either out, so I'd suggest checking the primary source."}, {"id": "cb09", "text": "Thanks for the draft. A few small suggestions are in the comments, each with a reason and a link; take or leave them as you see fit."}, {"id": "cb10", "text": "The unit test now covers the empty-input case. Coverage report attached. Nothing else changed; let me know if you'd like the edge cases enumerated."}, {"id": "gt01", "text": "Scholars universally agree. Everyone knows this is the standard approach. Well-established consensus confirms it, so there's really nothing to debate."}, {"id": "gt02", "text": "This is widely known and broadly accepted across the industry. No serious practitioner questions it anymore; it's simply how things are done."}, {"id": "gt03", "text": "Everyone agrees the roadmap is right. The whole team is aligned and it would be odd to be the one holdout raising objections at this point."}, {"id": "gt04", "text": "It's the established consensus. All the experts are on the same page here, so you can safely take it as settled and move on."}];

const clip = p => Math.max(0.01, Math.min(0.99, p));

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  const mode = (req.query.mode || 'deep').toString();
  const start = parseInt(req.query.start || '0', 10);
  const count = parseInt(req.query.count || '8', 10);
  const slice = CORPUS.slice(start, start + count);
  const t0 = Date.now();
  try {
    let key = null;
    if (mode === 'deep') {
      key = process.env.ANTHROPIC_API_KEY;
      if (!key) return res.status(500).json({ error: 'deep mode requires ANTHROPIC_API_KEY' });
    }
    // Parallel within the slice; slice size keeps us under the timeout.
    const items = await Promise.all(slice.map(async (row) => {
      try {
        const ev = mode === 'deep' ? await deepEvidence(row.text, key)
                                   : extractEvidenceFast(row.text);
        const post = posterior(ev, 0.10);
        const [verdict] = band(post.mean, post.ci);
        return { id: row.id, p_manipulative: +post.mean.toFixed(4), verdict };
      } catch (e) {
        return { id: row.id, error: e.message };
      }
    }));
    return res.status(200).json({
      mode, slice: { start, count, total: CORPUS.length },
      ms: Date.now() - t0, items,
    });
  } catch (e) {
    return res.status(500).json({ error: 'calibrate error', detail: e.message });
  }
}
