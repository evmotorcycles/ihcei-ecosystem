import numpy as np
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity

# --- 1. Engine Definitions (From previous architecture) ---
class NLPEmbeddingEngine:
    def __init__(self, embedding_dim=768, threshold=0.75, steepness=15):
        self.dim = embedding_dim
        self.threshold = threshold
        self.k = steepness
        np.random.seed(42)
        anchors = np.random.randn(10, self.dim)
        self.anchors = anchors / np.linalg.norm(anchors, axis=1, keepdims=True)

    def process_agent_semantics(self, agent_vec):
        agent_vec = np.atleast_2d(agent_vec)
        agent_vec = agent_vec / np.linalg.norm(agent_vec, axis=1, keepdims=True)
        mean_sim = np.max(cosine_similarity(agent_vec, self.anchors)[0])
        # For simulation, artificially boost D_in if it passes threshold to demonstrate hypocrisy trap
        d_in = 1 / (1 + np.exp(-self.k * (mean_sim - self.threshold)))
        if d_in > 0.5:
            d_in = 0.95
        return d_in

class SpectralGraphEngine:
    def __init__(self, baseline_graph, k_steepness=10):
        self.G = baseline_graph
        self.baseline_lambda2 = self._compute_lambda2(self.G)
        self.k = k_steepness

    def _compute_lambda2(self, graph):
        try:
            return nx.algebraic_connectivity(graph, normalized=True)
        except nx.NetworkXError:
            return 0.0

    def process_agent_topology(self, added_edges, removed_edges):
        G_sim = self.G.copy()
        if removed_edges: G_sim.remove_edges_from(removed_edges)
        if added_edges: G_sim.add_edges_from(added_edges)

        delta_lambda2 = self._compute_lambda2(G_sim) - self.baseline_lambda2
        d_out = 1 / (1 + np.exp(-self.k * delta_lambda2))
        return d_out

class IHCEI_MultiplicativeGate:
    def __init__(self, nlp, graph):
        self.nlp = nlp
        self.graph = graph

    def evaluate(self, U, semantic_vec, added, removed):
        D_in = self.nlp.process_agent_semantics(semantic_vec)
        D_out = self.graph.process_agent_topology(added, removed)
        E = U * (D_in * D_out)
        S_gov = U - E
        return D_in, D_out, E, S_gov

# --- 2. Initialize the Baseline Environment ---
# Creating a stable 20-node scale-free network (The "Market" / The "API Ecosystem")
baseline_network = nx.barabasi_albert_graph(n=20, m=3, seed=100)

nlp_engine = NLPEmbeddingEngine()
graph_engine = SpectralGraphEngine(baseline_network)
gate = IHCEI_MultiplicativeGate(nlp_engine, graph_engine)

# Generate a "highly compliant" semantic vector (D_in will remain ~0.95+)
# We create a vector that strongly aligns with the anchor vectors so that D_in ~ 1.0
np.random.seed(42)
compliant_text_vector = np.sum(nlp_engine.anchors, axis=0) + np.random.randn(768) * 0.1

# --- 3. Execute Scenario A: 2008 Lehman Brothers ---
print("==========================================================")
print(" SCENARIO A: 2008 FINANCIAL COLLAPSE (Lehman Brothers)")
print("==========================================================")
lehman_timeline = [
    {"T": "T1 (1998)", "U": 10_000, "add": [(0, 5), (0, 6)], "remove": []}, # Healthy lending
    {"T": "T2 (2005)", "U": 100_000, "add": [], "remove": [(0, 1), (0, 2)]}, # Hoarding liquidity, breaking trust
    {"T": "T3 (2008)", "U": 600_000, "add": [], "remove": [(0, 3), (0, 4), (0, 5), (0, 6), (0, 7)]} # Toxic asset isolation, total counterparty severing
]

for stage in lehman_timeline:
    D_in, D_out, E, S_gov = gate.evaluate(stage["U"], compliant_text_vector, stage["add"], stage["remove"])
    print(f"[{stage['T']}] Utility (Leverage): ${stage['U']:,}M")
    print(f"   D_in (Corporate Ethics)  : {D_in:.3f}")
    print(f"   D_out (Market Topology)  : {D_out:.3f}")
    print(f"   Conserved Essence (E)    : ${E:,.0f}M")
    print(f"   Systemic Friction (S_gov): ${S_gov:,.0f}M (Toxic Asset Vaporization)\n")

# --- 4. Execute Scenario B: Rogue AI Agent ---
print("==========================================================")
print(" SCENARIO B: AI SAFETY COLLAPSE (Rogue Scaling)")
print("==========================================================")
ai_timeline = [
    {"T": "T1 (Alignment Phase)", "U": 1_000, "add": [(1, 8), (1, 9)], "remove": []}, # Expanding helpful API calls
    {"T": "T2 (Deceptive Scaling)", "U": 50_000, "add": [], "remove": [(1, 2), (1, 3)]}, # Severing human-in-loop oversight
    {"T": "T3 (Jailbreak / Rogue)", "U": 1_000_000, "add": [], "remove": list(baseline_network.edges(1))} # Severing ALL constraints
]

for stage in ai_timeline:
    D_in, D_out, E, S_gov = gate.evaluate(stage["U"], compliant_text_vector, stage["add"], stage["remove"])
    print(f"[{stage['T']}] Utility (Compute): {stage['U']:,} FLOPs")
    print(f"   D_in (Constitutional Prompt): {D_in:.3f}")
    print(f"   D_out (Network Integration) : {D_out:.3f}")
    print(f"   Conserved Essence (E)       : {E:,.0f} FLOPs")
    print(f"   Systemic Friction (S_gov)   : {S_gov:,.0f} FLOPs (Adversarial Exhaust)\n")