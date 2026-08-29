// build_pagecode.mjs — inject the MEASURED audit into the page.
//   node page-code/build_pagecode.mjs           write pagecode.html
//   node page-code/build_pagecode.mjs --check   fail if it is not what a build makes
//
// The page must be one file with no <script src>, so the data is inlined. It is
// generated so the numbers on screen cannot drift from the run that produced
// them: --check asserts the committed page IS the generated one.
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, 'pagecode.html');
const ART = join(HERE, 'pagecode.artifact.html');

const CANNOT = [
  "It reads import statements. It does not read code and does not know what any of it does.",
  "A module that everything imports may be exactly right. This says it is there, never that it is wrong.",
  "A dependency reached through a string, a plugin registry, a subprocess or reflection is invisible here and will not appear in any reading.",
  "It cannot tell you whether a project works.",
];

export function build() {
  const tpl = readFileSync(join(HERE, 'pagecode_template.html'), 'utf8');
  const data = readFileSync(join(HERE, 'audit_data.json'), 'utf8');
  let html = tpl
    .replace('/*__DATA__*/null', data.trim())
    .replace('/*__CANNOT__*/[]', JSON.stringify(CANNOT, null, 1));
  const INTERNAL = ['IHCEI', 'NERE', 'OQM', 'GT v18'];
  const found = INTERNAL.filter(w => new RegExp(`\\b${w}\\b`).test(html));
  if (found.length) throw new Error(`internal vocabulary on a consumer page: ${found}`);
  return html;
}

function artifact(html) {
  return html
    .replace(/<!DOCTYPE html>\n/i, '').replace(/<html lang="en">\n/i, '')
    .replace(/<head>\n/i, '').replace(/^<meta [^>]*>\n/gim, '')
    .replace(/<\/head>\n/i, '').replace(/^<body>\n/im, '')
    .replace(/<\/body>\n/i, '').replace(/<\/html>\n?/i, '');
}

if (process.argv[2] === '--check') {
  const want = build();
  let got; try { got = readFileSync(OUT, 'utf8'); }
  catch { console.error('pagecode.html missing — run: node page-code/build_pagecode.mjs'); process.exit(1); }
  if (got !== want) { console.error('pagecode.html is not what a build produces.'); process.exit(1); }
  console.log('pagecode.html matches its sources');
} else {
  const html = build();
  writeFileSync(OUT, html);
  writeFileSync(ART, artifact(html));
  console.log(`pagecode.html written — ${(html.length / 1024).toFixed(1)} KB, one file`);
}
