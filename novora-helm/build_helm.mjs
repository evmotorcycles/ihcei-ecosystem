// build_helm.mjs — inline the kernel into helm.html.
// ============================================================================
//   node build_helm.mjs          write helm.html
//   node build_helm.mjs --check  exit 1 if helm.html is not what a build makes
//
// WHY A BUILD STEP AND NOT A HAND-WRITTEN PAGE
// helm.html has to be ONE file with no <script src>, because a <script src> is
// a second request and the whole claim is that there are none. That means the
// kernel is duplicated into the page, and duplicated code drifts. So the page
// is generated, --check asserts the committed page IS the generated one, and
// the suite runs --check. An edit to the page that the modules did not make
// fails the build in the same commit that made it.
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const MODULES = ['src/helm-core.mjs', 'src/primitives.mjs', 'src/order.mjs'];
const MARK = '/*__KERNEL__*/';

export function kernel() {
  return MODULES.map(rel => {
    const src = readFileSync(join(HERE, rel), 'utf8')
      // `export` is the only thing that makes these modules; strip it and the
      // same text is a classic script. Nothing else is transformed — what runs
      // in the page is character-for-character what runs under `node --test`.
      .replace(/^export\s+/gm, '')
      .trimEnd();
    return `/* ─────────── ${rel} ─────────── */\n${src}`;
  }).join('\n\n');
}

// Vocabulary internal to this project must not reach a consumer screen, and
// that includes the comments — a person who opens view-source is still the
// consumer. Enforced here rather than trusted, because the first run of this
// build shipped two of them inside the kernel's own header comment.
const INTERNAL = ['IHCEI', 'NERE', 'OQM', 'GT v18', 'RISE engine'];

export function build() {
  const tpl = readFileSync(join(HERE, 'helm_template.html'), 'utf8');
  if (!tpl.includes(MARK)) throw new Error(`template has no ${MARK} marker`);
  const html = tpl.replace(MARK, kernel());
  const found = INTERNAL.filter(w => new RegExp(`\\b${w}\\b`, 'i').test(html));
  if (found.length) {
    throw new Error(`internal vocabulary would ship to a consumer screen: ${found.join(', ')}`);
  }
  return html;
}

const OUT = join(HERE, 'helm.html');
const ART = join(HERE, 'helm.artifact.html');

// The hosted build. Same bytes, minus the document wrapper the host supplies.
// Generated from the same template so the two cannot say different things.
export function artifact(html) {
  return html
    .replace(/<!DOCTYPE html>\n/i, '')
    .replace(/<html lang="en">\n/i, '')
    .replace(/<head>\n/i, '')
    .replace(/^<meta [^>]*>\n/gim, '')
    .replace(/<\/head>\n/i, '')
    .replace(/^<body>\n/im, '')
    .replace(/<\/body>\n/i, '')
    .replace(/<\/html>\n?/i, '');
}

if (process.argv[2] === '--check') {
  const want = build();
  let got;
  try { got = readFileSync(OUT, 'utf8'); }
  catch { console.error('helm.html does not exist — run: node build_helm.mjs'); process.exit(1); }
  if (got !== want) {
    console.error('helm.html is not what a build produces. Edit the modules or the');
    console.error('template, then rebuild: node build_helm.mjs');
    process.exit(1);
  }
  console.log('helm.html matches its sources');
} else {
  const html = build();
  writeFileSync(OUT, html);
  writeFileSync(ART, artifact(html));
  console.log(`helm.html written — ${(html.length / 1024).toFixed(1)} KB, one file, no requests`);
  console.log('helm.artifact.html written — same page, hosted wrapper');
}
