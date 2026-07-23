#!/usr/bin/env bash
# =============================================================================
# reproduce_all.sh -- ONE command to reproduce EVERY test across the Novora /
# IHCEI stack. No API keys, no network. Requires: python3, node (>=18), pytest.
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
run "biorxiv-lism: tau_v publication-latency law on real bioRxiv (pre-registered)" py biorxiv-lism/test_biorxiv.py
run "qg-cos: 5 questions + Iqra + Nafs/Iblees" py qg-cos/test_five_questions.py qg-cos/test_iqra_channel.py qg-cos/test_nafs_iblees.py
run "repro: tau_v + yeast + CI attest"   py repro/test_reproduce.py
run "lism-cohorts: 4-cohort E=U*D meta (pre-registered)" py lism-cohorts/test_meta_lism.py
run "knowledge cohort: Barakah SE reproduces OFFLINE" py repro/test_se_offline.py
run "LISM circuit breaker: drop-in agent-pipeline guard" py lism-cohorts/test_circuit_breaker.py
run "hardware template: coupler-sweep prediction (no fabrication)" py hardware_interfaces/test_mock_willow_sweep.py
run "provenance: cryptographic origin lock verifies" py provenance/test_provenance.py

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
