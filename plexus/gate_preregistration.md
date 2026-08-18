# Pre-registration — Agent Gate, and the paradigm as an enforced declaration

Written and hashed **before** `lens.js`, `gate.js` or their suites were run once.

---

## The correction this file exists to record

The proposed design gates an agent chain on a **fidelity product**: each hop
supplies a fidelity `Dᵢ`, the gate multiplies them, and the chain stops when
`∏Dᵢ < D_min`.

**This repository already retired that gate**, and the record is
`FLOOR_RETIREMENT.md`:

- The semantic sensor that would supply `D` is **blind most of the time**:
  `D_enc_raw = 0` for 89.8% of PRs and `D_dec_raw = 0` for 83.7% on the VS Code
  cohort (N = 3,685); it fires on 23.4%. A hard gate on a quantity you cannot
  measure three times in four is not operable.
- The pre-registered, SHA-256-locked confirmatory test on an unseen cohort
  (Kubernetes, ~4,979 PRs) returned a **fully-powered null, p = 0.735**.
- The replacement — a probabilistic hazard floor on enforcement latency `τ_v`
  and dissonance `σ` — reached **AUC 0.898** against **0.828** for the
  deterministic `D_gap` floor.

So Agent Gate is **not** built on `∏Dᵢ < D_min`. Building it there would
resurrect a gate this project falsified with its own data, and would do it
inside the tool whose entire pitch is that it prints its limits. `gate.js`
therefore contains no `D_min`, no fidelity product, and exposes the retirement
record as a function so the refusal lives in the code rather than in a document
somebody can stop reading.

---

## What Agent Gate actually does

Three readouts, kept apart, because two are measurable per chain and the third
is not measurable at all until there is a history.

**1 · Perimeter.** The person names which parts of their plan an agent may
touch. Deterministic set arithmetic, no threshold: a link with both ends inside
is traversable, a link with one end outside is refused and names the part it
would have reached.

**2 · Sole routes.** From SPAR. A link whose bearing is 1.000 is in every
spanning tree — there is no other way round it. A hop across such a link has no
fallback. This is Foster arithmetic, not a tunable.

**3 · Hazard.** A JS port of `tau_v_monitor/core.py`, parity-checked against it.
Rising time-to-close on flagged problems, measured against the chain's *own*
history. Below the minimum window count it returns `INSUFFICIENT_DATA`, which on
a fresh install is every install.

---

## The worked plan (so the predictions are checkable)

Parts: `The supplier's price`, `The delivery date`, `The quote`, `The deposit`,
`The order ships`. Unit links: price→quote, date→quote, quote→deposit,
deposit→ships, date→ships. The agent is allowed to touch the first three parts
only.

---

## Predictions

| # | Prediction | Value |
|---|---|---|
| G1 | Perimeter: links wholly inside / crossing out / wholly outside | 2 / 2 / 1 |
| G2 | The two crossing links name the parts they would have reached | `The deposit`, `The order ships` |
| G3 | Bearings: one pendant link at sole route, four cycle links equal | 1.000000 and 0.750000 ×4 |
| G4 | Foster: total bearing = parts − pieces | 4.000000 = 5 − 1 |
| G5 | Sole routes found | exactly 1 — price→quote |
| G6 | Hazard, flat history | `OK`, direction `no trend` |
| G7 | Hazard, rising history | direction `increasing`, status `WATCH` or `ALERT` |
| G8 | Hazard, three closed items total | `INSUFFICIENT_DATA` |
| G9 | **Parity.** For every synthetic history, the JS port and `tau_v_monitor/core.py` agree on `status` and `trend_direction` exactly, and on `trend_p`, `trend_slope_per_window`, `robust_z`, `tail_ratio`, `baseline_tau_v`, `current_tau_v` | to 1e-9 |
| G10 | `gate.js` contains no `D_min`, no fidelity product, and invents no threshold beyond those `tau_v_monitor` already ships with its own disclaimer | asserted by reading the file |
| G11 | Every tool registered in `lens.js` declares at least one thing it cannot do **and** at least one check a person performs outside the software; one missing either is refused with a reason | refused |
| G12 | Every shipped page carries its tool's refusal sentence in the rendered HTML | asserted over the built files |

G9 is the one that could kill the port: a port nobody checks drifts, and then
the thing under test and the thing people touch stop being the same thing.
G10 and G11 are the ones that could kill the paradigm claim, and they are the
reason this is code and not a manifesto.

---

## Nulls, registered in advance

**NULL-G1 — the one that matters most, and it is about this file's own subject.**
A test can check that a refusal is **printed**. No test in this repository can
check that a refusal is **true**, or that printing it changes what anybody does.
"Mask versus lens" is a design commitment enforced at the level of *what the
software says about itself*, and that is strictly weaker than a claim about
honesty. Anyone reading the results should hold it at that strength.

**NULL-G2.** Nothing here shows an agent gated this way is safer, cheaper or
better. Perimeter and sole routes are structure; hazard is latency. Whether a
person acts on any of it is unmeasured and unmeasurable from inside the tool.

**NULL-G3.** On a fresh install, hazard reads `INSUFFICIENT_DATA` every time,
because τ_v is a trend over a history and a first run has none. That is the
honest answer and not a defect, and it is the same shape as the commons'
contribution rate refusing to return a number before anything has shipped.

**NULL-G4.** Six of the seven products named in the brief — Project Bay, Shapes
Commons bounty, Embed SDK, Desk shell, Institution kit, Provenance tape — are
**designs, not builds**. Only Agent Gate is implemented here. A design and a
measured thing must not be reported in the same voice.

---

## What would falsify this

1. **G9 fails.** The browser answers differently from the Python. Then the gate
   on a phone is not the gate that was tested, and it should not ship.
2. **G10 fails.** A fidelity product reappears. Then the tool resurrects a floor
   this project retired with a p = 0.735 null, inside the tool that claims to
   print its limits, and the paradigm is decoration.
3. **The declarations drift.** If a page's promise and its tool's declaration
   ever disagree, G12 fails in the same commit — which is the point of putting
   the philosophy in a test rather than a document.
