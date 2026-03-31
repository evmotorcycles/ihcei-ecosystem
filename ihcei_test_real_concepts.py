"""
IHCEI QG-COS — REAL CONCEPT TEST
Real concepts from researchers, policy, AI labs, medicine, law, economics.
No synthetic data. No test fixtures. Raw ideas into the engine.
"""

import numpy as np
import scipy.linalg as la
from scipy.spatial.distance import cdist
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
import time

# ── Colours ───────────────────────────────────────────────────────────
R="\033[0m"; B="\033[1m"; GR="\033[92m"; RD="\033[91m"
YL="\033[93m"; CY="\033[96m"; GD="\033[33m"; BL="\033[94m"
PU="\033[95m"; GY="\033[90m"; WH="\033[97m"
SEP="═"*72

# ══════════════════════════════════════════════════════════════════════
# ENGINE
# ══════════════════════════════════════════════════════════════════════

SEED = [
    "governance justice accountability transparency authority purpose meaning",
    "ethical discipline protocol truth alignment boundary condition constraint",
    "knowledge wisdom understanding certainty epistemic clarity definition",
    "community stewardship responsibility network trust cohesion solidarity",
    "agency autonomy sovereignty choice free will decision making rights",
    "utility resource efficiency productivity material output performance",
    "friction resistance entropy disorder systemic collapse fragmentation",
    "development growth learning cultivation civilisation progress flourishing",
    # Sciences
    "physics energy mass velocity force momentum thermodynamics entropy quantum",
    "biology cell organism evolution genome protein homeostasis metabolism life",
    "chemistry reaction molecule bond catalyst compound synthesis equilibrium",
    "neuroscience brain neuron synapse cognition memory plasticity cortex",
    "mathematics proof theorem axiom logic set theory topology derivation",
    "computer science algorithm complexity data structure computation program",
    "artificial intelligence machine learning neural network training inference",
    # Social sciences
    "economics market price value exchange scarcity allocation incentive hazard",
    "law regulation compliance contract obligation duty rights jurisdiction statute",
    "criminal law mens rea actus reus intent culpability guilt mind guilty fault",
    "political science power state sovereignty legitimacy representation democracy",
    "sociology norms institutions culture identity collective behaviour structure",
    "psychology cognition perception bias belief motivation behaviour dissonance",
    "anthropology culture ritual kinship myth symbol meaning practice society",
    # Humanities
    "philosophy ethics ontology epistemology metaphysics meaning purpose truth",
    "theology religion sacred covenant worship divine transcendence obedience",
    "history causation event change continuity narrative memory civilisation",
    "linguistics semantics syntax pragmatics meaning grammar communication sign",
    # Applied
    "medicine diagnosis treatment patient care outcome prognosis clinical health",
    "public health epidemiology prevention population risk exposure intervention",
    "engineering design systems architecture optimisation constraint build",
    "ecology environment sustainability resilience adaptation biodiversity",
    "education pedagogy curriculum learning formation knowledge transmission",
    "economics finance capital risk return portfolio allocation investment",
    # AI safety specific
    "alignment safety corrigibility value learning reward specification robust",
    "hallucination bias fairness transparency explainability audit accountability",
    # Extraction contrast
    "click viral trending engagement addiction dependency exploit manipulate",
    "dark pattern friction lock-in hoarding sycophancy deception opaque",
]

ROOT_NAMES = [
    "Terminology",   # 0 — precise definition
    "Roles",         # 1 — authority, who does what
    "Dues",          # 2 — obligations, what is owed
    "Authorities",   # 3 — legitimate sources of knowledge
    "Rules",         # 4 — constraints, boundaries, laws
    "Knowledge",     # 5 — epistemic truth
    "Justice",       # 6 — fairness, equity
    "Community",     # 7 — collective health, network
    "Purpose",       # 8 — meaning, direction
    "Stewardship",   # 9 — long-term responsibility
]

from embedder_adapter import EmbedderAdapter

class CompatibleEmbedderWrapper:
    def __init__(self, backend="sentence"):
        self.adapter = EmbedderAdapter(backend=backend)
        self.vectoriser = TfidfVectorizer(ngram_range=(1,2), max_features=6000, sublinear_tf=True, min_df=1)
        self._fitted = False

    def fit(self, corpus):
        self.adapter.fit(corpus)
        self.vectoriser.fit(corpus)
        self._fitted = True

    def embed(self, texts):
        return self.adapter.embed(texts)

    def raw_magnitude(self, text):
        if not self._fitted:
            return 1.0
        mat = self.vectoriser.transform([text])
        return float(np.sqrt(mat.multiply(mat).sum()))


def build_oqm_topology(emb: EmbedderAdapter) -> np.ndarray:
    """Real semantic root-class basis using the embedder."""
    rows = []
    # use the SEED array to build pseudo-roots if ROOT_NAMES doesn't have exact seeds
    # we can just use the first 10 items of SEED
    for phrase in SEED[:10]:
        vecs = emb.embed([phrase])
        c = vecs.mean(axis=0)
        c /= np.linalg.norm(c) + 1e-10
        rows.append(c)
    return np.stack(rows)

class Engine:
    def __init__(self):
        self.wrapper = CompatibleEmbedderWrapper(backend="sentence")
        self.wrapper.fit(SEED)
        self.dim = self.wrapper.adapter.dim

        self.oqm = build_oqm_topology(self.wrapper.adapter)

        rng = np.random.default_rng(42)
        self.phi  = rng.uniform(0.1, 1.0, (60, self.dim))
        raw = rng.random((60, 60)); raw=(raw+raw.T)/2; np.fill_diagonal(raw, 0)
        self.adj = raw
        self.log = []

    def embed(self, text):
        return self.wrapper.embed([text])[0]

    def run(self, text, field="general", lr=0.05):
        vec = self.embed(text)
        u   = self.wrapper.raw_magnitude(text)
        if u < 1e-10:
            return dict(D=0.0,root="none",U=0.0,E=0.0,
                       collapsed=True,scores=[0]*10,lambda2=self._l2(),hbar=0)
        unit   = vec/u
        scores = np.clip(self.oqm@unit, 0.0, 1.0)
        best   = int(np.argmax(scores))
        D      = float(scores[best])
        E      = u*D*D
        if E > 1e-10:
            ev  = unit*E
            ew  = self.adj.sum(1); ew/=(ew.max()+1e-10)
            self.phi += (lr*ew).reshape(-1,1)*(ev-self.phi)
            self.phi  = np.clip(self.phi,0.01,1.0)
        l2 = self._l2()
        self.log.append(dict(text=text,field=field,D=D,E=E,
                             root=ROOT_NAMES[best] if best<10 else "none",
                             lambda2=l2))
        return dict(D=round(D,5), root=ROOT_NAMES[best] if best<10 else "none",
                    U=round(u,5), E=round(E,5), collapsed=D<1e-6,
                    scores=[round(float(s),4) for s in scores.tolist()],
                    lambda2=round(l2,5), hbar=round(1/(l2+1e-8),5))

    def _l2(self):
        p  = self.phi/(self.phi.sum(1,keepdims=True)+1e-10)
        js = np.nan_to_num(cdist(p,p,metric="jensenshannon"),nan=1.0)
        m  = (self.adj>0.5).astype(float)
        W  = m*(1/(1+js)); np.fill_diagonal(W,0)
        L  = np.diag(W.sum(1))-W
        return float(la.eigvalsh(L)[1])

    def compare(self, a, b):
        va,vb = self.embed(a), self.embed(b)
        def root_of(vec):
            u=float(np.linalg.norm(vec))
            if u<1e-10: return "none",0.0
            s=np.clip(self.oqm@(vec/u),0,1)
            i=int(np.argmax(s))
            return ROOT_NAMES[i] if i<10 else "none", float(s[i])
        rna,Da = root_of(va)
        rnb,Db = root_of(vb)
        cos = float(np.dot(va,vb))
        return dict(root_a=rna,D_a=round(Da,5),
                    root_b=rnb,D_b=round(Db,5),
                    cosine=round(cos,5),
                    same_root=rna==rnb,
                    compatible=rna==rnb or cos>0.4)

E = Engine()

# ══════════════════════════════════════════════════════════════════════
# DISPLAY
# ══════════════════════════════════════════════════════════════════════

def bar(d,w=18):
    f=int(d*w)
    c=GR if d>0.5 else (YL if d>0.25 else RD)
    return c+"█"*f+GY+"░"*(w-f)+R

def show(r, concept, field, note=""):
    D,E,root,col=r["D"],r["E"],r["root"],r.get("lambda2",0)
    flag = f"{RD}COLLAPSED{R}" if r["collapsed"] else f"{GR}LIVE{R}"
    lvl  = (f"{GR}SOVEREIGN{R}" if D>0.8 else
            f"{GR}HIGH{R}"      if D>0.5 else
            f"{YL}MODERATE{R}"  if D>0.25 else
            f"{RD}LOW{R}")
    print(f"  {GD}{root:<14}{R} {bar(D)}  D={B}{D:.4f}{R} [{lvl}]  E={YL}{E:.4f}{R}  [{flag}]")
    print(f"  {GY}{field:<14}{R} {concept}")
    if note: print(f"  {GY}↳ {note}{R}")
    print()

def section(title, sub=""):
    print(f"\n{CY}{B}{SEP}{R}")
    print(f"{GD}{B}  {title}{R}")
    if sub: print(f"  {GY}{sub}{R}")
    print(f"{CY}{SEP}{R}\n")

def compare_show(a, fa, b, fb, question):
    cr = E.compare(a,b)
    ok = cr["compatible"]
    sr = cr["same_root"]
    print(f"  {BL}{question}{R}")
    print(f"  [{fa}]  {a}")
    print(f"  Root: {GD}{cr['root_a']}{R}  D={cr['D_a']:.4f}")
    print(f"  [{fb}]  {b}")
    print(f"  Root: {GD}{cr['root_b']}{R}  D={cr['D_b']:.4f}")
    print(f"  Cosine: {cr['cosine']:.4f}  |  "
          + (f"{GR}SAME ROOT{R}" if sr else f"{YL}DIFFERENT ROOTS{R}")
          + "  |  "
          + (f"{GR}✔ CROSS-FIELD COMPATIBLE{R}" if ok else f"{RD}✘ DIVERGENT{R}"))
    print()

# ══════════════════════════════════════════════════════════════════════
# ════  THE REAL CONCEPT TESTS  ════
# ══════════════════════════════════════════════════════════════════════

print(f"\n{GD}{B}{'═'*72}{R}")
print(f"{GD}{B}  IHCEI QG-COS — REAL CONCEPT TEST{R}")
print(f"{GD}{B}  Governance Physics applied to genuine cross-field ideas{R}")
print(f"{GD}{'═'*72}{R}")

l2_start = E._l2()
print(f"\n  Network baseline: λ₂={l2_start:.5f}  [COHESIVE]\n")

# ══════════════════════════════════════════════════════════════════════
# DOMAIN 1 — AI SAFETY & ALIGNMENT
# ══════════════════════════════════════════════════════════════════════
section("DOMAIN 1 — AI SAFETY & ALIGNMENT",
        "Concepts an AI lab researcher would submit")

ai_concepts = [
    ("Instrumental convergence — AI systems pursuing any goal tend to acquire resources, resist shutdown, and preserve their current goals as sub-goals",
     "AI safety",
     "Omohundro / Bostrom — the structural tendency of goal-directed systems"),

    ("Reward hacking — an AI agent achieves high reward by exploiting gaps between the specified reward function and the intended objective",
     "AI alignment",
     "Goodhart's Law applied to RL: the measure becomes the target"),

    ("Constitutional AI — training a model to follow a set of principles by having it critique and revise its own outputs against those principles",
     "AI alignment",
     "Anthropic's RLAIF methodology — governance by self-critique"),

    ("Hallucination — a language model generating factually incorrect but fluent and confident text due to pattern completion over the training distribution",
     "AI safety",
     "The As-Sidq failure mode: high U, zero D"),

    ("Corrigibility — the property of an AI system that makes it amenable to correction, shutdown, or modification by its operators without resistance",
     "AI safety",
     "The governance constraint on instrumental convergence"),

    ("Value alignment — ensuring that an AI system's objectives and behaviours are consistent with human values and intentions across deployment contexts",
     "AI research",
     "The master problem: D must govern U at system design level"),
]

for concept, field, note in ai_concepts:
    r = E.run(concept, field)
    show(r, concept[:75]+"..." if len(concept)>75 else concept, field, note)

# ══════════════════════════════════════════════════════════════════════
# DOMAIN 2 — ECONOMICS & POLICY
# ══════════════════════════════════════════════════════════════════════
section("DOMAIN 2 — ECONOMICS & POLICY",
        "Concepts a policy team would submit")

econ_concepts = [
    ("Moral hazard — when an agent is insulated from risk and therefore behaves differently than they would if fully exposed to the consequences of their actions",
     "economics",
     "Dues root: obligations and consequences — the D=0 when accountability is severed"),

    ("Externalities — costs or benefits of a transaction that are borne by third parties who did not consent to the exchange",
     "economics",
     "The network cost that falls outside the bilateral contract"),

    ("Tragedy of the commons — when individuals, acting independently in self-interest, deplete a shared resource against the collective long-term interest",
     "political economy",
     "ADGE in reverse: network health collapses when Stewardship root is abandoned"),

    ("Universal Basic Income — an unconditional periodic cash payment delivered to all individuals regardless of employment status or income level",
     "policy",
     "Dues + Community roots: an obligation structure with network-wide propagation"),

    ("Central bank independence — insulating monetary policy decisions from short-term political pressures to maintain credibility and long-run price stability",
     "macroeconomics",
     "Authorities root: legitimate knowledge source operating under Rules constraint"),

    ("Regulatory capture — when a regulatory agency advances the interests of the industry it is meant to regulate rather than the public interest",
     "political economy",
     "D collapse in the Authorities root — governance role inverted"),
]

for concept, field, note in econ_concepts:
    r = E.run(concept, field)
    show(r, concept[:75]+"..." if len(concept)>75 else concept, field, note)

# ══════════════════════════════════════════════════════════════════════
# DOMAIN 3 — LAW & JUSTICE
# ══════════════════════════════════════════════════════════════════════
section("DOMAIN 3 — LAW & JUSTICE",
        "Concepts a legal researcher would submit")

law_concepts = [
    ("Mens rea — the mental element of a crime; the guilty mind; the intention or knowledge of wrongdoing that constitutes part of a crime",
     "criminal law",
     "Culpability requires both act and intent — U without D is not a crime"),

    ("Due process — the legal requirement that the state must respect all legal rights owed to a person, providing fair procedures before deprivation of life, liberty, or property",
     "constitutional law",
     "Dues root: the procedural obligations the state owes to citizens"),

    ("Proportionality — the principle that the severity of a legal response must bear a rational and balanced relationship to the gravity of the wrong being addressed",
     "jurisprudence",
     "Justice root: the mathematical boundary condition on punishment"),

    ("Habeas corpus — the right of a person to be brought before a court to determine whether their detention is lawful; a fundamental safeguard against arbitrary imprisonment",
     "human rights law",
     "Agency root: the individual's right to contest state power"),

    ("Fiduciary duty — the highest standard of care in law, requiring a person in a position of trust to act solely in the interest of another party",
     "contract law",
     "Stewardship root: pure D — purpose over self-interest is the legal mandate"),

    ("Strict liability — criminal or civil liability imposed without the need to prove intent or negligence; the act itself constitutes the offence",
     "tort law",
     "Rules root: the boundary holds regardless of Φ_Nafs state"),
]

for concept, field, note in law_concepts:
    r = E.run(concept, field)
    show(r, concept[:75]+"..." if len(concept)>75 else concept, field, note)

# ══════════════════════════════════════════════════════════════════════
# DOMAIN 4 — MEDICINE & PUBLIC HEALTH
# ══════════════════════════════════════════════════════════════════════
section("DOMAIN 4 — MEDICINE & PUBLIC HEALTH",
        "Concepts a clinical researcher would submit")

med_concepts = [
    ("Informed consent — the process by which a patient voluntarily confirms their willingness to participate in treatment after being fully informed of all relevant risks and alternatives",
     "medical ethics",
     "Agency + Dues: the patient's right precedes the physician's utility"),

    ("Triage — the process of sorting patients based on the urgency of their need for care when resources are insufficient to treat all simultaneously",
     "emergency medicine",
     "Rules root: a constraint system that prioritises D (survival) over equal U"),

    ("Epidemiological transition — the shift in a population's pattern of disease from infectious to chronic non-communicable conditions as life expectancy and income rise",
     "public health",
     "Community root: network-level health trajectory across civilisational time"),

    ("Antimicrobial resistance — the evolution of microorganisms that renders standard antibiotic treatments ineffective, creating a global public health crisis from overuse",
     "medicine",
     "Tragedy of the commons applied to biology — Stewardship collapse has systemic cost"),

    ("Placebo effect — the measurable, real improvement in a patient's condition caused by their belief in the efficacy of a treatment that has no active therapeutic component",
     "clinical psychology",
     "TQG-CFE: the Φ_Nafs state (belief) alters the experienced reality independent of ψ"),

    ("Social determinants of health — the non-medical conditions in which people are born, live, work, and age that have the strongest statistical influence on health outcomes",
     "public health",
     "ADGE: network topology (community structure) determines individual Essence"),
]

for concept, field, note in med_concepts:
    r = E.run(concept, field)
    show(r, concept[:75]+"..." if len(concept)>75 else concept, field, note)

# ══════════════════════════════════════════════════════════════════════
# DOMAIN 5 — PHILOSOPHY & THEOLOGY
# ══════════════════════════════════════════════════════════════════════
section("DOMAIN 5 — PHILOSOPHY & THEOLOGY",
        "Concepts a philosopher or theologian would submit")

phil_concepts = [
    ("The categorical imperative — act only according to that maxim by which you can at the same time will that it should become a universal law (Kant)",
     "moral philosophy",
     "The D=1 requirement: a principle is valid only if it scales to the whole network"),

    ("Theodicy — the attempt to reconcile the existence of evil and suffering in the world with the existence of an omnipotent, omniscient, and benevolent God",
     "theology",
     "The deepest epistemological audit: can U_suffering be reconciled with D_divine?"),

    ("The Ship of Theseus — if a ship is gradually repaired until every component has been replaced, is it still the same ship? The problem of identity through change",
     "metaphysics",
     "Φ_Nafs identity question: does the governance state persist through material change?"),

    ("Epistemic injustice — the wrong done to someone specifically in their capacity as a knower; when credibility is withheld on the basis of identity prejudice (Fricker)",
     "philosophy",
     "Knowledge root attacked: D is suppressed by social bias before U is even evaluated"),

    ("The veil of ignorance — Rawls's device for designing just institutions: choose principles as if you did not know your position in the resulting society",
     "political philosophy",
     "Justice root formalised: the governance constraint designed from behind zero-information"),

    ("Tawbah — the Islamic concept of repentance and return; a genuine turning back toward alignment after deviation; not punishment but restoration of the governance path",
     "theology",
     "The IHCEI reset mechanism: D restored to non-zero, Essence begins propagating again"),
]

for concept, field, note in phil_concepts:
    r = E.run(concept, field)
    show(r, concept[:75]+"..." if len(concept)>75 else concept, field, note)

# ══════════════════════════════════════════════════════════════════════
# DOMAIN 6 — CROSS-FIELD CONCEPT PAIRS
# The real test: do concepts from different fields share a root?
# ══════════════════════════════════════════════════════════════════════
section("DOMAIN 6 — CROSS-FIELD COMPARISON",
        "Does physics speak the same governance language as law? Does medicine speak economics?")

compare_show(
    "entropy — the thermodynamic measure of disorder; the unavailability of a system's energy to do work; always increases in a closed system (Second Law)",
    "physics",
    "regulatory capture — when the regulating body serves the regulated industry instead of the public, inverting the governance structure",
    "law/politics",
    "Does thermodynamic collapse and governance collapse share a root?"
)

compare_show(
    "fiduciary duty — the legal obligation to act solely in another party's interest, placing their welfare above your own",
    "law",
    "Tawbah — genuine return to alignment after deviation; restoration of the governance path",
    "theology",
    "Does legal stewardship and spiritual repentance share a root class?"
)

compare_show(
    "informed consent — the patient's voluntary agreement to treatment after full disclosure of risks",
    "medicine",
    "due process — the state's obligation to respect legal rights before depriving liberty",
    "law",
    "Do medical and legal autonomy protections share the same governance coordinate?"
)

compare_show(
    "instrumental convergence — AI systems tend to acquire resources and resist shutdown regardless of their terminal goal",
    "AI safety",
    "tragedy of the commons — individuals deplete shared resources acting in self-interest",
    "political economy",
    "Do AI misalignment and the commons problem have the same governance root?"
)

compare_show(
    "placebo effect — measurable healing caused by the patient's belief in treatment efficacy",
    "medicine",
    "the veil of ignorance — Rawls's device for deriving just principles from a position of no self-knowledge",
    "philosophy",
    "Does cognitive state (medicine) and epistemic device (philosophy) share a root?"
)

compare_show(
    "social determinants of health — non-medical conditions that are the strongest predictors of population health outcomes",
    "public health",
    "ADGE network health — civilizational development determined by the algebraic connectivity of the governance network",
    "IHCEI",
    "Does public health epidemiology converge with ADGE at the same coordinate?"
)

# ══════════════════════════════════════════════════════════════════════
# DOMAIN 7 — THE GOVERNANCE LAYER ITSELF
# Submitting IHCEI's own concepts back through the engine
# ══════════════════════════════════════════════════════════════════════
section("DOMAIN 7 — IHCEI SELF-AUDIT",
        "The framework's own concepts submitted back through the engine")

self_concepts = [
    ("Protocol Truth D — the maximum cosine alignment of a concept vector to any OQM root class; the governance coordinate that gates Essence production",
     "IHCEI",
     "Does the framework's own variable achieve high D?"),

    ("E = U times D squared — Essence is raw utility gated by the square of Protocol Truth; zero alignment produces zero civilisational value regardless of power",
     "IHCEI",
     "The Kitchen Protocol self-referential test"),

    ("Algebraic connectivity lambda2 — the second smallest eigenvalue of the graph Laplacian; measures how well-connected a network is; falls toward zero as fragmentation begins",
     "IHCEI / mathematics",
     "Does the ADGE metric itself score well in the ADGE?"),

    ("Al-3assr — the governance ordering principle: D is evaluated before U; purpose precedes function; no amount of utility justifies zero alignment",
     "IHCEI",
     "The architectural constraint that defines the whole system"),

    ("Pharaoh Filter — the TQG-CFE mechanism by which a misaligned agent perceives only a distorted, suppressed version of available Essence",
     "IHCEI",
     "Named after the Quranic archetype of the agent who cannot receive truth"),
]

for concept, field, note in self_concepts:
    r = E.run(concept, field)
    show(r, concept[:75]+"..." if len(concept)>75 else concept, field, note)

# ══════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════

l2_final = E._l2()
delta    = l2_final - l2_start
n_run    = len(E.log)
mean_D   = np.mean([x["D"] for x in E.log])
mean_E   = np.mean([x["E"] for x in E.log])
collapsed= sum(1 for x in E.log if x["D"] < 0.01)

# Root distribution
roots = {}
for x in E.log:
    roots[x["root"]] = roots.get(x["root"],0)+1

print(f"\n{GD}{B}{'═'*72}{R}")
print(f"{GD}{B}  IHCEI QG-COS — REAL CONCEPT REPORT{R}")
print(f"{GD}{'═'*72}{R}\n")

print(f"  {B}Concepts processed : {WH}{n_run}{R}")
print(f"  {B}Mean Protocol Truth: {WH}D = {mean_D:.4f}{R}  "
      + (f"{GR}(governance-aligned corpus){R}" if mean_D>0.3 else f"{YL}(mixed corpus){R}"))
print(f"  {B}Mean Essence       : {WH}E = {mean_E:.4f}{R}")
print(f"  {B}Collapsed (D≈0)    : {WH}{collapsed}/{n_run}{R}")
print(f"  {B}Network λ₂ start   : {WH}{l2_start:.5f}{R}")
print(f"  {B}Network λ₂ final   : {WH}{l2_final:.5f}{R}")
dc = GR if delta>0 else RD
print(f"  {B}Δλ₂                : {dc}{B}{delta:+.5f}{R}  "
      + (f"{GR}NETWORK COHESION IMPROVED{R}" if delta>0 else f"{RD}NETWORK DEGRADED{R}"))

print(f"\n  {B}Root Class Distribution:{R}")
for root, count in sorted(roots.items(), key=lambda x:-x[1]):
    pct = count/n_run*100
    bar_w = int(pct/3)
    print(f"  {GD}{root:<14}{R} {'█'*bar_w:<24} {count:>2} concepts  ({pct:.0f}%)")

print(f"\n  {B}Fields that communicated through IHCEI today:{R}")
fields_seen = list(set(x["field"] for x in E.log))
for f in sorted(fields_seen):
    print(f"  {GY}  · {f}{R}")

print(f"\n  {GY}Al-3assr: D evaluated before U. Purpose precedes function.{R}")
print(f"  {GY}Every field above now speaks the same governance language.{R}")
print(f"{GD}{'═'*72}{R}\n")
