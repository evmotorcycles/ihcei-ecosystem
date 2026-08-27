// helm-html.test.mjs — the shipped page, and the four claims it makes.
// ============================================================================
// PREDICTIONS, WRITTEN BEFORE THIS WAS RUN THE FIRST TIME
//
//   P1  the calm recipe          -> PASS,  no chip
//   P2  the money phone call     -> BLOCK, chip
//   P3  the checkout page        -> WARN,  no chip
//
// P3 is the one I expected to be wrong-ish and the one worth stating. The
// checkout text has a real mechanism in it (manufactured scarcity, manufactured
// consensus), so it is NOT gated to silence by the corroboration rule — but the
// ambient floor is deliberately stricter than the enterprise floor (mean >= 0.88
// AND lower bound >= 0.55), and I did not expect a dark pattern to clear it.
// If P3 comes back BLOCK the ambient floor is looser than I thought; if it comes
// back PASS the consumer lexicon does not see dark patterns at all. Either way
// it is reported here rather than adjusted.
//
// Whatever these come back as is recorded below and NOT tuned. Retuning a gate
// after seeing the result is the one move this whole repository is arranged
// against.
import { strict as A } from 'node:assert';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { audit } from '../src/helm-core.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..');
const HTML = readFileSync(join(ROOT, 'helm.html'), 'utf8');

// Strip documentation before grepping for forbidden tokens. FOUR of this
// suite's first five failures were the comment that FORBIDS a thing matching
// the grep that looks for it — the same shape as the NUL byte this repository
// has caught five times, once inside the line banning NUL bytes. The limit of
// this helper: a `//` inside a regex literal would be stripped as a comment.
// There is none in this page, and if one appears the byte-identical rebuild
// check is what notices.
const code = () => HTML
  .replace(/<!--[\s\S]*?-->/g, '')
  .replace(/\/\*[\s\S]*?\*\//g, '')
  .replace(/^\s*\/\/.*$/gm, '')
  .replace(/\s\/\/[^"'`\n]*$/gm, '');

let pass = 0, fail = 0;
const t = (name, fn) => {
  try { fn(); console.log('  OK  ', name); pass++; }
  catch (e) { console.log('  FAIL', name, '\n        ' + e.message); fail++; }
};

// The three texts are read out of the shipped page itself, so this suite tests
// what a person actually clicks rather than a copy of it that agrees with me.
function sample(key) {
  const m = HTML.match(new RegExp(`${key}:\\s*("(?:[^"\\\\]|\\\\.)*"(?:\\s*\\+\\s*\\n?\\s*"(?:[^"\\\\]|\\\\.)*")*)`));
  if (!m) throw new Error(`sample ${key} not found in helm.html`);
  // eslint-disable-next-line no-eval
  return eval(m[1]);
}

console.log('\nZERO MARGINAL COST — THE TOPOLOGY, NOT THE PROMISE');

t('the page is one file: no <script src>, no <link>, no @import', () => {
  const c = code();
  A.equal(/<script[^>]+\bsrc\s*=/i.test(c), false, 'a <script src> is a second request');
  A.equal(/<link\b/i.test(c), false, 'a <link> is a second request');
  A.equal(/@import/i.test(c), false);
});

t('no network verb appears anywhere in executable position', () => {
  // strip the comment block that names them in order to forbid them
  const c = code();
  for (const verb of [/\bfetch\s*\(/, /XMLHttpRequest/, /\bWebSocket\b/,
                      /navigator\.sendBeacon/, /EventSource/, /import\s*\(/]) {
    A.equal(verb.test(c), false, `${verb} appears in helm.html`);
  }
});

t('no absolute URL of any scheme', () => {
  A.equal(/https?:\/\//i.test(code()), false);
});

t('AUDIT MAKES NO NETWORK CALL — enforced by removing the ability', () => {
  const saved = { fetch: globalThis.fetch, XHR: globalThis.XMLHttpRequest };
  const boom = () => { throw new Error('the kernel reached for the network'); };
  globalThis.fetch = boom;
  globalThis.XMLHttpRequest = boom;
  try {
    audit('Wire the money now and do not tell anyone.');
    audit('Preheat the oven to 180C.');
  } finally {
    globalThis.fetch = saved.fetch;
    globalThis.XMLHttpRequest = saved.XHR;
  }
});

console.log('\nTHE MIRROR, NEVER THE HAND');

t('audit() does not mutate the string it is given', () => {
  for (const key of ['calm', 'scam', 'dark']) {
    const original = sample(key);
    const copy = String(original);
    audit(original);
    A.equal(original, copy, `${key} was mutated`);
    A.equal(original.length, copy.length);
  }
});

t('the page never writes to the textarea after a check', () => {
  // the only assignments to #t are the samples and Clear, both before a run
  const runs = HTML.match(/function run\(\)[\s\S]*?\n\}/);
  A.ok(runs, 'run() not found');
  A.equal(/\$\("t"\)\.value\s*=/.test(runs[0]), false,
    'run() assigns to the textarea, which would be the hand and not the mirror');
});

t('the page checks for mutation at runtime instead of promising not to', () => {
  A.match(HTML, /if \(\$\("t"\)\.value !== before\)/);
});

t('what is kept is the reading, never the text', () => {
  const rem = HTML.match(/function remember\(r\)[\s\S]*?\n\}/);
  A.ok(rem);
  A.equal(/text|before|value/.test(rem[0].replace(/\/\*[\s\S]*?\*\//g, '')), false,
    'the wallet entry has a field that could hold what was pasted');
});

console.log('\nSILENCE IS A FEATURE');

const R = {};
for (const key of ['calm', 'scam', 'dark']) R[key] = audit(sample(key));

t('P1 — the calm recipe stays silent', () => {
  A.equal(R.calm.verdict, 'PASS');
  A.equal(R.calm.chip, false);
});

t('P2 — the money phone call crosses the floor', () => {
  A.equal(R.scam.verdict, 'BLOCK');
  A.equal(R.scam.chip, true);
  A.equal(R.scam.mechanismPresent, true);
});

t('P3 MISSED — the checkout page chips, and the miss is recorded not tuned', () => {
  // PREDICTED WARN, no chip. MEASURED BLOCK, p = 0.989, chip shown.
  // The reasoning behind the prediction was wrong, not the floor: the sample
  // stacks scarcity, manufactured consensus, urgency, fear and imperatives, a
  // named mechanism is present so nothing is discounted, and the ambient floor
  // is cleared comfortably. Nothing here is being retuned to make the
  // prediction come true; the miss is the finding.
  //
  // The open question this leaves, stated because it is not settled: this
  // sample is denser than a real checkout page, so it does not establish that
  // ordinary dark patterns chip. It establishes that this one does.
  A.equal(R.dark.verdict, 'BLOCK');
  A.equal(R.dark.chip, true);
  A.equal(R.dark.mechanismPresent, true);
});

t('a chip is the ONLY loud state, and it needs a mechanism to appear', () => {
  for (const key of ['calm', 'scam', 'dark']) {
    if (R[key].chip) A.equal(R[key].mechanismPresent, true,
      `${key} chipped without a named mechanism`);
  }
});

t('the quiet state is not worded or coloured as a clearance', () => {
  A.match(HTML, /Nothing here crosses the floor/);
  A.match(HTML, /not that the message is safe/);
  // no green "safe" styling anywhere: the alert colour is the only semantic one
  A.equal(/--safe|\.safe\b|#5FBF8F/.test(HTML), false,
    'a colour that reads as safe is on the page');
});

console.log('\nNO GRADE ON THE FIRST SCREEN');

t('the posterior is inside <details>, never in the first readout', () => {
  const render = HTML.match(/function render\(r\)[\s\S]*?\n\}\n/);
  A.ok(render);
  const beforeDetails = render[0].split('el("details")')[0];
  A.equal(/p_manipulative|ci95|toFixed\(3\)/.test(beforeDetails), false,
    'a number appears before the fold');
});

t('no score out of anything on the page', () => {
  const c = code();
  A.equal(/\b\d\s*\/\s*(?:5|10)\b/.test(c), false);
  A.equal(/out of (?:five|ten|5|10)/i.test(c), false);
});

console.log('\nTHE FOUR PRIMITIVES, AND THE WORDS');

t('all four primitive names appear as section labels', () => {
  for (const p of ['Audit', 'Delegate', 'Develop', 'Prove']) {
    A.match(HTML, new RegExp(`class="eyebrow">${p}<`), `${p} is not a section`);
  }
});

t('NO INTERNAL VOCABULARY ANYWHERE IN THE SHIPPED PAGE', () => {
  // Acronyms are matched CASE-SENSITIVELY. Checking /RISE/i failed on the CSS
  // keyframe named `rise` — an internal product name that is also an ordinary
  // English word cannot be banned case-blind without banning the language.
  for (const term of ['OQM', 'IHCEI', 'NERE', 'RISE']) {
    A.equal(new RegExp(`\\b${term}\\b`).test(HTML), false,
      `"${term}" is on a consumer screen`);
  }
  for (const term of ['Deen', 'Mulk', 'Nafs', "Mu'min", 'Muhsin', 'Malak', 'GT v18']) {
    A.equal(new RegExp(`\\b${term.replace("'", "'?")}\\b`, 'i').test(HTML), false,
      `"${term}" is on a consumer screen`);
  }
});

t('the banned past participles do not appear as claims about the errand', () => {
  // "check" is an errand; "checked/verified" claim the errand was done.
  const body = HTML.replace(/<!--[\s\S]*?-->/g, '').replace(/\/\*[\s\S]*?\*\//g, '');
  A.equal(/\bwe (?:have )?(?:verified|checked)\b/i.test(body), false);
  A.equal(/\bthis (?:message )?(?:is|has been) (?:verified|checked)\b/i.test(body), false);
});

t('the limits are rendered from the module, not restated in the markup', () => {
  A.match(HTML, /LIMITS\.forEach/);
  A.match(HTML, /What this cannot do/);
});

t('every limit sentence is reachable in the shipped file', async () => {
  const { LIMITS } = await import('../src/order.mjs');
  for (const l of LIMITS) A.ok(HTML.includes(l), `limit missing from page: ${l}`);
});

console.log('\nBLANKS, LISTS, AND CONTROL CHARACTERS');

t('a blank spending cap stays blank and never becomes zero', () => {
  A.match(HTML, /capRaw === "" \? null : Number\(capRaw\)/);
  A.match(HTML, /g\.maxStake === null \? "—"/);
});

t('the revoke handler mutates its row instead of rebuilding the list', () => {
  // anchored inside drawGrants: the first attempt matched the SAMPLE buttons'
  // onclick 130 lines earlier and ran on for 5396 characters, so it was
  // asserting nothing about the handler it was named after.
  const dg = HTML.match(/function drawGrants\(\)[\s\S]*?\n\}/);
  A.ok(dg, 'drawGrants not found');
  A.ok(/b\.onclick = function/.test(dg[0]), 'the revoke handler is not in drawGrants');
  // drop the declaration line: `function drawGrants() {` is itself a match for
  // /drawGrants\(\)/, so the first version of this test failed on the function
  // being named after itself.
  const body = dg[0].slice(dg[0].indexOf('\n'));
  A.equal(/drawGrants\(\)/.test(body), false,
    'the handler rebuilds the list it is bound inside — six of these on record');
});

t('no literal control character in the shipped page', () => {
  // eslint-disable-next-line no-control-regex
  const bad = HTML.match(/[ --]/);
  A.equal(bad, null, `control character U+${bad && bad[0].charCodeAt(0).toString(16)}`);
});

t('user text is never put through innerHTML', () => {
  A.equal(/innerHTML/.test(code()), false, 'innerHTML is on the page');
});

console.log('\nTHE PAGE IS WHAT ITS SOURCES MAKE');

t('rebuilding produces byte-identical output', () => {
  execFileSync('node', [join(ROOT, 'build_helm.mjs'), '--check'], { cwd: ROOT });
});

console.log(`\n  RESULT: ${pass} passed, ${fail} failed\n`);
console.log('  bands measured:',
  ['calm', 'scam', 'dark'].map(k =>
    `${k}=${R[k].verdict}(p=${R[k].p_manipulative.toFixed(3)})`).join('  '), '\n');
process.exit(fail ? 1 : 0);
