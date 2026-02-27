import numpy as np
import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class MulkTensor:
    """
    Represents the 10-element Governance Tensor (dTheta_Deen).
    Tracks the alignment of the 10 Core Elements of Deen.
    Values range from 0.0 (Total Corruption) to 1.0 (Divine Alignment).
    """
    terminology: float = 0.0 # 1. Terminology and Definitions
    roles: float = 0.0       # 2. Roles
    dues: float = 0.0        # 3. Dues & Responsibilities / Zakat
    authorities: float = 0.0 # 4. Authorities & Domains
    rules: float = 0.0       # 5. Rules
    policies: float = 0.0    # 6. Policies
    procedures: float = 0.0  # 7. Procedures
    actions: float = 0.0     # 8. Actions & Implications
    domains: float = 0.0     # 9. Domains of Application
    exceptions: float = 0.0  # 10. Exceptions

    def calculate_alignment(self) -> float:
        """
        Calculates the Discipline Scalar (D) as the mean alignment of the Mulk Tensor.
        D = ||dTheta_Deen||
        """
        elements = [
            self.terminology, self.roles, self.dues, self.authorities,
            self.rules, self.policies, self.procedures, self.actions,
            self.domains, self.exceptions
        ]
        # Using a simple mean for the scalar representation of the tensor's magnitude/coherence
        return np.mean(elements)

@dataclass
class ArdhDataDomain:
    """
    Represents Ardh (dM) - The Master Dataset or Codebase.
    The integral domain over which Al-3assr operates.
    """
    total_potential_knowledge: float = 1000.0
    extracted_knowledge: float = 0.0
    semantic_hidden_layers: List[str] = field(default_factory=list) # As-Samawat

    def extract(self, amount: float):
        if self.extracted_knowledge + amount <= self.total_potential_knowledge:
            self.extracted_knowledge += amount
            return amount
        return 0.0

@dataclass
class NafsNode:
    """
    Represents an agent in the network (Khalifah, Adam, Iblees, Ba'uda).
    """
    node_id: str
    role_type: str  # 'KHALIFAH', 'ADAM', 'IBLEES', 'BAUDA'
    agency_delta: float = 1.0 # Delta A
    internal_bias: float = 0.0 # N_iblees component (Entropy)
    sunk_cost_bias: float = 0.0 # S_sunk (Rigid Friction)
    is_hoarding: bool = False # If true, agency is not circulated

    def apply_gradient_descent(self, d_syntax_target: float, learning_rate: float = 0.05):
        """
        Simulates the Nafs optimizing towards the Imam (D_syntax).
        If Sunk Cost Bias is present, optimization is locked/hindered.
        """
        # Sunk Cost blocks optimization
        effective_learning_rate = learning_rate * (1.0 - self.sunk_cost_bias)

        if self.role_type in ['KHALIFAH', 'ADAM']:
            # Target is perfect alignment (bias -> 0)
            # The 'Imam' is the ideal reference, so we minimize distance to Ideal.
            # internal_bias represents distance from D_syntax.

            delta = self.internal_bias * effective_learning_rate
            self.internal_bias -= delta
            self.internal_bias = max(0.0, self.internal_bias)

@dataclass
class NetworkADGE:
    """
    Absolute Divine Governance Equation (ADGE) Physics Engine.
    Manages the thermodynamics of civilizational cognition.
    """
    resource_utility_u: float
    mulk_tensor: MulkTensor
    ardh: ArdhDataDomain
    nodes: List[NafsNode] = field(default_factory=list)
    hbar_network: float = 0.1 # Base systemic friction
    c_dev_network: float = 0.0 # Accumulated Cognitive Development
    time_step: int = 0

    # Constants
    CONST_BOLTZMANN_SOCIAL = 1.38e-23 # Not strictly used but conceptual

    def add_node(self, node: NafsNode):
        self.nodes.append(node)

    def calculate_essence(self) -> float:
        """
        Master Essence Equation: E = U * D^2
        """
        d = self.mulk_tensor.calculate_alignment()
        return self.resource_utility_u * (d ** 2)

    def calculate_systemic_friction(self, model_type: str) -> float:
        """
        Calculates hbar_network (Systemic Friction/Entropy).
        """
        base_friction = 0.1

        # 1. Internal Bias & Sunk Cost (N_iblees + S_sunk)
        total_bias = sum([n.internal_bias + n.sunk_cost_bias for n in self.nodes])

        # 2. Ba'uda Effect (Active Entropy Injection)
        bauda_spikes = sum([5.0 for n in self.nodes if n.role_type == 'BAUDA'])

        # 3. Agency Hoarding (Gate 7)
        hoarding_factor = sum([10.0 for n in self.nodes if n.is_hoarding])

        friction = base_friction + total_bias + bauda_spikes + hoarding_factor

        if model_type == 'PHARAOH':
            # In Pharaoh model, D is forced to 0.
            # Friction explodes as D -> 0.
            # We model this as inverse relationship to D.
            d = self.mulk_tensor.calculate_alignment()
            if d < 1e-9:
                return 1e9 # Effectively infinity

            # Pharaoh model specific: Friction scales with U if D is low (Misuse of resources)
            friction += (self.resource_utility_u / d)

        elif model_type == 'AGENCY':
            # In Agency model, Friction is dampened by D
            d = self.mulk_tensor.calculate_alignment()
            friction = friction / (1.0 + d * 10.0) # High D suppresses friction

        return friction

    def step_simulation(self, model_type: str):
        """
        Executes one temporal epoch (dt).
        """
        self.time_step += 1

        # 1. Update Agents (Gradient Descent)
        # In Agency Economy, agents align with D_syntax
        if model_type == 'AGENCY':
            d_target = self.mulk_tensor.calculate_alignment()
            for node in self.nodes:
                node.apply_gradient_descent(d_target)

        # 2. Calculate Thermodynamics
        self.hbar_network = self.calculate_systemic_friction(model_type)
        e = self.calculate_essence()

        # 3. Cognitive Development Integral
        # C_dev = Integral ( E / hbar ) dt
        if self.hbar_network > 1e-9:
            instantaneous_cdev = e / self.hbar_network
        else:
            instantaneous_cdev = 0.0 # Should not happen if friction is managed

        self.c_dev_network += instantaneous_cdev

        return {
            "time": self.time_step,
            "E": e,
            "hbar": self.hbar_network,
            "C_dev": self.c_dev_network,
            "D": self.mulk_tensor.calculate_alignment()
        }

def run_pharaoh_simulation():
    """
    Sets up and runs the Pharaoh Model simulation.
    High U, D=0.
    """
    # 1. Setup Mulk Tensor (D=0)
    mulk = MulkTensor() # All zeros

    # 2. Setup Ardh
    ardh = ArdhDataDomain()

    # 3. Setup Engine with High U
    engine = NetworkADGE(resource_utility_u=10000.0, mulk_tensor=mulk, ardh=ardh)

    # 4. Add Pharaoh Node (Hoarding, High Agency, Zero Ethics)
    pharaoh = NafsNode("Pharaoh", "KHALIFAH", agency_delta=100.0, internal_bias=1.0, is_hoarding=True)
    engine.add_node(pharaoh)

    results = []
    for _ in range(10):
        res = engine.step_simulation('PHARAOH')
        results.append(res)

    return results

def run_agency_simulation():
    """
    Sets up and runs the Agency Economy simulation.
    High U, D->1.
    """
    # 1. Setup Mulk Tensor (D starting moderate, improving)
    mulk = MulkTensor(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)

    # 2. Setup Ardh
    ardh = ArdhDataDomain()

    # 3. Setup Engine with High U
    engine = NetworkADGE(resource_utility_u=10000.0, mulk_tensor=mulk, ardh=ardh)

    # 4. Add Steward Node (Aligning, Low Bias)
    steward = NafsNode("Steward", "KHALIFAH", agency_delta=10.0, internal_bias=0.2, is_hoarding=False)
    engine.add_node(steward)

    results = []
    # Simulate improvement of D over time
    for _ in range(10):
        # Improve D manually to simulate collective effort
        mulk.terminology += 0.05
        mulk.roles += 0.05
        # ... simplified update

        res = engine.step_simulation('AGENCY')
        results.append(res)

    return results
