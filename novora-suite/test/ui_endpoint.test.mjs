// ui_endpoint.test.mjs — contract for api/ui.mjs (the function that serves the
// Novora UI at the domain root). node novora-suite/test/ui_endpoint.test.mjs
// ============================================================================
// project-6q4gj serves NO static files (API-only), so the bare domain `/` is
// rewritten to /api/ui, and api/ui.mjs returns the self-contained suite HTML.
// This regression-guards that contract IN THE REPO, so the fix can't silently
// break on a refactor (which is why the root kept "seeming" unfixed before).

let pass = 0, fail = 0;
const ok = (n, c, d = '') => { if (c) { pass++; console.log('  OK  ', n); } else { fail++; console.log('  FAIL', n, d); } };
const { default: handler } = await import('../../api/ui.mjs');

function mkRes() {
  return {
    _status: 200, _headers: {}, _body: '',
    setHeader(k, v) { this._headers[k.toLowerCase()] = v; },
    status(c) { this._status = c; return this; },
    send(b) { this._body = b; return this; },
    json(o) { this._body = JSON.stringify(o); return this; },
    end() { return this; },
  };
}

console.log('\nNovora Suite — api/ui.mjs serves the UI at the root');

const r = mkRes();
handler({ method: 'GET' }, r);
ok('returns 200', r._status === 200, String(r._status));
ok('Content-Type is text/html', /text\/html/.test(r._headers['content-type'] || ''), r._headers['content-type']);
ok('body is the Novora suite HTML', typeof r._body === 'string' && r._body.includes('<!DOCTYPE html>') && r._body.includes('Novora'));
ok('the page calls the $0 /api/screen backend', r._body.includes('/api/screen'));
ok('body is substantial (the full self-contained page)', r._body.length > 10000, r._body.length + ' bytes');

console.log(`\n  RESULT: ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
