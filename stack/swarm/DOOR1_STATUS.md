# Door 1 — feasibility gate: SHUT (from this container)

Probed 2026-09-17, before any prediction was written against it. This is the
gate the directive specified: *probe the container first; write no
pre-registration against unreachable weights.*

---

## The question

Door 1 needs **attention matrices from a trained transformer** — real `A` from
real weights on real tokens — so that `stack/perception/lmd_distance.py` reads a
bearing off something other than a graph this project drew. Everything the
perception module has measured so far is synthetic. The door is the difference
between "the engine behaves this way on rings and cliques" and "the engine
behaves this way on a trained model", and only trained weights close it.

## What was probed

Three things, in the order that can shut the door earliest.

| probe | result |
|---|---|
| `import torch` | **ABSENT** (`ModuleNotFoundError`) |
| `import transformers` | **ABSENT** (`ModuleNotFoundError`) |
| `import safetensors` | **ABSENT** (`ModuleNotFoundError`) |
| `import numpy` | PRESENT, 2.4.6 |
| `https://huggingface.co/` | **000** (no response) |
| `https://cdn-lfs.huggingface.co/` | **000** (no response) |
| `https://hf.co/` | **000** (no response) |
| `https://pypi.org/` | 200 |
| HF connector, `cat config.json` on a 70M model | **succeeded**, 567 bytes |
| HF connector, `ls` on the same repo | **succeeded**, `model.safetensors` listed at 166,029,852 bytes, LFS |
| HF connector, `cat model.safetensors --max-bytes 256` | **refused**: `HF_FS_TEXT_ONLY` — the connector is text-only by design |

Free disk was 29G, so size was never the binding constraint.

## Verdict — shut, and shut on egress specifically

> Door 1 aborted. No ML runtime is present in this container and no weight host
> is reachable from it. The two routes to a trained model both close: direct
> HTTPS to `huggingface.co`, `cdn-lfs.huggingface.co` and `hf.co` returns no
> response at all, and the Hugging Face connector — which does reach the Hub,
> and did read a model's `config.json` and file listing — refuses non-text
> files by design, so it can deliver a model's shape but never its weights.
> Synthetic graphs remain the only substrate for the perception module.

**The blocker is weights, not tooling.** `pypi.org` answered 200, so `torch` and
`transformers` are almost certainly installable here. That distinction matters
because it names what a networked runner would have to supply: not a different
container image, just egress to the weight hosts. **The install was not
attempted**, because it cannot change the verdict — a runtime with nothing to
load is still a shut door — and saying it was attempted when it was not would be
the kind of claim this repository exists to refuse.

**Same conditional wording as Door 2, for the same reason.** This verdict rests
on **container egress, not on inspection**. Nothing here was measured about
whether trained attention would confirm or break any prediction; the door was
never opened far enough to look. If a runner with network access reaches those
hosts, this verdict does not transfer to it, and the door opens there.

## The nearest reachable thing is not the door

`pip install torch` plus a randomly-initialised `GPTNeoXForCausalLM` would
produce an attention matrix, a Laplacian, and a bearing — all of it running,
none of it Door 1. Random weights give a matrix drawn from an initialiser, which
is a synthetic graph with more steps and a misleading provenance. Naming it here
so that it is not mistaken later for a cheap way through: **an attention matrix
from untrained weights is a synthetic fixture and must be labelled one.**

## What was NOT done, deliberately

**No predictions were registered.** There is no `prereg_door1.md` and no Door 1
test suite. A pre-registration against weights that cannot be fetched can never
be scored, and this repository already carries two files in that condition —
`plexus/substrate_preregistration.md`, locked and unrun, and the P24–P26 slot
Door 2 left empty. Three would stop being a recorded gap and start being the
house style.

What exists instead is `phase5/runner_spec.md`: the Door 1 text written out in
full and explicitly **UNLOCKED**, so that a networked runner can lock it, and so
that nothing locked here pretends to have been.

## The human check this leaves open

A reader with network access is asked to confirm the one thing the container
could not: that the weight hosts are blocked *by this environment's policy* and
not by an outage on the probe date. Status: **OPEN**. Recorded in
`stack/governance/declarations.md` §8.
