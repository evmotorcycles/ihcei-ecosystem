// api/gh-proxy.js — read-only monitor for the NERE D_gap sensor runs.
// Two fixed operations only (NOT a pass-through proxy; arbitrary paths are rejected):
//   /api/gh-proxy?op=status   -> latest run of dgap_sensor.workflow.yml (id/status/conclusion)
//   /api/gh-proxy?op=verdict  -> dgap_verdict.json extracted from the latest successful run's artifact
// Requires env vars: GOVPHYS_PAT (Actions:read). Uses adm-zip (see package.json).

const AdmZip = require('adm-zip');

const BASE = 'https://api.github.com/repos/evmotorcycles/ihcei-ecosystem';
const WORKFLOWS = ['dgap_sensor.workflow.yml', 'dgap_actions_sensor.yml'];
const ARTIFACT = 'dgap-sensor-results';

async function latestRun(token, params = '') {
  for (const wf of WORKFLOWS) {
    try {
      const d = await gh(token, `${BASE}/actions/workflows/${wf}/runs?per_page=1${params}`);
      const run = (d.workflow_runs || [])[0];
      if (run) return run;
    } catch (e) { /* workflow file may not exist; try next */ }
  }
  return null;
}

async function gh(token, url, binary = false) {
  const r = await fetch(url, {
    headers: {
      Authorization: `token ${token}`,
      Accept: 'application/vnd.github.v3+json',
      'User-Agent': 'ihcei-gh-proxy',
    },
  });
  if (!r.ok) {
    const body = await r.text();
    throw new Error(`GitHub ${r.status} on ${url}: ${body.slice(0, 200)}`);
  }
  return binary ? Buffer.from(await r.arrayBuffer()) : r.json();
}

module.exports = async (req, res) => {
  const token = process.env.githubapi || process.env.GOVPHYS_PAT;
  if (!token) return res.status(500).json({ error: 'githubapi / GOVPHYS_PAT not configured' });

  const op = (req.query && req.query.op) || 'status';
  try {
    if (op === 'status') {
      const run = await latestRun(token);
      if (!run) return res.status(200).json({ runs: 0, note: 'no sensor workflow runs found' });
      return res.status(200).json({
        id: run.id, status: run.status, conclusion: run.conclusion,
        created_at: run.created_at, html_url: run.html_url,
      });
    }

    if (op === 'verdict') {
      const run = await latestRun(token, '&status=success');
      if (!run) return res.status(404).json({ error: 'no successful runs yet' });
      const arts = await gh(token, run.artifacts_url);
      const art = (arts.artifacts || []).find((a) => a.name === ARTIFACT);
      if (!art) {
        return res.status(404).json({
          error: `artifact '${ARTIFACT}' not found`,
          available: (arts.artifacts || []).map((a) => a.name),
        });
      }
      const zipBuf = await gh(token, art.archive_download_url, true);
      const zip = new AdmZip(zipBuf);
      const entry = zip.getEntry('dgap_verdict.json') || zip.getEntry('dgap_sensor_results.json');
      if (!entry) {
        return res.status(404).json({
          error: 'dgap_verdict.json missing from artifact',
          contents: zip.getEntries().map((e) => e.entryName),
        });
      }
      res.setHeader('Content-Type', 'application/json');
      return res.status(200).send(entry.getData().toString('utf8'));
    }

    return res.status(400).json({ error: "op must be 'status' or 'verdict'" });
  } catch (e) {
    return res.status(502).json({ error: String(e && e.message ? e.message : e) });
  }
};
