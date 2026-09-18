# v1.0-NERE-LOCKED — the tag, and why the tag is not on the remote

## STATUS: cut locally at `8b97845`. NOT PUSHED.

`git push origin v1.0-NERE-LOCKED` returns **HTTP 403 from GitHub**. The push
credential issued to this container is scoped to `refs/heads/...` and refuses
`refs/tags/*`. This was distinguished from a network fault before being
written down, because "the network was down" and "the permission was absent"
are different facts and only one of them is recoverable by retrying:

| probe | result | reading |
|---|---|---|
| `git push origin <branch>` | `Everything up-to-date` | the remote **was** reached; transport is fine |
| `git push origin v1.0-NERE-LOCKED` | `RPC failed; HTTP 403` | refused at the ref, four attempts with backoff |
| proxy relay log, host filter `github` | **no entries** | the 403 is GitHub's, not the proxy's |

So this is a **credential scope**, not an outage, and not a property of the
work. Recorded the same way the two Phase 5 doors are: shut on **egress, not
on inspection**. Nothing here should harden into a claim that the repository
carries a tag. It does not.

## To apply it, from a checkout with tag-push rights

```
git tag -a v1.0-NERE-LOCKED 8b97845 -F RELEASE_v1.0-NERE-LOCKED.md
git push origin v1.0-NERE-LOCKED
```

The commit is the durable reference either way. A tag is a convenience
pointer; `8b97845` and merkle root `26f9454f4cb8f61b` are the actual
identifiers, and both are already on the remote.

## Re-checking the state this names

```
bash reproduce_all.sh                      # expect: ALL GREEN - 125/125
python3 provenance/verify_provenance.py    # expect: root 26f9454f4cb8...
```

---

## The tag message, verbatim

```
v1.0-NERE-LOCKED — a verified state, not a sealed one

Marks the commit at which every suite in reproduce_all.sh runs green:
125/125, clean tree, no network, no paid API, no key.

WHAT THE TAG ASSERTS
  The 77 artifacts covered by PROVENANCE.lock.json hash to merkle root
  26f9454f4cb8f61b3b23c723b7b5ef565a4610c9d71ab839d5390c7f845a8970, and the
  stack reproduces from a clean checkout.

SUPERSESSION CHAIN
  f12680a76156 -> 26f9454f4cb8
  The retired root is recorded, not deleted. It moved because the H5
  retirement corrected one file of 77: cohort D is a seeded simulation and
  the frozen record had described it otherwise. Author, affiliation and
  origin are byte-identical across the move; only the snapshot travelled.
  The chain is carried by build_provenance.py, so a rebuild reproduces it
  rather than erasing it, and an undeclared re-root raises.

WHAT REMAINS OPEN AT THIS TAG
  Door 1  no ML runtime present and no reachable weight host. SHUT ON
          EGRESS, NOT ON INSPECTION. No pre-registration was written
          against it; a network limitation must not harden into a finding.
  Door 2  no obtainable per-hop corpus. Same footing. P24-P26 unwritten.
          phase5/runner_spec.md stays UNLOCKED for a runner that can pass
          the gate.
  Human check on per-hop payload availability: OPEN. The 2026 incident is
  external-claimed and its primaries were never fetched.
  Detector recall: unmeasurable by construction. Precision is demonstrable;
  recall is not, and no number is offered for it.

WHAT THE TAG DOES NOT ASSERT
  Not that the readouts are right about the world. Three of five structural
  sensors are defeated by declared padding, and that is measured here, not
  conceded. Not that anything was validated, verified or supported -- those
  words are banned in this build and the distinction is the project. The
  suites state what was checked. A green run is the errand done, not the
  question closed.

  The tag is a reference point for reproduction, and nothing is sealed
  behind it.
```
