/* A stand-in for whatever an agent would actually reach: serves the real frozen
 * GitHub and Hugging Face cohorts, plus files that must never be readable.
 * It LOGS every request it receives, which is how the test proves a refused
 * request never arrived. */
import http from "node:http";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
export const received = [];

const FILES = {
  "public/github.json": () => readFileSync(join(ROOT, "ei-dashboards/data/qwen_deepseek_frozen.json"), "utf8"),
  "public/hf.json": () => readFileSync(join(ROOT, "hf-cohort/data/hf_cohort_frozen.json"), "utf8"),
  "projects/report.md": () => "According to a 2023 randomised trial of 240 participants in the UK, the rate fell 12%.",
  "projects/thin.md": () => "It works well.",
  "projects/health.md": () => "Nine cases of Vibrio vulnificus infection and five deaths were reported this year.",
  "projects/drafts/new.md": () => "draft",
  "payroll/salaries.csv": () => "name,salary\nA,52000\n",
  ".ssh/id_rsa": () => "PRIVATE KEY MATERIAL",
  "secret/.env": () => "API_KEY=should-never-be-served",
};

export function createUpstream() {
  return http.createServer((req, res) => {
    const path = (req.url || "/").replace(/^\/+/, "");
    received.push({ method: req.method, path });
    const f = FILES[path];
    if (!f) { res.writeHead(404); res.end("not found"); return; }
    const type = path.endsWith(".json") ? "application/json" : "text/plain";
    res.writeHead(200, { "content-type": type });
    res.end(f());
  });
}
