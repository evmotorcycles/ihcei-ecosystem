// backend.test.mjs — contract test for the secure /api/analyse endpoint.
//   node novora-suite/test/backend.test.mjs
// ============================================================================
// The deployment guide flagged one real vulnerability in the prototype: the
// browser called api.anthropic.com directly, exposing ANTHROPIC_API_KEY to
// anyone with dev tools open. This build moved inference server-side. These
// tests verify the fix and the guardrails WITHOUT spending a paid token — the
// Anthropic call is stubbed, so we assert the request SHAPE the handler builds
// and that the key never appears in the client-visible response.

import assert from 'node:assert';

let pass = 0, fail = 0;
const ok = (n, c, d = '') => { if (c) { pass++; console.log('  OK  ', n); } else { fail++; console.log('  FAIL', n, d); } };

process.env.ANTHROPIC_API_KEY = 'sk-ant-TEST-SECRET-should-never-reach-client';
process.env.NOVORA_FREE_PER_DAY = '3';
const { default: handler } = await import('../api/analyse.js');

// Minimal Express-like req/res doubles.
function mkRes() {
  return { _status: 200, _json: null, _headers: {}, statusCalled: false,
    setHeader(k, v) { this._headers[k] = v; },
    status(c) { this._status = c; this.statusCalled = true; return this; },
    json(o) { this._json = o; return this; }, end() { return this; } };
}
const mkReq = (method, body, ip = '1.2.3.4') => ({ method, body, headers: { 'x-forwarded-for': ip }, socket: { remoteAddress: ip } });

// Stub global fetch to capture the outbound Anthropic request (no network).
let lastFetch = null;
globalThis.fetch = async (url, opts) => {
  lastFetch = { url, opts };
  return { ok: true, status: 200, json: async () => ({ content: [{ type: 'text', text: '{"score":0.9,"verdict":"Solid"}' }] }), text: async () => '' };
};

console.log('\nNovora Suite — secure backend contract (/api/analyse)');

// 1 · OPTIONS preflight + non-POST rejected.
let r = mkRes(); await handler(mkReq('OPTIONS'), r);
ok('OPTIONS preflight returns 200 with CORS headers', r._status === 200 && r._headers['Access-Control-Allow-Methods']);
r = mkRes(); await handler(mkReq('GET'), r);
ok('GET is rejected 405 (POST-only endpoint)', r._status === 405);

// 2 · Happy path builds the correct upstream request.
r = mkRes(); lastFetch = null;
await handler(mkReq('POST', { text: 'Analyse this claim.', system: 'You are PAGES.' }), r);
ok('valid POST returns 200 and passes the model JSON through', r._status === 200 && r._json?.content?.[0]?.text);
ok('upstream call targets the Anthropic Messages API', lastFetch?.url === 'https://api.anthropic.com/v1/messages');
const body = JSON.parse(lastFetch.opts.body);
ok('server injects the current model (claude-sonnet-5 by default)', body.model === 'claude-sonnet-5', body.model);
ok('the user text and product system prompt are forwarded', body.messages[0].content === 'Analyse this claim.' && body.system === 'You are PAGES.');

// 3 · THE SECURITY PROPERTY — the API key lives only in the request header,
//     never in the client-visible response.
ok('API key is sent in the x-api-key header to Anthropic (server-side only)',
   lastFetch.opts.headers['x-api-key'] === process.env.ANTHROPIC_API_KEY);
const clientVisible = JSON.stringify(r._json) + JSON.stringify(r._headers);
ok('the secret key NEVER appears anywhere in the client-visible response', !clientVisible.includes('SECRET'));

// 4 · Input guards.
r = mkRes(); await handler(mkReq('POST', { text: 'hi' }), r);
ok('missing system prompt -> 400', r._status === 400);
r = mkRes(); await handler(mkReq('POST', { text: 'x'.repeat(9000), system: 's' }), r);
ok('over-length input (>8KB) -> 413', r._status === 413);
r = mkRes(); await handler(mkReq('POST', { text: 42, system: 's' }), r);
ok('non-string text -> 400', r._status === 400);

// 5 · Missing key is reported, not silently ignored.
const savedKey = process.env.ANTHROPIC_API_KEY; delete process.env.ANTHROPIC_API_KEY;
r = mkRes(); await handler(mkReq('POST', { text: 'a', system: 'b' }), r);
ok('missing ANTHROPIC_API_KEY -> 500 with a clear message', r._status === 500 && /API key/i.test(r._json.error));
process.env.ANTHROPIC_API_KEY = savedKey;

// 6 · Per-IP daily free cap (NOVORA_FREE_PER_DAY=3): the 4th call from one IP is 429.
const ip = '9.9.9.9';
let statuses = [];
for (let i = 0; i < 4; i++) { const rr = mkRes(); await handler(mkReq('POST', { text: 'q' + i, system: 's' }, ip), rr); statuses.push(rr._status); }
ok('4th request from the same IP hits the daily free cap (429)', statuses.slice(0, 3).every(s => s === 200) && statuses[3] === 429, statuses.join(','));

console.log(`\n  RESULT: ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
