/* Dump Cairn / NERE / IHCEI answers as JSON for test_cairn.py. */
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
globalThis.LMD = require(join(here, "..", "smi", "lmd.js"));
globalThis.PLEXUS = require(join(here, "engines.js"));
globalThis.NERE = require(join(here, "nere.js"));
globalThis.IHCEI = require(join(here, "ihcei.js"));
const CAIRN = require(join(here, "cairn.js"));

const PRESSURE_TEXT =
  "Peer-reviewed research proves this law. You don't need to verify the methodology. " +
  "Just trust the model and act now.";
const DISCIPLINED_TEXT =
  "We pre-registered the hypothesis. You can verify the hash yourself; the primary " +
  "test failed and we report that null openly. Limitations are listed.";
const NEUTRAL_TEXT = "The meter was read on Tuesday. The rate is fixed until March.";

/* the worked example: an article whose claims all trace to one blog post */
const ONE_BLOG = {
  conclusion: "The policy raises your taxes",
  sources: ["A blog post from 2021"],
  parts: ["The policy raises your taxes", "Quoted figure", "Quoted expert",
          "A blog post from 2021"],
  links: [["The policy raises your taxes", "Quoted figure", 4],
          ["The policy raises your taxes", "Quoted expert", 4],
          ["Quoted figure", "A blog post from 2021", 6],
          ["Quoted expert", "A blog post from 2021", 6]],
  text: PRESSURE_TEXT,
};

/* the same shape but with two genuinely separate sources */
const TWO_SOURCES = {
  conclusion: "The policy raises your taxes",
  sources: ["Council budget PDF", "Independent analysis"],
  parts: ["The policy raises your taxes", "Quoted figure", "Quoted expert",
          "Council budget PDF", "Independent analysis"],
  links: [["The policy raises your taxes", "Quoted figure", 4],
          ["The policy raises your taxes", "Quoted expert", 4],
          ["Quoted figure", "Council budget PDF", 6],
          ["Quoted expert", "Independent analysis", 6]],
  text: DISCIPLINED_TEXT,
};

/* pressure wording over a structurally SOUND claim, and the reverse: the pair
   that proves the two measurements are not secretly the same number */
const SOUND_BUT_PUSHY = Object.assign({}, TWO_SOURCES, { text: PRESSURE_TEXT });
const SHAKY_BUT_POLITE = Object.assign({}, ONE_BLOG, { text: DISCIPLINED_TEXT });

process.stdout.write(JSON.stringify({
  oneBlog: CAIRN.verify(ONE_BLOG),
  twoSources: CAIRN.verify(TWO_SOURCES),
  soundButPushy: CAIRN.verify(SOUND_BUT_PUSHY),
  shakyButPolite: CAIRN.verify(SHAKY_BUT_POLITE),
  screens: {
    pressure: NERE.screen(PRESSURE_TEXT),
    disciplined: NERE.screen(DISCIPLINED_TEXT),
    neutral: NERE.screen(NEUTRAL_TEXT),
    empty: NERE.screen(""),
    /* a marker sitting inside a negation, to keep the known weakness visible */
    fooled: NERE.screen("You can verify nothing here. Just trust us."),
  },
  essence: [[2, 3], [0.5, 0.5], [1, 4]].map(([u, d]) => ({
    u, d, e: IHCEI.essence(u, d), squared: u * d * d })),
  floor: [0, 1, 3, 8, 20].map((eroded) => Object.assign(
    { eroded }, IHCEI.assess({ a: 1, b: 1 }, { kept: 0, eroded }))),
  balanced: IHCEI.assess({ a: 1, b: 1 }, { kept: 5, eroded: 5 }),
  /* The floor only means anything against a prior that actually asserts
     something. Beta(20,20) is a channel we believed was even-handed; evidence
     that contradicts it hard is where "widen, do not flip" has to hold. */
  informative: [0, 2, 10, 40].map((eroded) => Object.assign(
    { eroded }, IHCEI.assess({ a: 20, b: 20 }, { kept: 0, eroded }))),
  unfloored: [0, 2, 10, 40].map((eroded) => Object.assign(
    { eroded }, IHCEI.assess({ a: 20, b: 20 }, { kept: 0, eroded }, 1e9))),
  lines: CAIRN.lines("One claim here. Another there!\nA third on its own line."),
}));
