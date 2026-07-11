#!/usr/bin/env python3
# ======================================================================
# scout_dataset.py  —  GT two-hop "decoding-hop" reconnaissance
# ----------------------------------------------------------------------
# Point this at ANY legal dataset (CSV / ZIP / folder of text files) and
# it reports whether the data can support a *legitimate* two-hop test,
# i.e. whether it contains:
#     (1) a LIVE decoding hop  (disposition/outcome with real variance),
#     (2) that is NOT a deterministic function of the topic/encoding
#         channel  (else D_gap collapses to D_enc, or the outcome is
#         circular with D_enc — the failure mode of the CAP legislative
#         and CAP SCOTUS files),
#     (3) a candidate E / cost / durability signal DISTINCT from the
#         decode hop  (else the two-hop "test" is a tautology),
#     (4) candidate U (load) columns and a text field for D_enc/D_dec.
#
# It prints a GO / NO-GO / GO-WITH-EXTRACTION verdict. It is designed to
# be ABLE TO SAY NO. A green light is not the goal; an honest one is.
#
# Colab:  !python scout_dataset.py /path/to/data            (csv/zip/dir)
#     or  from scout_dataset import scout; scout("/path/to/data")
#
# Deps: pandas, numpy, scipy, scikit-learn  (all preinstalled in Colab).
# Optional for .doc/.docx/.pdf/.rtf text extraction: textract / python-docx
# / pdfminer.six  — the script degrades gracefully and tells you if a
# format needs a converter.
# ======================================================================
import os, re, sys, io, zipfile, glob, math, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd

# ---------- thresholds (tune to taste; defaults are deliberately strict) ----------
ENT_LIVE      = 0.30   # min entropy (bits) for a decode hop to count as "live"
MODAL_MAX     = 0.97   # a column >97% one value is treated as ~constant/placeholder
V_DETERMIN    = 0.60   # Cramer's V above this => decode hop ~determined by topic (bad)
V_DISTINCT_E  = 0.40   # candidate E with V/|r| below this vs decode hop => usable as separate E
COVERAGE_MIN  = 0.60   # min share of docs a text-extractor must label to be trusted

# ---------- name patterns that hint at a column's ROLE ----------
PAT = {
 "decode":  r"(disposition|outcome|verdict|ruling|judgment|holding|result|"
            r"revers|affirm|remand|vacat|grant|dismiss|denied|overrul|"
            r"party_?win|winner|declaration_?uncon|precedent_?alter)",
 "topic":   r"(topic|issue|area|subject|category|majortopic|subtopic|pap_)",
 "text":    r"(text|facts?|summary|opinion|reasoning|body|content|description|"
            r"decision_text|full_?text)",
 "U_load":  r"(length|len\b|n_?judges|word|token|n_?parties|n_?cited|n_?citation|"
            r"duration|proc_?duration|pages?|size|complexity|amici|amicus)",
 "durab":   r"(leading|cited|citation|n_?cited|precedent|influence|later|"
            r"overrul|subsequent|durab)",
 "id":      r"(^id$|_id$|docket|citation|url|href|case_?name|doi|link|filename)",
}

# ---------- multilingual disposition lexicon (for RAW-TEXT corpora) ----------
# Maps a normalized decode-fidelity class to regex alternations.
# GRANTED  = higher court overturned the lower court (decode failure)
# REJECTED = higher court upheld the lower court     (faithful decode)
# he = Hebrew (your Israeli Supreme Court target), en/de/fr for others.
DISPO_LEX = {
 "granted": [
    r"\b(revers|vacat|set aside|overturn|appeal (is )?(allowed|granted|upheld|sustained)|"
      r"petition (is )?granted)\b",                                   # en
    r"(הערעור|העתירה|הבקשה)\s*(מתקבל[ת]?|התקבל[ה]?)", r"אנו\s+מקבלים", r"\bמבוטל\b", r"\bבטל\b",  # he
    r"\bgutgehei(ss|ß)en\b", r"\baufgehoben\b",                       # de
    r"\b(admis|accueilli|annul[eé])\b",                              # fr
 ],
 "rejected": [
    r"\b(affirm|uphe?ld|appeal (is )?(dismissed|denied|rejected)|petition (is )?(denied|dismissed))\b",  # en
    r"(הערעור|העתירה|הבקשה)\s*(נדח[הת]?|נדחית)", r"אנו\s+דוחים",       # he
    r"\babgewiesen\b", r"\babzuweisen\b",                             # de
    r"\b(rejet[eé]|d[ée]bout[eé])\b",                                 # fr
 ],
 "partial":  [r"\b(in part|partly|partially)\b", r"(בחלק[הו]|חלקית)", r"\bteilweise\b", r"\bpartiellement\b"],
 "inadmissible":[r"\b(inadmissible|dismissed for|struck)\b", r"\bנמחק[הת]?\b", r"\bNichteintreten\b", r"\birrecevable\b"],
 "remanded": [r"\b(remand|returned to the lower)\b", r"\bמוחזר\b", r"\bzur[üu]ckgewiesen\b", r"\brenvoy[eé]\b"],
}

# ======================================================================
def entropy_bits(series):
    p = series.dropna().value_counts(normalize=True).values
    p = p[p > 0]
    return float(-(p*np.log2(p)).sum()) if len(p) else 0.0

def modal_share(series):
    vc = series.dropna().value_counts(normalize=True)
    return float(vc.iloc[0]) if len(vc) else 1.0

def cramers_v(a, b):
    from scipy.stats import chi2_contingency
    m = pd.DataFrame({"a": a, "b": b}).dropna()
    if m["a"].nunique() < 2 or m["b"].nunique() < 2:
        return np.nan
    ct = pd.crosstab(m["a"], m["b"])
    chi2, _, _, _ = chi2_contingency(ct)
    return float(np.sqrt(chi2 / (ct.values.sum() * (min(ct.shape) - 1))))

def role_of(colname):
    n = str(colname).lower()
    for role in ("decode", "durab", "U_load", "topic", "text", "id"):
        if re.search(PAT[role], n):
            return role
    return "other"

# ---------- loaders ----------
def _read_csv_any(path, nrows=None):
    for enc in ("utf-8", "latin-1", "cp1252", "utf-16"):
        try:
            with open(path, "rb") as f:
                head = f.read(8192).decode(enc, errors="strict")
            sep = "\t" if head.count("\t") > head.count(",") else ","
            return pd.read_csv(path, encoding=enc, sep=sep, nrows=nrows,
                               low_memory=False, on_bad_lines="skip")
        except Exception:
            continue
    return pd.read_csv(path, encoding="latin-1", engine="python",
                       nrows=nrows, on_bad_lines="skip")

def _extract_text_from_file(fp):
    ext = os.path.splitext(fp)[1].lower()
    try:
        if ext in (".txt", ".md", ".json", ".html", ".htm", ".xml"):
            return open(fp, encoding="utf-8", errors="replace").read()
        if ext == ".docx":
            import docx; return "\n".join(p.text for p in docx.Document(fp).paragraphs)
        if ext == ".pdf":
            from pdfminer.high_level import extract_text; return extract_text(fp)
        if ext in (".rtf", ".doc"):
            import textract; return textract.process(fp).decode("utf-8", "replace")
    except Exception as e:
        return f"__UNREADABLE__({ext}:{e})"
    # unknown extension (e.g. Israeli-court .O03/.F05) -> try raw, else flag
    try:
        return open(fp, encoding="utf-8", errors="replace").read()
    except Exception:
        return "__UNREADABLE__(%s)" % ext

def load_any(path, sample_rows=None):
    """Return (df, kind). df always has usable columns; raw-text corpora
    come back as a df with a 'text' column."""
    if path.lower().endswith(".zip"):
        tmp = path + "__unz"
        os.makedirs(tmp, exist_ok=True)
        with zipfile.ZipFile(path) as z: z.extractall(tmp)
        path = tmp
    if os.path.isdir(path):
        csvs = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)
        if csvs:                                   # a folder that contains CSVs
            return _read_csv_any(csvs[0], nrows=sample_rows), "csv"
        docs = [p for p in glob.glob(os.path.join(path, "**", "*"), recursive=True)
                if os.path.isfile(p)]
        rows = [{"filename": os.path.basename(p), "text": _extract_text_from_file(p)}
                for p in docs[: (sample_rows or 100000)]]
        return pd.DataFrame(rows), "textcorpus"
    return _read_csv_any(path, nrows=sample_rows), "csv"

# ---------- text disposition extractor (for corpora with no labels) ----------
def extract_dispositions(texts):
    compiled = {k: [re.compile(p, re.I) for p in v] for k, v in DISPO_LEX.items()}
    labels = []
    for t in texts:
        t = "" if not isinstance(t, str) else t
        # look mainly at the tail, where operative rulings usually sit
        tail = t[-4000:] if len(t) > 4000 else t
        hits = [k for k, ps in compiled.items() if any(p.search(tail) for p in ps)]
        if not hits: labels.append(None)
        elif "granted" in hits and "rejected" in hits: labels.append("mixed")
        else: labels.append(hits[0])
    s = pd.Series(labels)
    coverage = float(s.notna().mean())
    return s, coverage

# ======================================================================
def scout(path, sample_rows=None, verbose=True):
    df, kind = load_any(path, sample_rows=sample_rows)
    L = []
    def out(x=""):
        L.append(str(x))
        if verbose: print(x)

    out("="*72)
    out(f"SCOUT REPORT  |  {path}")
    out(f"kind={kind}   rows={len(df):,}   cols={len(df.columns)}")
    out("="*72)

    # ---- column profile + role guess ----
    prof = []
    n = len(df)
    for c in df.columns:
        s = df[c]
        card = int(s.nunique(dropna=True))
        role = role_of(c)
        # a (near-)unique column is an identifier, not a usable topic/decode/text/durab
        # field. This stops per-row-unique ID/citation columns from producing spurious
        # Cramer's V = 1.0 in the independence gates.
        if n and card > 0.95 * n and role in ("topic", "decode", "text", "durab"):
            role = "id"
        mlen = float(s.dropna().astype(str).str.len().mean()) if s.notna().any() else 0.0
        prof.append(dict(col=c, role=role, dtype=str(s.dtype), card=card,
                         modal=round(modal_share(s), 3), ent=round(entropy_bits(s), 2),
                         nullpct=round(float(s.isna().mean()), 2), mlen=round(mlen, 0)))
    P = pd.DataFrame(prof)
    out("\nCOLUMN PROFILE (role guessed from name + stats):")
    out(P.drop(columns=["mlen"]).to_string(index=False, max_colwidth=28))

    # ---- unreadable-format warning for text corpora ----
    if kind == "textcorpus" and "text" in df:
        bad = df["text"].astype(str).str.startswith("__UNREADABLE__").mean()
        if bad > 0.1:
            out(f"\n[!] {bad:.0%} of files could not be text-extracted with the "
                "libraries present.")
            out("    Install a converter for the source format (e.g. Israeli-court "
                ".O03/.F05 are usually DOC/RTF/PDF):")
            out("    pip install textract python-docx pdfmin.six  — then re-run.")

    # ---- pick candidates ----
    def picks(role, min_ent=0.0):
        sub = P[(P.role == role) & (P.ent >= min_ent) & (P.modal <= MODAL_MAX)]
        return sub.sort_values("ent", ascending=False)

    decode_live = picks("decode", ENT_LIVE)
    decode_all  = P[P.role == "decode"]
    text_cols   = P[((P.role == "text") | (P.dtype == "object")) & (P.mlen >= 200)]
    U_cols      = P[(P.role == "U_load")]
    E_cols      = P[(P.role == "durab") | (P.role == "U_load")]
    topic_cols  = P[P.role == "topic"]

    out("\nCANDIDATES")
    out(f"  decode-hop (live, entropy>= {ENT_LIVE}): "
        + (", ".join(f"{r.col}[{r.ent}b]" for _, r in decode_live.iterrows()) or "NONE"))
    if len(decode_all) and not len(decode_live):
        out("     (decode-named columns exist but are ~constant/placeholder: "
            + ", ".join(f"{r.col}[{r.ent}b,modal {r.modal:.0%}]"
                        for _, r in decode_all.iterrows()) + ")")
    out(f"  text (for D_enc/D_dec):  "
        + (", ".join(text_cols.col.tolist()) or "NONE"))
    out(f"  U (load):                "
        + (", ".join(U_cols.col.tolist()) or "NONE"))
    out(f"  E / durability (distinct outcome candidates): "
        + (", ".join(P[P.role == 'durab'].col.tolist()) or "NONE"))

    # ---- GATES ----
    out("\nGATES")
    notes = []
    COARSE = max(100, int(0.05 * n))   # a usable topic/E categorical must be this coarse

    # Gate 1: a live decode hop in a structured column (or, failing that, from text)?
    g1 = len(decode_live) > 0
    best = decode_live.iloc[0]["col"] if g1 else None
    be   = decode_live.iloc[0]["ent"] if g1 else None
    if g1:
        out(f"  [1] LIVE decode hop .......... PASS  ({best}, {be} bits)")
    else:
        out("  [1] LIVE decode hop .......... FAIL  (no structured disposition/"
            "outcome column with real variance)")

    extracted = None
    if not g1 and len(text_cols):
        tcol = text_cols.iloc[0]["col"]
        out(f"\n  -> No structured decode column. Running text disposition "
            f"extractor on '{tcol}' (langs: en, he, de, fr) ...")
        extracted, cov = extract_dispositions(df[tcol].tolist())
        ent_x = entropy_bits(extracted)
        out(f"     coverage = {cov:.0%}   extracted-entropy = {ent_x:.2f} bits")
        out("     extracted class counts: "
            + str(extracted.value_counts(dropna=False).head(6).to_dict()))
        if cov >= COVERAGE_MIN and ent_x >= ENT_LIVE:
            g1 = True; best = f"{tcol}->extracted_dispo"; be = ent_x
            out("  [1] LIVE decode hop (via extraction) .... PASS")
        else:
            out(f"  [1] LIVE decode hop (via extraction) .... LOW-COVERAGE "
                f"(need cov>= {COVERAGE_MIN:.0%} & entropy>= {ENT_LIVE}); "
                "extend/validate the lexicon for this corpus/language before trusting.")

    # Gate 2: decode hop is not (near-)determined by a COARSE topic channel.
    # Only coarse categoricals count as "topic" here; per-row-unique columns are IDs.
    g2 = True
    if g1:
        dser = extracted if (extracted is not None) else df[best]
        topic_test = topic_cols[topic_cols.card <= COARSE]
        if len(topic_test):
            vmax, worst = 0.0, None
            for _, tr in topic_test.iterrows():
                v = cramers_v(dser, df[tr.col])
                if v == v and v > vmax: vmax, worst = v, tr.col   # v==v filters NaN
            if vmax <= V_DETERMIN:
                out(f"  [2] decode independent of topic ... PASS  "
                    f"(max Cramer's V={vmax:.2f} vs {worst})")
            else:
                g2 = False
                out(f"  [2] decode independent of topic ... FAIL  (V={vmax:.2f} vs "
                    f"{worst}: disposition ~determined by topic -> circular with D_enc)")
                notes.append("decode hop is largely a restatement of the topic channel")
        else:
            out("  [2] decode independent of topic ... N/A   "
                "(no coarse topic column to test against)")

    # Gate 3: an E / cost / durability signal that is DISTINCT from the decode hop.
    g3 = False; best_e = None; best_stat = None
    if g1:
        durab = P[P.role == "durab"]
        cand = [er.col for _, er in durab.iterrows()
                if pd.api.types.is_numeric_dtype(df[er.col]) or er.card <= COARSE]
        if cand:
            dser = extracted if (extracted is not None) else df[best]
            best_stat = 1.0
            for c in cand:
                col = df[c]
                if pd.api.types.is_numeric_dtype(col):
                    m = pd.DataFrame({"e": pd.to_numeric(col, errors="coerce"),
                                      "d": pd.factorize(dser)[0]}).dropna()
                    stat = abs(m.corr().iloc[0, 1]) if len(m) > 5 else 1.0
                else:
                    stat = cramers_v(col, dser)
                if stat == stat and stat < best_stat:
                    best_stat, best_e = stat, c
            if best_e is not None and best_stat <= V_DISTINCT_E:
                g3 = True
                out(f"  [3] distinct E signal ........ PASS  ({best_e}, "
                    f"coupling={best_stat:.2f} <= {V_DISTINCT_E})")
            elif best_e is not None:
                out(f"  [3] distinct E signal ........ WEAK  ({best_e}, "
                    f"coupling={best_stat:.2f}: correlated with the decode hop — "
                    "control for it or the two-hop test is a tautology)")
            else:
                out("  [3] distinct E signal ........ NONE")
        else:
            out("  [3] distinct E signal ........ NONE  (only the disposition is "
                "observed; derive a separate downstream outcome: later-overruled / "
                "citation durability / processing cost)")

    # ---- verdict ----
    out("\nVERDICT")
    U_txt = ", ".join(U_cols.col.tolist()) or "define one"
    T_txt = text_cols.iloc[0]["col"] if len(text_cols) else "none (link a full-text corpus)"
    if g1 and g2 and g3:
        verdict = "GO"
        out("  GO — supports a legitimate two-hop test.")
        out(f"       decode hop = {best};  separate E = {best_e};  U = {U_txt};  text = {T_txt}")
    elif g1 and g2 and not g3:
        verdict = "GO-BUT-DEFINE-E"
        out("  GO-BUT-DEFINE-E — real, non-circular decode hop, but no downstream outcome "
            "distinct from it. Derive one (later-overruled, citation durability, proc cost) "
            "before E=U·D vs U·D², or you rebuild the legislative tautology.")
    elif g1 and not g2:
        verdict = "NO-GO (circular)"
        out("  NO-GO — the decode hop is ~determined by the topic channel, so a D_gap built "
            "here is circular with D_enc (the CAP-file failure in a new guise).")
    elif extracted is not None:
        verdict = "GO-WITH-EXTRACTION" if g1 else "LOW-COVERAGE"
        out(f"  {verdict} — decode hop must be mined from text; validate the extractor "
            "on a hand-labelled sample before trusting it.")
    else:
        verdict = "NO-GO"
        out("  NO-GO — no live decode hop. CAP-file failure mode: any D_dec built here is "
            "~constant, so D_gap = D_enc and the two-hop model is inert.")
    for nt in notes: out("  note: " + nt)
    out("="*72)
    return {"verdict": verdict, "profile": P, "report": "\n".join(L)}

# ======================================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python scout_dataset.py <path-to-csv|zip|folder> [sample_rows]")
        sys.exit(1)
    p = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else None
    scout(p, sample_rows=n)
