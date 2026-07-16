// ei.mjs — Epistemological Intelligence: the unifying governance layer.
// ============================================================================
// EI is not a new model and not "AI safety." It is an independent, receiver-side
// EPISTEMOLOGICAL layer that sits between models, humans, and nodes and answers
// verifiable questions — is this claim grounded? is this delegation in-bounds?
// is the human still growing or hollowing? is the record intact? — WITHOUT ever
// censoring or mutating the token stream. It informs and calibrates human
// judgment; final release stays with the human. Non-suppressive by construction.
//
// EI is a COMPOSITION of primitives already tested elsewhere in this repo — it
// adds no new unproven engine, it wires the proven ones into one contract:
//
//   AUDIT    — the NERE corroboration gate (helm-core / page-code): fidelity,
//              methodology, grounding; a mechanism opens the gate, pressure alone
//              does not. Returns a calibrated posterior, never a censored output.
//   DELEGATE — a stake-bounded, revocable permission table (page-code): the OAuth
//              of agency; default-deny; payments/auth/CI off-limits.
//   DEVELOP  — the capacity meter (novora-helm): measures the say-do of the HUMAN
//              (ΔA) — verifying vs blindly accepting — and injects cognitive
//              friction when the trajectory turns to substitution.
//   PROVE    — a hash-chained receipt into Echo: every decision is attested and
//              tamper-evident.
//   HAZARD   — the LISM τ_v + Dissonance σ compass: throttle when a queue's
//              enforcement latency drifts above its own baseline.
//
// Everything is on-device, $0 marginal, no network (privacy by topology).

import { audit as auditText } from '../novora-helm/src/helm-core.mjs';
import { auditChange, CodePermissionTable } from '../page-code/pagecode.mjs';
import { CapacityTracker } from '../novora-helm/src/primitives.mjs';
import { EchoDB } from '../echo/echo.mjs';
import { reposOf, dissonance, thirdLawDirection } from '../cross-stack/lism_diagnostic.mjs';

export class EI {
  constructor({ frictionFloor = 0.5 } = {}) {
    this.permissions = new CodePermissionTable();       // DELEGATE
    this.capacity = new CapacityTracker();              // DEVELOP
    this.ledger = new EchoDB({ auditor: t => {          // PROVE
      const r = JSON.parse(t);
      return { verdict: r.verdict, p_manipulative: r.p, mechanismPresent: r.mechanism, mechanism_lexicon: r.lexicon };
    } });
    this.frictionFloor = frictionFloor;
  }

  // Convenience pass-throughs so callers grant/revoke on the same table.
  grant(rule) { return this.permissions.grant(rule); }
  revoke(id) { return this.permissions.revoke(id); }

  // ── AUDIT: epistemic fidelity of a text OR a code change ───────────────────
  audit({ text, change } = {}) {
    if (change) {
      const a = auditChange(change);
      return { verdict: a.verdict, p: a.mechanism_present ? 0.9 : 0.05, mechanism: a.mechanism_present,
        lexicon: a.mechanism_lexicon, mechanisms: a.mechanisms, reason: a.reason, domain: 'code' };
    }
    const a = auditText(text || '');
    return { verdict: a.verdict, p: a.p_manipulative, ci95: a.ci95, mechanism: a.mechanismPresent,
      lexicon: a.mechanism_lexicon, reason: (a.correction || null), domain: 'text' };
  }

  // ── DELEGATE: is this agent action within its stake-bounded grant? ─────────
  delegate({ agent, path, action = 'edit', stake = 0 } = {}) {
    return this.permissions.check({ agent, path, action, stake });
  }

  // ── DEVELOP: record the human's engagement, measure ΔA, inject friction ────
  develop(signal = {}) {
    this.capacity.record(signal);
    const rep = this.capacity.report();
    const friction = rep.developmentScore != null &&
      (rep.developmentScore < this.frictionFloor || rep.trend === 'substituting');
    return {
      developmentScore: rep.developmentScore, trend: rep.trend, n: rep.n,
      inject_friction: friction,
      prompt: friction
        ? 'Before releasing: explain the structural logic in your own words, or write the core yourself.'
        : null,
    };
  }

  // ── HAZARD: τ_v + σ compass over a queue/cohort; throttle when elevated ────
  hazard(cohort) {
    const repos = reposOf(cohort);
    const { rows } = dissonance(repos);
    const zombies = rows.filter(r => r.label === 'ZOMBIE').map(r => r.repo);
    const dir = thirdLawDirection(repos);
    // Throttle if any node's say-do dissonance is a zombie (loud-alive, rotting queue).
    return { throttle: zombies.length > 0, zombies, rows, third_law: dir };
  }

  // ── evaluate: run the whole EI contract on one interaction, attest it ──────
  // Returns a unified, NON-SUPPRESSIVE verdict; `release` is advisory — the
  // human decides. Every evaluation is hash-chained into the receipt ledger.
  evaluate({ text, change, agent, path, action = 'edit', stake = 0, engagement = {} } = {}) {
    const audit = this.audit({ text, change });
    const delegate = (agent && path) ? this.delegate({ agent, path, action, stake }) : null;
    const develop = this.develop(engagement);

    // Advisory release gate (informs; does not censor):
    //   hold if the content itself is BLOCK, or the action isn't permitted.
    const blocked = audit.verdict === 'BLOCK';
    const denied = delegate && delegate.decision === 'deny';
    const release = !blocked && !denied ? 'release' : 'hold-for-human';
    const reasons = [];
    if (blocked) reasons.push('AUDIT: ' + audit.reason);
    if (denied) reasons.push('DELEGATE: ' + delegate.reason);
    if (develop.inject_friction) reasons.push('DEVELOP: ' + develop.prompt);

    // PROVE: attest the decision.
    const receipt = this.ledger.put('ei-decision', JSON.stringify({
      verdict: audit.verdict, p: audit.p, mechanism: audit.mechanism, lexicon: audit.lexicon,
    }), { agent, path, action, release, denied: !!denied });

    return { release, audit, delegate, develop, reasons, receipt_id: receipt.id };
  }

  // Whole-history integrity of the attestation ledger.
  verify() { return this.ledger.verify(); }
  receipts() { return this.ledger.records; }
}
