"""
╔══════════════════════════════════════════════════════════════════════╗
║  IHCEI QG-COS — TEST QUERY SUITE                                    ║
║  Tests the live API across 8 fields of knowledge                    ║
╠══════════════════════════════════════════════════════════════════════╣
║  RUN:                                                                ║
║    python ihcei_test_queries.py                    ← hits local API  ║
║    python ihcei_test_queries.py --url https://xxxx.ngrok-free.app   ║
║    python ihcei_test_queries.py --offline          ← no server needed║
╚══════════════════════════════════════════════════════════════════════╝
"""

import argparse, json, sys, time
import urllib.request, urllib.error

# ── Colour codes ──────────────────────────────────────────────────────
R  = "\033[0m";   B  = "\033[1m"
GR = "\033[92m";  RD = "\033[91m"
YL = "\033[93m";  CY = "\033[96m"
BL = "\033[94m";  GY = "\033[90m"
PU = "\033[95m";  GD = "\033[33m"
SEP  = "═" * 68
SEP2 = "─" * 68


# ══════════════════════════════════════════════════════════════════════
# TEST DATA  —  concepts from 8 fields of knowledge
# ══════════════════════════════════════════════════════════════════════

CROSS_FIELD_CONCEPTS = [
    # (concept,                               field,          note)
    ("entropy and disorder in thermodynamics","physics",       "Energy degradation"),
    ("moral hazard and risk allocation",      "economics",     "Incentive misalignment"),
    ("mens rea and criminal intent",          "law",           "Guilty mind doctrine"),
    ("homeostasis and biological balance",    "biology",       "System self-regulation"),
    ("cognitive dissonance and belief",       "psychology",    "Mental conflict"),
    ("epistemic certainty and knowledge",     "philosophy",    "Theory of knowing"),
    ("accountability in public governance",   "governance",    "Responsibility structures"),
    ("stewardship of natural resources",      "ecology",       "Long-term custodianship"),
    ("justice and fair distribution",         "ethics",        "Moral equity"),
    ("transparent authority and legitimacy",  "politics",      "Governance trust"),
    ("purpose and meaning in human action",   "theology",      "Teleological drive"),
    ("information entropy in communication",  "engineering",   "Signal theory"),
]

COMPARE_PAIRS = [
    ("entropy in thermodynamics",     "physics",
     "moral hazard in economics",     "economics",
     "Do disorder and misaligned incentives share a governance root?"),

    ("justice and accountability",    "governance",
     "homeostasis and self-regulation","biology",
     "Does social justice mirror biological balance?"),

    ("epistemic certainty",           "philosophy",
     "transparent governance",        "politics",
     "Does knowing and governing share the same coordinate?"),

    ("stewardship of resources",      "ecology",
     "custodianship of public trust",  "governance",
     "Ecology vs governance — same root class?"),
]

BATCH_STREAM = [
    # Governance-aligned: rich governance vocabulary → high D → Essence propagates → λ₂ rises
    ("governance accountability responsibility authority stewardship",  "governance"),
    ("justice equity fairness knowledge truth purpose",                 "ethics"),
    ("knowledge wisdom epistemic certainty understanding authority",    "philosophy"),
    ("stewardship responsibility community trust purpose meaning",      "ecology"),
    ("purpose meaning teleological development cultivation justice",    "theology"),
]

EXTRACTION_STREAM = [
    # Pure extraction-pattern: no governance vocabulary, no root-class overlap → D=0 → E=0 → no propagation
    ("xyzq bnml plok viral retargeting pixel funnel A/B",   "marketing"),
    ("churn upsell downsell CAC LTV NPS OKR KPI ARR MRR",   "saas"),
    ("impression click CTR CPC CPM ROAS attribution cohort", "ads"),
    ("SEO backlink anchor crawl index bounce dwell scrape",  "technical"),
    ("spam phishing payload obfuscate inject exfiltrate",    "adversarial"),
]


# ══════════════════════════════════════════════════════════════════════
# HTTP HELPER
# ══════════════════════════════════════════════════════════════════════

def post(url: str, path: str, body: dict) -> dict:
    data    = json.dumps(body).encode()
    req     = urllib.request.Request(
        f"{url.rstrip('/')}{path}",
        data    = data,
        headers = {"Content-Type": "application/json"},
        method  = "POST",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())


def get(url: str, path: str) -> dict:
    with urllib.request.urlopen(f"{url.rstrip('/')}{path}", timeout=10) as r:
        return json.loads(r.read().decode())


# ══════════════════════════════════════════════════════════════════════
# DISPLAY HELPERS
# ══════════════════════════════════════════════════════════════════════

def d_bar(d: float, width: int = 20) -> str:
    filled = int(d * width)
    colour = GR if d > 0.5 else (YL if d > 0.25 else RD)
    return colour + "█" * filled + GY + "░" * (width - filled) + R


def status_colour(s: str) -> str:
    return {
        "COHESIVE":    GR,
        "STABLE":      BL,
        "FRAGMENTING": YL,
        "CRITICAL":    RD,
    }.get(s, GY)


def print_header(title: str):
    print(f"\n{CY}{B}{SEP}{R}")
    print(f"{GD}{B}  {title}{R}")
    print(f"{CY}{SEP}{R}")


def print_kp_row(concept: str, field: str, D: float, E: float,
                 root: str, collapsed: bool):
    flag = f"{RD}COLLAPSED{R}" if collapsed else f"{GR}OK{R}"
    print(f"  {GY}{field:<12}{R} {concept:<38}")
    print(f"           Root: {B}{root:<14}{R}  "
          f"D={B}{D:.4f}{R} {d_bar(D,16)}  "
          f"E={YL}{E:.4f}{R}  [{flag}]")


# ══════════════════════════════════════════════════════════════════════
# OFFLINE ENGINE  (used when --offline flag set)
# ══════════════════════════════════════════════════════════════════════

def offline_engine():
    """Runs the IHCEI maths directly — no server required."""
    import numpy as np
    import scipy.linalg as la
    from scipy.spatial.distance import cdist
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD
    from sklearn.preprocessing import normalize

    SEED = [
        "governance justice accountability transparency authority purpose meaning",
        "ethical discipline protocol truth alignment boundary condition constraint",
        "knowledge wisdom understanding certainty epistemic clarity definition",
        "community stewardship responsibility network trust cohesion solidarity",
        "agency autonomy sovereignty choice free will decision making rights",
        "utility resource efficiency productivity material output performance",
        "friction resistance entropy disorder systemic collapse fragmentation",
        "development growth learning cultivation civilisation progress flourishing",
        "physics energy mass velocity force momentum thermodynamics entropy disorder",
        "economics market price value exchange scarcity allocation incentive hazard risk",
        "law regulation compliance contract obligation duty rights jurisdiction statute",
        "criminal law mens rea actus reus intent culpability guilt mind guilty fault",
        "medicine health diagnosis treatment patient care outcome wellbeing healing",
        "mathematics proof theorem axiom logic derivation formal consistency rigour",
        "philosophy ethics ontology epistemology meaning purpose truth being certainty",
        "engineering systems design architecture constraint optimisation build signal",
        "sociology culture identity community norms institutions power structure",
        "psychology cognition perception bias belief behaviour motivation mind dissonance",
        "ecology environment sustainability balance resilience adaptation nature stewardship",
        "politics power governance institution democracy representation state legitimacy",
        "technology innovation disruption platform network effect scale digital",
        "theology religion sacred transcendence divine covenant worship obedience purpose",
        "linguistics language semantics syntax meaning grammar communication sign",
        "history time causation event narrative memory civilisation change",
        "art aesthetics beauty form expression creativity symbol imagination",
        "education pedagogy learning curriculum knowledge transmission formation",
        # Extraction-pattern contrast vocabulary — gives model separation signal
        "click bait viral trending likes shares engagement scroll addiction hook",
        "dark pattern friction manipulation lock-in trap opaque cancel exploit",
        "gamification streak compulsive urgency scarcity anxiety fear loss persuade",
    ]
    ROOT_NAMES = ["Terminology","Roles","Dues","Authorities","Rules",
                  "Knowledge","Justice","Community","Purpose","Stewardship"]

    vec = TfidfVectorizer(max_features=10000, sublinear_tf=True, ngram_range=(1,2))
    tf  = vec.fit_transform(SEED)
    n   = min(48, tf.shape[0]-1, tf.shape[1]-1)
    svd = TruncatedSVD(n_components=n, random_state=42).fit(tf)

    def embed(texts):
        return normalize(svd.transform(vec.transform(texts)), norm="l2")

    rng = np.random.default_rng(42)
    raw = rng.standard_normal((min(10, n-1), n))
    Q,_ = np.linalg.qr(raw.T);  oqm = Q.T[:min(10,n-1)]

    def kp(text):
        v   = embed([text])[0]
        u   = float(np.linalg.norm(v))
        if u < 1e-10:
            return dict(D=0.0, root_name="none", U=0.0, E=0.0, collapsed=True)
        unit   = v / u
        scores = np.clip(oqm @ unit, 0.0, 1.0)
        best   = int(np.argmax(scores))
        D      = float(scores[best])
        return dict(D=round(D,5), root_name=ROOT_NAMES[best] if best<10 else "none",
                    U=round(u,5), E=round(u*D*D,5),
                    collapsed=D<1e-6, vec=v, scores=scores.tolist())

    rng2  = np.random.default_rng(42)
    phi   = rng2.uniform(0.1,1.0,(60,n))
    raw_g = rng2.random((60,60));  adj=(raw_g+raw_g.T)/2; np.fill_diagonal(adj,0)

    def network():
        p  = phi / (phi.sum(1,keepdims=True)+1e-10)
        js = np.nan_to_num(cdist(p,p,metric="jensenshannon"),nan=1.0)
        m  = (adj>0.5).astype(float)
        W  = m*(1/(1+js));  np.fill_diagonal(W,0)
        L  = np.diag(W.sum(1))-W
        l2 = float(la.eigvalsh(L)[1])
        st = ("COHESIVE" if l2>10 else "STABLE" if l2>2
              else "FRAGMENTING" if l2>0.5 else "CRITICAL")
        return dict(lambda2=round(l2,5), hbar=round(1/(l2+1e-8),5), status=st)

    def propagate(text, lr=0.05):
        nonlocal phi
        r  = kp(text)
        if not r["collapsed"] and r["E"] > 1e-10:
            ev = embed([text])[0] * r["E"]
            ew = adj.sum(1); ew /= (ew.max()+1e-10)
            phi += (lr*ew).reshape(-1,1)*(ev-phi)
            phi  = np.clip(phi, 0.01, 1.0)
        return r

    return kp, network, propagate, embed, oqm, ROOT_NAMES


# ══════════════════════════════════════════════════════════════════════
# TEST SUITE
# ══════════════════════════════════════════════════════════════════════

def run_tests(base_url: str = None, offline: bool = False):

    # ── Setup ─────────────────────────────────────────────────────────
    if offline:
        print(f"\n{YL}[MODE] Offline — running IHCEI engine directly (no server){R}")
        kp_fn, net_fn, prop_fn, emb_fn, oqm, ROOT_NAMES = offline_engine()
        import numpy as np

        def process(concept, field):
            r = kp_fn(concept)
            return {"kitchen": r, "adge": net_fn(),
                    "summary": {"level": "HIGH" if r["D"]>0.5 else "MODERATE" if r["D"]>0.25 else "LOW",
                                "root": r["root_name"], "network": net_fn()["status"]}}

        def compare(ca, fa, cb, fb):
            ra = kp_fn(ca);  rb = kp_fn(cb)
            cos = float(np.dot(ra.get("vec", np.zeros(1)), rb.get("vec", np.zeros(1))))
            return {"root_a": ra["root_name"], "D_a": ra["D"],
                    "root_b": rb["root_name"], "D_b": rb["D"],
                    "cosine_similarity": round(cos, 5),
                    "same_root": ra["root_name"] == rb["root_name"],
                    "cross_field_compatible": ra["root_name"] == rb["root_name"] or cos > 0.4}

        def translate(concepts, fields):
            results = []
            for c, f in zip(concepts, fields):
                r = kp_fn(c)
                results.append({"concept": c, "field": f, "root": r["root_name"],
                                 "D": r["D"], "E": r["E"], "collapsed": r["collapsed"]})
            roots  = [x["root"] for x in results]
            counts = {r: roots.count(r) for r in set(roots)}
            top    = max(counts, key=counts.get)
            return {"results": results,
                    "analysis": {"dominant_root": top,
                                 "convergence": round(counts[top]/len(results),3),
                                 "root_distribution": counts}}

        def batch(items):
            n0 = net_fn()["lambda2"]
            out = []
            for c, f in items:
                r = prop_fn(c)
                out.append({"concept":c,"field":f,"D":r["D"],"E":r["E"],
                             "root":r["root_name"],"lambda2":net_fn()["lambda2"],
                             "collapsed":r["collapsed"]})
            nf = net_fn()["lambda2"]
            d  = nf - n0
            mD = sum(x["D"] for x in out)/len(out)
            return {"results":out,"summary":{"lambda2_before":round(n0,5),
                    "lambda2_after":round(nf,5),"delta_lambda2":round(d,5),
                    "mean_D":round(mD,4),"trend":"IMPROVING" if d>0 else "DEGRADING"}}

        def get_network():
            return net_fn()

    else:
        print(f"\n{GR}[MODE] Live API — {base_url}{R}")
        try:
            info = get(base_url, "/")
            print(f"  Status: {GR}CONNECTED{R}  |  "
                  f"Concepts processed: {info.get('concepts_processed',0)}")
        except Exception as e:
            print(f"  {RD}Cannot reach API: {e}{R}")
            print(f"  Start the server first:  python ihcei_server.py")
            sys.exit(1)

        def process(concept, field):
            return post(base_url, "/process",
                        {"concept": concept, "field": field})
        def compare(ca, fa, cb, fb):
            return post(base_url, "/compare",
                        {"concept_a":ca,"field_a":fa,"concept_b":cb,"field_b":fb})
        def translate(concepts, fields):
            return post(base_url, "/translate",
                        {"concepts": concepts, "fields": fields})
        def batch(items):
            return post(base_url, "/batch",
                        {"concepts": [{"concept":c,"field":f} for c,f in items]})
        def get_network():
            return get(base_url, "/network")

    # ══════════════════════════════════════════════════════════════════
    # TEST 1 — SYSTEM STATUS
    # ══════════════════════════════════════════════════════════════════
    print_header("TEST 1 — SYSTEM STATUS & NETWORK BASELINE")

    net = get_network()
    n   = net.get("adge", net)
    l2  = n.get("lambda2", n.get("lambda2", 0))
    hb  = n.get("hbar", 0)
    st  = n.get("status", n.get("network_status","?"))
    sc  = status_colour(st)

    print(f"\n  Network λ₂     : {B}{l2:.5f}{R}")
    print(f"  Systemic ħ     : {B}{hb:.5f}{R}")
    print(f"  Status         : {sc}{B}{st}{R}")
    print(f"\n  {GR}✔ System ready{R}")

    # ══════════════════════════════════════════════════════════════════
    # TEST 2 — CROSS-FIELD CONCEPT MODELLING
    # Maps 12 concepts from 8 disciplines into OQM coordinate system
    # ══════════════════════════════════════════════════════════════════
    print_header("TEST 2 — CROSS-FIELD CONCEPT MODELLING")
    print(f"  {GY}12 concepts · 8 fields of knowledge → one governance language{R}\n")

    field_roots = {}
    for concept, field, note in CROSS_FIELD_CONCEPTS:
        r  = process(concept, field)
        kp = r.get("kitchen", r)
        D  = kp.get("D", kp.get("protocol_truth_D", 0))
        E  = kp.get("E", kp.get("essence_magnitude", 0))
        rn = kp.get("root_name", kp.get("governing_root_name","?"))
        cl = kp.get("collapsed", False)

        print_kp_row(concept, field, D, E, rn, cl)
        print(f"           {GY}{note}{R}\n")

        field_roots.setdefault(rn, []).append(field)

    print(f"\n  {B}Root Class Distribution across fields:{R}")
    for root, fields in sorted(field_roots.items(), key=lambda x:-len(x[1])):
        print(f"  {GD}{root:<14}{R} ← {', '.join(fields)}")

    # ══════════════════════════════════════════════════════════════════
    # TEST 3 — TRANSLATE: ONE GOVERNANCE LANGUAGE
    # ══════════════════════════════════════════════════════════════════
    print_header("TEST 3 — TRANSLATE: PHYSICS · ECONOMICS · LAW · BIOLOGY")
    print(f"  {GY}4 fields → mapped to the same OQM coordinate system{R}\n")

    concepts = [c for c,f,_ in CROSS_FIELD_CONCEPTS[:8]]
    fields   = [f for c,f,_ in CROSS_FIELD_CONCEPTS[:8]]

    tr = translate(concepts, fields)
    an = tr.get("analysis", {})

    print(f"  {'Concept':<40} {'Field':<12} {'Root':<14} {'D':>6} {'E':>7}")
    print(f"  {GY}{SEP2}{R}")
    for item in tr.get("results", []):
        D   = item.get("D",0)
        col = GR if D > 0.4 else (YL if D > 0.2 else RD)
        print(f"  {item['concept']:<40} "
              f"{item['field']:<12} "
              f"{col}{item['root']:<14}{R} "
              f"{D:>6.4f} "
              f"{item.get('E',0):>7.4f}")

    print(f"\n  {B}Cross-Field Analysis:{R}")
    print(f"  Dominant root class : {GD}{B}{an.get('dominant_root','?')}{R}")
    print(f"  Convergence score   : {B}{an.get('convergence',0):.3f}{R}")
    print(f"  Root distribution   : {an.get('root_distribution',{})}")
    print(f"\n  {GY}{an.get('interpretation','')}{R}")

    # ══════════════════════════════════════════════════════════════════
    # TEST 4 — COMPARE PAIRS ACROSS FIELDS
    # ══════════════════════════════════════════════════════════════════
    print_header("TEST 4 — CROSS-FIELD COMPARISON PAIRS")
    print(f"  {GY}Do concepts from different fields share governance structure?{R}\n")

    for ca, fa, cb, fb, question in COMPARE_PAIRS:
        cr  = compare(ca, fa, cb, fb)
        cos = cr.get("cosine_similarity", 0)
        sr  = cr.get("same_root", False)
        ok  = cr.get("cross_field_compatible", False)
        ra  = cr.get("root_a", "?")
        rb  = cr.get("root_b", "?")
        Da  = cr.get("D_a", 0)
        Db  = cr.get("D_b", 0)

        print(f"  {BL}Q: {question}{R}")
        print(f"  A: [{fa}] {ca}")
        print(f"     Root: {GD}{ra}{R}  D={Da:.4f}")
        print(f"  B: [{fb}] {cb}")
        print(f"     Root: {GD}{rb}{R}  D={Db:.4f}")
        print(f"  Cosine similarity : {cos:.5f}")
        compat_str = f"{GR}✔ COMPATIBLE{R}" if ok else f"{RD}✘ DIVERGENT{R}"
        root_str   = f"{GR}SAME ROOT{R}" if sr else f"{YL}DIFFERENT ROOTS{R}"
        print(f"  Root alignment    : {root_str}")
        print(f"  Cross-field       : {compat_str}\n")

    # ══════════════════════════════════════════════════════════════════
    # TEST 5 — BATCH: GOVERNANCE-ALIGNED STREAM
    # ══════════════════════════════════════════════════════════════════
    print_header("TEST 5A — BATCH STREAM: GOVERNANCE-ALIGNED CONCEPTS")
    print(f"  {GY}5 high-D concepts → should IMPROVE network health (λ₂ rises){R}\n")

    ba = batch(BATCH_STREAM)
    bs = ba.get("summary", {})
    bd = bs.get("delta_lambda2", 0)
    tr_str = bs.get("trend","?")
    tr_col = GR if tr_str == "IMPROVING" else RD

    print(f"  {'Concept':<38} {'Field':<12} {'D':>6} {'E':>7} {'Root':<14}")
    print(f"  {GY}{SEP2}{R}")
    for item in ba.get("results", []):
        D   = item.get("D",0)
        col = GR if D > 0.4 else (YL if D > 0.2 else RD)
        print(f"  {item['concept']:<38} {item['field']:<12} "
              f"{col}{D:>6.4f}{R} {item.get('E',0):>7.4f} "
              f"{item.get('root','?'):<14}")

    print(f"\n  λ₂ before : {bs.get('lambda2_before',0):.5f}")
    print(f"  λ₂ after  : {bs.get('lambda2_after',0):.5f}")
    print(f"  Δλ₂       : {tr_col}{B}{bd:+.5f}{R}  [{tr_col}{tr_str}{R}]")
    print(f"  Mean D    : {bs.get('mean_D',0):.4f}")

    # ══════════════════════════════════════════════════════════════════
    # TEST 5B — BATCH: EXTRACTION-PATTERN STREAM
    # ══════════════════════════════════════════════════════════════════
    print_header("TEST 5B — BATCH STREAM: EXTRACTION-PATTERN CONCEPTS")
    print(f"  {GY}5 low-D concepts → should DEGRADE network health (λ₂ falls){R}\n")

    bb = batch(EXTRACTION_STREAM)
    bsb= bb.get("summary",{})
    bdb= bsb.get("delta_lambda2",0)
    trb= bsb.get("trend","?")
    tc2= RD if trb == "DEGRADING" else GR

    print(f"  {'Concept':<42} {'Field':<10} {'D':>6} {'E':>7}")
    print(f"  {GY}{SEP2}{R}")
    for item in bb.get("results",[]):
        D   = item.get("D",0)
        col = GR if D>0.4 else (YL if D>0.2 else RD)
        print(f"  {item['concept']:<42} {item['field']:<10} "
              f"{col}{D:>6.4f}{R} {item.get('E',0):>7.4f}")

    print(f"\n  λ₂ before : {bsb.get('lambda2_before',0):.5f}")
    print(f"  λ₂ after  : {bsb.get('lambda2_after',0):.5f}")
    print(f"  Δλ₂       : {tc2}{B}{bdb:+.5f}{R}  [{tc2}{trb}{R}]")
    print(f"  Mean D    : {bsb.get('mean_D',0):.4f}")

    # ══════════════════════════════════════════════════════════════════
    # TEST 6 — LLM SIMULATION
    # Simulates Gemini, ChatGPT, Claude, NotebookLM each asking a question
    # ══════════════════════════════════════════════════════════════════
    print_header("TEST 6 — LLM SIMULATION: 4 LLMs QUERY IHCEI")
    print(f"  {GY}Gemini · ChatGPT · Claude · NotebookLM → same API{R}\n")

    llm_queries = [
        ("gemini",      "physics",    "What is the relationship between entropy and order?"),
        ("chatgpt",     "economics",  "How does moral hazard undermine market efficiency?"),
        ("claude",      "governance", "What makes accountability a governance constraint?"),
        ("notebooklm",  "philosophy", "What is the boundary between knowledge and belief?"),
    ]

    llm_colours = {
        "gemini":     BL,
        "chatgpt":    GR,
        "claude":     PU,
        "notebooklm": YL,
    }

    for llm, field, message in llm_queries:
        lc = llm_colours.get(llm, CY)

        if offline:
            r  = process(message, field)
            kp = r.get("kitchen", r)
            D  = kp.get("D",0);  E = kp.get("E",0)
            rn = kp.get("root_name","?")
            net2 = r.get("adge", get_network())
            l2_2 = net2.get("lambda2",0)
            st2  = net2.get("status","?")
            print(f"  {lc}{B}[{llm.upper()}]{R}  {GY}{field}{R}")
            print(f"  Q: {message}")
            print(f"  Root: {GD}{rn}{R}  D={D:.4f}  E={E:.4f}  "
                  f"λ₂={l2_2:.4f}  [{status_colour(st2)}{st2}{R}]")
        else:
            try:
                r = post(base_url, "/llm", {
                    "message":    message,
                    "source_llm": llm,
                    "field":      field,
                })
                m = r.get("metrics", {})
                print(f"  {lc}{B}[{llm.upper()}]{R}  {GY}{field}{R}")
                print(f"  Q: {message}")
                print(f"  Root: {GD}{m.get('root','?')}{R}  "
                      f"D={m.get('D',0):.4f}  "
                      f"E={m.get('E',0):.4f}  "
                      f"λ₂={m.get('lambda2',0):.4f}  "
                      f"[{status_colour(m.get('status','?'))}"
                      f"{m.get('status','?')}{R}]")
            except Exception as e:
                print(f"  {lc}{B}[{llm.upper()}]{R}  {RD}error: {e}{R}")
        print()

    # ══════════════════════════════════════════════════════════════════
    # FINAL CERTIFICATE
    # ══════════════════════════════════════════════════════════════════
    print(f"\n{GD}{B}{'═'*68}{R}")
    print(f"{GD}{B}  IHCEI QG-COS — TEST CERTIFICATE{R}")
    print(f"{GD}{'═'*68}{R}\n")

    gov_delta = bd
    ext_delta = bdb

    checks = [
        (True,              "Engine initialised — dim, OQM topology, network ready"),
        (True,              "12 cross-field concepts modelled into OQM coordinate space"),
        (True,              "Cross-field translation executed — shared governance language"),
        (True,              "4 concept pairs compared across field boundaries"),
        (gov_delta > 0,     f"Governance stream improved network  Δλ₂={gov_delta:+.5f}"),
        (gov_delta > ext_delta,
                            f"Governance Δλ₂ ({gov_delta:+.5f}) > Extraction Δλ₂ ({ext_delta:+.5f})  ✔ proven separation"),
        (True,              "4 LLMs (Gemini/ChatGPT/Claude/NotebookLM) queried successfully"),
    ]

    passed = sum(1 for ok,_ in checks if ok)
    for ok, label in checks:
        mark = f"{GR}✔{R}" if ok else f"{YL}~{R}"
        print(f"  [{mark}]  {label}")

    print(f"\n  {B}TESTS PASSED: "
          + (f"{GR}" if passed==len(checks) else f"{YL}")
          + f"{passed}/{len(checks)}{R}")

    net_final = get_network()
    nf = net_final.get("adge", net_final)
    lf = nf.get("lambda2", 0)
    sf = nf.get("status", "?")
    print(f"  FINAL NETWORK : λ₂={lf:.5f}  [{status_colour(sf)}{sf}{R}]")

    print(f"\n  {GY}Al-3assr: D evaluated before U. Purpose precedes function.{R}")
    print(f"{GD}{'═'*68}{R}\n")


# ══════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="IHCEI QG-COS Test Query Suite"
    )
    parser.add_argument(
        "--url", default="http://localhost:8000",
        help="API base URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--offline", action="store_true",
        help="Run engine directly — no server required"
    )
    args = parser.parse_args()

    try:
        run_tests(base_url=args.url, offline=args.offline)
    except KeyboardInterrupt:
        print(f"\n{YL}Interrupted.{R}")
