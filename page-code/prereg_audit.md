# Pre-registration — Page Code on real third-party open source, and on our own products

Written and hashed **before `blueprint()` was run on any package below**. The
only graphs looked at when this was locked were this repository (401 files) and
`ihcei_v3/` (26), both reported in `BLUEPRINT_RESULTS.md`.

---

## What changed: there is a real third-party corpus after all

Last turn I said the weakest thing about the blueprint finding was that both
projects were mine, and that testing it needed repositories nobody here wrote.
Those are on this machine and were reachable the whole time:

`/usr/local/lib/python3.11/dist-packages` — **pandas (1421 files), scipy (973),
statsmodels (948), sklearn (653), jax (617), networkx (580), numpy (487),
pygments (339)**. Eight major open-source projects, none written by anyone in
this project, all readable offline.

`huggingface.co` remains **000** and GitHub repository access remains scoped, so
this is not the registered 30-repo audit and does not unblock it. It is a
different, better-than-nothing corpus that happened to be underfoot.

## And one product does not exist

**Trig has no code in this repository.** No directory, no file, no module. The
Confidence Meter is described in the design material and is not built. The audit
must therefore report *absence*, not zeros, and that is prediction C5.

---

## Predictions

| # | Prediction | Value |
|---|---|---|
| C1 | At least one third-party package has a hub fan-in **greater than 22** — this repository's busiest | ≥ 1 package |
| C2 | Median isolated-file fraction across the eight third-party packages is **below 0.40**, against this repository's **0.683** | < 0.40 |
| C3 | Every one of the eight third-party packages has **≥ 1 single point** | 8 of 8 |
| C4 | At least one Novora product directory has **zero intra-product edges** — its own files do not import each other | ≥ 1 |
| C5 | Trig **abstains as absent**, and no reading reports it as a project with zero of anything | abstains |
| C6 | The 1/m² law is exact on every hub measured | exact |

**C2 is the load-bearing one and it is a prediction against last turn's
headline.** If real libraries are densely wired and agent-built repositories are
not, then "two thirds of files stand alone" is a fact about *how this project
was built*, not about software, and the reach argument has to be restated. If
instead third-party packages are equally sparse, the finding generalises and is
much stronger. Either outcome is reported.

C6 is arithmetic and is listed as verification, not discovery.

---

## Nulls, registered in advance

**NULL-C1.** These packages are *installed distributions*, not source
repositories: no tests, no tooling, no build files, and vendored sub-packages
are present. A distribution's import graph is not its repository's import graph.

**NULL-C2.** Eight packages, all scientific-Python, all installed in one image.
That is not a sample of open source; it is a sample of what this container
happens to carry. Nothing generalises to "GitHub".

**NULL-C3.** A single point is not a defect and a hub is not a fault. `numpy`
having a module everything imports is what a numerical library *is*. The reading
says where the load sits; it is not permitted to say the load is misplaced.

**NULL-C4.** The extractor is syntactic. Python is AST-parsed so a commented-out
import is not an edge; JavaScript is regex after comment-stripping. Conditional
imports, lazy imports inside functions, and `__getattr__`-based lazy loading —
which pandas, scipy and sklearn all use heavily — will read as edges or as
nothing depending on where they are written, and no reading here corrects for
that.

**NULL-C5 — the revenue null, again and unchanged.** Nothing in this run
measures whether anybody would pay. Structure being readable and structure being
*bought* are different propositions and only the first is tested.

---

## What would falsify this

1. **C2 fails** — third-party packages are as sparse as this repository, meaning
   the isolation finding is about software generally rather than about agents,
   and last turn's framing was wrong in the other direction.
2. **C3 fails** — some large package has no cut vertex at all, meaning the
   sole-route reading has nothing to say about well-built libraries.
3. **C5 fails** — the audit reports Trig as a project with zero files rather
   than declining, which would mean absence and emptiness are being conflated.
4. **Any number moves between two runs.**
