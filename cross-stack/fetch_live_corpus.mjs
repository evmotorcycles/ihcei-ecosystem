// fetch_live_corpus.mjs — capture a fresh, real open-source prose corpus.
// ============================================================================
// Pulls live package metadata from the public npm and PyPI registries (both are
// on the sandbox no-proxy allow-list, so this is a genuine live fetch, not a
// replay). We keep the *descriptions* and *README summaries* — real human prose
// written by maintainers — as the substrate that flows through every engine in
// the cross-stack integration test (HELM/NERE gate, PAGES grounding, Page Code,
// Echo ingest, AIPS relay). Re-run to refresh; it rewrites the fixture with a
// new fetched_at so the snapshot is always attributable to a moment in time.
//
//   node cross-stack/fetch_live_corpus.mjs
//
// No API key, no auth, no GitHub — just the two open registries that ship the
// world's package prose.

import { writeFileSync } from 'node:fs';

// A cohort chosen to be ORDINARY: mainstream libraries whose descriptions are
// benign engineering prose. This is the honest false-positive test — the gate
// must stay silent across all of it. (Manipulation cases are injected in the
// test itself; here we only want real, un-cherry-picked maintainer text.)
const NPM = ['express', 'react', 'lodash', 'vue', 'axios', 'chalk', 'webpack',
  'eslint', 'jest', 'typescript', 'commander', 'debug', 'moment', 'fastify',
  'next', 'vite', 'rollup', 'prettier', 'zod', 'dotenv'];
const PYPI = ['requests', 'flask', 'numpy', 'pandas', 'django', 'pytest',
  'click', 'rich', 'fastapi', 'pydantic', 'httpx', 'scipy', 'pillow',
  'sqlalchemy', 'boto3'];

const firstSentences = (s, n = 3) =>
  String(s || '').replace(/\s+/g, ' ').split(/(?<=[.!?])\s+/).slice(0, n).join(' ').slice(0, 600);

async function npmOne(name) {
  const r = await fetch('https://registry.npmjs.org/' + name);
  if (!r.ok) throw new Error('npm ' + name + ' ' + r.status);
  const d = await r.json();
  const latest = d['dist-tags']?.latest;
  const v = d.versions?.[latest] || {};
  const readme = firstSentences(d.readme, 4);
  return { id: 'npm:' + name, registry: 'npm', name, version: latest,
    description: v.description || d.description || '', readme,
    homepage: v.homepage || '' };
}

async function pypiOne(name) {
  const r = await fetch('https://pypi.org/pypi/' + name + '/json');
  if (!r.ok) throw new Error('pypi ' + name + ' ' + r.status);
  const d = await r.json();
  const info = d.info || {};
  return { id: 'pypi:' + name, registry: 'pypi', name, version: info.version,
    description: info.summary || '',
    readme: firstSentences(info.description, 4),
    homepage: info.home_page || info.project_url || '' };
}

async function gather(names, one, label) {
  const out = [];
  for (const n of names) {
    try { out.push(await one(n)); process.stdout.write('.'); }
    catch (e) { process.stdout.write('x'); console.error('\n  ' + label + ' ' + n + ': ' + e.message); }
  }
  return out;
}

const npm = await gather(NPM, npmOne, 'npm');
const pypi = await gather(PYPI, pypiOne, 'pypi');
console.log();

const corpus = {
  description: 'LIVE real-world package prose from the public npm + PyPI registries ' +
    '(both on the sandbox no-proxy allow-list — a genuine live fetch). Maintainer-written ' +
    'descriptions + README opening sentences. Substrate for the cross-stack integration test: ' +
    'the HELM/NERE gate must stay silent on all of it (false-positive floor), and it flows ' +
    'through Echo, Page Code, PAGES and AIPS end-to-end.',
  fetched_at: new Date().toISOString(),
  sources: ['https://registry.npmjs.org/<pkg>', 'https://pypi.org/pypi/<pkg>/json'],
  n: npm.length + pypi.length,
  items: [...npm, ...pypi],
};
const path = new URL('fixtures/live_registry_corpus.json', import.meta.url);
writeFileSync(path, JSON.stringify(corpus, null, 1));
console.log('captured ' + corpus.n + ' real packages (' + npm.length + ' npm + ' + pypi.length + ' pypi) -> ' + path.pathname);
