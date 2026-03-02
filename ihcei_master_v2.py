import cmath
import numpy as np
from scipy.integrate import dblquad
from typing import Dict, List, Tuple, Any
from enum import Enum
from pydantic import BaseModel, Field

# ==========================================
# 1. ONTOLOGICAL ENUMS & SCHEMAS (Strict Typings)
# ==========================================

class GateOfJahannam(str, Enum):
    GATE_1 = "Vain Adornments"
    GATE_2 = "Groupthink / Confirmation Bias"
    GATE_3 = "Vanity"
    GATE_4 = "Greed / Hoarding"
    GATE_5 = "Envy"
    GATE_6 = "Wrath / Friction"
    GATE_7 = "Benevolent Tyranny / Agency Theft"

class ElementOfDeen(str, Enum):
    TERMINOLOGY = "Terminology"
    ROLES = "Roles"
    DUES = "Dues / Zakat"
    AUTHORITIES = "Authorities"
    RULES = "Rules"
    POLICIES = "Policies"
    PROCEDURES = "Procedures"
    ACTIONS = "Actions"
    DOMAINS = "Domains"
    EXCEPTIONS = "Exceptions"

class PressedPacket(BaseModel):
    """The 7-Stage Al-Asr Extraction Payload"""
    stage_1_tin: str = Field(description="Raw domain terminology")
    stage_2_sulalah: str = Field(description="Essence extraction; surface narrative removed")
    stage_3_nutfah: str = Field(description="The core governance principle seed")
    stage_4_alaqah: List[ElementOfDeen] = Field(description="Mapped to Elements of Deen")
    stage_5_mudghah: Dict[str, str] = Field(description="Cross-domain translations")
    stage_6_eizam: str = Field(description="Mathematical schematization reference")
    stage_7_lahm: str = Field(description="Operational software/protocol output")

class IHCEIVariables(BaseModel):
    """Unified Thermodynamic & Governance Variables"""
    U: float = Field(ge=0.0)                 # Raw Utility
    D: float = Field(ge=0.0, le=1.0)         # Protocol Truth
    alpha: float = Field(ge=0.0, le=1.0)     # Autonomy
    tau: float = Field(ge=0.0, le=1.0)       # Transparency
    rho: float = Field(ge=0.0, le=1.0)       # Protocol Alignment
    hbar_network: float = Field(ge=1e-6)     # Network Entropy (min threshold to avoid div/0)
    phi_nafs_mag: float = Field(ge=0.0)      # Magnitude of Cognitive Vector
    G_ij_matrix: Any = Field(default=None)   # Connectivity Tensor
    gates_triggered: List[GateOfJahannam] = Field(default_factory=list)

# ==========================================
# 2. CROSS-DOMAIN TRANSLATOR (Moral TCP/IP)
# ==========================================

class DomainTranslator:
    """Translates domain jargon into computable QG-COS variables."""

    DOMAIN_MAP = {
        "quantum entanglement": {"var": "G_ij_matrix", "val": 1.0, "note": "Direct Nafs-to-Nafs connectivity"},
        "uncertainty principle": {"var": "hbar_network", "val": 0.8, "note": "Governance noise"},
        "confirmation bias": {"var": "gates_triggered", "val": GateOfJahannam.GATE_2, "note": "Echo chamber friction"},
        "market efficiency": {"var": "G_ij_matrix", "val": 0.9, "note": "Zakat/Agency distribution"},
        "ego depletion": {"var": "alpha", "val": 0.2, "note": "Agency hoarding / cognitive fatigue"}
    }

    def translate(self, text: str, packet: IHCEIVariables) -> IHCEIVariables:
        lowered = text.lower()
        for term, mapping in self.DOMAIN_MAP.items():
            if term in lowered:
                if mapping["var"] == "gates_triggered":
                    packet.gates_triggered.append(mapping["val"])
                else:
                    setattr(packet, mapping["var"], mapping["val"])
        return packet

# ==========================================
# 3. CLASSICAL STACK: GOVERNANCE PHYSICS ENGINE
# ==========================================

class GovernancePhysicsEngine:

    @staticmethod
    def compute_adge_continuous(variables: IHCEIVariables, t_lim=(0, 10), M_lim=(0, 10)) -> float:
        """
        The ADGE Equation using continuous numerical double integration.
        Integrates interaction over Time (t) and Matter/Resources (M).
        """
        # Fallback to a scalar if G_ij_matrix is uninitialized
        g_ij_scalar = variables.G_ij_matrix if isinstance(variables.G_ij_matrix, float) else 0.8

        # dTheta_Deen function (assuming linear progression over time and matter)
        def integrand(t, M):
            interaction = (variables.phi_nafs_mag ** 2) * g_ij_scalar
            d_theta = variables.D * (0.1 * t + 0.05 * M)
            return interaction * d_theta

        # Double Integral over M and t
        integral_val, error_estimate = dblquad(integrand, t_lim[0], t_lim[1], lambda t: M_lim[0], lambda t: M_lim[1])

        c_dev = integral_val / variables.hbar_network
        return c_dev

    @staticmethod
    def compute_destiny(variables: IHCEIVariables) -> float:
        """E = U * D^2 * (ατρ) - Σ G_g V_g"""
        agency_term = variables.alpha * variables.tau * variables.rho
        base_essence = variables.U * (variables.D ** 2) * agency_term

        # Friction Penalty: Each triggered gate subtracts exponential value
        gate_penalty = np.exp(len(variables.gates_triggered) * 0.5) if variables.gates_triggered else 0.0

        return max(0.0, base_essence - gate_penalty)

    @staticmethod
    def compute_tqg_cfe_perception(variables: IHCEIVariables, s_gov: float = 1.0) -> complex:
        """Ψ_experienced = A_n(Φ_cog) * ψ_quantum * exp(i * S_gov / hbar_cognitive)"""
        # A_n modeled as a sigmoid of the cognitive magnitude
        A_n = 1 / (1 + np.exp(-variables.phi_nafs_mag))
        psi_quantum = 1.0 + 0j # Base physical reality

        # Complex phase shift
        phase = cmath.exp(1j * (s_gov / variables.hbar_network))

        psi_experienced = A_n * psi_quantum * phase
        return psi_experienced

# ==========================================
# 4. COGNITIVE MIRROR & ORCHESTRATOR
# ==========================================

class IHCEI_v2_Master:
    def __init__(self):
        self.translator = DomainTranslator()
        self.physics = GovernancePhysicsEngine()

    def process_packet(self, text: str, domain: str = "General", intention_score: float = 1.0) -> Dict[str, Any]:
        # 1. Initialize Default Variables, scaling Autonomy and Cognitive Vector by Niyyah (Intention)
        scaled_alpha = max(0.0, min(1.0, 0.9 * intention_score))
        scaled_phi_nafs = max(0.0, 1.2 * intention_score)

        vars = IHCEIVariables(
            U=10.0,
            D=0.8,
            alpha=scaled_alpha,
            tau=0.8,
            rho=0.9,
            hbar_network=0.5,
            phi_nafs_mag=scaled_phi_nafs
        )

        # 2. Route through Moral TCP/IP Translation using both text and domain
        vars = self.translator.translate(f"{domain} {text}", vars)

        # 3. Compute the Three Master Equations
        c_dev = self.physics.compute_adge_continuous(vars)
        essence = self.physics.compute_destiny(vars)
        psi_complex = self.physics.compute_tqg_cfe_perception(vars)

        # 4. Cognitive Mirror Interface (Socratic Outputs)
        prompts = []
        if essence < 5.0:
            prompts.append("Calculate your Agency Delta (ΔA). Is this transaction creating cognitive fatigue?")
        if vars.gates_triggered:
            prompts.append(f"Audit the Gates: {', '.join([g.value for g in vars.gates_triggered])} detected. How will this friction leak C_dev?")

        return {
            "C_dev_Network_Health": round(c_dev, 4),
            "Destiny_Essence": round(essence, 4),
            "Perception_Phase_Shift": f"{cmath.phase(psi_complex):.2f} rad",
            "M-GUI_Prompts": prompts
        }

if __name__ == "__main__":
    system = IHCEI_v2_Master()
    query = "How do we fix market efficiency when confirmation bias is present?"

    print("\n[ IHCEI v2.0 MASTER ENGINE COMPILED ]\n" + "="*40)
    result = system.process_packet(query)
    for key, value in result.items():
        print(f"{key}: {value}")
