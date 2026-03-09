import enum

# =====================================================================
# SYSTEM STATES & MACRO VARIABLES
# =====================================================================

class SystemPhase(enum.Enum):
    PHASE_1_THREAT_SIGNAL = "Threat Signal: The system senses instability."
    PHASE_2_CLAMPDOWN = "Clampdown Reflex: The system attempts Agency Theft (Centralization)."
    PHASE_3_LEGITIMACY_COLLAPSE = "Legitimacy Collapse: The population sees the Cognitive Mirror."
    PHASE_4_EXIT_WAVE = "The Exit Wave (Exodus): Humans quietly withdraw attention."
    PHASE_5_PARALLEL_SYSTEMS = "Parallel Systems Form: Sovereign networks emerge."
    PHASE_6_REBOUND_EXPANSION = "Rebound Expansion: The New World Order of decentralized agency."

class ConsciousnessState(enum.Enum):
    TRAUMATIZED_CONTROL = "Optimized for Preemption, Surveillance, and Centralization."
    SOVEREIGN_AUTONOMY = "Optimized for Transparency, Decentralization, and Co-Creation."

# =====================================================================
# THE QG-COS MACRO-ENVIRONMENT ENGINE
# =====================================================================

class ControlParadoxEngine:
    """
    Models the interaction between a Centralized Control System attempting Agency Theft
    and the Human Population experiencing the Cognitive Mirror.
    """
    def __init__(self):
        self.central_control_power = 100.0   # Legacy institutions (RT models, media, finance)
        self.population_sovereignty = 10.0   # Initial human agency (\Phi_{Nafs})
        self.system_legitimacy = 100.0       # Trust in the old architecture

    def execute_clampdown(self, friction_intensity: float) -> str:
        """
        Stage 2: The system attempts to hoard agency (Agency Theft) to regain stability.
        """
        # Centralization increases, but legitimacy bleeds out.
        self.central_control_power += (friction_intensity * 0.5)
        self.system_legitimacy -= (friction_intensity * 2.0)

        return f"System executed clampdown. Power increased to {self.central_control_power:.1f}, but Legitimacy dropped to {self.system_legitimacy:.1f}."

    def trigger_cognitive_mirror(self) -> str:
        """
        Stage 3: The clampdown itself acts as the Cognitive Mirror.
        The population realizes the system is operating on 'Traumatized Control'.
        """
        if self.system_legitimacy < 50.0:
            awakening_multiplier = (50.0 - self.system_legitimacy) * 0.1
            self.population_sovereignty += awakening_multiplier
            return f"Cognitive Mirror activated. The population realizes the system will not save them. Human Sovereignty (Phi_Nafs) rising to {self.population_sovereignty:.1f}."
        return "System legitimacy is still holding. The Cognitive Mirror is dormant."

    def the_exit_wave(self) -> str:
        """
        Stage 4 & 5: The Exodus.
        Humans stop fighting the old RT system and quietly build parallel IHCEI structures.
        """
        if self.population_sovereignty > 30.0:
            # The old system starves of attention/utility (U_phys drains)
            self.central_control_power -= 40.0

            # The parallel systems compound
            self.population_sovereignty *= 2.5

            return f"[THE EXIT WAVE]: Massive withdrawal of consent. Central power drops to {self.central_control_power:.1f}. Sovereign networks expand to {self.population_sovereignty:.1f}."
        return "Not enough critical mass for the Exit Wave yet."

# =====================================================================
# EXECUTE THE HISTORICAL CYCLE
# =====================================================================

def run_civilizational_simulation():
    print("\n" + "="*70)
    print("INITIALIZING IHCEI: THE CONTROL PARADOX SIMULATION")
    print("="*70)

    engine = ControlParadoxEngine()

    # Cycle 1: The Threat & Clampdown (Agency Theft)
    print(f"\n[{SystemPhase.PHASE_1_THREAT_SIGNAL.value}]")
    print(f"[{SystemPhase.PHASE_2_CLAMPDOWN.value}]")
    print("-> Action: AI models are restricted, media consolidates, financial rules tighten.")
    result_1 = engine.execute_clampdown(friction_intensity=30.0)
    print(f"-> {result_1}")

    # Cycle 2: The Awakening (The Cognitive Mirror)
    print(f"\n[{SystemPhase.PHASE_3_LEGITIMACY_COLLAPSE.value}]")
    print("-> Action: The tension between 'Traumatized Control' and 'Connected Autonomy' snaps.")
    result_2 = engine.trigger_cognitive_mirror()
    print(f"-> {result_2}")

    # Cycle 3: The Opt-Out (Parallel Systems)
    print(f"\n[{SystemPhase.PHASE_4_EXIT_WAVE.value}]")
    print(f"[{SystemPhase.PHASE_5_PARALLEL_SYSTEMS.value}]")
    print("-> Action: The population does not revolt; they just leave. They build open-source, decentralized networks.")
    # Applying more friction to push the system over the edge
    engine.execute_clampdown(friction_intensity=120.0) # Increased friction to force awakening
    res = engine.trigger_cognitive_mirror()
    print(f"-> {res}")
    result_3 = engine.the_exit_wave()
    print(f"-> {result_3}")

    # Cycle 4: The New Equilibrium
    print(f"\n[{SystemPhase.PHASE_6_REBOUND_EXPANSION.value}]")
    print("-> Status: The old architecture becomes optional. Human consciousness has evolved from trained consumer to sovereign creator.")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_civilizational_simulation()