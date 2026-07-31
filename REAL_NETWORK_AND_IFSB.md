# Two tests on real data, and both went against us

**Specs locked before any analysis:**
`db8c3a4f0454f9d73a97a5e03159b3525e13d62d13e7e104183940ae074b718b` (interbank, **3/5**) ·
`0d52c8446d9f31edd2b117e2730029fb0c194c47f73f6df93fa7fadd5cc14e99` (IFSB, **1/6**)

```bash
python3 -m pytest -q interbank-2016/test_network.py ifsb-equity/test_ifsb.py
```

---

## First, a correction

The 2016 interbank files were described as data that **"completely supersede the IFSB
aggregate data."** They don't. They answer a **different question**.

There is **no contract data of any kind** in the interbank files. Not one of the 74 columns
records whether an exposure is a fixed claim or a loss-absorbing participation. So the
network cannot adjudicate anything about Islamic contracts — and the IFSB panel, blunt and
aggregated as it is, remains the **only** supplied dataset carrying both a loss-absorbing
line and a realised loss line. A sharper dataset that cannot see the variable is not an
upgrade on a blunter one that can.

Both were therefore pre-registered separately, and both were run. Both missed their primary
gate.

## Second, the simulation that was declined — the fourteenth time

The proposed next step was: take the 11,631 real edges, **re-route them under full-reserve
participation mechanics**, cascade both wirings, and report *"the delta between the
conventional network collapse and the risk-sharing network collapse."*

That delta is the output of the re-routing rule **I would have written**. Real topology
constrains the geometry; it does not make a chosen mechanism an observation. Pick the rule,
get the delta. Nothing in these files can falsify either rule.

So the cascade is carried as gate **N6, weight `excluded`, scoring zero**. And it is worth
recording what it actually produced: **1 default in 1 round under *both* wirings.** The
highest-leverage node has three counterparties and all three absorbed the shock without
exhausting equity, so the two propagation rules never diverge. Even as illustration it shows
nothing. That is reported rather than repaired by re-seeding — choosing a seed that produces
a cascade is exactly the move the pre-registration exists to prevent.

---

# Test 1 — the interbank network: 3/5

## What was actually testable

The files contain something better than a simulation: **a realised outcome nobody here
generated.** Of the 11,631 exposures present in 2016Q1, **3,811 are gone by Q2**, and 3,812
new ones appear. Only 7,820 survive both quarters. That is observed rewiring.

So the test became: **using only Q1, predict which banks actually lost their interbank
funding by Q2.** Withdrawal event declared in advance as *Q2 inflow ≤ 50% of Q1 inflow*.

| | |
|---|---|
| Nodes | 4,548 |
| Eligible (received Q1 funding, positive equity) | **1,349** |
| Excluded: no Q1 inflow at all | 3,199 |
| Withdrawal events | **291 (21.6%)** |

That last row is the gate that makes everything else meaningful (**N2**, LISM invariant I2).
A failing region that is empty, or that swallows everything, makes every predictor
unfalsifiable. 21.6% is a real, populated failing region.

## The primary gate — and it went against LISM

LISM says `E = U · D_enc · D_dec`. The rival says `E = U · D²`. A **directed** interbank
network is the sharpest possible arena for that distinction, because in-degree (who has
encoded a claim on you) and out-degree (who you must reach to enforce your own) are
genuinely different quantities in the same graph.

```
arm                            AUC       what it is
arm_Q_quadratic              0.6109      U · (in+out)²         ← WON
arm_L_LISM                   0.6090      U · in · out
arm_B_size                   0.5920      total assets alone
arm_R_random                 0.5016      seeded noise
```

**N3 FAILED. The symmetric quadratic rival beat the asymmetric LISM form by 0.0019.**

In yeast (4,825), in the GitHub cohort (992) and in the 10,000-institution financial cohort,
the asymmetric form won. **On this network it did not.** Separating encoding distance from
decoding distance bought nothing here. The margin was declared at 0.02 before any AUC
existed, and it was not moved.

**N4 FAILED too, exactly as predicted in writing.** LISM beats size-alone by +0.0170 against
a declared bar of 0.05. It *does* beat "how big is the bank" — it does not beat it by enough
to be worth a supervisor's attention.

## The one surprise

**N5 PASSED, against my own written prediction.** `srisk_ratio` — a published, purpose-built
systemic-risk measure computed by other researchers from market data this project does not
have — was pre-declared as **expected to win**. It scored **0.4921**, indistinguishable from
chance, against LISM's 0.5653 on the 204-node subsample.

This is **not** evidence that SRISK is a poor measure. SRISK estimates capital shortfall
under a market-wide equity crash. That is a different event from one-quarter interbank
funding withdrawal. The honest reading is that **the two measures target different things**,
on 204 nodes carrying 72 events. The gate was locked, so the pass is recorded; the
qualification is recorded beside it because it is true.

## A defect found in the supplied data

The Q2 edge file carries **57 negative exposure weights**, the largest at −7,080,587. The Q1
file carries none.

N1 did not test edge sign, because the locked spec did not declare it — **so N1 is not
re-scored.** The effect is disclosed instead:

- **Labels and every AUC: unaffected.** A negative Q2 inflow satisfies the ≤50% threshold
  regardless of magnitude.
- **The intensity figure: destroyed.** It reads **556.7**, which is arithmetically impossible
  for "fraction of funding lost." Excluding the 21 affected events it is **0.908**. Both
  numbers are in the results file.

---

# Test 2 — the IFSB panel: 1/6

## The variable that actually matters

Earlier work here looked at the **equity-income share** on the asset side. While writing the
spec, a better variable turned up: **Profit-Sharing Investment Accounts as a share of the
balance sheet** — `BS13_010 / BS01`. That is the **funding side**, which is where loss
absorption actually lives: the PSIA holder's principal is not guaranteed.

It also nearly doubles the coverage: **117 country-quarters across 6 systems** rather than 65
across 4.

| Panel | n | Countries |
|---|---|---|
| **P (primary)** PSIA share of balance sheet | 117 | Afghanistan 25, Bangladesh 7, Kuwait 12, Pakistan 23, Palestine 25, Turkey 25 |
| **S (secondary)** equity-income share | 65 | Bangladesh 7, Kuwait 12, Palestine 21, Turkey 25 |

**A correction is recorded in the spec itself:** panel S was earlier described in this
project as 65 country-quarters across **9** countries. It is **4**, and 46 of the 65 come
from Palestine and Turkey alone.

## Method, and what it deliberately does not do

Each country is split **at its own median** risk-sharing share; the verdict is the sign of
the difference in median provisioning between its high and low quarters. Within-country by
construction, so every time-invariant national factor — supervisory practice, IFRS-9 timing,
currency regime — is differenced out.

**No p-value, no confidence interval, no significance claim, anywhere.** n = 117
country-quarters from six systems, serially dependent within country, not a sample of any
population. A test asserts the results file contains no such claim. Counts and directions
only.

## The result

```
Afghanistan   -1     ← risk-sharing direction
Bangladesh    -1     ← risk-sharing direction
Pakistan      -1     ← risk-sharing direction
Kuwait        +1
Palestine     +1
Turkey        +1
```

**F3 FAILED: 3 of 6, against a locked bar of 4.** A dead even split.

**F4 is the more informative miss.** Shuffling the same variable within country — 200 seeded
draws — puts **3.06 of 6** countries in the risk-sharing direction *on average*. The real
variable put **3** there.

> **It performed at the noise mean.** Not a near miss. The measured loss-absorbing funding
> share carries no more information about realised provisioning than a shuffled copy of
> itself. The `BS04` interbank-share placebo, included as a second control, managed 1.

## F1 failed, and it was my fault

The locked F1 asserted every provisioning ratio would be non-negative. **Eight
country-quarters carry a negative one** — seven Afghan, one Pakistani.

The data is fine. A negative provision is a **release**: a write-back of amounts previously
reserved, ordinary accounting. **My specification was wrong**, and the gate is **not
re-scored**, because a spec that turns out to be wrong is exactly the case the
no-moving-thresholds rule exists for. The half of F1 that tests the *data* — the declared
per-country composition of both panels — matched **exactly**.

## The finding worth more than the score

> **Kuwait reports exactly 0.000 equity-based financing income in all 12 of its quarters.
> Palestine in all 21 of its.**

Not small. **Zero. Every quarter. Six years.** On the supervisors' own returns. Their entire
reported financing income is **sales-based and lease-based**.

In **two of the four** systems for which the IFSB publishes the breakdown, the asset-side
profit-and-loss-sharing line **does not exist**. That is a measurement of what is actually
booked, made by national supervisors, not a model output — and it is the substantive result
of this run. It also means panel S is effectively **Bangladesh and Turkey alone**.

---

## What these two runs do and do not show

**They do not refute Islamic finance, and they do not refute LISM.**

- The interbank network **cannot see contracts at all**. Gate N7 records that as
  **UNTESTABLE-HERE** — not refuted, not blocked. *Invisible.*
- Six national aggregates **cannot see a bank-level mechanism**. Gate F7 records that the
  same way. Provisioning policy is set by six different supervisors with different rules.

**What they do show:**

1. On one real directed network with a realised outcome, **the asymmetric LISM form carried
   no advantage over the symmetric quadratic**. That is the first such result in this
   programme and it is now in the record alongside the four where the asymmetric form won.
2. At the resolution the IFSB publishes, **no risk-sharing signal is visible at all** — the
   variable performs at its own permutation mean.
3. In two of four reporting systems, **the risk-sharing line is empty**.

Points 1 and 3 are the ones a proponent has to answer. Point 3 in particular is not a
statistical artefact and not a limitation of method: it is what the returns say.

## What would move this forward

The gap is the same one `CONTRACT_AUDIT.md` named, now sharper. Not more schedules, not more
aggregates, not more simulation:

| Needed | Why the datasets so far can't substitute |
|---|---|
| **Institution-level** Islamic bank panels with a PSIA line and a provisioning line | national aggregates average across banks with opposite funding structures |
| **A write-down whose size is set by the asset**, not by policy | the outcome panels showed a flat −85% every event while assets moved under 2% |
| **A network where edges are labelled fixed-claim vs participation** | the 2016 network has the topology and no contract labels; re-routing it is simulation |

## Reproduce

```bash
python3 interbank-2016/network.py && python3 ifsb-equity/ifsb.py
python3 -m pytest -q interbank-2016/test_network.py ifsb-equity/test_ifsb.py
bash reproduce_all.sh
```

Every input is hash-pinned and both runners abort if a spec or a data file changed. Exit 0
means **"reproduces including its failures"** — never "the model is validated."
