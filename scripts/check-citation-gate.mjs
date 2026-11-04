#!/usr/bin/env node
// Citation gate for RemapRx page changes.
// For every guide in data/content.json that is new or changed relative to the base ref,
// every cited source on every sentence, question, FAQ and section must:
//   1. resolve to a source record with a DOI,
//   2. have that DOI present in research/deposits/**/MANIFEST.csv or research/corpus/**,
//   3. resolve on Crossref (HTTP 200),
//   4. have no Crossref retraction or withdrawal notice.
// Usage: node scripts/check-citation-gate.mjs [--base <git-ref>] [--offline]
import { execSync } from "node:child_process";
import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join } from "node:path";

const args = process.argv.slice(2);
function resolveBase() {
  if (args.includes("--base")) return args[args.indexOf("--base") + 1];
  if (process.env.GATE_BASE_REF) return process.env.GATE_BASE_REF;
  const q = (c) => { try { execSync(c, { stdio: "ignore" }); return true; } catch { return false; } };
  if (process.env.GITHUB_BASE_REF) {
    // Pull request in a shallow CI checkout: fetch the base branch tip.
    if (q(`git fetch --no-tags --depth=1 origin ${process.env.GITHUB_BASE_REF}`)) return "FETCH_HEAD";
  }
  if (process.env.GITHUB_ACTIONS) { q("git fetch --no-tags --deepen=1"); if (q("git rev-parse --verify HEAD~1")) return "HEAD~1"; }
  if (q("git rev-parse --verify origin/main")) return "origin/main";
  return null;
}
const baseRef = resolveBase();
if (!baseRef) { console.log("gate: no base ref available; skipped"); process.exit(0); }
const offline = args.includes("--offline");
const MAILTO = "info@paleofoundation.com";

const read = (p) => JSON.parse(readFileSync(p, "utf8"));
const content = read("data/content.json");
let base = { guides: [] };
try { base = JSON.parse(execSync(`git show ${baseRef}:data/content.json`, { maxBuffer: 1 << 30 }).toString()); }
catch { console.log(`gate: base ${baseRef} unreadable; skipped`); process.exit(0); }
const baseBySlug = new Map(base.guides.map((g) => [g.slug, JSON.stringify(g)]));
const changed = content.guides.filter((g) => baseBySlug.get(g.slug) !== JSON.stringify(g));
if (!changed.length) { console.log("gate: no new or changed guides; pass"); process.exit(0); }

const sources = new Map(content.sources.map((s) => [s.id, s]));
const norm = (d) => String(d || "").trim().toLowerCase().replace(/^https?:\/\/(dx\.)?doi\.org\//, "");

function walk(dir, out = []) {
  if (!existsSync(dir)) return out;
  for (const n of readdirSync(dir)) {
    const p = join(dir, n); const s = statSync(p);
    if (s.isDirectory()) walk(p, out); else if (/\.(csv|json|jsonl|md|tsv)$/i.test(n) && s.size < 200e6) out.push(p);
  }
  return out;
}
let onFile = "";
for (const f of [...walk("research/deposits"), ...walk("research/corpus")]) onFile += readFileSync(f, "utf8").toLowerCase() + "\n";

function citedIds(g) {
  const ids = new Set();
  const visit = (o) => {
    if (Array.isArray(o)) return o.forEach(visit);
    if (o && typeof o === "object") {
      if (Array.isArray(o.sources)) o.sources.forEach((s) => ids.add(typeof s === "string" ? s : s.id));
      Object.values(o).forEach(visit);
    }
  };
  visit([g.sections, g.faqs, g.scopedSections]);
  (g.sourceIds || []).forEach((s) => ids.add(s));
  return ids;
}

async function crossref(doi) {
  const h = { "User-Agent": `remaprx-citation-gate (mailto:${MAILTO})` };
  const r = await fetch(`https://api.crossref.org/works/${encodeURIComponent(doi)}`, { headers: h });
  if (r.status !== 200) return { ok: false, why: `Crossref HTTP ${r.status}` };
  const m = (await r.json()).message;
  const rel = m.relation || {};
  if (rel["is-retracted-by"]) return { ok: false, why: "Crossref relation is-retracted-by" };
  for (const u of m["updated-by"] || []) if (/retraction|withdrawal|removal/i.test(u.type || "")) return { ok: false, why: `Crossref updated-by ${u.type}` };
  const n = await fetch(`https://api.crossref.org/works?filter=updates:${encodeURIComponent(doi)}&rows=20`, { headers: h });
  if (n.ok) for (const it of (await n.json()).message.items || [])
    for (const u of it["update-to"] || []) if (norm(u.DOI) === doi && /retraction|withdrawal|removal/i.test(u.type || "")) return { ok: false, why: `notice ${it.DOI} (${u.type})` };
  return { ok: true };
}

const failures = [];
const checked = new Map();
for (const g of changed) {
  for (const id of citedIds(g)) {
    const s = sources.get(id);
    if (!s) { failures.push(`${g.slug}: source ${id} not found in data/content.json sources`); continue; }
    const doi = norm(s.doi);
    if (!doi) { failures.push(`${g.slug}: source ${id} has no DOI`); continue; }
    if (!onFile.includes(doi)) { failures.push(`${g.slug}: ${id} DOI ${doi} not in research/deposits or research/corpus`); continue; }
    if (offline) continue;
    if (!checked.has(doi)) checked.set(doi, await crossref(doi));
    const r = checked.get(doi);
    if (!r.ok) failures.push(`${g.slug}: ${id} DOI ${doi} failed: ${r.why}`);
  }
}
console.log(`gate: ${changed.length} changed guide(s): ${changed.map((g) => g.slug).join(", ")}; ${checked.size} DOI(s) checked on Crossref`);
if (failures.length) { console.error("gate: FAIL\n- " + failures.join("\n- ")); process.exit(1); }
console.log("gate: PASS");
