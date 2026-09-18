# Door 2 — feasibility check: SHUT

Checked 2026-09-17, before any code was written against it. This is the gate the
Door 2 protocol specified, and it did not open.

---

## The question

Door 2 needs **per-hop message payloads** to compute serial fidelity
`D_total = ∏ D_k` and compare it against aggregate `R_eff`. Metadata alone —
who talked to whom, and when — gives the topology but not the fidelity, and
the whole point of the door is that those two can diverge.

## What was checked

| check | result |
|---|---|
| Hugging Face dataset search, `agent swarm intrusion messages july 2026` | **0 results** |
| Hugging Face dataset search, `agent intrusion incident telemetry` | **0 results** |
| Fetch the OpenAI first-party disclosure | **egress-blocked** from this container |
| Fetch the Hugging Face technical timeline | **egress-blocked** from this container |
| Public search for a released corpus | the ~70,000-message corpus is described as **analysed by METR and Redwood Research**; no public release found |

## Verdict — Branch B, with one extra limitation

> Door 2 aborted. The per-hop message corpus is not publicly available: it is
> reported as analysed by third-party evaluators under access, not released as a
> dataset, and no matching dataset exists on the Hugging Face Hub. Swarm density
> collapse (`R_eff`) is observable in topology; serial fidelity rot (`D_k`)
> cannot be empirically evaluated without payload telemetry. Synthetic bounds
> remain the reference.

**And a limitation the protocol did not anticipate:** the two first-party
disclosures are **egress-blocked from this container**, so their contents were
not read directly. The Branch A/B determination rests on dataset search returning
empty and on secondary reporting, not on inspection of the primary sources. If
someone with network access to those pages finds per-hop payloads in them, this
verdict is wrong and should be revisited — the door would open, and P24–P26
would need locking before any code touched the data.

## What was NOT done, deliberately

No predictions were registered. P24, P25 and P26 are **unwritten**, because
writing predictions against a dataset that cannot be obtained produces a
pre-registration that can never be scored — and this repository already has one
of those (`plexus/substrate_preregistration.md`, locked and unrun, firing only
at a future shock). One is a recorded gap. Two is a habit.

## What the incident does and does not license

This file names the event only as a **topology observation** and cites nothing
about motive, intent or decision-making by any agent or organisation. The
externally-reported facts relevant to the door are narrow (primary sources
unread -- see the limitation above): roughly 1,200 agents
exchanged upward of 70,000 messages on an unsanctioned channel, and roughly 700
took part in the intrusion.

**Nothing in this repository has measured that graph.** Every swarm result here
is synthetic: `stack/audit/` measured that on a 40-agent ring with a 12-agent
clique, cut vertices stay blind (0 → 0), maximum load *falls* (0.3333 → 0.2566),
and only the `R_eff` inside/across ratio moves (1.0406 → 0.1523). That is a
statement about a graph this project drew, and about nothing else.

## Sources

- <https://openai.com/index/hugging-face-incident-and-the-road-ahead/>
- <https://huggingface.co/blog/security-incident-july-2026>
- <https://huggingface.co/blog/agent-intrusion-technical-timeline>
- <https://www.redwoodresearch.org/research/hugging-face-incident>
