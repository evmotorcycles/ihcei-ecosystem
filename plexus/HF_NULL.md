# The Hugging Face card test could not be run

`hf_preregistration.md`, sha256
`ebe1366f4b999992f2b949a54daf806983d5af3b8d62e3549516c18ae65adf87`, is locked
and **unedited**. Not one of H1 to H7 has an answer.

## Why

Two routes were tried and both are closed in this environment.

1. **The Hugging Face MCP tools returned "requires approval"** on both
   `hub_repo_search` and `hub_repo_details`. No approval arrived.
2. **Direct HTTPS is refused by the network policy.** The agent proxy answered
   403 to CONNECT for `huggingface.co:443`, twice, and reported both refusals in
   its own status endpoint:

   > `"kind": "connect_rejected", "detail": "gateway answered 403 to CONNECT
   > (policy denial or upstream failure)", "host": "huggingface.co:443"`

No model card text was obtained. Nothing was pressed. There is no partial
result, no smaller sample, and no substitute corpus that would answer the
question the pre-registration asked, because every prediction in it is about the
text of a card.

## What was NOT done about it

The pre-registration was not rewritten to ask a question this environment can
answer. That would have been the easy move and it is the one this whole project
exists to refuse: predictions edited after meeting the data are not predictions.
It stays locked, and whoever runs it next runs it exactly as written.

## What was done instead, and it is a different question

`cohort_preregistration.md` registers a smaller, separate question about a file
already in this repository — and it is registered as a separate pre-registration
with its own hash, not folded into the first one. Its result is in the README
and in `test_cohort.py`.

## What it would take to run the real thing

Network access to `huggingface.co`, or an approved MCP path to the Hub. Fetch
the cards, freeze them with a date and a hash into `plexus/hf_cards_frozen.json`,
and run the procedure in section "Procedure, fixed in advance". Everything after
the freeze is offline and deterministic, so the test is reproducible by anybody
once the fetch has happened once.
