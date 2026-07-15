# Echo — the Agency Database

*A database that knows what it stores, proves the past is intact, and never
silently drops anything. The persistence layer for the agency stack — where
audits, delegations, and hop envelopes live.*

## The one-sentence version

A normal database trusts whoever writes to it: it stores what it is given, keeps
no proof the past wasn't rewritten, and has no idea whether the thing it just
persisted is a scam or a genuine record. **Echo** adds the three properties an
agency layer needs — **content-audited writes, append-only tamper-evidence, and
Merkle-provable inclusion** — reusing only already-tested primitives (the NERE
kernel and the same canonical SHA-256 as the certificate wallet and hop
envelope), fully on-device, no network.

## What a normal database can't do — and Echo does

| | Normal DB | Echo |
|---|---|---|
| Is the record it just stored a scam? | no notion of content | **audited on write**; verdict stored alongside |
| Can it list every manipulative record? | not without re-scanning | **one query** (`{mechanism:true}`) |
| Was a past row silently rewritten? | undetectable | **`verify()`** locates the exact record |
| Prove one record is in the DB without revealing the rest? | no | **Merkle inclusion proof** vs a published root |
| Does it ever silently drop content? | app-dependent | **never — non-suppressive by contract** |

## The three properties (`echo.mjs`)

1. **Content-audited, non-suppressive writes.** `put(kind, content, meta)` passes
   the content through the NERE kernel and stores the verdict (PASS/WARN/BLOCK,
   posterior, mechanism, `mechanism_lexicon`) *with* the record. It **never
   refuses a write** — it records what it concluded and lets the reader decide.
2. **Append-only + hash-chained.** Each record links to the previous by
   `hash = SHA-256(prev_hash + canonical(body))`, so any edit to history is
   detectable and `verify()` returns the exact `brokenAt` index.
3. **Merkle-provable.** `root()` commits to the whole set in one hash; `proofFor(seq)`
   yields a portable proof that a single record is in the DB, checkable by anyone
   holding the published root — **without being shown the other records**.

## Results — tested on real open-source data

`node echo/field_test.mjs` (assertions: `echo.test.mjs` **14/14**,
`scam_taxonomy.test.mjs` **7/7**). Benign inputs are real, live-fetched (the OSS
field-trial registry corpus); scams are labeled.

- **Ingest:** 281 real registry texts + 6 labeled scams → **287 records stored,
  nothing dropped** (PASS 281 · WARN 2 · BLOCK 4).
- **Query the ledger:** `{mechanism:true}` isolates the scam ledger — **6/6 scams
  flagged, 0 false positives** on the 281 real registry docs.
- **Two-layer tamper-evidence:** an insider rewrites a stored scam's verdict to
  PASS → `verify()` locates it at the exact record; and because the record's
  honest leaf was never in the **published Merkle root**, any external holder of
  that root rejects it using a proof issued at commit time — **no cooperation
  from the database required**. A hash chain also can't be patched at one point:
  repairing record *k* breaks record *k+1*'s link, so tampering forces a full
  re-hash that a published root still catches.
- **Normal-DB baseline:** the same rewrite on a plain object store leaves **no
  evidence** — no chain, no root, no verify.

### NERE scam taxonomy (`scam_taxonomy.test.mjs`)

One representative per manipulation mechanism, all caught with the mechanism
identified, while legitimate emergencies stay silent:

| scam type | mechanisms fired | verdict |
|---|---|---|
| grandparent impersonation | opacity + urgency + secrecy + payment + impersonation | BLOCK |
| authority / IRS threat | fear + secrecy + payment | BLOCK |
| account-suspended gift-card | urgency + fear + payment + scarcity | BLOCK |
| tech-support bypass | payment (removal fee) | caught |
| delivery-fee phishing | payment (redelivery fee) | caught |
| prize / scarcity | payment + scarcity | caught |
| *3 real emergencies* | *none* | **silent** |

The last three were fast-mode misses on the first run — they use advance-fee
payment phrasing ("pay the removal fee", "processing fee") that wasn't in the
lexicon. That is a genuine payment-pressure *mechanism*, so the consumer-v1
payment lexicon was broadened to include the fee-scam family — verified to add
**zero** false alarms on the 281 registry docs, the 306 README paragraphs, and
the emergency set (all still 0.0%). This is lexicon growth where a real mechanism
was missed by phrasing — distinct from reworded/evasive coercion, which remains
fast mode's ceiling and deep mode's job.

## What it's solving

The agency stack produces records that *must not be quietly rewritten* — an audit
verdict, a delegation grant, a hop envelope. Put them in a normal database and an
insider (or an attacker with write access) can clear a scam flag or alter a grant
with no trace. Echo is the store where that is impossible to do invisibly: every
record carries its own verdict, the whole history is tamper-evident, and any
single record's membership is provable against a published root. It is to agency
records what a hash-chained ledger is to transactions — but content-aware and
non-suppressive.

## Honest scope

- **Real and tested:** the write/audit path, the hash chain and `verify()`, the
  Merkle root and inclusion proofs, tamper localization, non-suppression, and the
  scam-taxonomy detection — all on real data, 21/21 across the two suites.
- **Not built here:** durable storage/replication, concurrent writers, and a
  query language beyond the in-memory filters — Echo is the reference *engine*,
  not yet a server. The evasive-coercion ceiling is inherited from fast mode.
