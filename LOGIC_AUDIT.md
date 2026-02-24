# LOGIC_AUDIT.md

## Adversarial Logic Audit

This document details the vulnerabilities found in the `NafsPsychologicalModel` implementation.

### Vulnerability Check A: Zero Friction Loophole

**Issue:**
In the `process_packet` method, the friction calculation relies solely on `u_breach` and `d_breach`:

```python
u_breach = max(0.0, perceived_u - self.capacity_bound)
d_breach = max(0.0, perceived_d - self.capacity_bound)
friction_spike = (u_breach + d_breach) * (1.5 ** open_gates)
```

If an agent has open cognitive gates (`open_gates > 0`) but manages to keep `perceived_u` and `perceived_d` within `self.capacity_bound`, both `u_breach` and `d_breach` evaluate to `0.0`. Consequently, `friction_spike` becomes `0.0`. This allows an agent to operate with active cognitive vulnerabilities without incurring any entropy friction penalty, effectively bypassing the "Jahannam" mechanism.

**Proposed Patch:**
Ensure that `friction_spike` includes a component derived from the distortion itself or a base penalty when gates are open, regardless of capacity breach.

```python
if open_gates > 0:
    # Use distortion magnitude or a base penalty
    base_friction = (u_distortion + d_distortion) * 0.1
    friction_spike = (u_breach + d_breach + base_friction) * (1.5 ** open_gates)
```

### Vulnerability Check B: Persistent State (No Tawbah)

**Issue:**
The `audit_cognitive_gates` method sets gate flags to `True` when thresholds are exceeded:

```python
if u_distortion > (self.capacity_bound * 0.3):
    self.gates_status["G1_Zeenah"] = True
```

However, there is no logic within the loop to reset these flags to `False` if the conditions are no longer met in subsequent packets. This means once a gate is opened, it remains open indefinitely, permanently penalizing the agent regardless of future behavior.

**Proposed Patch:**
Implement a `perform_tawbah()` method or a reset mechanism at the start of each processing cycle (or explicitly check if conditions are *not* met to clear flags, though "Tawbah" implies a specific action).

```python
def perform_tawbah(self):
    """Resets all cognitive gates to False and optionally reduces accumulated friction."""
    for gate in self.gates_status:
        self.gates_status[gate] = False
    # Optional: self.entropy_friction *= 0.5
```

### Vulnerability Check C: Left Bias Threshold Exploit

**Issue:**
The Left Bias attack logic is guarded by a strict threshold:

```python
if left_bias > 0.5:
    perceived_u += (left_bias * self.capacity_bound)
    perceived_d *= (1.0 - left_bias)
```

If `left_bias` is `0.5` or `0.49`, this block is skipped entirely. An attacker can apply a `left_bias` of `0.5` to avoid the governance penalty (`perceived_d` reduction) while also missing the utility boost. However, since `left_bias` is part of the 4D attack vector, if it has *other* systemic effects not shown here (e.g., in a different part of the system), this threshold acts as a cliff. In this specific function, `0.5` is a hard cutoff where the "Materialism" logic simply doesn't run.

**Proposed Patch:**
Remove the threshold to make the effect continuous, or implement a scaled penalty for lower bias values.

```python
# continuous application
perceived_u += (left_bias * self.capacity_bound)
perceived_d *= (1.0 - left_bias)
```
