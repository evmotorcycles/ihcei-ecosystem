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


def load(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    for r in rows:
        r["ref"] = "%s:%s" % (r["surah_no"], r["ayah_no_surah"])
        r["tokens"] = [normalise(t) for t in re.findall(r"[؀-ۿ]+", r["ayah_ar"])]
        r["bases"] = [base(t) for t in r["tokens"]]
    return rows
