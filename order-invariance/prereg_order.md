# Pre-registration — next-token reading vs structural reading, on one document

Written and hashed **before the run**. 2026-09-14.

Terminology note: every label in the code and results below is ordinary English.
The document's own vocabulary stays in the document. That is this project's
standing rule and it costs nothing here — the structure is what is being read,
not the words.

---

## The question

A language model reads a document as a **sequence** and predicts what comes
next. Its object is the token stream, and its reading is therefore a function of
**order**.

The structural engine in this repository has no notion of "next". Its object is
a **graph someone drew** — parts and links — and effective resistance is a
global quantity computed from the whole Laplacian at once. There is no first
node and no last node.

So the two should differ in a way that is not a matter of degree. This run
measures whether they do, on the same document, on the same day.

## What the document declares

An uploaded study argues that a short chapter means "the pressing". Its declared
structure, read off the document and recorded here so a reader can disagree with
the reading rather than reverse-engineer it:

- **three cited passages**, each containing the same image
- **one declared interpretive method**, stated at the front, which the document
  says is required to read any of them
- **one conclusion** about the chapter
- **three prerequisites** (prior segments a reader is told to watch first)

`where`: the uploaded PDF, sections "In This Segment", "Understanding the
Metaphor", and the concluding section.

The modelling decision that carries everything: **the three passages route
through the one declared method**, because the document says explicitly that
without that method the passages "will not make any sense to you". A reader who
thinks the passages stand independently of the method would draw a different
graph and should get a different number — that is the point of drawing it.

---

## Predictions

| # | Prediction | Value |
|---|---|---|
| N1 | Three passages on one declared method settle **1/9** each | 0.111111… |
| N2 | The declared method is a **cut vertex** — removing it breaks the argument | yes |
| N3 | **Over 500 random shuffles of the input order, every structural reading is identical** | max deviation < 1e-12 |
| N4 | Renaming every node to an opaque token leaves the reading identical to floating-point | < 1e-9 |
| N5 | A next-word model trained on the document's own text **drops** in mean log-probability when the sentences are shuffled | drops |
| N6 | The declared prerequisites do **not** enter the support graph, because the document states them as prerequisites rather than as evidence | absent |

**N3 is the whole answer and N5 is its contrast.** If N3 holds and N5 holds, the
two readings differ in kind: one is destroyed by shuffling and the other cannot
be moved by it.

**N5 is a PROXY, not a language model.** It is a bigram next-word model fitted on
this document alone. No LLM is run here and no claim is made about what any LLM
would output. The proxy shares exactly one property with a language model — it
predicts a next token from a previous one — and that is the only property under
test.

---

## Nulls, registered in advance

**NULL-N1.** Order-invariance is not a virtue. It is the correct property for
reading a structure and the **wrong** property for reading prose. A document's
argument often depends on order — "A, therefore B" is not "B, therefore A" — and
the structural engine is blind to that. Anyone who drew the graph in the wrong
direction gets a confident, stable, wrong number.

**NULL-N2.** The graph is hand-drawn from the document by me. The engine
measures what was drawn. If the modelling decision above is wrong, every number
here is a correct reading of a wrong picture.

**NULL-N3.** Nothing here reads meaning. The engine cannot tell whether the
document's conclusion is right, well-argued, or even about what it says it is
about. It reports what rests on what, given a drawing.

**NULL-N4.** A cut vertex is not a fault. A shared method being load-bearing is
what a method IS. The reading says where the load sits.

**NULL-N5.** n = 1 document. Nothing generalises.

---

## What would falsify this

1. **N3 fails** — the structural reading moves under permutation, which would
   mean it has an order dependence nobody declared and the engine is not what it
   claims to be.
2. **N5 fails** — the next-word proxy is *also* order-invariant, which would
   collapse the contrast this run is built on.
3. **N1 fails** — the three-on-one shape does not produce 1/9, which would mean
   the law does not hold on a hand-drawn argument graph.
