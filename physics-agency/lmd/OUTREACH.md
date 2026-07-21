# How we make contact — an honest outreach plan

Goal: reach the right scientists at Google Quantum AI (and, for the systems prong, DeepMind)
without burning credibility on the first impression. Everything below uses **verifiable**
channels only. Claims we could **not** verify are flagged in §4 — do not use them until you
confirm them from a primary source.

---

## 1. Sequence (priority order)

1. **Post a preprint first (arXiv, physics.quant-ph / gr-qc).** This establishes public,
   citable priority *before* outreach, and gives you a stable link to send. It also lets a busy
   PI evaluate in one click. Pair it with the repo (reproducible) and the provenance root.
   *Cost: $0. This is the single highest-leverage step.*
2. **Email individual PIs directly**, short and specific (template in §3). Find current contacts
   from **primary sources**: the Google Quantum AI team page, the authors' own
   university/lab pages, or the corresponding-author email on their most recent paper. Do **not**
   pull names/roles from secondary summaries.
3. **Use Google Quantum AI's official published collaboration/contact channel** if one exists at
   the time you send (check quantumai.google). Prefer a named PI over a generic inbox — a generic
   inbox is high-latency and low-signal.
4. **Conference / workshop route** (parallel, slower): APS March Meeting, Q2B, or a quantum-info
   workshop where the relevant groups present. A 3-minute in-person ask often beats cold email.

## 2. What to link them to (so an audit takes 5 minutes)

- The **one-command reproduce:** `python3 physics-agency/lmd/run_lmd.py` → 0/8640 triangle
  violations, slope −0.5000, R² 1.0.
- The **provenance check:** `python3 provenance/verify_provenance.py` → root
  `ebe469891cbc9dfe5e89e64b2784e156dba883933a11e3ea529132e3aebef2d5`.
- The **LMD spec hash** (pre-registered before the run):
  `7ea3099985c5be60e3808284a4dec8c202ac604e0ce5b0fe9a2b57ce9d558217`.
- The **pitch** (`GOOGLE_QUANTUM_AI_PITCH.md`), the **red-team** (`RED_TEAM.md`), and the real
  telemetry (`lism-cohorts/appendix/cohort_D_decay.csv`).
- Repo runs offline, `$0`, no proprietary API — a reviewer clones and verifies with no account.

## 3. Cover email — draft (fill the brackets; keep it short)

> **Subject:** Proposed non-destructive coupler-sweep test of a latency→distance scaling law on
> a superconducting array
>
> Dear Dr. [LAST NAME],
>
> I lead an open-science project (Novora Research Initiative) proposing a small, non-destructive
> experiment your group is uniquely equipped to run: pin two qubits at fixed coordinates, sweep
> the tunable-coupler bias J between them, read out operator-scrambling latency (OTOC / butterfly
> front), and fit log(distance) vs log(J).
>
> The prediction is pre-registered under a public SHA-256, and the analysis is blind. We state
> upfront that our offline result (slope −0.5000) is an algebraic property of graph effective
> resistance — **not** a discovery. The open, falsifiable question is physical: does the array
> reproduce that −½ contraction, or is it flat (`∂d/∂J = 0`, a fixed background)? Either outcome
> is publishable; the null is pre-registered with equal weight.
>
> Everything is reproducible offline at zero cost — clone and run `python3
> physics-agency/lmd/run_lmd.py` (repo: [LINK]; preprint: [arXiv LINK]). We bring the locked
> protocol, blinded analysis, and a pre-registered decoherence null control; we ask only for
> secondary diagnostic runtime and co-authorship with your group as experimental lead.
>
> Two paragraphs of detail and the full protocol are attached. Would a short call be worthwhile?
>
> With respect,
> [NAME], Novora Research Initiative — [CONTACT]

**Tips:** one ask, one link that works, no metaphysics in the email body (keep "emergent
spacetime" out — it's Layer-3 and reads as a red flag in a cold email). Lead with the honest
tautology concession; it signals competence faster than any claim.

## 4. Claims from secondary sources you MUST verify before using

These appeared in strategy notes we received; we could **not** confirm them and they must be
checked against primary Google sources before they go into any outbound message:

- **A specific Google intake form URL** (e.g. a `forms.gle/...` link) — do **not** submit to an
  unverified form; confirm the real intake path on quantumai.google first.
- **"GPAR / Google Public Sector – Program for Accelerated Research"** as a route — verify it
  exists and is the right channel before citing it.
- **Specific individuals and their exact titles** (e.g. "Principal Architect of X", "Chief
  Quantum Chemist") — confirm current names and roles from the team page or recent papers.
  Misnaming or mis-titling a scientist in the salutation is a first-impression killer.
- **"Quantum Echoes" as a named algorithm** and a **"December 2025 progress report"** — cite only
  if you can point to the primary Google publication.
- **A pre-registration hash `011b7b53…`** — this is our *earlier* telemetric spec in
  `physics-agency/prereg/`, **not** the LMD experiment. For LMD, cite `7ea30999…`. Using the wrong
  hash in front of reviewers who will recompute it looks careless.

## 5. After they reply

Use `RED_TEAM.md` — the three anticipated objections (tautology / decoherence / closed-source
absorption) and the honest defenses are rehearsed there. Hold the guardrails in
`GOOGLE_QUANTUM_AI_PITCH.md` §Appendix A: raw data (not smoothed summaries), symmetric-null
publication, independent verification preserved, and Layer discipline in any joint press.
