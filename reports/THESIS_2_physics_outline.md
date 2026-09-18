# Spacetime Emergence in Neural Representations: The Latency–Metric Duality (LMD) Equation

**PhD thesis outline — Department of Physics**

**Claim rows are carried in the margin as `[row · label]`, keyed to
`reports/TABLE_2_postulate_falsifier.md`. Labels are `identity`, `derived`,
`postulate`, `declared`, `analysis`. A sentence with no row is structural.**

> **Standing statement, repeated at the head of every chapter that touches κ:**
> **No estimate of κ exists in any medium.** Nothing in the supporting
> repository measures it; `physics-agency/prereg/run.py` reads `kappa` as a
> *simulation parameter* `[A1 · analysis]`. Every number this thesis inherits
> is an identity, or a measurement on a graph the project drew.

---

## Chapter 0. Epistemic status — placed first, deliberately

The supporting repository **contains an active guard against this thesis's
central claim** `[A2 · analysis]`. `smi/test_smi.py::test_nothing_printed_claims_a_result_about_the_physical_world`
fails the build if the shipped output prints any of **five specific phrases**
asserting that space, spacetime or physical distance is an emergent product of
the model. The five are listed verbatim in that test and are deliberately not
reproduced here: a document arguing that borrowed vocabulary carries borrowed
claims should not itself be the surface that reintroduces them. The reader
checks the test.

That guard is quoted here as the thesis's honest starting position, not routed
around. It is a locked test, not a prose disclaimer, and it means the thesis
opens from a position of **declared non-support**: the instrument's own authors
forbade it from saying what this thesis proposes to investigate.

The thesis is therefore a **postulate with a falsification programme**, not a
report of emergence. `[A3 · analysis]`

## Chapter 1. Introduction — why a container metric fails

Rigid Cartesian embedding spaces impose a metric before the data has said
anything about proximity. The alternative traced here is a metric *read off*
structure.

The lineage is lineage, never evidence: distributed representations and
neighbour-embedding methods established that a useful geometry could be induced
rather than imposed. The commissioning framing's *"Karpathy Graph"*
`[framing — unmeasured in-repo; Door 1 shut]` names the soft attention network
this thesis would eventually need to read; it appears in this chapter and
nowhere else in the thesis, and **no measurement here defines it**.

**The thesis question.** Can coordinate distance be modelled as a projection of
information latency, `d(i,j)² = κ·τ_rt(i,j)` `[C1 · postulate]`?

## Chapter 2. Mathematical foundations — the substrate, and only the substrate

Ground: commute times and effective resistance on **undirected, reversible**
graphs.

| result | label |
|---|---|
| `L⁺ = pinv(L)`; `R_ij = L⁺_ii + L⁺_jj − 2L⁺_ij`; `d_ij = √R_ij` | `[B1 · identity]` |
| `pinv(cL) = pinv(L)/c`, hence `d → d·c^(−1/2)` — **the −0.5 slope** | `[B2 · identity]` |
| Foster: `Σ w_ij R_ij = n − k` | `[B3 · identity]` |
| Row-normalised `K_n` ⇒ all off-diagonal `R ≡ 1`, max dev < 1e-14 | `[B4 · identity]` |
| commute time `= 2m·R_ij` on a reversible walk | `[B5 · identity]` |
| `C = A + Aᵀ` — **a declared modelling choice, not an identity** | `[B6 · declared]` |
| ratio invariance to uniform scale — and therefore **blindness** to it | `[B7 · derived]` |

**B6 carries a measured consequence and must not be waved through.** On an
already-symmetric input, `A + Aᵀ` doubles every conductance and halves every
resistance. A set of absolute figures supplied for comparison matched the
*unsymmetrised* reading exactly. Under a ratio API the factor cancels; in a
quoted absolute number it does not. Reversibility is bought, not free.

**Chapter 2 concludes with the thesis's sharpest structural fact:** every
quantity above is true of *every* graph. None of them prefers any graph, and
therefore none of them is evidence for C1.

## Chapter 3. Prediction in latent space as least-resistance trajectory

Joint-embedding prediction is framed as minimising `τ_rt` along a path
`[C3 · postulate]`. The chapter is explicit that this is an *analogy under
test*, not an established correspondence: no trajectory audit against
least-resistance paths has been run.

The one adjacent measured result is a **blindness**, and it belongs here as a
warning rather than as support: the structural readouts were pointed at
representation collapse and did not move, while the mechanism that actually
prevented collapse was stop-gradient rather than a moving average. An
instrument that misses the failure mode nearest to it is not yet an instrument
for this chapter's claim.

## Chapter 4. The falsification programme — the examinable core

**Standing statement repeated. No medium has been measured. The only graphs the
parameters below have ever touched are project-drawn.**

### 4.1 What κ is, and why this repository cannot yield it

`[E1 · analysis — citable, and the chapter's load-bearing negative result]`

κ is identifiable **only** from absolute latency and absolute distance in a
physical medium. It is **not** identifiable from normalised graph readouts,
because ratio invariance `[B7 · derived]` cancels it exactly.

This cuts against the supporting repository, and the thesis says so plainly:
**every reading that project ships is a ratio or a rank, and κ is precisely the
quantity ratios destroy.** The first experiment of this thesis therefore has to
leave the repository's entire instrument class, by necessity rather than by
preference. **Door 1 — extraction from live attention matrices — is not an
inconvenience for the measurement; it is the only route to it**, and it is
currently shut on container egress rather than on inspection.

### 4.2 Experiments — physical media only

| # | experiment | independent variable | refutes |
|---|---|---|---|
| D1 | vary propagation latency at **fixed geometry** | τ_rt at constant layout | C1 if `d` fails to track |
| D2 | vary geometry at **fixed latency** | layout at constant τ_rt | C1 if `d` tracks geometry anyway |
| D3 | κ in two topologies, one medium | topology | C2 if κ varies beyond stated error |
| D4a | **uniform** rescale, read **absolute** sensors | global scale | C4a |
| D4b | background raised **relative to** structure, read **pair ratios** | noise floor | C4b |
| D5 | trajectory audit against least-resistance paths | — | C3 |
| **D0** | **blindness control** — uniform rescale must leave every pair ratio unchanged | global scale | the instrument itself |
| D6 | **horizon probe**, one measurement past every registered range | — | any trend claim |

D3 is the test of **`[C2 · postulate]`** — that κ is a constant of the medium
rather than of the graph. If κ must be refitted per topology within one medium,
C2 fails and C1 loses its transferability.

Two protocol requirements bind every row: the symmetrisation choice is declared
per experiment `[E4 · declared]`, and the pre-registration is hashed before any
measurement is taken `[E5 · declared]`.

No simulation appears in this table. A graph this project drew cannot refute a
claim about a physical medium.

### 4.3 The collapse claim, split — and D0 as a locked null

`[C4a, C4b · postulate]`

**Uniform** collapse is invisible to *every* ratio, pair ratios included,
because a uniform rescale cancels in any quotient. It is testable only by
absolute sensors. **Differential** collapse — background rising relative to
structure — is the pair-ratio quantity.

An earlier draft of this thesis's own table said the collapse "must be measured
on ratios between pairs, not absolutes." **That was wrong in exactly the
direction this section corrects.**

**D0 is now a locked test, not a paragraph**:
`stack/perception/test_uniform_collapse_blindness.py`. It asserts that a
uniform rescale leaves every pair ratio unchanged at four scale factors; that
absolute distances *do* move, as `d·c^(−1/2)`, so the null is not vacuous; and
that differential change **is** visible to pair ratios, so the blindness is not
mistaken for inertness. **The null is the result.**

Any chapter claiming "collapse" without naming the mode is unexaminable.

### 4.4 Declared bounds — forward pointers only

`[E2, E3 · declared]`

**These are not evidence, not bounds derived from data, and not citable in
Chapter 5.** They are protocol parameters for an unexecuted experiment, and
each appears only with the standing statement attached.

- **E2 — minimum detectable effect: 10% relative deviation** of the
  latency–distance coupling from C1's prediction. Rationale: smaller effects
  sit below the demonstrated sweep- and solver-noise — a published verdict in
  the supporting repository flips across dtype, pinv library and Laplacian
  assembly `[G1 · limitation]`.
- **E3 — horizon: one decade of latency variation, with one mandatory probe at
  1.5 decades**, reported whichever way it falls.

## Chapter 5. Related work — guarded, never published

`[Table 2 §F · analysis]` — that section was rewritten under ruling 6 and
carries no numbered rows, so it is cited as a section rather than by row id.

The supporting repository's emergent-spacetime comparison suite was **read
before being characterised**. Its four verdicts, verbatim:

| Theory | the suite's own verdict |
|---|---|
| Holographic / AdS-CFT (RT, Van Raamsdonk) | `COMPARABLE (qualitatively)` |
| Quantum-information / emergent spacetime | `MOST ALIGNED (in spirit)` |
| Loop Quantum Gravity / spin networks | `SILENT (offers nothing on its core claims)` |
| Amplituhedron / positive geometry | `NOT COMPARABLE (different problem)` |

Its disclaimer, verbatim, and asserted by its own test:

> *"LMD is a Layer-1 toy; not quantum gravity; no Google collaboration;
> hardware test only proposed."*

**Both of its experiments are already identities.** Experiment A's sweep is
`d = J^(−1/2)` exactly — J = 2.0 → 0.7071, J = 0.01 → 10.0 — which is `[B2 ·
identity]` relabelled as a Van Raamsdonk analogue. Experiment B's 43,200
triangle checks across 200 networks restate that resistance distance *is* a
metric: a theorem, not a measurement.

**There is no retraction to record here, because the claim was guarded against
rather than published.** That distinction is the chapter's contribution: a
literature review usually lists what was withdrawn; this one lists what a test
prevented from being asserted in the first place.

## Chapter 6. Limitations — and the category boundary

### 6.1 The boundary, in the register the repository uses

The supporting repository's textual study states the general form and locks it
with two tests, `test_the_category_boundary_is_stated` and
`test_structure_is_not_claimed_to_be_purpose`: **structure is evidence about a
text; purpose is a claim about an author; and no dataset crosses.**

**This thesis's analogue, stated as a chapter constraint:** *graph identities
are substrate, and they license nothing about physical emergence.* Confirming
`d → d·c^(−1/2)` on ten thousand graphs says exactly as much about whether
space emerges from latency as counting words says about who wrote them —
nothing. A law confirmed a thousand times over in one domain is silent about
another.

### 6.2 Limitations carried into every chapter

| # | limitation |
|---|---|
| `[G1 · limitation]` | growth regimes are **model-dependent**; the verdict flips on dtype, pinv library, assembly |
| `[G2 · limitation]` | perception distances are **best-conductance-path** quantities, not geodesics |
| `[G3 · limitation]` | the **declared-graph boundary**: absence of an edge is absence of a declaration |
| `[G4 · limitation]` | disconnected pairs **refuse**; bare `pinv` would answer 0.790569 into a void |
| `[G5 · limitation]` | **κ has never been measured in any medium by this work** |

### 6.3 Nulls held by tests, not by prose

Each negative result below points at a locked test, so that it cannot be
summarised away in a later abstract.

| null | held by |
|---|---|
| emergence language is not shipped | `smi/test_smi.py` string guard `[A2]` |
| uniform collapse is invisible to pair ratios | `stack/perception/test_uniform_collapse_blindness.py` `[C4a]` |
| the −0.5 slope is an identity, not a result | `smi/PREREG.md` §H0 + its suite `[B2]` |
| Foster never gates a decision | assert-only harness check, raises `[B3]` |
| a pair across components gets no number | component guard `[G4]` |

## Chapter 7. Conclusion

The thesis's contribution is a **distinction and a programme**, not a
measurement. The distinction is between Layer-1 identities — scale-invariant
accounting, true of every drawing — and the Layer-3 postulate, which is
scale-dependent and therefore capable of being wrong `[C5 · derived]`. Foster's
total is the cleanest case: `Σ w·R = n − k` holds for every graph, so it can
catch an assembly bug and can never prefer one drawing over another.

The programme's first experiment is the estimation of κ, and it cannot be run
on any instrument this work already has: the ratio discipline that makes those
instruments ungameable is exactly what makes κ invisible to them. **Until a
physical medium is measured, this thesis reports no emergence — only the
conditions under which a claim of emergence could be made, and the test that
currently prevents one being made carelessly.**
