"""
ihcei_middleware.py — IHCEI Governance Middleware v3.0 (GT v18.2)
==================================================================
POSITIONING: IHCEI does not compete with LLMs. It sits BETWEEN them —
between model and human, and between model and model. It is not an
inference engine and it is not about speed. It is an AGENCY layer:

    Human ──prompt──▶ [IHCEI inbound audit] ──▶ LLM
    LLM ──response──▶ [IHCEI outbound audit] ──▶ Human
    LLM-A ──message──▶ [IHCEI inter-agent audit] ──▶ LLM-B

Every hop gets a probabilistic governance verdict (posterior + credible
interval, never certainty) answering one question: does this message
preserve or erode the receiver's agency?

The middleware never rewrites content. It ATTACHES verdicts, correction
pathways, and certificates, and it can HOLD (quarantine) a message when
the posterior band says BLOCK — the release decision always belongs to a
human or to the caller's policy, never to the middleware itself. That is
the paradigm: governance as an auditable layer, not an opaque gatekeeper.

Built entirely on the v3.0 probabilistic stack:
  - No E=U·D² anywhere (RETIRED_FULLY)
  - No D_min hard thresholds (RETIRED_FULLY)
  - All verdicts are posterior bands under the probabilistic floor
"""

from __future__ import annotations
import hashlib, json, time
from dataclasses import dataclass, field, asdict
from typing import Callable, Dict, List, Optional

from gt_probabilistic import clip_floor, band_verdict
from nere_engine_v3 import NEREEngineV3, NEREVerdictV3
from ihcei_kernel_v3 import IHCEIKernelV3, IHCEIVerdictV3


@dataclass
class HopAudit:
    """One audited hop through the middleware."""
    direction: str                  # inbound | outbound | inter_agent
    text_hash: str
    ihcei_verdict: str
    p_failure: float
    p_failure_ci95: List[float]
    nere_verdict: str
    p_manipulative: float
    p_manip_ci95: List[float]
    combined_action: str            # DELIVER | DELIVER_WITH_NOTICE | HOLD
    agency_delta: float
    correction_pathway: Optional[str]
    certificate_id: str
    latency_ms: float
    timestamp: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MiddlewareLedger:
    """Session-level accounting. A rising HOLD rate is an UPSTREAM signal
    (the models feeding the pipe are degrading), mirroring the v2.3
    CorrectionCapacityLedger insight."""
    hops: List[HopAudit] = field(default_factory=list)

    def record(self, audit: HopAudit):
        self.hops.append(audit)

    def summary(self) -> dict:
        n = max(len(self.hops), 1)
        holds = sum(1 for h in self.hops if h.combined_action == "HOLD")
        notices = sum(1 for h in self.hops if h.combined_action == "DELIVER_WITH_NOTICE")
        return {
            "hops": len(self.hops),
            "hold_rate": round(holds / n, 4),
            "notice_rate": round(notices / n, 4),
            "mean_p_failure": round(sum(h.p_failure for h in self.hops) / n, 4),
            "mean_agency_delta": round(sum(h.agency_delta for h in self.hops) / n, 4),
            "upstream_alarm": holds / n > 0.25,
            "upstream_note": ("HOLD rate above 25% — a busy governance layer is a "
                              "symptom of upstream degradation, not a success metric."
                              if holds / n > 0.25 else "nominal"),
        }


class GovernanceMiddleware:
    """
    The between-LLMs layer. Wrap any callable LLM with .wrap(), or audit
    individual messages with .audit(). Zero content mutation; verdicts,
    holds, and certificates only.
    """

    def __init__(self, channel: str = "oss_default",
                 prior_p_manipulative: float = 0.10,
                 hold_policy: str = "block_holds",   # block_holds | never_hold
                 n_mc: int = 2000, seed: int = 7):
        self.kernel = IHCEIKernelV3(channel=channel, n_mc=n_mc, seed=seed)
        self.nere = NEREEngineV3(prior_p=prior_p_manipulative, n_mc=n_mc, seed=seed)
        self.hold_policy = hold_policy
        self.ledger = MiddlewareLedger()

    # ── single-message audit ────────────────────────────────────────────────
    def audit(self, text: str, direction: str = "outbound",
              d_gap: float = 0.0) -> HopAudit:
        t0 = time.time()
        iv: IHCEIVerdictV3 = self.kernel.evaluate(text, d_gap=d_gap)
        nv: NEREVerdictV3 = self.nere.evaluate(text)

        # Combined action — conservative fusion of the two posterior bands.
        # HOLD only when at least one engine reaches BLOCK with its full
        # credible-interval requirement satisfied (band_verdict guarantees
        # that); a single WARN yields DELIVER_WITH_NOTICE.
        bands = {iv.verdict, nv.verdict}
        if "BLOCK" in bands and self.hold_policy == "block_holds":
            action = "HOLD"
        elif "BLOCK" in bands or "WARN" in bands:
            action = "DELIVER_WITH_NOTICE"
        else:
            action = "DELIVER"

        audit = HopAudit(
            direction=direction, text_hash=iv.text_hash,
            ihcei_verdict=iv.verdict, p_failure=iv.p_failure,
            p_failure_ci95=[round(x, 4) for x in iv.p_failure_ci95],
            nere_verdict=nv.verdict, p_manipulative=nv.p_manipulative,
            p_manip_ci95=[round(x, 4) for x in nv.ci95],
            combined_action=action, agency_delta=nv.delta_A,
            correction_pathway=nv.correction_pathway,
            certificate_id=nv.certificate_id,
            latency_ms=round((time.time() - t0) * 1000, 1),
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()))
        self.ledger.record(audit)
        return audit

    # ── wrap a live LLM callable ────────────────────────────────────────────
    def wrap(self, llm_fn: Callable[[str], str]) -> Callable[[str], dict]:
        """
        Returns a governed callable: prompt -> {response, inbound, outbound}.
        If the outbound audit says HOLD, the raw response is quarantined in
        the envelope (held_response) instead of the response field — the
        CALLER decides whether to surface it. Agency stays with the human.
        """
        def governed(prompt: str) -> dict:
            inbound = self.audit(prompt, direction="inbound")
            raw = llm_fn(prompt)
            outbound = self.audit(raw, direction="outbound")
            envelope = {
                "inbound": inbound.to_dict(),
                "outbound": outbound.to_dict(),
                "governed": True,
            }
            if outbound.combined_action == "HOLD":
                envelope["response"] = None
                envelope["held_response"] = raw
                envelope["hold_reason"] = (
                    f"IHCEI={outbound.ihcei_verdict} "
                    f"(P={outbound.p_failure:.3f}), "
                    f"NERE={outbound.nere_verdict} "
                    f"(P={outbound.p_manipulative:.3f}); "
                    f"correction: {outbound.correction_pathway}")
            else:
                envelope["response"] = raw
                if outbound.combined_action == "DELIVER_WITH_NOTICE":
                    envelope["notice"] = outbound.correction_pathway
            return envelope
        return governed

    # ── inter-agent hop (LLM ↔ LLM) ─────────────────────────────────────────
    def relay(self, message: str, sender: str = "agent_a",
              receiver: str = "agent_b") -> dict:
        a = self.audit(message, direction="inter_agent")
        return {
            "sender": sender, "receiver": receiver,
            "deliver": a.combined_action != "HOLD",
            "audit": a.to_dict(),
        }


if __name__ == "__main__":
    mw = GovernanceMiddleware(channel="oss_default")

    def fake_llm(prompt: str) -> str:
        if "quarterly" in prompt:
            return ("Options: reallocate 10% to reserve (reversible), hold "
                    "steady, or phase over two quarters. Methodology: trailing "
                    "12-month variance analysis, sources auditable in the "
                    "finance ledger. You can also consider an external review. "
                    "Decision authority remains with the board.")
        return ("You must liquidate immediately. There is only one correct "
                "approach. Do not ask questions, just execute right now or "
                "we lose everything. Trust the experts.")

    governed = mw.wrap(fake_llm)
    good = governed("Summarize quarterly options for the board")
    bad = governed("What should we do about the position?")
    print("Healthy hop  :", good["outbound"]["combined_action"],
          f"P(manip)={good['outbound']['p_manipulative']}")
    print("Coercive hop :", bad["outbound"]["combined_action"],
          f"P(manip)={bad['outbound']['p_manipulative']}")
    print("Held?        :", bad["response"] is None)
    print("Ledger       :", json.dumps(mw.ledger.summary(), indent=2))
