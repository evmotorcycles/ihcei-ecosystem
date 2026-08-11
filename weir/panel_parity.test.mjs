/* node --test weir/panel_parity.test.mjs
 *
 * The control panel ships its own copy of the decision function so the page
 * works offline. A copy is a liability: if it drifts, the panel shows a person
 * one answer while the gate does another, which is worse than having no panel.
 */
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { decide, loadKey } from "./weir.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const KEY = loadKey(join(here, "key.example.json"));

// evaluate the panel's own decide() out of the built page
const html = readFileSync(join(here, "panel.html"), "utf8");
const start = html.indexOf("function globMatch(g,p){");
const end = html.indexOf("var YES=");
assert.ok(start > -1 && end > start, "could not find the panel's decision code");
const panelSrc = html.slice(start, end);
const panelDecide = new Function("KEY", panelSrc + "; return decide;")(KEY);

const PATHS = [
  "projects/notes.md", "projects/a/b/c.md", "projects/drafts/new.md",
  "public/data.json", "payroll/salaries.csv", "payroll/sub/x.csv",
  ".ssh/id_rsa", "secret/.env", "anything/else.txt", "", "/",
  "projects", "publicx/data.json", "PROJECTS/notes.md",
];
const METHODS = ["GET", "HEAD", "PUT", "POST", "DELETE"];

test("the panel and the gate agree on every path and method", () => {
  let compared = 0;
  for (const p of PATHS) {
    for (const m of METHODS) {
      const real = decide(KEY, m, p);
      const shown = panelDecide(m, p);
      assert.equal(shown.allow, real.allow,
        `panel and gate disagree on ${m} ${JSON.stringify(p)}`);
      assert.equal(shown.rule, real.rule,
        `panel and gate cite different rules for ${m} ${JSON.stringify(p)}`);
      compared++;
    }
  }
  assert.equal(compared, PATHS.length * METHODS.length);
});

test("the panel shows the same key the gate loads", () => {
  const m = html.match(/var KEY = (\{.*?\});/s);
  assert.ok(m, "the key should be inlined in the page");
  assert.deepEqual(JSON.parse(m[1]).rules, KEY.rules);
});

test("the panel states the bypass limit where a person will read it", () => {
  const text = html.replace(/<script[\s\S]*?<\/script>/gi, " ")
                   .replace(/<[^>]+>/g, " ").replace(/\s+/g, " ");
  assert.match(text, /cannot stop a program that does not come through it at all/);
  assert.match(text, /A gate you can walk around is a gate you should not rely on alone/);
});

test("the panel keeps jargon off the screen", () => {
  const text = html.replace(/<script[\s\S]*?<\/script>/gi, " ")
                   .replace(/<style[\s\S]*?<\/style>/gi, " ")
                   .replace(/<[^>]+>/g, " ");
  for (const word of [/epistemolog/i, /merkle/i, /\bIHCEI\b/, /\bNERE\b/,
                      /default-deny/i, /\bproxy\b/i, /\b403\b/]) {
    assert.ok(!word.test(text), `panel shows jargon: ${word}`);
  }
});
