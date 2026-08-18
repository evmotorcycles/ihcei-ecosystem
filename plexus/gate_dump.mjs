import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
globalThis.LMD = require(join(here, "..", "smi", "lmd.js"));
globalThis.PLEXUS = require(join(here, "engines.js"));
const G = require(join(here, "gate.js"));
const L = require(join(here, "lens.js"));

const DAY = 86400;
const out = {};

// ---------------------------------------------------------------- the plan --
// A quote, a deposit and a delivery. Ordinary, small, and it has exactly one
// step with no way round it, which is the point.
const PLAN = {
  parts: ["The supplier's price", "The delivery date", "The quote",
          "The deposit", "The order ships"],
  links: [
    ["The supplier's price", "The quote", 1.0],
    ["The delivery date", "The quote", 1.0],
    ["The quote", "The deposit", 1.0],
    ["The deposit", "The order ships", 1.0],
    ["The delivery date", "The order ships", 1.0],
  ],
};
const ALLOWED = ["The supplier's price", "The delivery date", "The quote"];

out.plan = PLAN;
out.perimeter = G.perimeter(PLAN, ALLOWED);
out.soleRoutes = G.soleRoutes(PLAN);
out.sealed = G.perimeter(PLAN, PLAN.parts);
out.unknownPart = G.perimeter(PLAN, ALLOWED.concat(["A part nobody entered"]));

// ------------------------------------------------------------- histories ----
// Deterministic, no randomness, so the Python side can build exactly the same
// events from the same description.
function history(name, perWindow, latencies, nWindows) {
  // latencies[k] is the latency in days for every item closed in window k
  const now = 400 * DAY;
  const win = 30 * DAY;
  const evs = [];
  for (let k = 0; k < nWindows; k++) {
    // window k counted from the OLDEST end
    const end = now - (nWindows - 1 - k) * win;
    for (let i = 0; i < perWindow; i++) {
      const closedAt = end - win + ((i + 1) * win) / (perWindow + 1);
      const lat = latencies[k];
      evs.push({ openedAt: closedAt - lat * DAY, closedAt: closedAt });
    }
  }
  return { name, now, events: evs };
}

const HISTORIES = [
  history("flat", 5, [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10], 12),
  history("rising", 5, [5, 6, 8, 9, 11, 14, 17, 21, 26, 32, 40, 50], 12),
  history("falling", 5, [50, 40, 32, 26, 21, 17, 14, 11, 9, 8, 6, 5], 12),
  history("noisy", 5, [12, 9, 14, 8, 15, 11, 13, 10, 16, 9, 14, 12], 12),
  history("jump", 5, [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 45], 12),
  history("thin", 1, [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10], 12),
  history("short", 5, [10, 12, 11], 3),
];

// One with items still open, so the backlog tail is exercised too.
{
  const h = history("with-backlog", 4, [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], 12);
  for (let i = 0; i < 6; i++) {
    h.events.push({ openedAt: h.now - (300 - i * 10) * DAY, closedAt: null });
  }
  HISTORIES.push(h);
}

out.histories = {};
out.hazards = {};
for (const h of HISTORIES) {
  out.histories[h.name] = { now: h.now, events: h.events };
  out.hazards[h.name] = G.hazard(h.events, { now: h.now });
}

out.emptyHistory = G.hazard([], { now: 0 });
out.retiredFloor = G.retiredFloor();
out.disclaimer = G.DISCLAIMER;

// review must present the three side by side and never add them together
out.review = G.review(PLAN, ALLOWED, HISTORIES[1].events, { now: HISTORIES[1].now });
out.reviewKeys = Object.keys(out.review);

// ------------------------------------------------------------------ lens ----
out.tools = L.tools().map(t => ({
  name: t.name, page: t.page, does: t.does,
  measures: t.measures, cannot: t.cannot, goCheck: t.goCheck,
}));
out.paradigm = L.PARADIGM;
out.refusals = {};
for (const page of ["index.html", "flint.html", "commons.html", "gate.html"]) {
  out.refusals[page] = L.refusalsFor(page);
}

out.lensRefusals = {};
function lensRefuse(name, tool) {
  out.lensRefusals[name] = L.problems(tool);
}
const GOOD = { name: "A tool", page: "x.html", does: "Do one thing.",
               measures: ["a number"], cannot: ["It cannot do the other thing."],
               goCheck: ["Go and look at the thing."] };
lensRefuse("ok", GOOD);
lensRefuse("noCannot", Object.assign({}, GOOD, { cannot: [] }));
lensRefuse("noGoCheck", Object.assign({}, GOOD, { goCheck: [] }));
lensRefuse("noMeasures", Object.assign({}, GOOD, { measures: [] }));
lensRefuse("emptyCheck", Object.assign({}, GOOD, { goCheck: ["   "] }));
lensRefuse("noName", Object.assign({}, GOOD, { name: "" }));

process.stdout.write(JSON.stringify(out, null, 1));
