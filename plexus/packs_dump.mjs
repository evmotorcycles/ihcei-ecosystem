import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
globalThis.LMD = require(join(here, "..", "smi", "lmd.js"));
globalThis.PLEXUS = require(join(here, "engines.js"));
const P = require(join(here, "packs.js"));
const LIB = require(join(here, "packlib.js"));

const by = Object.fromEntries(LIB.packs.map(p => [p.id, p]));
const out = { order: LIB.packs.map(p => p.id) };

// Every pack is well formed, and its structure and effort are reported.
out.packs = {};
for (const p of LIB.packs) {
  out.packs[p.id] = {
    title: p.title,
    why: P.checkPack(p),
    asks: p.asks.map(a => ({ key: a.key, label: a.label, optional: !!a.optional })),
    derive: p.derive.map(d => d.key),
    assumes: p.assumes,
    goCheck: p.goCheck,
    structure: P.structure(p),
    effort: P.effort(p),
  };
}

// ---------------------------------------------------------- worked cases ----
// The metered bill that prompted all of this.
const METER = { now: 70, before: 58, rate: 5032, fee: 1700, printed: 62084 };
out.meter = P.fill(by["metered-bill"], METER);
out.meterPaid = P.fill(by["metered-bill"], Object.assign({}, METER, { paid: 65000 }));
out.meterWrong = P.fill(by["metered-bill"], Object.assign({}, METER, { printed: 63000 }));
out.meterShort = P.fill(by["metered-bill"], Object.assign({}, METER, { printed: 61000 }));

// The optional field left empty must make the row VANISH, never read zero.
out.meterNoPaid = {
  rowKeys: out.meter.rows.map(r => r.key),
  hasCarried: out.meter.rows.some(r => r.key === "carried"),
  carriedInValues: "carried" in out.meter.values,
};

// A required field left empty is named, and nothing downstream is invented.
out.meterMissing = P.fill(by["metered-bill"], { now: 70, before: 58, printed: 62084 });

// Numbers typed with spaces and commas, because people do that.
out.meterMessy = P.fill(by["metered-bill"],
  { now: "70", before: "58", rate: "5,032", fee: "1 700", printed: "62,084" });
out.meterNotANumber = P.fill(by["metered-bill"],
  Object.assign({}, METER, { rate: "about five thousand" }));

// The other five.
out.payslip = P.fill(by["payslip"],
  { gross: 4200, tax: 630, pension: 210, other: 0, printed: 3360 });
out.invoice = P.fill(by["invoice-with-tax"],
  { subtotal: 1200, percent: 18, printed: 1416 });
out.deposit = P.fill(by["deposit-returned"],
  { held: 1500, d1: 200, d2: 75, d3: 0, printed: 1225 });
out.split = P.fill(by["splitting-a-bill"], { total: 1000, people: 8 });
out.splitByZero = P.fill(by["splitting-a-bill"], { total: 1000, people: 0 });
out.instalments = P.fill(by["paying-in-instalments"],
  { cash: 900, deposit: 100, each: 80, howmany: 12 });

// ------------------------------------------------------------- refusals -----
out.refusals = {};
function refuse(name, mutate) {
  const p = JSON.parse(JSON.stringify(by["splitting-a-bill"]));
  mutate(p);
  let why;
  try { why = P.checkPack(p); } catch (e) { why = "THREW: " + e.message; }
  out.refusals[name] = why;
}
refuse("ok", () => {});
refuse("noAssumes", p => { p.assumes = []; });
refuse("noGoCheck", p => { p.goCheck = []; });
refuse("unknownKey", p => { p.derive[0].expr = ["/", "total", "nobody"]; });
refuse("selfReference", p => { p.derive[0].expr = ["/", "each", "people"]; });
refuse("badOperator", p => { p.derive[0].expr = ["^", "total", "people"]; });
refuse("duplicateKey", p => { p.derive.push({ key: "total", label: "Again", expr: 1 }); });
refuse("noLabel", p => { p.asks[0].label = "  "; });
refuse("badId", p => { p.id = "Splitting A Bill"; });
refuse("threeWayMinus", p => { p.derive[0].expr = ["-", "total", "people", "total"]; });

// The friction claim, over the whole library.
out.effortTotals = {
  asks: LIB.packs.reduce((n, p) => n + P.effort(p).asks, 0),
  byHand: LIB.packs.reduce((n, p) => n + P.effort(p).byHand, 0),
  allLessWork: LIB.packs.every(p => P.effort(p).lessWork),
};

process.stdout.write(JSON.stringify(out, null, 1));
