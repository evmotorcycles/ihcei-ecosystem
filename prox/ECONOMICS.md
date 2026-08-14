# How PROX earns

## The structural fact everything else follows from

Learned relevance costs **GPU-seconds per item at index time and per query at
search time**. That marginal cost never goes to zero, which is why every provider
must meter it, and metering is why relevance is rented.

PROX costs **CPU-seconds at index time and microseconds per query, with no
inference anywhere**. Its marginal cost is close enough to zero that metering it
would cost more than the compute.

You cannot win a metered market by metering slightly less. You win it by removing
the meter and selling what a universal free layer makes valuable. The GUI was never
the product; it was the thing that made everything above it sellable.

**So the engine is Apache-2.0 and free forever.** That is the strategy, not a
concession to it.

---

## Where the revenue is

### 1. Prox Sync — consumer subscription

One coordinate system across your phone, laptop and tablet. The critical property:
**a PROX index stores coordinates, not content.** It cannot reconstruct your
documents, so syncing it is small and privacy-preserving in a way that syncing
embeddings-plus-text is not.

| Tier | Price | Notes |
|---|---|---|
| Low-income markets (PPP-adjusted) | $1.49/mo | deliberately below a data bundle |
| Standard | $3.99/mo | |
| Family (5 devices) | $7.99/mo | |

Marginal cost is object storage and bandwidth only — no inference — so gross
margin sits above 90% at any scale. This is the volume line.

### 2. Prox for Teams — the auditability premium

Org-wide proximity across shared drives, tickets, code and chat. The differentiator
against embeddings is not quality, it is **explainability**: effective resistance
decomposes into the paths that produced it, so *"why were these two judged
related?"* has a concrete answer — a list of shared features and bridging
documents — that you can put in front of an auditor or a regulator. No learned
embedding can answer that question at all.

Combined with on-premises and air-gapped operation (trivial when there is no model
to serve), this is the line that sells into health, finance, legal and government.

- $7 / seat / month
- Enterprise and on-prem from $25k / year

### 3. Prox Embed — OEM royalty

Per-device licence for handset, TV, set-top, car and appliance makers who want
on-device proximity **without adding an NPU or any bill-of-materials cost**. This is
the distribution mechanism that made graphical interfaces universal: ship it in the
platform, not the app store.

- $0.02 – $0.10 per device, volume-tiered
- 300M devices at $0.05 ≈ $15M/year, at essentially zero incremental cost

### 4. Prox Cloud — developer API

Hosted index build and hosting for developers who would rather not run it. Priced
per million items indexed. It undercuts embedding APIs by roughly two orders of
magnitude, and that gap is set by **hardware economics, not by a pricing decision**
— CPU-seconds against GPU-seconds — so it cannot be competed away by a price cut.

### 5. Certified connectors — marketplace

Connectors that map a domain into a coupling graph (EHR systems, farm records,
case files, mail). 15% revenue share on paid connectors, plus a certification fee
for the "Prox Certified" interoperability mark.

### 6. Public-interest licence — free, permanently

Public health, education, agricultural extension, courts, and NGOs below a revenue
threshold pay nothing. This is not philanthropy. Universal layers become universal
through reference deployments, and a ministry that already runs PROX in its clinics
is not a customer to be won later — it is the proof that wins the commercial ones.

---

## Why the free core is defensible

The usual objection is that an Apache-2.0 core invites a hyperscaler to fork it.
Three answers, in increasing order of strength:

1. **There is nothing expensive to fork.** The engine is a few hundred lines over
   numpy and scipy. Its value was never scarcity of the code.
2. **The index format is the network effect.** `PROX/1` is a coordinate system.
   Once mail, files, photos and messages share one, the value is in being *the*
   shared frame — and shared frames consolidate rather than fragment.
3. **The incumbents' incentives point the other way.** A provider whose relevance
   business is metered per token cannot enthusiastically ship a free, unmetered,
   on-device substitute for it. That reluctance is the moat, and it is structural.

---

## What would kill this

Stated plainly, because a business case that lists no failure modes is not a
business case.

- **On-device inference gets cheap enough fast enough.** If a good embedding model
  runs free on a $40 phone, the cost argument weakens sharply. The auditability and
  determinism arguments survive; the affordability one does not.
- **"Good enough" is a higher bar than measured here.** PROX loses known-item
  retrieval to BM25 by 8x (see README §4). The router makes that a non-issue for
  the product, but it means PROX must ship *alongside* term search, never instead
  of it, and a competitor bundling both is the real threat.
- **Adoption is a distribution problem, not a technical one.** Nothing in the
  engineering guarantees anyone integrates it. The OEM channel is the risk that
  matters, and it is a sales problem with a long cycle.
- **Corpus structure is a precondition.** PROX derives association from structure
  in the collection. Sparse, unlinked, tiny collections give it nothing to work
  with, and those users will not perceive any benefit at all.
