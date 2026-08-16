/* Dump the manifold's measurements as JSON for test_manifold.py. */
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
globalThis.LMD = require(join(here, "..", "smi", "lmd.js"));
globalThis.PLEXUS = require(join(here, "engines.js"));
globalThis.ETI = require(join(here, "eti.js"));
const M = require(join(here, "manifold.js"));

function base() {
  const s = M.defaults();
  M.install(s, "Files", "app");
  M.install(s, "Summariser", "ai");
  M.install(s, "Water bill", "data");
  return s;
}

/* One route: You -- Node, nothing else touching it. */
const oneRoute = [0.02, 0.2, 2, 20, 200].map((J) => {
  const s = M.defaults();
  M.install(s, "Solo", "app");
  s.residual = J;
  return { J, distance: M.distance(s, "Solo"), exponent: M.exponent(s, "Solo") };
});

/* Two routes: the same link, plus You -- Data -- Node. */
const twoRoutes = [0.02, 0.2, 2, 20, 200].map((J) => {
  const s = M.defaults();
  M.install(s, "App", "app");
  M.install(s, "Data", "data");
  M.couple(s, "Data", "App", 1);
  s.residual = 1;
  /* raise only the You--App coupling by using intent on App */
  s.boost = J - 1;
  s.intent = { App: true };
  return { J, distance: M.distance(s, "App"), exponent: M.exponent(s, "App") };
});

/* Intent on and off, on a realistic little workspace. */
const idle = base();
const t0 = M.telemetry(idle);
const busy = base();
busy.intent = { "Water bill": true, Summariser: true };
const t1 = M.telemetry(busy);
const cleared = base();
cleared.intent = { "Water bill": true };
cleared.intent = {};
const t2 = M.telemetry(cleared);

/* Errors are values, not exceptions. */
const dup = M.defaults();
M.install(dup, "Files", "app");
const errors = {
  duplicate: M.install(dup, "Files", "app"),
  badKind: M.install(dup, "Thing", "widget"),
  empty: M.install(dup, "   ", "app"),
  reservedName: M.install(dup, "You", "app"),
  selfCouple: M.couple(dup, "Files", "Files", 1),
  missing: M.couple(dup, "Files", "Nope", 1),
  okInstall: M.install(dup, "Notes", "app"),
};

/* Uninstalling must take its couplings with it. */
const un = base();
M.couple(un, "Summariser", "Water bill", 3);
const beforeUn = M.graph(un).links.length;
M.uninstall(un, "Water bill");
const afterUn = M.graph(un).links.length;

/* Nothing installed at all. */
const emptyState = M.defaults();
const emptyFrame = M.frame(emptyState, { w: 360, h: 320 });

process.stdout.write(JSON.stringify({
  oneRoute, twoRoutes,
  idle: t0, busy: t1, cleared: t2,
  errors,
  uninstall: { before: beforeUn, after: afterUn,
               names: M.graph(un).names, affinities: un.affinities.length },
  empty: { dead: emptyFrame.dead, nodes: emptyFrame.nodes.length,
           integrity: emptyFrame.integrity },
  graphIdle: M.graph(idle),
  graphBusy: M.graph(busy),
}));
