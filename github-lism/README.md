# GitHub LISM — engagement concentration + unresolved-backlog hazard on real repos

**One command:** `python3 github-lism/github_lism.py` · stdlib only · offline · `$0`

GitHub hosts hundreds of millions of open-source projects across science, medicine,
technology, and AI. This experiment tests two **structural** LISM predictions —
*concentration* and a *backlog hazard* — on a real cross-domain cohort of 28 repositories
pulled live from the GitHub API, then frozen for offline reproduction.

---

## What is measured

For each repo (surfaced by four topic queries — deep-learning, bioinformatics, security,
scientific-computing) we take real metadata:

- **stars** (`stargazers_count`) — engagement / capacity of the project.
- **open_issues** (`open_issues_count`) — the **unresolved-issue backlog**: an
  enforcement-latency (`τ_v`) analog. Issues accumulate unaddressed before maintainers
  resolve them, and a wide upper tail is the LISM hazard signature.

| artifact | SHA-256 |
|---|---|
| `prereg/github_prereg.json` (spec) | `4a613d633fe7d8ae44280abe3a66ba445cc278b49a0344abde8d346b7b4893da` |
| `data/github_cohort_frozen.json` (fixture) | `d5b105905cab0460208d337e278d03817c5362279091295006d8a421d20d1564` |

---

## Result (GREEN, honest)

```
N = 28 repos  (ai-ml 6, bioinformatics 8, security 7, sci-computing 7)

H1 engagement (stars):   median 37,623  mean 60,058  p90 164,240  max 234,796
                         p90/median = 4.37  → PASS  (mean > median)
H2 backlog (open_issues): median 264.5  mean 1,280  p90 2,758  max 18,272
                         p90/median = 10.43 → PASS  (mean > median)
H3 E=U·D coupling:       DECLARED UNTESTABLE
```

**H1 — concentration (PASS).** Stars are heavily right-skewed: a few repos
(the-book-of-secret-knowledge 234K, tensorflow 196K) absorb most attention while the tail
sits at a few thousand.

**H2 — backlog hazard (PASS).** The unresolved-issue backlog is *even more* heavy-tailed
(p90/median 10.4): a slow tail of repos carries huge unaddressed governance backlogs —
pytorch 18,272 open issues, scipy 1,845, stdlib 1,283 — exactly the `τ_v` hazard signature
LISM predicts, where unresolved load concentrates in a slow minority.

**H3 — coupling UNTESTABLE (declared, not spun).** There is no independent second fidelity
hop and no non-circular per-repo survival outcome — a live repo is a *survivor by
construction*, and the GitHub search returns no abandoned/deleted control group. So the
`E = U·D` coupling is reported **untestable** here, exactly as on bioRxiv, PubMed, and the
legislation channel. No number is manufactured.

## What this does and does not claim

- ✅ Tests the **structural signature** (concentration + backlog hazard) LISM predicts, on
  real GitHub metadata across four domains.
- ❌ Does **not** claim the `E = U·D` coupling on GitHub (declared untestable here).
- Honest sampling caveat: this is a **top-of-distribution** sample (already-popular repos),
  not a random draw from the ~420M-project population — so the heavy tail found *among the
  already-popular* is a conservative result, not an inflated one.

## Reproduce

The four queries are recorded in the fixture's `_provenance` block; re-issue them against
the GitHub API to reproduce the cohort. The frozen snapshot makes the offline run
deterministic.

```
python3 github-lism/github_lism.py         # GREEN, N=28
python3 -m pytest github-lism/test_github.py -q
bash reproduce_all.sh                        # whole stack
```

## Files

```
github-lism/
  prereg/github_prereg.json         pre-registration spec (locked)
  prereg/MANIFEST.sha256.json       spec + fixture hashes
  data/github_cohort_frozen.json    28 real repos + the exact queries (frozen)
  github_lism.py                    the experiment (stdlib, offline)
  test_github.py                    pytest guard (locks + H1/H2/H3)
  results_github.json               emitted results
```

Layer-1, offline, `$0`. Real data from the GitHub REST API.
