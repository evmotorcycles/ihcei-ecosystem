#!/usr/bin/env bash
# keel/install.sh — put keel on this machine.
#
#   bash keel/install.sh
#
# Installs to ~/.local/bin/keel (or $KEEL_BIN). Nothing is downloaded, no
# account is made, nothing is sent anywhere.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
BIN="${KEEL_BIN:-$HOME/.local/bin}"

if ! command -v node >/dev/null 2>&1; then
  echo "keel needs node (version 18 or newer). Install it, or build the"
  echo "standalone binary instead:  python3 keel/build_exe.py --binary"
  exit 1
fi
MAJOR="$(node -p 'process.versions.node.split(".")[0]')"
if [ "$MAJOR" -lt 18 ]; then echo "keel needs node 18 or newer (found $MAJOR)"; exit 1; fi

python3 "$HERE/build_exe.py" >/dev/null
mkdir -p "$BIN"
cp "$HERE/dist/keel.cjs" "$BIN/keel.cjs"
printf '#!/bin/sh\nexec node "%s/keel.cjs" "$@"\n' "$BIN" > "$BIN/keel"
chmod +x "$BIN/keel"

POLICY="$HOME/.keel/policy.json"
if [ ! -f "$POLICY" ]; then
  mkdir -p "$HOME/.keel"
  cp "$HERE/policy.example.json" "$POLICY"
  echo "wrote a starter key to $POLICY"
fi

echo
echo "  keel is installed at $BIN/keel"
echo
echo "  Try:   keel key"
echo "         keel check \"According to a 2023 trial of 240 people in the UK, X fell 12%\""
echo
case ":$PATH:" in *":$BIN:"*) ;; *) echo "  NOTE: $BIN is not on your PATH yet."; echo;; esac
cat <<'NOTE'
  THE ONE THING THAT MATTERS
  Keel governs the actions handed to it. It cannot stop a program that never
  comes through it. Put it where the assistant has no other route — a
  container, or a network with no other way out — or you have installed advice
  with extra steps.
NOTE
