import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
globalThis.LMD = require(join(here, "..", "smi", "lmd.js"));
globalThis.PLEXUS = require(join(here, "engines.js"));
const C = require(join(here, "commons.js"));
const L = require(join(here, "library.js"));

const out = { entries: {}, order: [] };

for (const e of L.entries) {
  out.order.push(e.id);
  const m = C.measure(e);
  out.entries[e.id] = {
    ok: m.ok,
    why: m.why,
    title: m.title,
    provenanceKind: m.provenance && m.provenance.kind,
    licence: m.provenance && m.provenance.licence,
    drawn: slim(m.drawn),
    actual: slim(m.actual),
    remedy: slim(m.remedy),
    blindSpot: m.blindSpot,
    relief: m.relief,
    drawnSourceCount: e.drawn.sources.length,
  };
}

function slim(s) {
  if (!s) return null;
  return {
    parts: s.parts, pieces: s.pieces,
    totalBearing: s.totalBearing, expected: s.expected, conserved: s.conserved,
    bearings: s.links.map(r => r.bearing),
    singlePoints: s.singlePoints.map(r => r.part),
    support: s.support,
    deepest: s.deepest,
    restsOnOneThread: s.restsOnOneThread,
    dependences: s.bySource.map(r => ({ source: r.source, dependence: r.dependence })),
  };
}

const spots = L.entries.map(e => C.measure(e).blindSpot);
out.meanBlindSpot = spots.reduce((a, b) => a + b, 0) / spots.length;

out.families = C.families(L.entries);

// The refusals. Each of these must come back as a REASON, never as a throw.
const good = L.entries[4];                       // two-ways-into-the-vault
out.refusals = {};
function refuse(name, mutate) {
  const e = JSON.parse(JSON.stringify(good));
  mutate(e);
  let why;
  try { why = C.validate(e); } catch (err) { why = "THREW: " + err.message; }
  out.refusals[name] = why;
}
refuse("ok", () => {});
refuse("freeTextField", e => { e.actual.description = "Ada Lovelace, 12 Rue Neuve"; });
refuse("entryExtraKey", e => { e.owner = "someone"; });
refuse("badLicence", e => { e.provenance.licence = "MIT"; });
refuse("noProvenanceKind", e => { delete e.provenance.kind; });
refuse("noProvenanceWhere", e => { e.provenance.where = "   "; });
refuse("badId", e => { e.id = "Two Ways"; });
refuse("selfSupport", e => { e.actual.sources = ["The data"]; });
refuse("danglingLink", e => { e.actual.links.push(["The key", "Nowhere", 1.0]); });
refuse("negativeWeight", e => { e.actual.links[0][2] = -1; });
refuse("selfLink", e => { e.actual.links.push(["The key", "The key", 1.0]); });
refuse("noActual", e => { delete e.actual; });
/* A part carrying FATHOM's reserved ground. Written as an ESCAPE. This is the
   FOURTH literal NUL committed to this codebase and the fourth caught. */
refuse("nulInAPart", e => {
  const bad = "The data\u0000";
  e.actual.parts[0] = bad;
  e.actual.links.forEach(l => {
    if (l[0] === "The data") l[0] = bad;
    if (l[1] === "The data") l[1] = bad;
  });
  e.actual.conclusion = bad;
});

// Transfer: same shape, no shared word. Checked here on the raw signatures so
// the test can compare them itself rather than trusting a boolean from here.
const byId = Object.fromEntries(L.entries.map(e => [e.id, e]));
out.signatures = {};
for (const id of ["sole-maintainer", "three-audits-one-threat-model", "inline-only-under-csp"]) {
  const m = C.measure(byId[id]);
  out.signatures[id] = {
    drawn: C.signature(m.drawn),
    actual: C.signature(m.actual),
    remedy: C.signature(m.remedy),
    words: byId[id].actual.parts,
  };
}

// The number that would show the commons is real, and is not measurable here.
out.contributionRate = C.contributionRate(null);
out.contributionRateIfShipped = C.contributionRate({ buyers: 1000, contributed: 61 });

// Matching is a suggestion and must never feed a measurement.
out.match = C.match(L.entries, ["the registry", "package 3", "the build succeeds"]);

process.stdout.write(JSON.stringify(out, null, 1));
