# The firewall

The instruction this module exists under, quoted exactly:

> "Note NCU terminology are Governce philosophy prior terminology they can't move
> from layer 2 and 1 but what can be do is abstracting layer 1 telemetry into
> metaphorical representation to explain the Governance philosophy. Note their is
> no Dataset or computer simulation that can prove NCU. I repeat what can be done
> is abstracting computational telemetry in to metaphorical representation to
> illustrate Governce philosophy."

And:

> "Nafs is a cognitive essence it's primary functions are Salat and Zakat."

## What that means in code

```
    LAYER 1                    LAYER 3
    measured telemetry   ──▶   metaphorical representation
    (LMD, LISM, swarm)         (illustrates the philosophy)

                         ◀──   NOTHING COMES BACK
```

**One direction only.** Layer-1 numbers may be *abstracted into* a metaphor.
A metaphor may never be abstracted back into a number, used as an input, tuned
against, or counted as support.

## Four rules, each enforced by a test

1. **No NCU term appears in any layer-1 module.** The philosophy vocabulary does
   not migrate down. `test_ncu.py` greps every measurement module and fails if
   it finds one.
2. **Every metaphor cites a real measured number**, by file and field, from a
   results file that a test re-reads. A metaphor with an invented number is a
   fabrication wearing a metaphor's clothes.
3. **No metaphor is ever an input.** Nothing in this package is imported by any
   layer-1 module, and this package computes nothing.
4. **Every rendering carries the stamp.** `PROVES: NOTHING`, on every entry, in
   the data structure — not only in a footnote someone can crop.

## The thing this module must never be mistaken for

**No dataset and no simulation can prove NCU.** The swarm dataset in
`swarm-lmd/data/` is simulated; the LMD numbers are measurements of a
pseudo-inverse. Neither is evidence for a philosophy, and a metaphor built from
them is an *illustration*, not an argument. That is the whole point of putting a
firewall here rather than a bridge.
