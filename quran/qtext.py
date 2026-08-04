"""
qtext.py -- shared loader and Arabic normaliser for the Quran lexical run.

NORMALISATION NOTES, because two of them changed the answer:
  1. The dataset writes long /a:/ with a DAGGER ALIF (U+0670), e.g. nasara as
     نَصَٰرَىٰ. A naive diacritic strip deletes it and yields نصري, which matches
     nothing. It must become a full alif.
  2. But a dagger alif FOLLOWING alif-maqsura (ىٰ) marks that letter's own long
     vowel -- it is not an extra alif. Handled first, or نصارى becomes نصاريا.
  3. Combining marks are removed by Unicode CATEGORY (Mn), not by a hand-written
     range. A hand-written range missed U+064B-U+0652 (fatha, damma, shadda,
     sukun) in a first attempt and silently corrupted every count.
"""
import csv
import re
import unicodedata

csv.field_size_limit(10 ** 7)
CLITICS = ("وبال", "فبال", "وال", "فال", "بال", "كال", "لل", "ال",
           "و", "ف", "ب", "ك", "ل")


def normalise(s):
    s = unicodedata.normalize("NFD", s)
    s = s.replace("ىٰ", "ى")                 # dagger on alif-maqsura: its own vowel
    s = s.replace("ٰ", "ا")                   # any remaining dagger alif IS a long a
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("ـ", "").replace("ٱ", "ا")
    s = re.sub("[آأإ]", "ا", s)
    s = s.replace("ءا", "ا")
    s = s.replace("ى", "ي").replace("ة", "ه")
    return s


def base(w):
    """Strip a leading clitic (conjunction / preposition / definite article)."""
    for p in CLITICS:
        if w.startswith(p) and len(w) - len(p) >= 3:
            return w[len(p):]
    return w


# ---------------------------------------------------------------------------
# ADDED FOR v3. A DEFECT IN THE v1/v2 INSTRUMENT, STATED PLAINLY.
#
# normalise() above deletes every combining mark by Unicode category Mn. SHADDA
# (U+0651) is category Mn. So normalise() cannot tell نَزَّلَ (Form II) from
# أَنزَلَ (Form IV) from يَنزِلُ (Form I) -- it returns the same skeleton for all
# three. N159 and N161 make the فَعَلَ / فَعَّلَ distinction load-bearing, and
# N159's central claim is about a verb FORM. The v1/v2 screens were therefore
# blind to the one distinction the source documents insist on. Nothing below
# changes normalise(), so v1 and v2 reproduce byte-identically.
# ---------------------------------------------------------------------------
SHADDA = "ّ"


def voc(s):
    """Letter shapes unified, EVERY diacritic kept. The vocalised path."""
    s = unicodedata.normalize("NFC", s)
    return s.replace("ـ", "").replace("ٱ", "ا")


def skeleton(s):
    """Consonant skeleton with SHADDA PRESERVED -- enough to read verb form."""
    s = unicodedata.normalize("NFD", s)
    s = s.replace("ىٰ", "ى").replace("ٰ", "ا")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn" or c == SHADDA)
    s = s.replace("ـ", "").replace("ٱ", "ا")
    s = re.sub("[آأإ]", "ا", s)
    return s.replace("ءا", "ا").replace("ى", "ي").replace("ة", "ه")


def defective(w):
    """Drop long vowels, so a root can be sought as a contiguous run.

    NOT sufficient on its own: fa- + a root in s-h-* (سحر، سحق، سيح، سحت، حشر)
    leaves فسح contiguous and yields a FALSE POSITIVE. v3 pins that down with an
    enumerated form list and keeps those five ayahs as a negative control.
    """
    return "".join(c for c in w if c not in "اوي")


def load_voc(path):
    """Same rows as load(), plus the vocalised and shadda-bearing token lists."""
    rows = load(path)
    for r in rows:
        raw = re.findall(r"[؀-ۿ]+", r["ayah_ar"])
        # r["raw"] keeps WASLA (U+0671) intact. voc() folds it to plain alif, which
        # is fine for reading vowels but destroys the one signal that says where a
        # stem begins -- so anything doing morphology must read r["raw"].
        r["raw"] = raw
        r["voc"] = [voc(t) for t in raw]
        r["skel"] = [skeleton(t) for t in raw]
    return rows


def load(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    for r in rows:
        r["ref"] = "%s:%s" % (r["surah_no"], r["ayah_no_surah"])
        r["tokens"] = [normalise(t) for t in re.findall(r"[؀-ۿ]+", r["ayah_ar"])]
        r["bases"] = [base(t) for t in r["tokens"]]
    return rows
