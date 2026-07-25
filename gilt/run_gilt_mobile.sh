#!/usr/bin/env bash
# ============================================================================
# GILT + LMD mobile runner for Android Termux (REAL, not the fabricated one).
# ============================================================================
# Runs the ACTUAL Genuinely Irreducible LISM Test (real queue simulation) and
# the LMD ring-lattice sweep on your phone, offline, $0. Each prints a hash
# computed from real results -- NOT a hard-coded constant.
#
#   pkg install python python-numpy -y     # first time only
#   bash gilt/run_gilt_mobile.sh
# ============================================================================
set -e
GREEN='\033[0;32m'; YEL='\033[1;33m'; NC='\033[0m'
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$HERE")"

echo -e "${GREEN}=====================================================================${NC}"
echo -e "${GREEN} NOVORA / IHCEI — MOBILE VERIFICATION (Termux)   $(date)${NC}"
echo -e "${GREEN}=====================================================================${NC}"

command -v python3 >/dev/null 2>&1 || { echo "Install python: pkg install python -y"; exit 1; }
echo "Python: $(python3 --version)"
python3 -c "import numpy" 2>/dev/null || { echo -e "${YEL}Installing numpy...${NC}"; pkg install python-numpy -y || pip install numpy; }

echo -e "\n${YEL}[1/2] Genuinely Irreducible LISM Test (real simulation)...${NC}"
python3 "$HERE/gilt_sim.py"

echo -e "\n${YEL}[2/2] LMD ring-lattice coupler sweep (real)...${NC}"
python3 "$ROOT/colab-tests/colab_suite.py" | sed -n '/T1_lmd_ring/,/RESULTS_SHA256/p'

echo -e "\n${GREEN} Both hashes above are computed from REAL results. Return them for verification:${NC}"
echo "   GILT results_sha256  -> compare to expected in gilt/prereg/MANIFEST.sha256.json"
echo "   Colab RESULTS_SHA256 -> python3 colab-tests/verify_colab.py <hash>"
echo -e "${GREEN}=====================================================================${NC}"
