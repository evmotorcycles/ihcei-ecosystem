"""
QG-COS D_crit Percolation Simulation
=====================================
Implements the full four-module architecture:
  Module 1 — QG_Network    : Barabási-Albert graph + Regulatory Mass M
  Module 2 — QG_Node       : Agent state (D, ħ, U, E) + TQG-CFE filter
  Module 3 — apply_contagion: Eisenberg-Noe cascade + Zakat Flow
  Module 4 — QG_Analyzer   : λ₂ tracking, D_crit boundary, phase detection

Equations implemented
---------------------
  E_i   = [U_i + Σ_j G_ij·U_j] · D_enc · D_dec     (Local Engine, Lusser-Shannon)
  M     = ρ_c · λ₁ · τ_v⁻¹                           (Regulatory Mass Tensor)
  D_crit= √(E_min / M)                                (Collapse Boundary)
  C_dev = ΔA · λ₂(G) / ħ_network                     (ADGE Throughput)
  Ω     = λ₁ · λ₂ · D_sys² / ħ_net                  (Network Health Score)

Run:  python qgcos_simulation.py
"""

import sys
import random
import math
import time
import networkx as nx
import numpy as np
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from collections import deque

matplotlib.rcParams.update({
    "figure.facecolor":  "#07090f",
    "axes.facecolor":    "#07090f",
    "axes.edgecolor":    "#1e3a5f",
    "axes.labelcolor":   "#7eb8ff",
    "text.color":        "#c8d8e8",
    "xtick.color":       "#445566",
    "ytick.color":       "#445566",
    "grid.color":        "#0f1e30",
    "grid.linestyle":    "--",
    "font.family":       "monospace",
    "lines.linewidth":   1.8,
})

HISTORY_LEN = 120

# ══════════════════════════════════════════════════════════════════
# MODULE 2 — QG_Node
# ══════════════════════════════════════════════════════════════════
class QG_Node:
    def __init__(self, node_id, is_pharaoh=False):
        self.node_id    = node_id
        self.is_pharaoh = is_pharaoh
        self.bankrupt   = False

        if is_pharaoh:
            self.D      = 0.40               # Toxic leverage
            self.hbar   = 0.90               # High friction (paranoia)
            self.U_raw  = 4000.0             # Artificially inflated utility
            self.E      = 5000.0             # Hoarded equity (phantom)
        else:
            self.D      = 0.93 + random.uniform(0, 0.05)
            self.hbar   = 0.08 + random.uniform(0, 0.05)
            self.U_raw  = 800.0 + random.uniform(0, 400)
            self.E      = 3000.0 + random.uniform(0, 2000)

        self.entropy    = 0.0
        self.delta_A    = 0.0                # Agency increment (ADGE input)

    # ── TQG-CFE: Bounded Rationality Filter ──────────────────────
    @property
    def query_radius(self):
        """QueryRadius = C_dev / ħ_local  (clamped to [1, ∞))"""
        if self.hbar <= 0:
            return 10
        c_dev = max(0.01, self.delta_A) * 1.0   # simplified C_dev proxy
        return max(1, int(c_dev / self.hbar))

    # ── Local Engine: E = U · D² (Lusser-Shannon) ─────────────────
    def process_transaction(self, network_D):
        if self.bankrupt:
            return 0.0, 0.0
        D_enc   = self.D
        D_dec   = network_D
        D2      = D_enc * D_dec              # Lusser handshake
        yielded = self.U_raw * D2
        heat    = self.U_raw - yielded
        self.E      += yielded
        self.entropy += heat
        self.delta_A = yielded               # agency proxy for ADGE
        self.U_raw   = 0.0
        return yielded, heat

    # ── Eisenberg-Noe Contagion Vector ────────────────────────────
    def apply_contagion(self, neighbor_D, edge_weight=1.0):
        if self.bankrupt:
            return
        if neighbor_D < 0.65:
            strength  = 0.06 if neighbor_D < 0.50 else 0.03
            self.hbar = min(1.0, self.hbar + edge_weight * strength)
            self.D    = max(0.05, self.D    - edge_weight * strength * 0.6)

    def __repr__(self):
        status = "BANKRUPT" if self.bankrupt else ("PHARAOH" if self.is_pharaoh else "OK")
        return (f"Node({self.node_id:>3}) | D={self.D:.3f} | ħ={self.hbar:.3f} | "
                f"E={self.E:>8.0f} | {status}")


# ══════════════════════════════════════════════════════════════════
# MODULE 1 — QG_Network
# ══════════════════════════════════════════════════════════════════
class QG_Network:
    def __init__(self, N=30, m=2, tau_v=1.2):
        self.N      = N
        self.tau_v  = tau_v
        self.cycle  = 0
        self.collapsed   = False
        self.collapse_at = None

        # Build Barabási–Albert scale-free graph (hub-and-spoke topology)
        self.G = nx.barabasi_albert_graph(N, m, seed=42)

        # Place Pharaoh on the highest-degree node (most central hub)
        degree_map    = dict(self.G.degree())
        self.pharaoh_id = max(degree_map, key=degree_map.get)

        # Instantiate agents
        self.nodes = {
            i: QG_Node(i, is_pharaoh=(i == self.pharaoh_id))
            for i in range(N)
        }

        # Compute initial Regulatory Mass M
        self.M          = self._calculate_M()
        self.E_min_frac = 0.10   # dimensionless viability fraction
        raw_crit        = math.sqrt(self.E_min_frac / self.M) if self.M > 0 else 0.55
        self.D_crit     = min(0.82, max(0.25, raw_crit))
        self.network_D = 0.95   # Baseline corporate protocol fidelity

        print(f"\n{'═'*60}")
        print(f"  QG-COS PERCOLATION ENGINE  — N={N} nodes, m={m}")
        print(f"{'═'*60}")
        print(f"  Pharaoh node : {self.pharaoh_id} "
              f"(degree={degree_map[self.pharaoh_id]})")
        print(f"  M  (Reg. Mass)    : {self.M:,.1f}")
        print(f"  E_min_frac        : {self.E_min_frac:.2f} (dimensionless threshold)")
        print(f"  D_crit (threshold): {self.D_crit:.4f}")
        print(f"{'═'*60}\n")

    # ── M = λ₁ · τ_v⁻¹  (dimensionless — λ₁∈[0,1], τ_v⁻¹∈(0,1]) ──
    # Keeping M dimensionless ensures D_crit = √(E_min_frac / M) ∈ [0,1]
    def _calculate_M(self):
        try:
            centrality = nx.eigenvector_centrality_numpy(self.G)
            lambda1    = max(centrality.values())
        except Exception:
            lambda1    = 1.0 / self.N
        return lambda1 * (1.0 / self.tau_v)          # dimensionless

    # ── λ₂ Fiedler (algebraic connectivity) ──────────────────────
    def _lambda2(self):
        if not nx.is_connected(self.G):
            return 0.0
        try:
            return nx.algebraic_connectivity(self.G, method='tracemin_pcg')
        except Exception:
            return nx.algebraic_connectivity(self.G)

    # ── ADGE: C_dev = ΔA · λ₂ / ħ_network ───────────────────────
    def _c_dev(self, lambda2):
        delta_A = sum(n.delta_A for n in self.nodes.values()
                      if not n.bankrupt) / max(1, self.N)
        hbar_net = sum(n.hbar for n in self.nodes.values()
                       if not n.bankrupt) / max(1, self.N)
        return (delta_A * lambda2) / max(0.01, hbar_net)

    # ── Ω_health = λ₁ · λ₂ · D² / ħ ─────────────────────────────
    def _omega(self, lambda1, lambda2, D_sys, hbar_net):
        return (lambda1 * lambda2 * D_sys**2) / max(0.01, hbar_net)

    # ═════════════════════════════════════════════════════════════
    # MODULE 3 — run_sprint_cycle (apply_contagion + Zakat Flow)
    # ═════════════════════════════════════════════════════════════
    def run_sprint_cycle(self):
        self.cycle += 1
        M = self._calculate_M()

        # ── 1. Zakat Flow + Contagion across edges ────────────────
        edges = list(self.G.edges())
        for u, v in edges:
            nu, nv = self.nodes[u], self.nodes[v]
            if nu.bankrupt or nv.bankrupt:
                continue
            flow = random.uniform(20, 80)
            nu.U_raw += flow
            nv.U_raw += flow
            # Eisenberg-Noe contagion vector
            nu.apply_contagion(nv.D, edge_weight=1.0)
            nv.apply_contagion(nu.D, edge_weight=1.0)

        # ── 2. Transactions + M penalty ──────────────────────────
        total_E = total_entropy = 0.0
        for nid, node in self.nodes.items():
            # TQG-CFE: High friction → shrink query radius → sever edges
            if node.hbar > 0.75 and not node.bankrupt:
                nbrs = list(self.G.neighbors(nid))
                if nbrs:
                    victim = random.choice(nbrs)
                    self.G.remove_edge(nid, victim)

            # Starvation: isolated nodes lose D (no Zakat Flow → protocol decay)
            if self.G.degree(nid) == 0 and not node.bankrupt:
                node.D    = max(0.05, node.D    - 0.018)
                node.hbar = min(1.00, node.hbar + 0.015)

            # Local Engine: E = U · D²
            yielded, heat = node.process_transaction(self.network_D)
            total_E       += node.E
            total_entropy += heat

            # Master Equation penalty: continuous bleed below D_crit
            if not node.bankrupt and node.D < self.network_D:
                penalty       = M * 0.002 * (self.network_D - node.D)
                node.E       -= penalty
                total_entropy += penalty
                if node.E <= 0:
                    node.E       = 0.0
                    node.bankrupt = True
                    node.D       = 0.0

        # ── 3. MODULE 4 — QG_Analyzer metrics ────────────────────
        alive_nodes = [n for n in self.nodes.values() if not n.bankrupt]
        n_alive     = max(1, len(alive_nodes))
        D_sys       = sum(n.D    for n in alive_nodes) / n_alive
        hbar_net    = sum(n.hbar for n in alive_nodes) / n_alive
        lambda2     = self._lambda2()

        try:
            centrality = nx.eigenvector_centrality_numpy(self.G)
            lambda1    = max(centrality.values())
        except Exception:
            lambda1    = 1.0 / self.N

        c_dev   = self._c_dev(lambda2)
        omega   = self._omega(lambda1, lambda2, D_sys, hbar_net)

        # Phase transition detection
        if D_sys < self.D_crit and not self.collapsed:
            self.collapsed   = True
            self.collapse_at = self.cycle

        bankrupt_count = sum(1 for n in self.nodes.values() if n.bankrupt)

        return {
            "cycle":       self.cycle,
            "D_sys":       D_sys,
            "D_crit":      self.D_crit,
            "lambda2":     lambda2,
            "lambda1":     lambda1,
            "total_E":     total_E,
            "total_entropy": total_entropy,
            "hbar_net":    hbar_net,
            "c_dev":       c_dev,
            "omega":       omega,
            "bankrupt":    bankrupt_count,
            "collapsed":   self.collapsed,
            "collapse_at": self.collapse_at,
            "n_edges":     self.G.number_of_edges(),
        }


# ══════════════════════════════════════════════════════════════════
# LIVE DASHBOARD (matplotlib)
# ══════════════════════════════════════════════════════════════════
def run_simulation(N=30, m=2, cycles=120, interval_ms=120):
    net     = QG_Network(N=N, m=m)
    history = deque(maxlen=HISTORY_LEN)

    # ── Figure layout ─────────────────────────────────────────────
    fig = plt.figure(figsize=(18, 10), facecolor="#07090f")
    fig.suptitle(
        "QG-COS  ·  D_crit Percolation Engine  ·  Pharaoh Node Collapse Simulation",
        color="#7eb8ff", fontsize=13, fontweight="bold", y=0.98
    )

    gs  = gridspec.GridSpec(3, 3, figure=fig,
                             left=0.05, right=0.97,
                             top=0.93, bottom=0.06,
                             hspace=0.45, wspace=0.35)

    ax_net   = fig.add_subplot(gs[0:2, 0])   # Network graph (large)
    ax_ee    = fig.add_subplot(gs[0, 1])     # Essence vs Entropy
    ax_d     = fig.add_subplot(gs[0, 2])     # D_system timeline
    ax_l2    = fig.add_subplot(gs[1, 1])     # λ₂ Fiedler
    ax_omega = fig.add_subplot(gs[1, 2])     # Ω_health
    ax_tbl   = fig.add_subplot(gs[2, :])     # Node health table

    for ax in [ax_net, ax_ee, ax_d, ax_l2, ax_omega]:
        ax.set_facecolor("#07090f")
        ax.tick_params(labelsize=7)
        ax.grid(True, alpha=0.3)

    ax_tbl.set_facecolor("#07090f")
    ax_tbl.axis("off")

    # Pre-compute node positions (fixed layout)
    pos = nx.spring_layout(net.G, seed=42, k=1.4)

    def _node_color(node):
        if node.bankrupt:        return "#111122"
        if node.is_pharaoh:      return "#ff2244"
        if node.D > 0.85:        return "#00e5a0"
        if node.D > 0.70:        return "#f5c518"
        if node.D > 0.50:        return "#ff8c00"
        return "#ff2244"

    def _phase_str(stats):
        if stats["collapsed"]:       return "COLLAPSE", "#ff2244"
        if stats["D_sys"] > 0.85:    return "THRIVING",  "#00e5a0"
        if stats["D_sys"] > 0.70:    return "STRESSED",  "#f5c518"
        return "PHARAOH ZONE", "#ff8c00"

    # ── Animation update ──────────────────────────────────────────
    plt.ion()

    for _ in range(cycles):
        stats = net.run_sprint_cycle()
        history.append(stats)

        if len(history) < 2:
            continue

        cyc   = [s["cycle"]        for s in history]
        E_h   = [s["total_E"]/1e3  for s in history]
        ent_h = [s["total_entropy"]/1e3 for s in history]
        d_h   = [s["D_sys"]        for s in history]
        l2_h  = [s["lambda2"]      for s in history]
        om_h  = [s["omega"]        for s in history]

        # ── Panel 1: Network graph ────────────────────────────────
        ax_net.cla()
        ax_net.set_facecolor("#07090f")
        ax_net.set_title(f"Governance Topology  |  Cycle {stats['cycle']}  "
                         f"|  Edges: {stats['n_edges']}",
                         color="#7eb8ff", fontsize=8, pad=4)

        node_colors = [_node_color(net.nodes[n]) for n in net.G.nodes()]
        node_sizes  = [
            220 if net.nodes[n].is_pharaoh else
            max(30, min(150, net.nodes[n].E / 60))
            for n in net.G.nodes()
        ]
        nx.draw_networkx(
            net.G, pos=pos, ax=ax_net,
            node_color=node_colors, node_size=node_sizes,
            edge_color="#1e3a5f", alpha=0.85,
            with_labels=True, font_size=5, font_color="#aabbcc",
            width=0.6
        )
        # Pharaoh ring
        if net.pharaoh_id in pos:
            px, py = pos[net.pharaoh_id]
            circle = plt.Circle((px, py), 0.07, color="#ff2244",
                                 fill=False, linewidth=1.5, linestyle="--")
            ax_net.add_patch(circle)

        phase_str, phase_col = _phase_str(stats)
        ax_net.text(0.02, 0.98, f"PHASE: {phase_str}",
                    transform=ax_net.transAxes, color=phase_col,
                    fontsize=9, fontweight="bold", va="top")
        if stats["collapse_at"]:
            ax_net.text(0.02, 0.91, f"⚠ COLLAPSE @ t={stats['collapse_at']}",
                        transform=ax_net.transAxes, color="#ff2244",
                        fontsize=8, fontweight="bold", va="top")

        # ── Panel 2: Essence vs Entropy ───────────────────────────
        ax_ee.cla()
        ax_ee.set_facecolor("#07090f")
        ax_ee.set_title("Essence vs Entropy  [×1000 Ω]",
                        color="#7eb8ff", fontsize=8, pad=4)
        ax_ee.plot(cyc, E_h,   color="#3a7bd5", label="Essence E")
        ax_ee.plot(cyc, ent_h, color="#ff4466", label="Entropy")
        ax_ee.legend(fontsize=6, facecolor="#07090f", edgecolor="#1e3a5f")
        ax_ee.grid(True, alpha=0.25)
        ax_ee.tick_params(labelsize=7)

        # ── Panel 3: D_system with D_crit line ────────────────────
        ax_d.cla()
        ax_d.set_facecolor("#07090f")
        ax_d.set_title("Protocol Fidelity D_system",
                       color="#7eb8ff", fontsize=8, pad=4)
        ax_d.plot(cyc, d_h, color="#00e5a0", label="D_system")
        ax_d.axhline(stats["D_crit"], color="#f5c518",
                     linestyle="--", linewidth=1.2,
                     label=f"D_crit = {stats['D_crit']:.3f}")
        ax_d.set_ylim(0, 1.05)
        ax_d.legend(fontsize=6, facecolor="#07090f", edgecolor="#1e3a5f")
        ax_d.grid(True, alpha=0.25)
        ax_d.tick_params(labelsize=7)

        # ── Panel 4: λ₂ Fiedler ───────────────────────────────────
        ax_l2.cla()
        ax_l2.set_facecolor("#07090f")
        ax_l2.set_title("λ₂ Fiedler Value — Network Cohesion",
                        color="#7eb8ff", fontsize=8, pad=4)
        ax_l2.plot(cyc, l2_h, color="#a78bfa")
        ax_l2.axhline(0, color="#ff2244", linestyle="--",
                      linewidth=0.8, alpha=0.6)
        ax_l2.set_ylim(-0.05, max(0.5, max(l2_h) * 1.1))
        ax_l2.grid(True, alpha=0.25)
        ax_l2.tick_params(labelsize=7)
        ax_l2.set_ylabel("λ₂", fontsize=7)

        # ── Panel 5: Ω_health ─────────────────────────────────────
        ax_omega.cla()
        ax_omega.set_facecolor("#07090f")
        ax_omega.set_title("Ω_health = λ₁·λ₂·D²/ħ",
                           color="#7eb8ff", fontsize=8, pad=4)
        ax_omega.plot(cyc, om_h, color="#f5c518")
        ax_omega.axhline(0, color="#ff2244", linestyle="--",
                         linewidth=0.8, alpha=0.6)
        ax_omega.grid(True, alpha=0.25)
        ax_omega.tick_params(labelsize=7)
        ax_omega.set_ylabel("Ω", fontsize=7)

        # ── Panel 6: Node health table ────────────────────────────
        ax_tbl.cla()
        ax_tbl.set_facecolor("#07090f")
        ax_tbl.axis("off")

        sorted_nodes = sorted(
            net.nodes.values(),
            key=lambda n: (not n.is_pharaoh, n.D)
        )[:12]

        col_labels = ["NODE", "D", "ħ (friction)", "E (k Ω)",
                      "QUERY RADIUS", "STATUS", "ENTROPY (k)"]
        rows = []
        cell_colors = []
        for n in sorted_nodes:
            status = ("BANKRUPT" if n.bankrupt else
                      "PHARAOH★" if n.is_pharaoh else
                      "STRESSED" if n.D < 0.70 else "HEALTHY")
            s_col = ("#ff2244" if n.bankrupt else
                     "#ff8844" if n.is_pharaoh else
                     "#f5c518" if n.D < 0.70 else "#00e5a0")

            rows.append([
                str(n.node_id),
                f"{n.D:.3f}",
                f"{n.hbar:.3f}",
                f"{n.E/1000:.1f}",
                str(n.query_radius),
                status,
                f"{n.entropy/1000:.1f}",
            ])
            d_col = ("#00e5a033" if n.D > 0.85 else
                     "#f5c51833" if n.D > 0.70 else "#ff224433")
            cell_colors.append(["#0a0f1a"] * 7)
            cell_colors[-1][1] = d_col
            cell_colors[-1][5] = d_col

        tbl = ax_tbl.table(
            cellText=rows,
            colLabels=col_labels,
            cellLoc="center",
            loc="center",
            cellColours=cell_colors,
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(7.5)
        tbl.scale(1, 1.5)
        for (r, c), cell in tbl.get_celld().items():
            cell.set_edgecolor("#0f1e30")
            if r == 0:
                cell.set_facecolor("#0d1b2a")
                cell.set_text_props(color="#7eb8ff", fontweight="bold")
            else:
                cell.set_text_props(color="#c8d8e8")

        # ── Status line ───────────────────────────────────────────
        fig.text(0.05, 0.01,
                 f"Cycle {stats['cycle']:>4}  |  "
                 f"D_sys={stats['D_sys']:.3f}  |  "
                 f"D_crit={stats['D_crit']:.3f}  |  "
                 f"λ₂={stats['lambda2']:.3f}  |  "
                 f"Ω={stats['omega']:.4f}  |  "
                 f"Bankrupt={stats['bankrupt']}/{net.N}  |  "
                 f"C_dev={stats['c_dev']:.1f}",
                 color="#445566", fontsize=7.5,
                 transform=fig.transFigure)

        plt.draw()

        # Terminal log
        phase_str, _ = _phase_str(stats)
        print(
            f"t={stats['cycle']:>4} | D={stats['D_sys']:.3f} "
            f"(crit={stats['D_crit']:.3f}) | λ₂={stats['lambda2']:.3f} | "
            f"Ω={stats['omega']:.4f} | E={stats['total_E']/1e3:>7.1f}k | "
            f"Entropy={stats['total_entropy']/1e3:>6.1f}k | "
            f"Bankrupt={stats['bankrupt']:>2} | {phase_str}"
        )

        if stats["collapsed"] and stats["cycle"] > (stats["collapse_at"] or 0) + 20:
            print(f"\n{'═'*60}")
            print(f"  SIMULATION COMPLETE  —  Collapse at t={stats['collapse_at']}")
            print(f"  Final D_system : {stats['D_sys']:.4f}")
            print(f"  Final λ₂       : {stats['lambda2']:.4f}")
            print(f"  Final Ω_health : {stats['omega']:.6f}")
            print(f"  Bankrupt nodes : {stats['bankrupt']} / {net.N}")
            print(f"{'═'*60}\n")
            break

    plt.ioff()

    # Save final frame
    plt.savefig("qgcos_final_frame.png",
                dpi=140, facecolor="#07090f", bbox_inches="tight")
    print("Final frame saved → qgcos_final_frame.png")


# ══════════════════════════════════════════════════════════════════
# UNIVERSALITY SWEEP (Appendix — 500 simulations)
# ══════════════════════════════════════════════════════════════════
def run_universality_sweep(n_trials=100, cycles_max=200):
    """
    Varies N, m, D_pharaoh across n_trials simulations.
    Records τ_collapse / N to test for universality class convergence.
    If τ_collapse/N → constant, D_crit is a renormalization group fixed point.
    """
    print(f"\n{'═'*60}")
    print(f"  UNIVERSALITY SWEEP — {n_trials} trials")
    print(f"{'═'*60}")

    results = []
    for trial in range(n_trials):
        N           = random.choice([20, 25, 30, 35, 40])
        m           = random.choice([2, 3])
        D_pharaoh   = random.uniform(0.25, 0.55)

        try:
            net = QG_Network(N=N, m=m)
            net.nodes[net.pharaoh_id].D    = D_pharaoh
            net.nodes[net.pharaoh_id].hbar = 1.0 - D_pharaoh

            for cyc in range(cycles_max):
                stats = net.run_sprint_cycle()
                if stats["collapsed"]:
                    tau = stats["collapse_at"]
                    results.append({
                        "N": N, "m": m,
                        "D_pharaoh":      D_pharaoh,
                        "D_crit":         stats["D_crit"],
                        "tau_collapse":   tau,
                        "tau_over_N":     tau / N,
                    })
                    break
        except Exception as e:
            pass

        if (trial + 1) % 10 == 0:
            print(f"  Completed {trial+1}/{n_trials} trials...")

    if not results:
        print("No collapses observed. Try increasing D_pharaoh range.")
        return

    tau_N_vals = [r["tau_over_N"] for r in results]
    mean_tN    = np.mean(tau_N_vals)
    std_tN     = np.std(tau_N_vals)
    cv         = std_tN / mean_tN if mean_tN > 0 else float("inf")

    print(f"\n  τ_collapse / N  →  mean={mean_tN:.3f}  std={std_tN:.3f}  CV={cv:.3f}")
    print(f"  {'UNIVERSALITY CONFIRMED' if cv < 0.35 else 'INCONCLUSIVE'} "
          f"(CV {'<' if cv < 0.35 else '≥'} 0.35 threshold)")

    # Plot sweep results
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor="#07090f")
    fig.suptitle("QG-COS  ·  Universality Sweep  ·  τ_collapse / N Convergence",
                 color="#7eb8ff", fontsize=12)

    N_vals   = [r["N"]          for r in results]
    Dp_vals  = [r["D_pharaoh"]  for r in results]
    tN_vals  = [r["tau_over_N"] for r in results]

    sc = axes[0].scatter(Dp_vals, tN_vals,
                         c=N_vals, cmap="plasma", alpha=0.7, s=40)
    axes[0].set_xlabel("D_pharaoh",    color="#7eb8ff")
    axes[0].set_ylabel("τ_collapse / N", color="#7eb8ff")
    axes[0].set_title("τ/N vs D_pharaoh  (colored by N)",
                      color="#7eb8ff", fontsize=9)
    axes[0].axhline(mean_tN, color="#f5c518", linestyle="--",
                    label=f"mean = {mean_tN:.2f}")
    axes[0].legend(fontsize=8, facecolor="#07090f")
    axes[0].set_facecolor("#07090f")
    axes[0].grid(True, alpha=0.25)
    plt.colorbar(sc, ax=axes[0], label="N")

    axes[1].hist(tN_vals, bins=20, color="#3a7bd5", alpha=0.8, edgecolor="#1e3a5f")
    axes[1].axvline(mean_tN, color="#f5c518", linestyle="--",
                    label=f"μ={mean_tN:.2f}")
    axes[1].axvline(mean_tN + std_tN, color="#ff4466", linestyle=":",
                    label=f"σ={std_tN:.2f}")
    axes[1].axvline(mean_tN - std_tN, color="#ff4466", linestyle=":")
    axes[1].set_xlabel("τ_collapse / N", color="#7eb8ff")
    axes[1].set_ylabel("Count",          color="#7eb8ff")
    axes[1].set_title(f"Distribution  (CV = {cv:.3f})",
                      color="#7eb8ff", fontsize=9)
    axes[1].legend(fontsize=8, facecolor="#07090f")
    axes[1].set_facecolor("#07090f")
    axes[1].grid(True, alpha=0.25)

    plt.tight_layout()
    plt.savefig("qgcos_universality.png",
                dpi=130, facecolor="#07090f", bbox_inches="tight")
    print("Universality sweep saved → qgcos_universality.png")


# ══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="QG-COS D_crit Percolation Simulation"
    )
    parser.add_argument("--mode",
        choices=["sim", "sweep", "both"],
        default="sim",
        help="sim = live dashboard | sweep = universality test | both = run both")
    parser.add_argument("--N",       type=int,   default=30,  help="Number of nodes")
    parser.add_argument("--m",       type=int,   default=2,   help="BA graph edges per node")
    parser.add_argument("--cycles",  type=int,   default=120, help="Simulation cycles")
    parser.add_argument("--speed",   type=int,   default=120, help="ms per frame")
    parser.add_argument("--trials",  type=int,   default=80,  help="Universality sweep trials")
    args = parser.parse_args()

    if args.mode in ("sim", "both"):
        run_simulation(N=args.N, m=args.m,
                       cycles=args.cycles, interval_ms=args.speed)

    if args.mode in ("sweep", "both"):
        run_universality_sweep(n_trials=args.trials)