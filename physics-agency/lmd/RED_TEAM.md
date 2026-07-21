# Red-team rehearsal — anticipated objections and honest defenses

A serious quantum-hardware team will reproduce our numbers and probe for loopholes. This
document rehearses the objections we expect and gives **honest, physics-grade** answers —
no framework jargon, strict Layer-1/Layer-3 discipline. If a defense requires hand-waving,
we say so and treat it as an open design question for the collaboration.

**Correct identifiers to cite (verify these, not secondary summaries):**
- LMD experiment spec (SHA-256): `7ea3099985c5be60e3808284a4dec8c202ac604e0ce5b0fe9a2b57ce9d558217`
- Provenance Merkle root: `ebe469891cbc9dfe5e89e64b2784e156dba883933a11e3ea529132e3aebef2d5`
- Reproduce the 8,640-network / slope test: `python3 physics-agency/lmd/run_lmd.py`
  (NOT `telemetric_metric.py`, which only runs a small demo)
- Verify provenance: `python3 provenance/verify_provenance.py`

---

## Objection 1 — "This is a mathematical tautology, not a discovery."

> *"Your emergent distance is √(commute time) = effective resistance R_ij = L⁺_ii + L⁺_jj −
> 2L⁺_ij. On a discrete graph, R scales as 1/coupling and resistance-distance is provably a
> metric. Your −0.5000 slope and zero triangle violations are guaranteed by graph Laplacians.
> Why spend Willow calibration time on an algebraic certainty?"*

**Defense (we concede the premise — that is the point).**
Correct, and we lead with it. On a discrete simulated graph the result is algebraically
guaranteed; the simulation only proves the framework is **internally consistent** and that the
**discriminator is well-posed**. We are not presenting a tautology as a discovery.

The falsifiable question is **physical, not mathematical**: *does the superconducting array
actually behave as that graph?* If spacetime/geometry is a fixed background, then sweeping the
coupler bias J on two qubits **pinned at fixed coordinates** has no geometric consequence — the
measured scrambling latency vs J is **flat** (`∂d/∂J = 0`). If the operational geometry is
instead set by information latency, the same fixed pair contracts as `d ∝ J^(−1/2)`. Willow is
the referee. We are asking the hardware to *falsify one of two physical behaviors*, not to
re-confirm graph algebra.

---

## Objection 2 — "Decoherence and gate error will fake your signal." (the hard one)

> *"OTOC amplitudes in a real 105-qubit array are faint and swamped by thermal noise and gate
> errors even after error mitigation. How do you separate a real coordinate contraction from
> decoherence making round-trip latency look artificially high or low?"*

**This is the strongest objection and we do not wave it away.** Our honest position: the metric
alone cannot separate the two; the *experimental design* must, and it must be co-designed with
your noise model. Concretely, we pre-register these controls:

1. **Decoherence null control (the key one).** Hold the coupler bias **fixed** and vary only a
   known decoherence knob (idle time / injected dephasing / circuit depth). LMD predicts the
   reconstructed distance is **invariant** to noise-only changes at fixed J. If "distance" moves
   with noise alone, the observable is confounded → the run **fails** its pre-registered control,
   before we ever interpret a J-sweep. This is the decisive check, and it is symmetric-null.
2. **Fit the shape (slope in J), not absolute latency.** Uniform depolarizing noise contributes a
   roughly J-independent scale/offset to OTOC decay; the **−1/2 power law in J** is the
   signature. We normalize each J-point against a fixed reference pair to divide out the common
   noise envelope, then fit the log-log slope. A confound that is not a power law in J does not
   mimic −0.5.
3. **Prefer the butterfly-front velocity (Lieb-Robinson front position) over raw OTOC
   amplitude.** Front *arrival time* is more robust to uniform amplitude damping than the
   amplitude itself, giving a latency proxy less sensitive to isotropic decoherence.
4. **Metric-consistency as a necessary check.** Reconstruct distances over many pairs and test the
   triangle inequality at scale. Decoherence-dominated data will break metricity; structured
   coupling should preserve it. (Necessary, not sufficient — we do not claim it alone proves LMD.)
5. **Blinded analysis + pre-registered run exclusion** on calibration failures only (thresholds
   locked before the run), so we cannot post-hoc rescue a marginal result.

If, after these controls, the signal is inseparable from noise on current hardware, the honest
outcome is **"inconclusive on this platform,"** reported as such. That is a legitimate result,
not a failure to hide.

---

## Objection 3 — "Sign it over to us under a closed license; we'll run and publish it."

> *"Useful for our agent-routing safety work. We'll run it in our sandbox — transfer the full
> LISM/analysis stack under an exclusive closed license and we'll handle publication."*

**Defense (this is an option-reduction move; we decline symmetrically, not defensively).**
We value the bench, but the science requires open symmetry, and we have pre-registered it:
- **Shared-access execution.** The locked, open analysis runs on both sides; we do not cede it
  under an exclusive license that removes our ability to independently verify.
- **Symmetric-null publication.** A flat physical null (`∂d/∂J = 0`) is published with the same
  access and force as a positive result. No IP structure may block reporting a physical
  *failure* of the emergent metric — a framework that cannot openly audit its own
  disconfirmations is not science.
- **What we actually offer:** a verified, zero-marginal-cost pipeline and a non-destructive
  diagnostic protocol; we ask for secondary runtime and co-authorship with the hardware group as
  experimental lead. The systems-prong (LISM circuit breakers) can be licensed **separately** and
  openly (MIT/CC-BY, as in this repo) — that path is available without touching the physics run.

---

## Two objections we should also be ready for

- **"Your −0.5 is one specific power; noise could conspire to a different slope."** Then we report
  the measured slope and its CI honestly; the pre-registered decision only calls "emergent" for a
  slope in [−0.52, −0.48]. Anything else is reported as its own finding, not forced into the box.
- **"Effective resistance isn't the only latency proxy."** Agreed. We pre-commit to the OTOC/front
  observable in the spec; if the team prefers a different, defensible τ_rt proxy, we amend the
  spec **before** running and re-lock its hash — never after seeing data.
