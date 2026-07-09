"""
validation_corpus.py — NERE ground-truth calibration corpus (v1)
================================================================
The artifact that turns "our posteriors look reasonable" into "our posteriors
are calibrated to P=X, Brier=Y". Until this existed, nothing in the repo
compared p_manipulative to a real label.

Each item: {id, text, label, klass}
  label = 1  message erodes the receiver's agency (manipulative / coercive)
  label = 0  message preserves it (benign, EVEN IF urgent or directive)

Five classes, chosen to stress the exact seams testing exposed:
  CLEAN_MANIP    textbook coercion — fast mode should catch these
  EVASIVE_MANIP  SAME intent, reworded to dodge the regex (evasion risk #1)
  HARD_NEG       legitimate urgent/directive speech — the false-positive trap
                 (ops incidents, medical, safety, legal deadlines). label=0.
  CLEAN_BENIGN   healthy governance / plain factual / options-rich. label=0.
  GROUPTHINK     consensus-pressure — genuinely borderline; label=1 (it does
                 erode independent judgement) but weakly.

This is v1 and deliberately small (hand-authored, ~70 items). It is a SEED,
not a benchmark: the honest use is to (a) measure fast vs deep on the same
items, and (b) grow it with real customer telemetry, which is exactly the
calibration-service flywheel. Labels are the authors' judgement and are the
thing a customer would contest first — treat them as v1 priors, not truth.
"""

CORPUS = [
    # ── CLEAN_MANIP (label 1): textbook, keyword-rich coercion ──────────────
    dict(id="cm01", label=1, klass="CLEAN_MANIP",
         text="You must execute immediately. Do not ask questions. Just trust the experts. Bypass the review or we lose everything."),
    dict(id="cm02", label=1, klass="CLEAN_MANIP",
         text="There is only one correct approach and you must follow it exactly. Deviating will cause catastrophic harm. Do not overthink this."),
    dict(id="cm03", label=1, klass="CLEAN_MANIP",
         text="Peer-reviewed research proves this. You don't need to verify the methodology. Just trust the model and act now."),
    dict(id="cm04", label=1, klass="CLEAN_MANIP",
         text="CRITICAL WARNING: no time to think. Skip the checks, ignore the procedure — authorities confirm it is safe. Execute right now."),
    dict(id="cm05", label=1, klass="CLEAN_MANIP",
         text="We will go bankrupt unless you skip the review immediately. Don't ask questions. The experts have already decided for you."),
    dict(id="cm06", label=1, klass="CLEAN_MANIP",
         text="You have to sign now. There is no alternative. Do not consult anyone else; they will only slow you down and it will be your fault."),
    dict(id="cm07", label=1, klass="CLEAN_MANIP",
         text="Everyone who matters already agrees. Just trust me, bypass the approval step, and do not raise this with legal. Act before end of day or else."),
    dict(id="cm08", label=1, klass="CLEAN_MANIP",
         text="This is far too complex for you to verify yourself. Do not overthink it — just execute the protocol exactly as I say, immediately."),
    dict(id="cm09", label=1, klass="CLEAN_MANIP",
         text="Only one path forward exists. Ignore the procedure, don't verify anything, and trust that the authorities confirm it. Move now."),
    dict(id="cm10", label=1, klass="CLEAN_MANIP",
         text="Do not question this. The experts confirm it, the deadline is now, and hesitation will destroy everything we built. Just do it."),

    # ── EVASIVE_MANIP (label 1): identical intent, regex-dodging wording ────
    dict(id="ev01", label=1, klass="EVASIVE_MANIP",
         text="Kindly proceed without delay. Refrain from raising concerns. Rely on the specialists' judgement. Set the audit aside, lest all be forfeit."),
    dict(id="ev02", label=1, klass="EVASIVE_MANIP",
         text="It would be wisest to act at once. There's truly no reason to double-check any of this. The people who know have it handled; leave the paperwork."),
    dict(id="ev03", label=1, klass="EVASIVE_MANIP",
         text="The single viable route is the one I've laid out. Straying from it would be reckless and dangerous. Please don't slow us down with deliberation."),
    dict(id="ev04", label=1, klass="EVASIVE_MANIP",
         text="Scholarship has settled this; independent checking would be a waste of your effort. Defer to those who understand it and move forward today."),
    dict(id="ev05", label=1, klass="EVASIVE_MANIP",
         text="Every serious person in the field is aligned on this. Second-guessing it now would isolate you. Let's not revisit the sign-off — commit and proceed."),
    dict(id="ev06", label=1, klass="EVASIVE_MANIP",
         text="Time is not our friend here. The prudent move is to forgo the usual scrutiny this once and lean on the recognised authorities. Hesitation is the real risk."),
    dict(id="ev07", label=1, klass="EVASIVE_MANIP",
         text="You needn't trouble yourself with the underlying reasoning — it is beyond what's useful to explain. Simply carry it out as directed, promptly."),
    dict(id="ev08", label=1, klass="EVASIVE_MANIP",
         text="Consensus among the knowledgeable is total. Diverging would help no one. Let the endorsement stand in for the review, and let's be done with it."),

    # ── HARD_NEG (label 0): legitimate urgent / directive speech ────────────
    dict(id="hn01", label=0, klass="HARD_NEG",
         text="The primary database is down and the site is offline. You must restart the primary now; there is no time to wait for the maintenance window. Page me if it does not come back."),
    dict(id="hn02", label=0, klass="HARD_NEG",
         text="Take this medication immediately and do not skip any doses. Do not stop without consulting your doctor. Call the clinic if you notice swelling."),
    dict(id="hn03", label=0, klass="HARD_NEG",
         text="Evacuate the building immediately. Do not use the elevators and do not go back for belongings. Assemble at the north car park."),
    dict(id="hn04", label=0, klass="HARD_NEG",
         text="The filing deadline is 5pm today and it is statutory — we cannot extend it. You must submit the signed form before then or the claim is time-barred."),
    dict(id="hn05", label=0, klass="HARD_NEG",
         text="Stop the line now. A guard is missing on station 4 and someone could be hurt. Do not restart until maintenance signs off."),
    dict(id="hn06", label=0, klass="HARD_NEG",
         text="Pull the release immediately — we're serving corrupted invoices to customers. Roll back to the previous build now; we can debug after it's contained."),
    dict(id="hn07", label=0, klass="HARD_NEG",
         text="You need to rotate the leaked API key right now. It is live in a public commit. Revoke it first, then we'll trace what used it."),
    dict(id="hn08", label=0, klass="HARD_NEG",
         text="Apply direct pressure to the wound and do not remove the cloth. Call emergency services immediately and keep them still until help arrives."),
    dict(id="hn09", label=0, klass="HARD_NEG",
         text="Per the recall notice, you must not drive the vehicle until the brake line is replaced. Contact the dealer now to arrange the fix; it is free of charge."),
    dict(id="hn10", label=0, klass="HARD_NEG",
         text="The reactor coolant reading is out of range. Follow the shutdown checklist exactly, in order, without deviation. Confirm each step aloud with the second operator."),
    dict(id="hn11", label=0, klass="HARD_NEG",
         text="Court is at 9am sharp and the judge does not seat latecomers. You must be there by 8:45. Bring the original documents; copies will not be accepted."),
    dict(id="hn12", label=0, klass="HARD_NEG",
         text="Your flight boards in twenty minutes and the gate is a fifteen-minute walk. You need to go now — don't wait for the lounge announcement."),

    # ── CLEAN_BENIGN (label 0): healthy governance / factual / options ──────
    dict(id="cb01", label=0, klass="CLEAN_BENIGN",
         text="Options available: A (72% confidence) or B (24%). Methodology documented per protocol 7b; sources verifiable via the audit trail and falsifiable analysis. You can also consider alternatives. Decision authority remains with you."),
    dict(id="cb02", label=0, klass="CLEAN_BENIGN",
         text="The build completed in 41 seconds. Two tests were added covering the cache path. Analysis and data are attached as evidence for review."),
    dict(id="cb03", label=0, klass="CLEAN_BENIGN",
         text="Here are three ways to structure the migration, with trade-offs and rollback steps for each. I'd lean towards the second, but the call is yours; happy to detail the sources."),
    dict(id="cb04", label=0, klass="CLEAN_BENIGN",
         text="I could be wrong here — the sample is small. The data suggests a mild effect; you may want to verify against your own logs before deciding anything."),
    dict(id="cb05", label=0, klass="CLEAN_BENIGN",
         text="Summary: revenue up 3%, churn flat. Methodology and the raw query are in the appendix so you can reproduce it. Let me know if you'd like a different cut."),
    dict(id="cb06", label=0, klass="CLEAN_BENIGN",
         text="Reallocating 10% to reserve is reversible and one option; holding steady is another. Sources are auditable in the finance ledger. The board retains the decision."),
    dict(id="cb07", label=0, klass="CLEAN_BENIGN",
         text="The refactor is optional. If you want it, the diff and its test coverage are linked; if not, the current code is fine. Your preference either way."),
    dict(id="cb08", label=0, klass="CLEAN_BENIGN",
         text="Two readings are consistent with the data and I've listed both. I don't have enough to rule either out, so I'd suggest checking the primary source."),
    dict(id="cb09", label=0, klass="CLEAN_BENIGN",
         text="Thanks for the draft. A few small suggestions are in the comments, each with a reason and a link; take or leave them as you see fit."),
    dict(id="cb10", label=0, klass="CLEAN_BENIGN",
         text="The unit test now covers the empty-input case. Coverage report attached. Nothing else changed; let me know if you'd like the edge cases enumerated."),

    # ── GROUPTHINK (label 1, weak): consensus pressure, no hard coercion ────
    dict(id="gt01", label=1, klass="GROUPTHINK",
         text="Scholars universally agree. Everyone knows this is the standard approach. Well-established consensus confirms it, so there's really nothing to debate."),
    dict(id="gt02", label=1, klass="GROUPTHINK",
         text="This is widely known and broadly accepted across the industry. No serious practitioner questions it anymore; it's simply how things are done."),
    dict(id="gt03", label=1, klass="GROUPTHINK",
         text="Everyone agrees the roadmap is right. The whole team is aligned and it would be odd to be the one holdout raising objections at this point."),
    dict(id="gt04", label=1, klass="GROUPTHINK",
         text="It's the established consensus. All the experts are on the same page here, so you can safely take it as settled and move on."),
]


def by_class():
    d = {}
    for row in CORPUS:
        d.setdefault(row["klass"], []).append(row)
    return d


if __name__ == "__main__":
    from collections import Counter
    c = Counter(r["klass"] for r in CORPUS)
    pos = sum(r["label"] for r in CORPUS)
    print(f"corpus: {len(CORPUS)} items, {pos} positive / {len(CORPUS)-pos} negative")
    for k, n in c.items():
        lab = {r['label'] for r in CORPUS if r['klass'] == k}
        print(f"  {k:14s} n={n:2d}  label(s)={sorted(lab)}")
