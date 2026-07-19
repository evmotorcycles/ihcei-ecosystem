# Emergent distance from information latency: a pre-registered numerical study and a proposed bench test of Latency–Metric Duality

*Registered Report (Stage-1 accepted-in-principle format) — prepared for a venue such
as* Physical Review Research *or* Entropy.
*Novora / IHCEI ecosystem. Pre-registration locked 2026-07-18, canonical SHA-256*
`011b7b53e9df4d12cc54e7689639209b82a282b3199b88f4d9ce481e6fdb7e3c`.

---

## Abstract

We ask whether a distance metric can emerge, with full metric structure and a
predicted scaling law, from nothing but an information-coupling matrix — and
whether the resulting construction furnishes a laboratory-testable discriminator
between "space is a fundamental container" and "space is a rendered read-out of
information latency." We formalize the latter as **Latency–Metric Duality (LMD)**
and its line element, the **Telemetric Metric** `d(i,j)² = κ·τ_rt`, in which proper
distance is the round-trip information latency (commute time per coupling rate,
equal to the effective resistance `R_ij`) of a correlation network. In a
**pre-registered** numerical study (parameters, seeds, and thresholds frozen under a
SHA-256 lock prior to execution) we confirm three predictions: (H1) the metric is
genuine — 0/8640 triangle-inequality violations; (H2) it obeys `d ∝ 1/√coupling`
— log-log slope −0.5000, R² = 1.00000; (H3, primary) it discriminates — holding two
sites at fixed labels and changing only their coupling moves the emergent distance
(range 0.94) while a fundamental-container null is frozen (range 0). A
multidimensional-scaling embedding renders the same effect in 3D: the topology is
fixed across a coupling sweep, yet the rendered coordinates contract exactly as
`1/√coupling`. We then specify the physical experiment — a tunable-coupling qubit
lattice or entangled optical-clock network — whose sign-and-scaling response would
decide the ontological question. The physical experiment is proposed, not performed;
the claim that physical spacetime is emergent is neither claimed nor proven.

## I. Introduction

The relational view of geometry has a long lineage, from Mach through the modern
holographic program. Van Raamsdonk argued that the connectivity of spacetime is
built from entanglement: reduce the mutual information between two boundary regions
and the dual bulk distance grows until the geometry pinches off. The Ryu–Takayanagi
formula ties areas to entanglement entropy. These are profound but largely
qualitative and model-specific (AdS/CFT). What has been missing is a **discrete,
universal, benchable law** — one statement that (i) applies to any correlation
network, (ii) predicts a quantitative scaling, and (iii) yields a single laboratory
observable that separates emergent from fundamental geometry.

We propose such a law and validate its mathematical content under pre-registration.
The construction is deliberately elementary — effective resistance and commute times
on weighted graphs — precisely so that it is reproducible on a laptop and portable to
any experimental platform that can tune coupling.

## II. Theory and pre-registered predictions

For a network specified by a symmetric coupling matrix `W`, let `L = Diag(deg) − W`
be the graph Laplacian and `L⁺` its Moore–Penrose pseudoinverse. The effective
resistance is `R_ij = L⁺_ii + L⁺_jj − 2L⁺_ij`; the Doyle–Snell commute time is
`C_ij = vol·R_ij` with `vol = Σ deg`; and the round-trip information latency is
`τ_rt = C_ij/ν = R_ij`, with `ν` the coupling/hop rate. The Telemetric Metric is

> **d(i,j)² = κ·τ_rt(i,j) = κ·R_ij.**

**LMD.** Geometry is emergent bookkeeping of round-trip latency; distance is a
rendered read-out of correlation, not a fundamental backdrop.

Pre-registered predictions (locked before any run; full spec in
`prereg/telemetric_prereg.json`):

- **H1 (metric).** `d = √(κ·R_ij)` satisfies the metric axioms; endpoint =
  triangle-inequality violations; pass iff exactly 0 over 40 random networks.
- **H2 (scaling).** `d ∝ 1/√coupling`; endpoint = log-log slope; pass iff
  `|slope + 0.5| < 0.02` and `R² > 0.999`.
- **H3 (discriminator, primary).** Changing only the coupling of two fixed sites
  moves the emergent distance while a fundamental-container null does not; pass iff
  emergent range > 0.05 and null range < 1e-9.

**Symmetric-null rule.** Any endpoint missing its locked threshold is reported as a
null, with no post-hoc adjustment of parameters, seeds, thresholds, or
sub-populations.

## III. Methods (pre-registered)

Networks: `N = 6` nodes; 40 independent random symmetric couplings with edge weights
`~ U(0.2, 1.0)` (H1); a single random network swept over coupling
`c ∈ {0.5,1,2,4,8,16}` (H2); a fixed base network with the coupling of two probe
sites `(0,5)` scaled over `{0.5,1,2,4}` (H3). `κ = 1`. Seeds are fixed in the spec
(7, 11, 29). `L⁺` is computed by the standard `(L + J/N)⁻¹ − J/N` identity.
Endpoints and thresholds are read only from the frozen spec by the runner
(`prereg/run.py`); the runner cannot modify them. Provenance (Section VI) is
generated by an on-device audit that verifies the pre-registration lock, bounds the
runner's write access, and hash-chains the spec and results.

A separate visualization (`telemetric_3d.py`) embeds the distance matrix of a fixed
8-node small-world graph into 3D by classical MDS across a coupling sweep, to render
the H3 effect geometrically.

## IV. Results

All three pre-registered hypotheses passed against their locked thresholds
(**verdict PASS, 3/3**):

| ID | Endpoint | Locked pass condition | Result |
|---|---|---|---|
| H1 | triangle violations | `== 0` | **0 / 8640** |
| H2 | log-log slope; R² | `|slope+0.5|<0.02 ∧ R²>0.999` | **−0.5000**; **1.00000** |
| H3 | emergent vs null range | `emergent>0.05 ∧ null<1e-9` | **0.9425** vs **0** |

For H3 the emergent distance of the fixed pair contracted monotonically
(`1.21 → 0.78 → 0.47 → 0.27`) as its coupling rose (`0.5 → 1 → 2 → 4`), while the
fundamental-container value was identically frozen.

**3D rendering (Fig. 1).** With the topology held fixed and only the coupling swept
`{0.5, 1, 2, 5}`, the MDS-embedded coordinates contract and the mean telemetric
distance falls `0.999 → 0.706 → 0.499 → 0.316`, tracking `1/√coupling` to three
figures. *(Figure: `physics-agency/figures/telemetric_3d_contraction.png`.)*

## V. Discussion

The results establish, under pre-registration, that a full metric geometry emerges
from a pure coupling matrix, obeys the predicted inverse-square-root scaling, and —
crucially — furnishes a **decisive discriminator**: a fixed pair's operational
distance responds to correlation alone under LMD but is inert under a fundamental
container. This translates van Raamsdonk's qualitative "entanglement glue" into a
concrete discrete law and a single benchable observable, and it supplies the
viability dynamics that fitness-first accounts of perception (Hoffman's interface
theory) otherwise lack.

**Limitations.** (i) This is Layer-1 mathematics; no physical measurement is made.
(ii) The mapping from physical entanglement to graph coupling, and from a physical
"distance" probe to commute time, must be fixed operationally by an experimenter;
different choices change `κ` and could change the exponent — that is a quantity to be
measured, not assumed. (iii) The constructions are finite-size and classical;
extending to continuum limits and to genuinely quantum commute-time observables is
future work.

**Epistemic firewall.** Layer 1 (proven here): on discrete information networks a
genuine distance metric is an emergent function of coupling obeying `d ∝ 1/√coupling`.
Layer 3 (not claimed): that physical spacetime is a latency read-out. That is the
hypothesis the proposed experiment (companion protocol) would test; LMD is falsified
physically if a fixed pair's operational distance is flat under a coupling sweep.

## VI. Data availability, code, and provenance

All code is standard-library Python and Node with no network dependency.
Pre-registration: `physics-agency/prereg/telemetric_prereg.json` (SHA-256
`011b7b53…`, locked in `MANIFEST.sha256.json`). Runner: `prereg/run.py`. Audited
pipeline: `prereg/audit.mjs` (lock verification, agency bounds via Page Code,
hash-chained attestation via Echo, independent audit via EI, epistemic screen via
NERE/PAGES). Machine-readable provenance: `prereg/provenance.json`. Figure:
`figures/telemetric_3d_contraction.png`. Reproduce:
`node physics-agency/prereg/audit.mjs`, `python3 physics-agency/telemetric_3d.py`,
`python3 -m pytest physics-agency/`.

## References (indicative)

1. M. Van Raamsdonk, "Building up spacetime with quantum entanglement," *Gen. Rel.
   Grav.* **42**, 2323 (2010).
2. S. Ryu, T. Takayanagi, "Holographic derivation of entanglement entropy from
   AdS/CFT," *Phys. Rev. Lett.* **96**, 181602 (2006).
3. J. Maldacena, L. Susskind, "Cool horizons for entangled black holes" (ER=EPR),
   *Fortsch. Phys.* **61**, 781 (2013).
4. P. G. Doyle, J. L. Snell, *Random Walks and Electric Networks* (MAA, 1984).
5. D. J. Klein, M. Randić, "Resistance distance," *J. Math. Chem.* **12**, 81 (1993).
6. D. Hoffman et al., "The interface theory of perception," *Psychon. Bull. Rev.*
   **22**, 1480 (2015).
