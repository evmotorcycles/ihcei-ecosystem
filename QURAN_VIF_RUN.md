# The VIF number does not survive its own null

**Spec** `af27d2c9c9398ca4f99a4772e6769a23cf4ab8198542067f453971c83e6c09b3` · **1/3** ·
[Artifact](https://claude.ai/code/artifact/6a670fd9-4b1c-4368-842a-dcb24da91ff9)

```bash
python3 -m pytest -q quran/test_qvif.py
```

## The claim and the prior question

A VIF of **1.000073** between a Ṣalāt track and a Zakāt track was offered as showing the text
handles seeking and sharing as independent channel legs. Before accepting it, the prior
question: **on this substrate, does a near-1.0 VIF distinguish anything at all?**

`VIF = 1/(1−r²)`, and across 6,236 ayahs almost every word is absent from almost every ayah.
Two rare tracks are both nearly all zeros, so `r` lands near zero *whatever the words mean*.

## The answer

```
  99.8% of 1,200 frequency-matched RANDOM unrelated word pairs clear VIF < 1.05
  null median VIF              1.000032
  measured VIF(SALAT, ZAKAT)   1.000028      r = −0.005302
  its percentile                   46th
```

**54% of arbitrary unrelated word pairs are more "orthogonal" than Ṣalāt and Zakāt.**
A test that cannot fail is not evidence — and on this substrate it could not fail.

## Every pair looks orthogonal, including same-root words

**28 of 28** pairs among the eight declared tracks clear the bar:

| Pair | | VIF |
|---|---|---:|
| **ĪMĀN \| MUʾMIN** | **the same root** | 1.004136 |
| **MILLAH \| NAṢĀRĀ** | co-occur in 2:120 | 1.016447 |
| MUʾMIN \| MUSLIM | matrix maximum | 1.019291 |
| SALAT \| ZAKAT | the pair under test | 1.000028 |

A metric that reports *īmān* and *muʾmin* as independent is not measuring independence here.

## It is also not the same quantity as the yeast number

Yeast **1.0026** and GitHub **1.0203** were computed on **continuous per-node features**,
where every unit has a real value on both axes and collinearity is a live possibility.
Per-ayah word counts are overwhelmingly zero. Sharing the name does not make them comparable.

## W5 also failed, and that one is a real finding

Using the same designation matcher that scored **7 of 7** control proper nouns at zero
(spec `708ac80e`):

```
  "those who believed"   الَّذِينَ آمَنُوا   root A-M-N    268 times
  "those who submitted"  الَّذِينَ أَسْلَمُوا  root S-L-M      1 time   (5:44)
```

The gate needed ≥ 5 for each root and is reported **failed**. The verb *aslama* exists and is
used (~22 finite tokens), but this text names a **group** by that act exactly once. The
group-by-action designation attaches overwhelmingly to **īmān**, not to **islām** — 268 to 1.

## The integrity gate earned its place

The first run failed W1: three track patterns matched nothing, because hamza-on-waw (U+0624)
decomposes under NFD into waw + a combining mark (so *muʾmin* is `مومن`), and *zakāt* carries
a waw (`زكوٰة`). Regexes corrected, run repeated. **W2's result is unchanged** — the null never
depended on the track definitions.

## What none of this licenses

Nothing about what any word means. Nothing about any living community. And nothing about
design: even had the tracks come out independent, **distributional independence is not
evidence of authorial architecture** — that inference does not follow, and would not have
followed had the number gone the other way.
