#!/usr/bin/env bash
# =============================================================================
# install.sh -- set Weir up on this machine.
#
#   bash weir/install.sh
#
# There is nothing to download and nothing to sign up for. This checks you have
# what you need, writes you a key you can edit in a text editor, and tells you
# the one thing that matters: WHERE to put the gate so it cannot be walked
# around.
# =============================================================================
set -u
cd "$(dirname "$0")/.."
KEY="${1:-$HOME/.weir/key.json}"

echo "Weir — the gate your assistant crosses"
echo "======================================"

if ! command -v node >/dev/null 2>&1; then
  echo "  node is not installed. Weir needs node 18 or newer."
  echo "  Install it, then run this again."
  exit 1
fi
MAJOR=$(node -p "process.versions.node.split('.')[0]")
if [ "$MAJOR" -lt 18 ]; then
  echo "  node $(node -v) is too old. Weir needs 18 or newer."; exit 1
fi
echo "  node $(node -v)  ok"

mkdir -p "$(dirname "$KEY")"
if [ -f "$KEY" ]; then
  echo "  a key already exists at $KEY — leaving it alone"
else
  cp weir/key.example.json "$KEY"
  echo "  wrote you a starter key at $KEY"
fi

echo
echo "  Check it works:"
echo "      node --test weir/weir.test.mjs"
echo
echo "  Open the control panel (no server needed):"
echo "      weir/panel.html"
echo
echo "  Run the gate:"
echo "      node weir/weir.mjs --key $KEY --upstream <where your files are> --port 8080"
echo "  then point your assistant at http://127.0.0.1:8080"
echo
echo "  THE ONE THING THAT MATTERS"
echo "  --------------------------"
echo "  A gate only works if there is no way round it. Point the assistant here AND"
echo "  make sure it has no other route — run it in a container with no direct network,"
echo "  or behind a firewall rule that only allows this port. Weir cannot do that for"
echo "  you, and without it an assistant that ignores the proxy is unaffected."
