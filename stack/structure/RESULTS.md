# Results — Commit 4, the certificate layer

Run 2026-09-17. Offline, deterministic. 13 assertions.

## What this port is

`stack/structure/lintel.py` **imports** root `lintel/`. Nothing here recomputes
a cut vertex, a rewrite or a candidate edge. What is new is the certificate
layer: naming the invariance group, marking counts untrusted, emitting the
dispute residue.

**The requested "bit-identical regression" is a tautology here** and is recorded
as one rather than shipped as if it meant something. It compares
`ported.cuts is root_lintel.cuts` — a function to itself.
`stack/organization/` had a real regression to run because the pre-rename
arithmetic lived in a separate file and could have drifted; here there is
nothing to drift from. `test_the_engine_regression_is_a_tautology_and_says_so`.

## The frozen numbers could not be asserted, and that is the finding

`invisible-edges/RESULTS.md` recorded 27 declared cut vertices, 18 stable under
omission, 9 lost, 4 gained. Re-run today:

| | recorded | today |
|---|---|---|
| modules in graph | 156 | **169** |
| declared cut vertices | 27 | **31** |
| stable under omission | 18 | **23** |
| lost / gained | 9 / 4 | **8 / 6** |

Adding `stack/` changed the graph the repository audits. **The repository is its
own subject and it grew.** This is the same defect `page-code/` hit when
`files_scanned == 401` broke to 402 the moment its own test file was added, and
the fix is the same: assert the relationships that carry the finding, never the
frozen count.

It is also the counts-are-untrusted rule arriving somewhere I did not expect it.
I had treated *names* as the trustworthy half. The **number of names moves too**
— not because the finding is unstable under a transformation, but because the
subject is not the same subject. A certificate has to carry a date, not just a
group.

## What holds

- **P7** — the rewrite certificate names `GROUP_REWRITE`, keeps every name, and
  emits counts flagged `counts_trusted: False` with the inflation note.
- **P8** — the omission certificate keeps a clear majority, the two sets are not
  nested (lost ≥ 1 and gained ≥ 1), and the residue accounts fully:
  `stable + lost == declared`. With no candidates the residue is empty — the
  control that stops the test passing for the wrong reason.
- **P9** — both certificates side by side. `act_on` is the intersection of two
  named groups, which is a set operation, not a score. An unnamed invariance
  group raises.
- **The two groups genuinely disagree** — fewer names survive omission than
  rewrites. If they agreed, naming the group would be ceremony.

## What this cannot do

- **A certificate does not say a finding is true.** It says it survived a named
  family. A stable finding can be a stable mistake.
- **It is not transferable between families**, which is why the group is named.
- **It is not a breach detector.** Candidate edges are not real edges; 31 of 92
  candidates on this repository sat only in comments or docstrings. Disputes are
  disputed, not wrong.
- **Counts are untrusted, and now so is the count of names** across time.

## Reproduce

```
python3 -m pytest stack/structure -q
```
