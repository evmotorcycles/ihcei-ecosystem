#!/usr/bin/env python3
"""Payload Recovery — monitors the NERE v3.1 sensor run and prints the verdict.
Fixes vs. draft: (1) resolves the run from the sensor workflow specifically,
not the newest run of any workflow; (2) polls the pinned run ID so a cron or
other workflow starting mid-wait can't hijack tracking; (3) permission-aware
errors (artifact download needs Actions:read on fine-grained PATs)."""
import os, time, sys, io, json, zipfile
import requests

OWNER, REPO = "evmotorcycles", "ihcei-ecosystem"
WORKFLOW_FILE = "dgap_sensor.workflow.yml"   # filename in .github/workflows/
ARTIFACT_NAME = "dgap-sensor-results"
TARGET_FILE = "dgap_verdict.json"

TOKEN = os.environ.get("GOVPHYS_PAT")
if not TOKEN:
    print("ERROR: export GOVPHYS_PAT='your_token' first."); sys.exit(1)
H = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
API = f"https://api.github.com/repos/{OWNER}/{REPO}"

def gj(url):
    r = requests.get(url, headers=H, timeout=30)
    if r.status_code == 403:
        print(f"\n403 on {url}\nIf this is a fine-grained PAT, it needs "
              f"'Actions: read' permission for artifact/run access."); sys.exit(1)
    r.raise_for_status()
    return r.json()

# 1. Pin the newest run OF THIS WORKFLOW
runs = gj(f"{API}/actions/workflows/{WORKFLOW_FILE}/runs?per_page=1").get("workflow_runs", [])
if not runs:
    print(f"No runs found for workflow '{WORKFLOW_FILE}'. Did the dispatch start?"); sys.exit(1)
run_id = runs[0]["id"]
print(f"── Tracking run {run_id} ({runs[0].get('display_title','')}) ──")

# 2. Poll the pinned run ID
while True:
    run = gj(f"{API}/actions/runs/{run_id}")
    if run["status"] == "completed":
        break
    sys.stdout.write(f"\rStatus: {run['status'].upper()} ... polling every 30s ")
    sys.stdout.flush()
    time.sleep(30)

print(f"\nCompleted. Conclusion: {run['conclusion'].upper()}")
if run["conclusion"] != "success":
    print("Run did not succeed — check the Actions logs."); sys.exit(1)

# 3. Fetch + extract the verdict
arts = gj(run["artifacts_url"]).get("artifacts", [])
art = next((a for a in arts if a["name"] == ARTIFACT_NAME), None)
if not art:
    print(f"Artifact '{ARTIFACT_NAME}' not found. Available: {[a['name'] for a in arts]}"); sys.exit(1)
zr = requests.get(art["archive_download_url"], headers=H, timeout=120)
zr.raise_for_status()
with zipfile.ZipFile(io.BytesIO(zr.content)) as z:
    if TARGET_FILE not in z.namelist():
        print(f"{TARGET_FILE} missing; zip contains {z.namelist()}"); sys.exit(1)
    payload = json.load(z.open(TARGET_FILE))

print("\n" + "=" * 60)
print(f" FINAL VERDICT ({TARGET_FILE})")
print("=" * 60 + "\n")
print(json.dumps(payload, indent=2))
print("\n" + "=" * 60)
