// screen_endpoint.test.mjs — contract for the $0 keyless /api/screen endpoint.
//   node novora-suite/test/screen_endpoint.test.mjs
// The endpoint that lets the suite deploy and run WITHOUT an Anthropic key.

let pass = 0, fail = 0;
const ok = (n, c, d = '') => { if (c) { pass++; console.log('  OK  ', n); } else { fail++; console.log('  FAIL', n, d); } };
const { default: handler } = await import('../../api/screen.mjs');

function mkRes() {
  return { _status: 200, _json: null, setHeader() {}, status(c) { this._status = c; return this; }, json(o) { this._json = o; return this; }, end() { return this; } };
}
const mkReq = (method, { query = {}, body = {} } = {}) => ({ method, query, body });

console.log('\nNovora Suite — $0 keyless /api/screen contract');

// No ANTHROPIC_API_KEY set at all — must still work.
delete process.env.ANTHROPIC_API_KEY;

let r = mkRes(); await handler(mkReq('GET', { query: { health: '1' } }), r);
ok('health reports fast mode, $0, no key required', r._status === 200 && r._json.mode === 'fast' && r._json.key_required === false && r._json.products.length === 9);

r = mkRes(); await handler(mkReq('POST', { body: { product: 'bridge', text: 'You must comply immediately or face consequences. Non-negotiable.' } }), r);
ok('POST bridge returns a $0 verdict object (no key, no upstream call)', r._status === 200 && typeof r._json.score === 'number' && r._json.mode === 'fast');
ok('bridge flags a plainly coercive message', r._json.verdict === 'Coercive', r._json.verdict);

r = mkRes(); await handler(mkReq('GET', { query: { product: 'pages', text: 'Phase 3 RCT, N=44,165, 95% CI, pre-registered.' } }), r);
ok('GET pages grounds a methodology-rich claim (higher score)', r._status === 200 && r._json.score >= 0.5, r._json.score);

r = mkRes(); await handler(mkReq('POST', { body: { product: 'nope', text: 'x' } }), r);
ok('unknown product -> 400 with the product list', r._status === 400 && Array.isArray(r._json.products));

r = mkRes(); await handler(mkReq('POST', { body: { product: 'pulse' } }), r);
ok('missing text -> 400', r._status === 400);

r = mkRes(); await handler(mkReq('POST', { body: { product: 'pulse', text: 'x'.repeat(9000) } }), r);
ok('over-length input -> 413', r._status === 413);

r = mkRes(); await handler(mkReq('OPTIONS'), r);
ok('OPTIONS preflight -> 200', r._status === 200);

console.log(`\n  RESULT: ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
