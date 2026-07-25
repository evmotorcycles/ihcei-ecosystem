#!/usr/bin/env python3
"""
circuit_breaker.py -- a drop-in circuit breaker for sequential (multi-hop) agent
pipelines, derived from the LISM cascade law.
================================================================================
Sequential agent pipelines (Agent A's output -> Agent B's input -> ...) lose
fidelity multiplicatively:  H_n = prod_{i=1..n} D_i.  Because agents run at
silicon speed, a pipeline can keep executing long after its joint fidelity has
dropped below any usable floor -- a hyper-active, zero-utility "zombie network".

This class halts propagation once cumulative fidelity falls below a floor D_min,
after an enforcement latency of tau_v hops (how long the system tolerates being
below the floor before it actually trips -- models real detection lag).

    from circuit_breaker import LISM_CircuitBreaker
    cb = LISM_CircuitBreaker(d_min=0.10, tau_v=0)
    for d_i in per_hop_fidelities:
        st = cb.step(d_i)
        if st["tripped"]:
            break            # stop calling the next agent

Honest scope: this is the CONTROL mechanism. It does not measure D_i for you --
your framework supplies each hop's fidelity (a verifier score, a self-consistency
check, a retrieval-grounding score, etc.). The value here is the trip law and the
resource accounting, validated against the repo's real Cohort D telemetry.

No dependencies (standard library only). Zero cost, offline, deterministic.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))


class LISM_CircuitBreaker:
    """Trips (halts a sequential pipeline) when cumulative fidelity prod(D_i) falls
    below D_min for longer than tau_v hops.

    Parameters
    ----------
    d_min : float in (0, 1]   minimum permissible joint fidelity (the floor).
    tau_v : int >= 0          enforcement latency: hops the system may stay below
                              the floor before the breaker actually trips (0 = trip
                              immediately on the first crossing).
    """

    def __init__(self, d_min, tau_v=0):
        if not (0.0 < d_min <= 1.0):
            raise ValueError("d_min must be in (0, 1]")
        if tau_v < 0 or int(tau_v) != tau_v:
            raise ValueError("tau_v must be a non-negative integer (hops)")
        self.d_min = float(d_min)
        self.tau_v = int(tau_v)
        self.cumulative = 1.0
        self.hops = 0
        self.tripped = False
        self.trip_hop = None
        self._below_since = None

    def step(self, d_i):
        """Process one hop's per-hop fidelity d_i in [0, 1]. Returns a status dict.
        Once tripped, further steps are no-ops (propagation is halted)."""
        if not (0.0 <= d_i <= 1.0):
            raise ValueError("per-hop fidelity d_i must be in [0, 1]")
        if self.tripped:
            return self.status()
        self.cumulative *= d_i
        self.hops += 1
        if self.cumulative < self.d_min:
            if self._below_since is None:
                self._below_since = self.hops
            if self.hops - self._below_since >= self.tau_v:
                self.tripped = True
                self.trip_hop = self.hops
        else:
            self._below_since = None
        return self.status()

    def status(self):
        return {"hops": self.hops, "cumulative": self.cumulative,
                "tripped": self.tripped, "trip_hop": self.trip_hop}


def simulate(per_hop_fidelities, d_min, tau_v=0):
    """Run a governed pipeline vs. an ungoverned one over the same per-hop fidelities.

    Returns a dict with the trip hop, hops the breaker prevented, and the number of
    "zombie" hops (executed while cumulative fidelity was already below the floor)
    that the breaker avoided.
    """
    n = len(per_hop_fidelities)
    cb = LISM_CircuitBreaker(d_min, tau_v)
    for d in per_hop_fidelities:
        if cb.step(d)["tripped"]:
            break
    # ungoverned: how many hops ran below the floor (pure waste / drift)
    cum = 1.0
    zombie = 0
    for d in per_hop_fidelities:
        cum *= d
        if cum < d_min:
            zombie += 1
    executed = cb.hops
    return {
        "n_hops": n,
        "d_min": d_min,
        "tau_v": tau_v,
        "trip_hop": cb.trip_hop,
        "governed_hops_executed": executed,
        "hops_prevented": n - executed,
        "ungoverned_zombie_hops": zombie,
        "final_cumulative_governed": round(cb.cumulative, 6),
    }


def _load_cohort_d_per_hop():
    """Derive per-hop fidelities from the repo's real Cohort D mean-fidelity curve
    (cohort_D_decay.csv): d_i = meanD[depth] / meanD[depth-1]."""
    path = os.path.join(HERE, "appendix", "cohort_D_decay.csv")
    rows = list(csv.DictReader(open(path)))
    depths = [(int(r["hop_depth"]), float(r["mean_joint_fidelity_D"])) for r in rows]
    depths.sort()
    per_hop = []
    prev = 1.0
    for _, d in depths:
        per_hop.append(min(1.0, d / prev) if prev > 0 else 0.0)
        prev = d
    return per_hop


def _demo():
    bar = "=" * 78
    print(bar)
    print(" LISM_CircuitBreaker — governed vs ungoverned on the REAL Cohort D profile")
    print(bar)
    per_hop = _load_cohort_d_per_hop()
    for d_min in (0.10, 0.05):
        r = simulate(per_hop, d_min=d_min, tau_v=0)
        print("\n D_min = %.2f :" % d_min)
        print("   pipeline length ............ %d hops" % r["n_hops"])
        print("   breaker trips at hop ....... %s (cumulative fidelity fell below the floor)" % r["trip_hop"])
        print("   hops the breaker prevented . %d" % r["hops_prevented"])
        print("   'zombie' hops avoided ...... %d (would have run below the floor, ungoverned)" % r["ungoverned_zombie_hops"])
    print("\n Reading: without a floor, the pipeline keeps executing far past the point where")
    print(" its joint fidelity is usable. The breaker stops it — that is the difference between")
    print(" a governed swarm and a zombie network. Standard library only; $0; deterministic.")
    print(bar)


if __name__ == "__main__":
    _demo()
