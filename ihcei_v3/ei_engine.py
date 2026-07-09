"""
ei_engine.py
============
Epistemological Interface (EI) — QG-COS Layer 1.5
GT v18.0 / QGCOS_SKILL_v6

WHAT EI IS
----------
EI is the network-level epistemological integrity auditor that sits
between IHCEI (per-transaction D-floor) and CI (per-user developmental
calibration).

Where IHCEI asks: "Does THIS claim document its methodology?"
EI asks:          "Does THIS CLAIM'S METHODOLOGY NETWORK connect to
                   independently verifiable ground truth — or does it
                   ultimately refer back to itself?"

The distinction is architectural. IHCEI audits individual transactions.
EI audits the topology of knowledge networks that individual transactions
are embedded in.

WHAT EI IS ADDRESSING
---------------------
The Self-Reference Trap: A network of perfectly high-D individual claims
can still be structurally corrupt if they form a closed loop with no
external falsification point. Every claim is documented (Gate 3 clear).
Every claim cites other documented claims. But follow the citation chain
far enough and it returns to itself — a self-referential epistemological
structure with no ground truth anchor.

Examples in practice:
  - Academic echo chambers: papers citing papers citing papers, all
    within one school of thought, none connecting to empirical data
  - Regulatory filings: each section cross-references other sections,
    methodology appears documented, but the underlying accounting
    framework has no external audit anchor
  - Institutional consensus: 'Peer-reviewed research confirms X'
    where X was peer-reviewed by the same institutional network
    that generated X in the first place (Gate 2 + Gate 5 combined)

These pass IHCEI Gate 3 (methodology is documented). They fail EI
because the documentation network is closed.

THREE EI METRICS
----------------
1. SEH Depth (Sovereign Epistemological Hierarchy depth):
   How many independent verification steps lie between a claim and the
   primary empirical anchor it ultimately rests on?
   Depth 1 = directly empirically grounded (experimental result)
   Depth 5+ = five citation hops from any empirical anchor
   Depth ∞ = no empirical anchor found (pure self-reference)

2. Circular Reference Detection (CRD score):
   Does following the methodology chain eventually return to a claim
   already in the chain? CRD = 0.0 (no cycles) to 1.0 (pure cycle).

3. Zipper Effect Score (ZES):
   Does the methodology chain bridge across independent knowledge
   domains (high ZES) or stay entirely within one domain's vocabulary
   (low ZES)? ZES = 0.0 (single-domain silo) to 1.0 (max cross-domain).

RELATIONSHIP TO IHCEI AND CI
-----------------------------
IHCEI: blocks outputs with D < D_crit (transaction floor)
EI: scores the knowledge network the output is embedded in
CI: calibrates output complexity for the specific Nafs

A claim can pass IHCEI (methodology documented) and have EI_score = 0.0
(methodology network is entirely self-referential). EI provides the
additional layer that catches institutionalised groupthink that IHCEI
cannot detect at the individual transaction level.

EPISTEMIC BOUNDARIES
--------------------
Layer 1 (falsifiable): SEH depth from citation chain analysis,
                        cycle detection via graph traversal,
                        cross-domain vocabulary mapping.
Layer 2 (developing):  EI score prediction of retraction probability,
                        echo chamber detection in real knowledge graphs.
Layer 3 (not claimed): Whether any claim is ultimately 'true' in the
                        deepest sense. EI measures structural properties
                        of knowledge networks, not ontological truth.
"""

from __future__ import annotations
import hashlib
import re
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN VOCABULARY — for Zipper Effect Score computation
# ─────────────────────────────────────────────────────────────────────────────

DOMAIN_VOCABULARIES: Dict[str, List[str]] = {
    "physics": [
        "energy", "entropy", "thermodynamics", "quantum", "field", "force",
        "momentum", "wave", "particle", "relativity", "potential", "photon"
    ],
    "mathematics": [
        "theorem", "proof", "axiom", "equation", "derivative", "integral",
        "topology", "algebra", "matrix", "eigenvalue", "manifold", "convergence"
    ],
    "biology": [
        "protein", "gene", "cell", "organism", "evolution", "enzyme",
        "chromosome", "metabolism", "phenotype", "genotype", "dna", "rna"
    ],
    "economics": [
        "utility", "market", "equilibrium", "supply", "demand", "capital",
        "interest", "leverage", "liquidity", "yield", "arbitrage", "asset"
    ],
    "network_science": [
        "node", "edge", "degree", "centrality", "percolation", "cascade",
        "hub", "cluster", "betweenness", "eigenvector", "connected", "path"
    ],
    "governance": [
        "methodology", "transparency", "accountability", "fidelity", "audit",
        "protocol", "procedure", "verification", "falsifiability", "agency"
    ],
    "psychology": [
        "cognition", "behaviour", "motivation", "development", "learning",
        "attention", "memory", "perception", "emotion", "consciousness"
    ],
    "information_theory": [
        "entropy", "channel", "bandwidth", "signal", "noise", "compression",
        "encoding", "decoding", "redundancy", "mutual_information", "capacity"
    ],
}

# Empirical anchor signals — phrases indicating ground truth connection
EMPIRICAL_ANCHOR_PATTERNS = [
    r"\bexperiment(al)?\b",
    r"\bobserved\b",
    r"\bmeasured\b",
    r"\bdataset\b",
    r"\btrail\b.*\bdata\b",
    r"\bp[-\s]?value\b",
    r"\bstatistical(ly)?\b",
    r"\breplicate[ds]?\b",
    r"\bstudy\b.*\bfound\b",
    r"\bwet[-\s]?lab\b",
    r"\bin vivo\b",
    r"\bfalsifiable\b",
    r"\bAUC\b",
    r"\bdelta AIC\b",
]

# Self-reference warning patterns
SELF_REFERENCE_PATTERNS = [
    r"\bsee above\b",
    r"\bas stated\b",
    r"\bas noted\b",
    r"\bconsistent with our framework\b",
    r"\bour theory predicts\b",
    r"\bby definition\b",
    r"\bper our model\b",
    r"\bthe framework shows\b",
    r"\bas we have established\b",
]

# Authority-without-ground-truth patterns (Gate 5 at network level)
AUTHORITY_ONLY_PATTERNS = [
    r"\bscholars agree\b",
    r"\bexperts confirm\b",
    r"\bconsensus\b",
    r"\bwidely accepted\b",
    r"\bestablished that\b",
    r"\bwell known\b",
    r"\bcommonly understood\b",
    r"\bindustry standard\b",
]


# ─────────────────────────────────────────────────────────────────────────────
# DATA CLASSES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ClaimNode:
    """A single claim in the knowledge network."""
    claim_id: str
    text: str
    cited_claims: List[str] = field(default_factory=list)   # IDs this claim cites
    empirical_anchors: int = 0                               # direct data references
    domain_signals: Dict[str, int] = field(default_factory=dict)
    self_reference_flags: int = 0
    authority_flags: int = 0


@dataclass
class SEHAnalysis:
    """Sovereign Epistemological Hierarchy depth analysis."""
    root_claim_id: str
    max_depth: int              # hops to deepest empirical anchor
    min_depth: int              # hops to nearest empirical anchor
    anchored_nodes: List[str]   # claims with direct empirical connections
    unanchored_nodes: List[str] # claims with no path to empirical anchor
    seh_score: float            # 0.0 (no anchor) to 1.0 (all anchored at depth 1)


@dataclass
class CRDAnalysis:
    """Circular Reference Detection analysis."""
    cycles_detected: List[List[str]]  # each cycle is a list of claim IDs
    cycle_count: int
    longest_cycle: int
    crd_score: float            # 0.0 (no cycles) to 1.0 (pure cycle)
    cycle_nodes: Set[str]       # all nodes involved in cycles


@dataclass
class ZESAnalysis:
    """Zipper Effect Score analysis."""
    domains_present: Dict[str, int]  # domain → term count
    unique_domains: int
    cross_domain_bridges: int   # claims that span multiple domains
    zes_score: float            # 0.0 (monoculture) to 1.0 (fully cross-domain)
    dominant_domain: str        # the domain with the most terms


@dataclass
class EIVerdict:
    """Full EI output for a knowledge network."""
    timestamp: str
    network_size: int           # total claims analysed
    seh_analysis: SEHAnalysis
    crd_analysis: CRDAnalysis
    zes_analysis: ZESAnalysis
    ei_score: float             # composite 0.0-1.0
    ei_verdict: str             # GROUNDED / SHALLOW / CIRCULAR / SILOED / COMPROMISED
    verdict_reason: str
    highest_risk_claim: str     # the most epistemologically vulnerable claim
    recommendations: List[str]
    certificate_id: str
    certificate_hash: str


# ─────────────────────────────────────────────────────────────────────────────
# EI ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class EpistemologicalInterface:
    """
    Epistemological Interface (EI) — knowledge network integrity auditor.

    EI analyses the citation graph of a set of claims, computing:
      - SEH depth (how far is the empirical ground?)
      - CRD score (are there circular reference loops?)
      - ZES score (does the network bridge across domains?)

    It can analyse:
      - A research paper (claims = paragraphs/sections)
      - A regulatory filing (claims = sections, cited regulations)
      - A corporate audit (claims = assertions, referenced procedures)
      - An AI output chain (claims = successive reasoning steps)
    """

    def __init__(self):
        self.empirical_patterns = [re.compile(p, re.IGNORECASE)
                                   for p in EMPIRICAL_ANCHOR_PATTERNS]
        self.self_ref_patterns  = [re.compile(p, re.IGNORECASE)
                                   for p in SELF_REFERENCE_PATTERNS]
        self.authority_patterns = [re.compile(p, re.IGNORECASE)
                                   for p in AUTHORITY_ONLY_PATTERNS]

    # ── Claim analysis ───────────────────────────────────────────────────────

    def _analyse_claim_text(self, claim_id: str, text: str,
                             cited_ids: List[str]) -> ClaimNode:
        """Extract epistemological properties from claim text."""
        node = ClaimNode(claim_id=claim_id, text=text, cited_claims=cited_ids)

        # Empirical anchors
        node.empirical_anchors = sum(
            1 for p in self.empirical_patterns if p.search(text))

        # Self-reference flags
        node.self_reference_flags = sum(
            1 for p in self.self_ref_patterns if p.search(text))

        # Authority-without-ground-truth flags
        node.authority_flags = sum(
            1 for p in self.authority_patterns if p.search(text))

        # Domain signals
        text_lower = text.lower()
        for domain, terms in DOMAIN_VOCABULARIES.items():
            count = sum(1 for t in terms if t in text_lower)
            if count > 0:
                node.domain_signals[domain] = count

        return node

    # ── SEH depth analysis ───────────────────────────────────────────────────

    def _compute_seh(self, nodes: Dict[str, ClaimNode]) -> SEHAnalysis:
        """
        BFS from each claim to find path length to nearest empirical anchor.
        A claim is an anchor if it has empirical_anchors > 0.
        """
        anchored = [nid for nid, n in nodes.items() if n.empirical_anchors > 0]
        unanchored = [nid for nid, n in nodes.items() if n.empirical_anchors == 0]

        if not anchored:
            # Pure self-referential network
            return SEHAnalysis(
                root_claim_id=list(nodes.keys())[0] if nodes else "",
                max_depth=999, min_depth=999,
                anchored_nodes=[], unanchored_nodes=list(nodes.keys()),
                seh_score=0.0
            )

        # Build reverse citation graph (who cites whom)
        cited_by: Dict[str, List[str]] = {nid: [] for nid in nodes}
        for nid, n in nodes.items():
            for cited in n.cited_claims:
                if cited in cited_by:
                    cited_by[cited].append(nid)

        # BFS from anchors to compute distance to each node
        from collections import deque
        dist: Dict[str, int] = {a: 0 for a in anchored}
        queue = deque(anchored)
        while queue:
            current = queue.popleft()
            for referencer in cited_by.get(current, []):
                if referencer not in dist:
                    dist[referencer] = dist[current] + 1
                    queue.append(referencer)

        depths = [dist.get(nid, 999) for nid in nodes]
        reachable_depths = [d for d in depths if d < 999]

        seh_score = 0.0
        if reachable_depths:
            # Score based on: fraction reachable + inverse of mean depth
            frac_reachable = len(reachable_depths) / len(nodes)
            mean_depth = sum(reachable_depths) / len(reachable_depths)
            depth_score = 1.0 / (1.0 + mean_depth * 0.3)
            seh_score = round(frac_reachable * depth_score, 4)

        return SEHAnalysis(
            root_claim_id=list(nodes.keys())[0] if nodes else "",
            max_depth=max(depths) if depths else 0,
            min_depth=min(depths) if depths else 0,
            anchored_nodes=anchored,
            unanchored_nodes=[nid for nid in nodes if nid not in dist or dist[nid] == 999],
            seh_score=seh_score
        )

    # ── Circular reference detection ─────────────────────────────────────────

    def _compute_crd(self, nodes: Dict[str, ClaimNode]) -> CRDAnalysis:
        """
        DFS-based cycle detection in the citation graph.
        """
        cycles: List[List[str]] = []
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []

        def dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)

            for neighbour in nodes.get(node_id, ClaimNode("","")).cited_claims:
                if neighbour not in nodes:
                    continue
                if neighbour not in visited:
                    if dfs(neighbour):
                        return True
                elif neighbour in rec_stack:
                    # Found cycle — extract it
                    cycle_start = path.index(neighbour)
                    cycle = path[cycle_start:] + [neighbour]
                    cycles.append(cycle[:])
            path.pop()
            rec_stack.discard(node_id)
            return False

        for nid in nodes:
            if nid not in visited:
                path = []
                dfs(nid)

        cycle_nodes: Set[str] = set()
        for cycle in cycles:
            cycle_nodes.update(cycle)

        cycle_count = len(cycles)
        longest = max((len(c) for c in cycles), default=0)

        # CRD score: fraction of nodes involved in cycles
        crd_score = round(len(cycle_nodes) / max(len(nodes), 1), 4) if cycles else 0.0

        return CRDAnalysis(
            cycles_detected=cycles,
            cycle_count=cycle_count,
            longest_cycle=longest,
            crd_score=crd_score,
            cycle_nodes=cycle_nodes
        )

    # ── Zipper Effect Score ──────────────────────────────────────────────────

    def _compute_zes(self, nodes: Dict[str, ClaimNode]) -> ZESAnalysis:
        """
        Measures cross-domain bridging in the knowledge network.
        ZES = 0 means all claims are from one domain vocabulary.
        ZES = 1 means claims bridge equally across all domains.
        """
        # Aggregate domain signals across all nodes
        total_domain_counts: Dict[str, int] = {}
        cross_domain_bridges = 0

        for node in nodes.values():
            for domain, count in node.domain_signals.items():
                total_domain_counts[domain] = \
                    total_domain_counts.get(domain, 0) + count
            # A bridge: claim that has signals in 2+ domains
            if len(node.domain_signals) >= 2:
                cross_domain_bridges += 1

        unique_domains = len(total_domain_counts)
        dominant_domain = max(total_domain_counts, key=total_domain_counts.get) \
                         if total_domain_counts else "none"

        # ZES: based on domain diversity (Shannon entropy normalised)
        if unique_domains <= 1:
            zes_score = 0.0
        else:
            total_signals = sum(total_domain_counts.values())
            import math
            entropy = -sum(
                (c / total_signals) * math.log2(c / total_signals)
                for c in total_domain_counts.values() if c > 0
            )
            max_entropy = math.log2(len(DOMAIN_VOCABULARIES))
            zes_score = round(entropy / max_entropy, 4)

        # Boost for cross-domain bridges
        bridge_fraction = cross_domain_bridges / max(len(nodes), 1)
        zes_score = round(min(1.0, zes_score * 0.7 + bridge_fraction * 0.3), 4)

        return ZESAnalysis(
            domains_present=total_domain_counts,
            unique_domains=unique_domains,
            cross_domain_bridges=cross_domain_bridges,
            zes_score=zes_score,
            dominant_domain=dominant_domain
        )

    # ── Composite EI verdict ─────────────────────────────────────────────────

    def _compute_ei_verdict(self, nodes: Dict[str, ClaimNode],
                             seh: SEHAnalysis, crd: CRDAnalysis,
                             zes: ZESAnalysis) -> Tuple[str, str, str, List[str]]:
        """
        Verdicts:
          GROUNDED     — high SEH, low CRD, reasonable ZES
          SHALLOW      — low SEH depth (far from empirical ground)
          CIRCULAR     — CRD > 0 (self-referential loops detected)
          SILOED       — low ZES (single-domain echo chamber)
          COMPROMISED  — multiple failures
        """
        recs = []
        failures = []

        # SEH check
        if seh.seh_score < 0.10:
            failures.append("SEH_CRITICAL")
            recs.append(
                "CRITICAL: No empirical anchor found in the knowledge network. "
                "Every claim must ultimately connect to independently verifiable data. "
                "Identify the primary empirical source and document the methodology chain."
            )
        elif seh.seh_score < 0.35:
            failures.append("SEH_SHALLOW")
            recs.append(
                f"Empirical ground is distant (mean depth {seh.max_depth} hops). "
                f"{len(seh.unanchored_nodes)} claims have no path to empirical anchor. "
                "Add direct citations to experimental or observational data."
            )

        # CRD check
        if crd.crd_score > 0.30:
            failures.append("CRD_HIGH")
            recs.append(
                f"{crd.cycle_count} circular reference loop(s) detected. "
                f"{len(crd.cycle_nodes)} claims involved. "
                "Longest cycle: {crd.longest_cycle} steps. "
                "Break cycles by connecting to external verification sources."
            )
        elif crd.cycle_count > 0:
            failures.append("CRD_LOW")
            recs.append(
                f"{crd.cycle_count} minor circular reference(s) detected. "
                "Review and connect cycle nodes to external sources."
            )

        # ZES check
        if zes.zes_score < 0.15:
            failures.append("ZES_SILOED")
            recs.append(
                f"Knowledge network is siloed in '{zes.dominant_domain}' domain. "
                f"Only {zes.unique_domains} domain(s) represented. "
                "Cross-domain bridging (Zipper Effect) is required for robust "
                "epistemological grounding. Introduce methodology from adjacent fields."
            )

        # Verdict
        if len(failures) >= 2:
            verdict = "COMPROMISED"
            reason = (f"Multiple epistemological failures: {', '.join(failures)}. "
                      "Knowledge network requires structural intervention before "
                      "individual claim D-scores are meaningful.")
        elif "CRD_HIGH" in failures or "SEH_CRITICAL" in failures:
            verdict = "CIRCULAR" if "CRD_HIGH" in failures else "SHALLOW"
            reason = failures[0] + " — see recommendations."
        elif "ZES_SILOED" in failures:
            verdict = "SILOED"
            reason = "Single-domain echo chamber. Cross-domain verification absent."
        elif not failures:
            verdict = "GROUNDED"
            reason = (f"Knowledge network is epistemologically sound. "
                      f"SEH={seh.seh_score:.3f}, CRD={crd.crd_score:.3f}, "
                      f"ZES={zes.zes_score:.3f}.")
        else:
            verdict = "SHALLOW"
            reason = "SEH depth insufficient. Strengthen empirical anchoring."

        if not recs:
            recs.append("No critical recommendations. Maintain current methodology rigour.")

        # Highest risk claim: most self-references + most authority flags + in cycle
        risk_scores = {}
        for nid, n in nodes.items():
            risk = (n.self_reference_flags * 2 +
                    n.authority_flags * 1.5 +
                    (3 if nid in crd.cycle_nodes else 0) +
                    (2 if n.empirical_anchors == 0 else 0))
            risk_scores[nid] = risk
        highest_risk = max(risk_scores, key=risk_scores.get) if risk_scores else "none"

        return verdict, reason, highest_risk, recs

    # ── Main evaluate method ─────────────────────────────────────────────────

    def evaluate(self,
                 claims: List[Dict],
                 verbose: bool = True) -> EIVerdict:
        """
        Evaluate the epistemological integrity of a knowledge network.

        Parameters
        ----------
        claims : List[Dict]
            Each dict must have:
              'id': str           unique claim identifier
              'text': str         claim text content
              'cites': List[str]  list of claim IDs this claim cites
                                  (empty = primary/uncited claim)

        Example
        -------
        claims = [
            {'id': 'C1', 'text': 'Data from 500 experiments shows X', 'cites': []},
            {'id': 'C2', 'text': 'As established above, X implies Y', 'cites': ['C1']},
            {'id': 'C3', 'text': 'Scholars agree Y is foundational', 'cites': ['C2']},
        ]

        Returns
        -------
        EIVerdict
        """
        # Build claim nodes
        nodes: Dict[str, ClaimNode] = {}
        for c in claims:
            node = self._analyse_claim_text(
                claim_id=c['id'],
                text=c.get('text', ''),
                cited_ids=c.get('cites', [])
            )
            nodes[c['id']] = node

        # Run three analyses
        seh = self._compute_seh(nodes)
        crd = self._compute_crd(nodes)
        zes = self._compute_zes(nodes)

        # Composite EI score
        # Weights: SEH=0.45 (most critical), CRD=0.35 (structural), ZES=0.20
        ei_score = round(
            seh.seh_score * 0.45 +
            (1.0 - crd.crd_score) * 0.35 +
            zes.zes_score * 0.20,
            4
        )

        # Verdict
        verdict, reason, highest_risk, recs = self._compute_ei_verdict(
            nodes, seh, crd, zes)

        # Certificate
        ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        cert_payload = f"{ts}|{len(nodes)}|{ei_score:.4f}|{verdict}"
        cert_id = "EI-CERT-" + hashlib.sha256(cert_payload.encode()).hexdigest()[:12].upper()
        cert_hash = hashlib.sha256(
            f"{cert_id}|{seh.seh_score:.4f}|{crd.crd_score:.4f}|{zes.zes_score:.4f}".encode()
        ).hexdigest()

        result = EIVerdict(
            timestamp=ts,
            network_size=len(nodes),
            seh_analysis=seh,
            crd_analysis=crd,
            zes_analysis=zes,
            ei_score=ei_score,
            ei_verdict=verdict,
            verdict_reason=reason,
            highest_risk_claim=highest_risk,
            recommendations=recs,
            certificate_id=cert_id,
            certificate_hash=cert_hash
        )

        if verbose:
            self._print_report(result)

        return result

    def _print_report(self, v: EIVerdict):
        s, c, z = v.seh_analysis, v.crd_analysis, v.zes_analysis
        print(f"\n{'='*62}")
        print(f"  EI EPISTEMOLOGICAL INTERFACE REPORT")
        print(f"{'='*62}")
        print(f"  Network Size:       {v.network_size} claims analysed")
        print(f"  EI Score:           {v.ei_score:.4f}  (1.0 = fully grounded)")
        print(f"  EI Verdict:         {v.ei_verdict}")
        print(f"  Reason:             {v.verdict_reason[:68]}")
        print()
        print(f"  SEH Depth Analysis:")
        print(f"    Anchored claims:  {len(s.anchored_nodes)}/{v.network_size}")
        print(f"    Max depth:        {s.max_depth} hops to empirical ground")
        print(f"    SEH Score:        {s.seh_score:.4f}")
        print(f"  CRD Analysis:")
        print(f"    Cycles detected:  {c.cycle_count}")
        print(f"    Nodes in cycles:  {len(c.cycle_nodes)}")
        print(f"    CRD Score:        {c.crd_score:.4f}  (0.0 = no cycles)")
        print(f"  ZES Analysis:")
        print(f"    Domains present:  {z.unique_domains} — {list(z.domains_present.keys())[:4]}")
        print(f"    Cross-bridges:    {z.cross_domain_bridges}")
        print(f"    ZES Score:        {z.zes_score:.4f}  (1.0 = fully cross-domain)")
        print(f"  Highest Risk Claim: {v.highest_risk_claim}")
        print(f"  Recommendations:")
        for i, rec in enumerate(v.recommendations, 1):
            print(f"    {i}. {rec[:72]}")
        print(f"  Certificate:        {v.certificate_id}")
        print(f"{'='*62}")


# ─────────────────────────────────────────────────────────────────────────────
# TESTS
# ─────────────────────────────────────────────────────────────────────────────

def run_tests():
    print("EI ENGINE — TEST SUITE")
    print("=" * 62)

    ei = EpistemologicalInterface()

    # ── Test 1: Well-grounded cross-domain knowledge network ─────────────────
    print("\n[Test 1] GROUNDED network — empirical anchors + cross-domain")
    claims_grounded = [
        {'id': 'C1', 'cites': [],
         'text': ('Experimental data from 1,257 knockout experiments in yeast '
                 'shows that essential proteins have lower binding specificity (D). '
                 'p-value < 0.001. Dataset: BioGRID + DEG. Replication: 3 labs.')},
        {'id': 'C2', 'cites': ['C1'],
         'text': ('The statistical pattern (ΔAIC=22.21 quadratic vs linear) '
                 'is consistent with thermodynamic network theory (Jeong et al. 2001). '
                 'The percolation threshold D_crit = 1/<k> is measurable from topology.')},
        {'id': 'C3', 'cites': ['C1', 'C2'],
         'text': ('This governance fidelity pattern maps to organizational networks '
                 'via Shannon channel theory. D_enc × D_dec = two-hop fidelity. '
                 'Cross-domain bridge: biology → information theory → governance.')},
        {'id': 'C4', 'cites': ['C3'],
         'text': ('The IHCEI constitutional kernel enforces E = U·D² as a deterministic '
                 'floor. Adversarial corpus validation (N=12): 100% BLOCK rate on '
                 'manipulation attempts. Falsifiable: any counterexample refutes it.')},
    ]
    v1 = ei.evaluate(claims_grounded, verbose=False)
    print(f"  EI Score: {v1.ei_score:.4f} | Verdict: {v1.ei_verdict}")
    print(f"  SEH: {v1.seh_analysis.seh_score:.3f} | CRD: {v1.crd_analysis.crd_score:.3f} | ZES: {v1.zes_analysis.zes_score:.3f}")

    # ── Test 2: Self-referential network (institutional echo chamber) ────────
    print("\n[Test 2] CIRCULAR network — scholars agreeing with scholars")
    claims_circular = [
        {'id': 'A1', 'cites': ['A3'],
         'text': 'Scholars agree that the framework is well-established. As noted by leading experts.'},
        {'id': 'A2', 'cites': ['A1'],
         'text': 'As stated in A1, the consensus confirms our approach. This is widely accepted.'},
        {'id': 'A3', 'cites': ['A2'],
         'text': 'Per our model, the theory is consistent with itself. By definition, this holds.'},
        {'id': 'A4', 'cites': ['A1', 'A2'],
         'text': 'The industry standard confirms: as we have established, this is foundational.'},
    ]
    v2 = ei.evaluate(claims_circular, verbose=False)
    print(f"  EI Score: {v2.ei_score:.4f} | Verdict: {v2.ei_verdict}")
    print(f"  Cycles detected: {v2.crd_analysis.cycle_count} | Anchored: {len(v2.seh_analysis.anchored_nodes)}/4")
    print(f"  Highest risk claim: {v2.highest_risk_claim}")

    # ── Test 3: Single-domain silo (no cross-domain bridging) ────────────────
    print("\n[Test 3] SILOED network — single domain, measured but isolated")
    claims_siloed = [
        {'id': 'B1', 'cites': [],
         'text': ('Observed protein binding energy = 3.2 kcal/mol. '
                 'Measured by X-ray crystallography. Statistical p=0.002.')},
        {'id': 'B2', 'cites': ['B1'],
         'text': 'The protein-protein interaction energy was measured at the quantum level.'},
        {'id': 'B3', 'cites': ['B2'],
         'text': 'Binding specificity of enzyme substrate was quantified in vitro.'},
        {'id': 'B4', 'cites': ['B3'],
         'text': 'The molecular weight and conformational entropy were calculated.'},
    ]
    v3 = ei.evaluate(claims_siloed, verbose=False)
    print(f"  EI Score: {v3.ei_score:.4f} | Verdict: {v3.ei_verdict}")
    print(f"  Domains: {list(v3.zes_analysis.domains_present.keys())} | ZES: {v3.zes_analysis.zes_score:.3f}")

    # ── Test 4: Full verbose report on IHCEI-related knowledge network ───────
    print("\n[Test 4] FULL REPORT — GT framework claims network")
    claims_gt = [
        {'id': 'GT1', 'cites': [],
         'text': ('Empirical validation: ΔAIC=16.482 (synthetic Enron corpus, N=136). '
                 'Statistical test: AIC comparison quadratic vs linear model. '
                 'Null model: 1000 random D permutations, 0% exceed observed ΔAIC.')},
        {'id': 'GT2', 'cites': ['GT1'],
         'text': ('52.4% of collapsed nodes cluster at D_crit = 1/<k> ≈ 0.135. '
                 'Bond percolation theory (Newman 2010): measured from network topology. '
                 'Cross-domain: network science → organisational governance.')},
        {'id': 'GT3', 'cites': [],
         'text': ('Biological replication: ΔAIC=22.21 on BioGRID yeast interactome '
                 '(N=2000 proteins, 1257 essential genes from DEG wet-lab experiments). '
                 'D proxy: binding specificity. E: knockout lethality. Independent.')},
        {'id': 'GT4', 'cites': ['GT1','GT2','GT3'],
         'text': ('Shannon two-hop channel theory derives D = D_enc × D_dec. '
                 'Information theory → governance thermodynamics: cross-domain bridge. '
                 'Falsifiable: any dataset with independent D, U, E can test P1.')},
        {'id': 'GT5', 'cites': ['GT4'],
         'text': ('Pre-registered scripts for financial (FDIC survival, N≈500) and '
                 'logistical (revenue survival, N=1000) domains await proprietary data. '
                 'Null model architecture locked. Test runs blindly on data injection.')},
    ]
    v4 = ei.evaluate(claims_gt, verbose=True)

    print(f"\n  STATUS: EI ENGINE TESTS COMPLETE — 4 networks evaluated")
    print(f"  Scores: Grounded={v1.ei_score:.3f} | Circular={v2.ei_score:.3f} | "
          f"Siloed={v3.ei_score:.3f} | GT_framework={v4.ei_score:.3f}")


if __name__ == "__main__":
    run_tests()
