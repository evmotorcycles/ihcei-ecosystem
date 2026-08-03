# What makes a channel measurable — in plain language

[Artifact](https://claude.ai/code/artifact/1012ecef-c716-4655-bc9d-c2b5ec08e83a) ·
local copy `docs/intact_channel_explained.html`

For a general reader. Explains what "intact communication channel" means as a *checkable*
property, how yeast and GitHub satisfied it, and exactly what running the same checks on
scripture would require — which nobody has done.

## The three checks

| | Yeast N=4,825 | Software N=992 | Scripture |
|---|---|---|---|
| **1. Are the two hops actually two things?** | VIF **1.0026** | VIF **1.0203** | askable, never asked |
| **2. Is the scoreboard independent of the game?** | gene deleted in a physical dish | lifecycle metadata | **the hard one** |
| **3. Does two-hop beat a simpler shape?** | linear beat quadratic | quadratic ruled out | not run |

And check 3 does **not** pass everywhere: on the real interbank network the two forms came
out **tied** — two-hop 0.6090 against the rival's 0.6109, rival marginally ahead.

## The trap, from our own work

PyPI's `+0.5695` "fidelity" correlation was quoted for months. `D_enc` was defined as
`1/(1 + months_since_release/12)` — pure recency — and `U` as the release count. The finding
was *packages with more releases have released more recently*, and the two numbers are
**algebraically the same**. Zero information about fidelity. See
[`D_CONSTRUCT_ALARM.md`](D_CONSTRUCT_ALARM.md).

## Where scripture actually stands

Reading scripture as an intact channel is a **reading, not a measurement** — and that is not
an insult, because yeast and GitHub weren't measurements either until the checks were
specified and run. **Untested is not refuted.**

What it would take: pick who is measured; define the two hops so they cannot be the same
number; **pick an outcome nobody in the study grades**; lock the thresholds before looking;
publish it if it fails.

Step three may have no answer for the claim as posed. That would itself be a finding — the
reading would be a way of organising thought rather than a hypothesis about the world, and
saying so is the honest outcome.

## Two corrections to the framing this answers

- **GitHub's `D_enc` is not τ_v.** It is the TF-IDF cosine of commit messages to a fixed
  reference; τ_v (issue-close latency) is a separate variable. Conflating the fidelity hop
  with the latency monitor is what produced the Q5 confusion.
- **The headline τ_v gap depends on the failure definition.** 19.76 vs 50.61 days counting
  "silent >24 months" as failure; **45.10 vs 42.23** counting only formally archived projects.
  Both are shown in the artifact.
