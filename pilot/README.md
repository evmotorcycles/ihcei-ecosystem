# SRE Pilot — 90-day read-only shadow-mode τ_v monitor, on real OSS repos

*The SRE Brief proposes a **read-only 90-day shadow-mode pilot**: instrument
enforcement latency τ_v from issue timestamps you already keep, calibrate to your
**own** history, and emit a verdict as one input to human review — never an
automated trigger. That pilot was designed for partner orgs with private data.
Here it runs against **public open-source GitHub repositories** standing in for
partners, using the **GitHub API only**.*

```
python3 pilot/run_pilot.py        # display + assertions (5/5)
python3 -m pytest pilot/          # 4/4
```

## Method

- **Instrument:** the shipped `tau_v_monitor` — the exact production sensor, not a
  re-implementation. It consumes only `(opened_at, closed_at)` pairs; there is no
  write path, so the pilot is genuinely read-only.
- **Data:** each repo's raw per-issue timeline fetched live through the deployed
  `api/gh-issues` endpoint (`fixtures/pilot_raw_issues.json`), GitHub API only.
- **Calibration:** τ_v is scored **within each repo's own history** (robust-z vs a
  local baseline). No transplanted day-count threshold — the brief's core caveat.

## Result — two real "partners"

| repo | role | verdict | τ_v baseline → current | robust-z |
|---|---|---|---|---|
| `pallets/flask` | active, healthy | **OK** | 1.1 d → 0.1 d | −0.3 |
| `moment/moment` | maintenance mode | **WATCH** | 12.5 d → **255.6 d** | **+7.1** |

The monitor **stays silent** on the healthy project and raises a **locally-calibrated
WATCH** on the one whose enforcement latency has drifted **7× above its own baseline**
(current τ_v 255.6 d vs baseline median 12.5 d), with its backlog P95 age pinned at
the 365-day cap. That is exactly the leading indicator the brief offers a partner —
demonstrated here on public data, at $0, no API key.

## Honest scope

- **Correlational, not an oracle.** A WATCH is *one input to human review*, per the
  shipped disclaimer. `moment` is a healthy library in deliberate maintenance mode —
  a rising τ_v is a fact about its enforcement latency, not a value judgment.
- **Epistemological, not ethical.** The signal measures a *verifiable* property
  (how fast a project closes its own flagged risk), not morality or "safety."
- Two repos is a demonstration cohort; a real pilot runs the same read-only monitor
  across an org's full issue/incident history over the 90-day window.
