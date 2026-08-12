#!/usr/bin/env bash
# =============================================================================
# reproduce_all.sh -- ONE command to reproduce EVERY test across the Novora /
# IHCEI stack. No API keys, no network.
#
# Requires: python3, node (>=18), and the packages in requirements.txt. Most
# suites are pure stdlib; a handful are not, and without them the run fails with
# bare ModuleNotFoundError in seven places, which looks like a broken repository
# rather than a missing install. The preflight check below names what is missing.
#
#   bash reproduce_all.sh
#
# Exit code 0 = everything green. Non-zero = at least one suite failed (the name
# is printed). This is the single entrypoint any person or agent (Jules, Claude,
# CI) can run to verify the whole repository from scratch.
# =============================================================================
set -u
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1

pass=0; fail=0; FAILED=()
bar() { printf '%s\n' "------------------------------------------------------------------------"; }
run() { # run "<label>" <command...>
  local label="$1"; shift
  printf '  %-52s ' "$label"
  if "$@" >/tmp/repro_out 2>&1; then echo "PASS"; pass=$((pass+1));
  else echo "FAIL"; fail=$((fail+1)); FAILED+=("$label"); sed 's/^/      /' /tmp/repro_out | tail -8; fi
}
node_test() { node --test "$@"; }        # node:test suites
node_run()  { node "$1"; }               # custom harness scripts (self-exit)
py()        { python3 -m pytest -q "$@"; }

echo "========================================================================"
echo " NOVORA / IHCEI — full reproducibility run"
echo " python: $(python3 --version 2>&1 | tr -d '\n')   node: $(node --version)"
echo "========================================================================"

# --- preflight: name missing packages instead of failing seven suites cryptically
missing=$(python3 - <<'PY'
import importlib
need = {"numpy":"numpy","scipy":"scipy","pandas":"pandas","statsmodels":"statsmodels",
        "networkx":"networkx","sklearn":"scikit-learn","jax":"jax","openpyxl":"openpyxl"}
out = []
for mod, pkg in need.items():
    try:
        importlib.import_module(mod)
    except Exception:
        out.append(pkg)
print(" ".join(out))
PY
)
if [ -n "$missing" ]; then
  echo
  echo "  NOTE: these Python packages are missing: $missing"
  echo "        Install them first, or the suites that need them will FAIL on import:"
  echo "          python3 -m pip install -r requirements.txt"
  echo "        Everything else below still runs and is unaffected."
  echo
fi

bar; echo "  NERE / IHCEI kernel (Python)"; bar
run "ihcei_v3: NERE/IHCEI kernel"        py ihcei_v3/test_ihcei_nere_v3.py
run "ihcei_v3: fast/deep extractor seam" py ihcei_v3/test_deep_seam.py
run "ihcei_v3: 4D bias engine"           py ihcei_v3/test_four_d_bias.py
run "tests: tau_v hazard monitor"        py tests/test_tau_v_monitor.py

bar; echo "  HELM / Page Code / Echo / cross-stack (Node)"; bar
run "novora-helm: core + parity + prereg + contribution" node_test novora-helm/test/helm.test.mjs novora-helm/test/parity.test.mjs novora-helm/test/prereg.lock.test.mjs novora-helm/test/contribution.test.mjs
run "page-code: permission table + change audit" node_test page-code/pagecode.test.mjs
run "echo: hash-chain + scam taxonomy"   node_test echo/echo.test.mjs echo/scam_taxonomy.test.mjs
run "cross-stack: integration + github pilot" node_test cross-stack/integration.test.mjs cross-stack/github_pilot.test.mjs

bar; echo "  Novora suite / PAGES (Node)"; bar
run "novora-suite: suite + screen + ui + backend" node_test novora-suite/test/suite.test.mjs novora-suite/test/screen_endpoint.test.mjs novora-suite/test/ui_endpoint.test.mjs novora-suite/test/backend.test.mjs
run "novora-improvement: PAGES confidence/abstain (agency+security)" node_test novora-improvement/pages_confidence.test.mjs

bar; echo "  EI / EI-LLM (Node)"; bar
run "ei: whole contract on real GitHub data (17 checks)" node_run ei/ei.test.mjs
run "ei: adversarial edge cases"         node_test ei/ei_adversarial.test.mjs
run "ei-llm: 8-model unit suite"         node_test ei-llm/ei-llm.test.mjs
run "ei-llm: field harness (real 22-repo cohort)" node_run ei-llm/field_test.mjs

bar; echo "  Understanding & control tests (Node)"; bar
run "Hinton 'Grand Canyon' test (8 tools)" node_run hinton-test/hinton_test.mjs
run "Russell 'Gorilla Problem' control test" node_run russell-test/russell_test.mjs
run "EI + 8 models: Hinton & Russell (pre-registered)" node_run ei-tests/ei_hinton_russell.mjs
run "benchmark-governance: HLE/ARC/FrontierMath (pre-registered)" node_run benchmarks-governance/bench_governance.mjs
run "hf-cohort: real HF models audited by the stack (pre-registered)" node_test hf-cohort/hf.test.mjs
run "hf-cohort: digital-swarm E=U*D + revocation tau_v (pre-registered)" py hf-cohort/swarm/test_hf_swarm.py
run "hf-media: PAGES governance over real video/audio-gen cohort (pre-registered)" node_test hf-media/hf_media.test.mjs
run "validation stage 1&2: evasive + emergency (pre-registered)" node_run validation-stages/stage12_screen.mjs
run "validation stage 3: swarm fidelity N>=434 (pre-registered)" py validation-stages/test_stage3.py

bar; echo "  ADG / TQG / LISM / QG-COS telemetry (Python)"; bar
run "adg-tqg: experiment + Wolfram/Hoffman" py adg-tqg/test_experiment.py adg-tqg/test_wolfram_hoffman.py
run "hoffman-agents: conscious-agent FBT + LISM + tau_v (pre-registered)" py hoffman-agents/test_hoffman.py
run "colab-tests: run-elsewhere reproduction hash (pre-registered)" py colab-tests/test_colab.py
run "gilt: irreducibility tipping-point (real sim, pre-registered)" py gilt/test_gilt.py
run "det-telemetry: generator/evaluator decoupling law (pre-registered)" py det-telemetry/test_det.py
run "two-regime: soft-linear / hard-threshold / serial-quadratic on real GitHub (pre-registered)" py two-regime/test_two_regime.py
run "det-cohorts: D>=Dmin binary-gate cohorts on GitHub/PubMed/HF (pre-registered)" py deterministic-cohorts/test_det_cohorts.py
run "agency-discovery: AlphaAgency verified allocator + honest limitation (pre-registered)" py agency-discovery/test_agency.py
run "agency-substrates: triage-first methodology on real GitHub/PubMed/HF/bioRxiv (pre-registered)" py agency-substrates/test_substrates.py
run "adversarial-kernel: dF_out/dF_gen=0 — safety kernel rejects hallucinated gains (pre-registered)" py adversarial-kernel/test_kernel.py
run "agency-constitution: 3-law allocator beats naive+triage on GitHub/HF; Law-2-in-objective falsified (pre-registered)" py agency-constitution/test_constitution.py
run "biomedical-agency: 4 telemetry laws on real yeast/PubMed/bioRxiv/GitHub (OQM case study, firewalled, pre-registered)" py biomedical-agency/test_biomedical.py
run "bell-telemetry: Bell/CHSH nonlocality as device-independent telemetry (classical 2, quantum 2√2, PR-box rejected)" py bell-telemetry/test_bell.py
run "knowledge-breakthroughs: status vs fidelity on real GitHub/HF/bioRxiv/PubMed — thesis FALSIFIED, null locked" py knowledge-breakthroughs/test_knowledge.py
run "cohort-audit: Yeast 4825 / GitHub 992 / swarm evidentiary audit — gaps + simulations locked" py cohort-audit/test_cohort_audit.py
run "cohort-audit: gap closure — yeast outcome + GitHub 992 CLOSED (rows committed)" py cohort-audit/test_gap_closure.py
run "cohort-audit: N=992 independent re-analysis — summary recomputes from raw rows" py cohort-audit/test_992.py
run "ei-dashboards: ASSAY — real stack over real Qwen+DeepSeek repos + offline dashboards" node_test ei-dashboards/assay.test.mjs
run "cairn: EI engine + Hinton Grand Canyon test (anti-overclaim control locked)" py cairn/test_ei_llm.py
run "cairn: the handles — a 5/5 fabrication still hands over what kills it" py cairn/test_handles.py
run "cairn: the handles reach the screen in both browser apps" py cairn/test_handles_gui.py
run "cairn CI: centric intelligence on real Qwen+DeepSeek — calibration gate FALSIFIED, locked" py cairn/test_ci.py
run "safety-coverage: does the warning fire? baseline 61% miss -> 4% on a sealed set" py safety-coverage/test_coverage.py
run "weir: the gate — refused requests provably never reach upstream" node_test weir/weir.test.mjs
run "weir: control panel agrees with the gate on every path and method" node_test weir/panel_parity.test.mjs
run "weir: the stop card — a refusal to guess renders as a result, not a crash" py weir/test_stop.py
run "governance-os: structural test — interposition real, mandatory routing still missing" node_test governance-os/os.test.mjs
run "launcher: the front door — every link opens, no jargon reaches it" py test_launcher.py
run "layers: IHCEI/NERE stay infrastructure; the desks stay jargon-free" py test_layers.py
run "growth-study: composition by era + whether the evidence exists (pre-registered)" py growth-study/test_growth.py
run "governance-learning: 6 obligations inside a learner (pre-registered)" py governance-learning/test_gla.py
run "readers: documents, data, code, transcripts — every reader declares its blind spots" node_test readers/readers.test.mjs
run "website: self-contained, links resolve, limits and failed gate on the page" py website/test_website.py
run "novora-suite: browser bundle parity with the tested engine (9 products)" node_test novora-suite/test_bundle_parity.mjs
run "novora-suite: offline nine-product GUI — abstains, no network, no key" py novora-suite/test_suite_html.py
run "cairn: browser engine parity with the audited Python engine (20 cases)" py cairn/test_parity.py
run "cairn: plain-language browser app — offline, measured numbers, limits kept" py cairn/test_plain.py
run "plumb: governance language semantics + out-of-sample cohort B (pre-registered)" py plumb/test_plumb.py
run "plumb: governance obligations inside ordinary Python (RT vs Governance)" py plumb/test_governance.py
run "plumb: the handles obligation — a count never travels without what it counted" py plumb/test_handles.py
run "biorxiv-lism: tau_v publication-latency law on real bioRxiv (pre-registered)" py biorxiv-lism/test_biorxiv.py
run "pubmed-lism: retraction failure-burden concentration on real PubMed (pre-registered)" py pubmed-lism/test_pubmed.py
run "github-lism: engagement + backlog heavy-tail on real GitHub cohort (pre-registered)" py github-lism/test_github.py
run "openalex-lism: pre-registered NULL (locked gate not met, zero-inflated) reported honestly" py openalex-lism/test_openalex.py
run "text-channel: pre-registered textual claims — 1 untestable, 1 marginal, 1 not operationalised" py text-channel/test_text_channel.py
run "qg-cos: 5 questions + Iqra + Nafs/Iblees" py qg-cos/test_five_questions.py qg-cos/test_iqra_channel.py qg-cos/test_nafs_iblees.py
run "repro: tau_v + yeast + CI attest"   py repro/test_reproduce.py
run "lism-cohorts: 4-cohort E=U*D meta (pre-registered)" py lism-cohorts/test_meta_lism.py
run "knowledge cohort: Barakah SE reproduces OFFLINE" py repro/test_se_offline.py
run "LISM circuit breaker: drop-in agent-pipeline guard" py lism-cohorts/test_circuit_breaker.py
run "hardware template: coupler-sweep prediction (no fabrication)" py hardware_interfaces/test_mock_willow_sweep.py
run "provenance: cryptographic origin lock verifies" py provenance/test_provenance.py
run "financial-system: Mudaraba Ledger + Sabbath Lock" py financial-system/test_financial_system.py
run "financial-system: Sovereign Mesh Telemetry" py financial-system/test_sovereign_mesh_telemetry.py

bar; echo "  Physics-agency: Telemetric Metric (Python)"; bar
run "physics: metric + scaling + discriminator" py physics-agency/test_telemetric_metric.py
run "physics: emergent spacetime"        py physics-agency/test_emergent_spacetime.py
run "physics: telemetry machines (F=ma/E=mc2)" py physics-agency/test_telemetry_machines.py
run "physics: 3D coordinate emergence"   py physics-agency/test_telemetric_3d.py
run "physics: pre-registered locked run" py physics-agency/prereg/test_prereg.py
run "physics: LMD spacetime-verdict-matrix (pre-registered)" py physics-agency/lmd/test_lmd.py
run "physics: LMD vs 4 emergent-spacetime theories (honest)" py physics-agency/lmd/comparison/test_comparison.py

echo
echo "========================================================================"
if [ "$fail" -eq 0 ]; then
  echo " ALL GREEN — $pass/$((pass+fail)) suites passed. The whole stack reproduces."
else
  echo " $pass/$((pass+fail)) suites passed; $fail FAILED: ${FAILED[*]}"
fi
echo "========================================================================"
exit "$fail"
