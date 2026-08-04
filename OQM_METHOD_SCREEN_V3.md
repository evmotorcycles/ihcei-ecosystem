# The OQM Method-Conformance Screen (v3)

**Spec** `b5eaa3051ebe499b7751ac72c477204061a5414ff4f0613e21414c02e940c669`
· supersedes v2 `d8243d3a…` · **8/8** · 16 tests · 6,236 āyāt · 0 simulated values

Run: `cd quran && python3 oqm_screen_v3.py && python3 -m pytest test_oqm_screen_v3.py -q`

---

## What changed, and why it needed to change

v1 and v2 screened Qurʾānic terms along axes **I invented** — grammatical class
(verbal / mixed / nominal), then mutability (can the state be entered and left).
Both were measured honestly and both still reproduce. But no source document asks
for either. They were my reconstruction of what an OQM screen *ought* to test.

Then sixteen primary OQM documents were supplied and read. They state their own
method rules explicitly, and those rules turn out to be machine-checkable. So v3
stops inventing axes and does two different things:

1. implements **the rules the documents state**, as gates on every verdict; and
2. checks the instrument against **flat textual claims the documents themselves
   make** — so the controls are *source-supplied* rather than chosen by me for
   convenience.

A control I pick is a control I can pick to pass. A control N159 states before I
arrive is not.

## Getting the documents open at all

`Read(pages=…)` failed on every PDF: poppler-utils is not installed in this
container, so `pdftoppm` could not render pages. Text was extracted with `pypdf`
instead. **`Duaa_Publication_1.pdf` is scanned page images** and yielded nothing
but running headers — it is recorded as *unread*, not summarised from its title.

## The two rules, quoted

**The Janāḥ rule** — YT89, expounding 6:38 `مَّا فَرَّطْنَا فِى ٱلْكِتَٰبِ مِن شَىْءٍ`:

> anytime you come up with an idea, it is not enough to have one piece of
> evidence. You have to have a minimum of two

Operationalised: a verdict needs ≥ 2 witnesses in **distinct sūrahs**. Exactly one
witness returns `ONE_WING` — which **withholds** a verdict rather than issuing a
negative one.

**The coverage rule** — N159, on 58:11:

> The root فَسَحَ and جَلَسَ are only used in this single Aya… therefore, we cannot
> produce a relevant interpretation for this Aya. Referring to a Dictionary will
> only yield a plausible opinion!

Operationalised: a root attested in one āya is `UNTESTABLE_BY_OQM` and its score is
not evidence. N159 raises this *against OQM itself* — *"How Can We Claim that the
OQM is useful (let alone essential) if we can only produce an unsupported
opinion?"* A method that names its own coverage limit is behaving correctly. This
is that verdict, pre-registered.

## The defect the documents exposed in my own instrument

`qtext.normalise()` removes every combining mark by Unicode category `Mn`. **Shadda
is `Mn`.** So v1 and v2 could not tell `فَعَلَ` from `فَعَّلَ` — Form I from Form II —
which is the single distinction N159 and N161 make load-bearing. The v1/v2 screens
were blind to the one thing the sources insist on.

v3 adds a vocalisation-preserving path. `normalise()` is **unchanged**, so v1 and v2
reproduce byte-identically and are not re-scored. Gate Z1 *demonstrates* the
blindness rather than asserting it.

## Results

| Gate | Result |
|---|---|
| Z1 instrument can read verb form | ✅ `skeleton` separates `يُنَزِّل`/`يَنزِلُ`; `normalise` collapses them |
| Z2 positive control — root ج-ل-س | ✅ exactly `['58:11']` (`ٱلْمَجَٰلِسِ`) |
| Z3 negative control — root ف-س-ح | ✅ exactly `['58:11']`, all 3 tokens, all 5 near-misses rejected |
| Z4 Janāḥ rule binds | ✅ withholds the `islām` verdict v2 issued |
| Z5 coverage rule fires | ✅ both roots `UNTESTABLE_BY_OQM` |
| Z6 **risky** — no Form IV imperfect `يُنْزِل` | ✅ **0 found** |
| Z7 **risky** — `نَزَّلَ`/`أَنزَلَ` minimal pairs | ✅ both witnesses, clears Janāḥ at its minimum |
| Z8 …and it does not generalise | ✅ reported against interest |
| Z9 does any of this establish meaning | **excluded** — a test that cannot fail is not evidence |
| Z10 claims about living communities | **excluded** — none made |

### The risky claim survived

N159 asserts the Form IV imperfect `يُنْزِل` is **absent from the text**. A single
counterexample ends it. There are none. Every imperfect of *n-z-l* is Form II
(`يُنَزِّل`, 27), Form V (`تَنَزَّل`), or Form I (`يَنزِلُ`, 2 — at 34:2 and 57:4).
Form I is **not** a counterexample and Z6 refuses to count it as one.

### One claim that holds only where it is tested

N159's `نَزَّلَ`-for-the-Qurʾān / `أَنزَلَ`-for-the-Torah split holds on both minimal
pairs:

- **3:3** carries both forms *inside one āya* — `نَزَّلَ عَلَيْكَ ٱلْكِتَٰبَ … وَأَنزَلَ ٱلتَّوْرَىٰةَ وَٱلْإِنجِيلَ`. Context cannot be disputed.
- **47:9** `كَرِهُوا۟ مَآ أَنزَلَ ٱللَّهُ` vs **47:26** `كَرِهُوا۟ مَا نَزَّلَ ٱللَّهُ` — identical frame, differing only in verb form.

Those are exactly **2 independent sūrahs**, because 47:9 and 47:26 share a sūrah and
count once. The Janāḥ rule binds here at its minimum rather than comfortably.

**Corpus-wide it does *not* hold as a categorical rule**: 26 non-Form-II uses with
al-Kitāb/Qurʾān against 14 Form II. Reported, not buried. The broad test is the
*weaker* instrument — `ٱلْكِتَٰب` is itself ambiguous between the Qurʾān and earlier
scripture, which is the very thing in dispute, so a context window cannot adjudicate
it. Declaring N159 refuted on that proxy would be the overclaiming this discipline
forbids.

## What v3 corrects in v2

Under the Janāḥ rule, `islām` has **one** witness (9:74) → `ONE_WING`, **no verdict**.
v2 called it `FIXED`. That was a verdict issued on one wing. `īmān` has 8 witnesses
across 5 sūrahs and stands.

## Two matcher defects caught and fixed mid-run

Both are recorded in the code rather than smoothed over:

1. An index-0 ambiguity rule rejected all five near-misses correctly but **silently
   dropped `يَفْسَحِ`**, a genuine ف-س-ح token in 58:11. The gate still passed — 58:11
   was carried by its other tokens — but a matcher that discards a true positive is
   broken whatever it scores.
2. The replacement rule uses **waṣla** (`ٱ`, U+0671) as the signal for where a stem
   begins — a discriminator that is *in the source text*, not in my judgement. But
   `voc()` folds waṣla to plain alif, so `فَٱفْسَحُوا۟` was lost until the matcher was
   fed raw tokens.

Final rule, applied identically to every root: strip the leading proclitic run,
halting at waṣla.

```
فَٱفْسَحُوا۟   fa + ٱ → stop → stem فسحوا      root f-s-h   KEPT
أَفَسِحْرٌ     ʾa + fa, no waṣla → stem سحر     root s-h-r   DROPPED
فَسُحْقًۭا      fa, no waṣla     → stem سحقا     root s-h-q   DROPPED
ٱلْمَجَٰلِسِ    waṣla at index 0 → stem intact   root j-l-s   KEPT
```

The five near-misses — 52:15, 67:11, 9:2, 20:61, 4:172 — are all `fa-` plus a root in
س-ح-*, which leaves `فسح` contiguous after long-vowel stripping. **I chose none of
them**; they are whatever the corpus throws at a ف-س-ح matcher, which is what makes
them a stronger control than any I would have picked.

## A document claim reported precisely rather than endorsed

N159 says the form `نُفَرِّق` *"occurs 4 times (2:136, 2:285, 3:84, and 4:152)"*. The
exact form occurs at **three** of those; **4:152 carries `يُفَرِّقُوا۟`** — same root,
same Form II, different person. The wording is loose about *form* versus *root*.

Recorded, endorsed in neither direction, and deliberately **not used as a gate** — a
claim that is ambiguous as stated cannot be a pass/fail test of anything.

## The firewall: what is still not established

Nothing here establishes **meaning**. Verb form, root coverage and witness counts are
morphological and distributional facts; none selects between competing readings of
any term.

N186 defines the governance terms by **function within a governance system**:

> Muslim: someone who submits to the Deen in accordance with its Governance ·
> Muʾmin: someone who understands the justification and bases for the Governance ·
> Muḥsin: someone who explains at least some of the motivation and need for the
> details of the Governance · Malak: someone who can navigate and execute across
> multiple areas of the Governance

and N167, on 53:21–23, supplies the warrant for refusing inherited labels:

> They are but labels that you and your forefathers have named, and in which Allahh
> has not instilled any authoritativeness.

**N186 asserts these definitions. It does not derive them from a measurement, and
this screen does not test them.** They are Layer 3. A morphological screen *cannot*
adjudicate whether these are governance-functional labels or theological-identity
labels, because neither reading is a morphological claim.

What the documents *do* settle is that the governance-label reading is in fact what
the OQM documents say. That is a question **about the documents**, and it is answered
by quotation — not a morphological result, and this screen does not pretend to be
one.
