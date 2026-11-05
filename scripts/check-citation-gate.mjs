#!/usr/bin/env node
// Citation gate for RemapRx page changes.
// For every guide in data/content.json that is new or changed relative to the base ref,
// every cited source on every sentence, question, FAQ and section must either:
//   1. carry a DOI that is present in research/deposits/**/MANIFEST.csv or research/corpus/**,
//      resolves on Crossref, and has no Crossref retraction, withdrawal, or removal notice, or
//   2. omit a DOI only when explicitly typed regulatory-label or agency-page
//      (sourceTier official_label or regulatory_guidance counts) and a public http(s) URL is set, or
//   3. omit a DOI only when explicitly typed no-doi-article, with a public URL and a PubMed id
//      already in those research files, whose Europe PMC record has no DOI.
// Crossref and Europe PMC HTTP 429 responses retry with backoff. A rate limit that remains
// after those retries does not fail the pull request. Persistent 5xx, HTTP 404, a retraction,
// a DOI missing from the research files, and an untyped source with no DOI still fail.
// Usage: node scripts/check-citation-gate.mjs [--base <git-ref>] [--offline]
import { execSync } from "node:child_process";
import { readFileSync, readdirSync, statSync, existsSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

export const MAILTO = "info@paleofoundation.com";
export const USER_AGENT = `remaprx-citation-gate (mailto:${MAILTO})`;
const VERIFIED_TTL_MS = 2 * 60 * 60 * 1000;
const RATE_LIMIT_TTL_MS = 15 * 60 * 1000;
const TIER_KIND = {
  official_label: "regulatory-label",
  regulatory_guidance: "agency-page",
};

export function norm(value) {
  return String(value || "").trim().toLowerCase().replace(/^https?:\/\/(dx\.)?doi\.org\//, "");
}

export function explicitNonDoiKind(source) {
  const declared = String(source?.nonDoiSourceType || "").trim().toLowerCase().replace(/_/g, "-");
  if (declared === "regulatory-label" || declared === "agency-page" || declared === "no-doi-article") return declared;
  const tier = String(source?.sourceTier || "").trim().toLowerCase();
  return TIER_KIND[tier] || null;
}

export function publicHttpUrl(source) {
  const url = String(source?.url || "").trim();
  return /^https?:\/\//i.test(url) ? url : null;
}

export function parseRetryAfter(value, now = Date.now()) {
  if (value == null) return null;
  const text = String(value).trim();
  if (!text) return null;
  if (/^\d+(\.\d+)?$/.test(text)) return Math.min(Number(text) * 1000, 15000);
  const when = Date.parse(text);
  if (Number.isNaN(when)) return null;
  return Math.min(Math.max(0, when - now), 15000);
}

function header(response, name) {
  const headers = response?.headers;
  if (!headers) return null;
  if (typeof headers.get === "function") return headers.get(name) ?? headers.get(name.toLowerCase());
  const lower = name.toLowerCase();
  return headers[name] ?? headers[lower] ?? null;
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function fetchWithBackoff(url, {
  fetchImpl = globalThis.fetch,
  sleep = delay,
  headers = { "User-Agent": USER_AGENT },
  maxAttempts = 5,
  service = "Crossref",
} = {}) {
  let waitMs = 1000;
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    let response;
    try {
      response = await fetchImpl(url, { headers });
    } catch (error) {
      if (attempt === maxAttempts) {
        const message = error instanceof Error ? error.message : String(error);
        return { ok: false, status: 0, why: `${service} request failed: ${message}` };
      }
      await sleep(waitMs);
      waitMs = Math.min(waitMs * 2, 16000);
      continue;
    }
    if (response.status === 200) return { ok: true, status: 200, response };
    const transient = response.status === 429 || response.status === 500 || response.status === 502 || response.status === 503 || response.status === 504;
    if (!transient) return { ok: false, status: response.status, why: `${service} HTTP ${response.status}` };
    if (attempt === maxAttempts) {
      return {
        ok: false,
        status: response.status,
        rateLimited: response.status === 429,
        why: `${service} HTTP ${response.status}`,
      };
    }
    const retryAfter = response.status === 429 ? parseRetryAfter(header(response, "retry-after")) : null;
    const pause = retryAfter == null ? waitMs : Math.min(Math.max(retryAfter, waitMs), 15000);
    await sleep(pause);
    waitMs = Math.min(waitMs * 2, 16000);
  }
  return { ok: false, status: 0, why: `${service} request failed` };
}

async function readJson(response) {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

export async function crossrefLookup(doi, deps = {}) {
  const headers = { "User-Agent": USER_AGENT };
  const work = await fetchWithBackoff(`https://api.crossref.org/works/${encodeURIComponent(doi)}`, { ...deps, headers, service: "Crossref" });
  if (work.rateLimited && !work.ok) return { ok: true, deferred: true, rateLimited: true, why: "Crossref HTTP 429 after retries" };
  if (!work.ok) return { ok: false, why: work.why };
  const body = await readJson(work.response);
  const message = body?.message;
  if (!message) return { ok: false, why: "Crossref response was not a work record" };
  const relation = message.relation || {};
  if (relation["is-retracted-by"]) return { ok: false, why: "Crossref relation is-retracted-by" };
  for (const update of message["updated-by"] || []) {
    if (/retraction|withdrawal|removal/i.test(update.type || "")) return { ok: false, why: `Crossref updated-by ${update.type}` };
  }
  const notice = await fetchWithBackoff(
    `https://api.crossref.org/works?filter=updates:${encodeURIComponent(doi)}&rows=20`,
    { ...deps, headers, service: "Crossref" },
  );
  if (notice.rateLimited && !notice.ok) return { ok: true, deferred: true, rateLimited: true, why: "Crossref HTTP 429 after retries" };
  if (!notice.ok) return { ok: false, why: notice.why };
  const items = await readJson(notice.response);
  if (!items?.message) return { ok: false, why: "Crossref retraction query was not a work list" };
  for (const item of items.message.items || []) {
    for (const update of item["update-to"] || []) {
      if (norm(update.DOI) === doi && /retraction|withdrawal|removal/i.test(update.type || "")) {
        return { ok: false, why: `notice ${item.DOI} (${update.type})` };
      }
    }
  }
  return { ok: true };
}

export async function europePmcPmid(pmid, deps = {}) {
  const query = `EXT_ID:${pmid} AND SRC:MED`;
  const url = `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=${encodeURIComponent(query)}&format=json&resultType=lite&pageSize=1`;
  const got = await fetchWithBackoff(url, { ...deps, service: "Europe PMC" });
  if (got.rateLimited && !got.ok) return { ok: true, deferred: true, rateLimited: true, why: "Europe PMC HTTP 429 after retries" };
  if (!got.ok) return { ok: false, why: got.why };
  const body = await readJson(got.response);
  const hit = body?.resultList?.result?.[0];
  if (!hit || String(hit.pmid || hit.id || "") !== String(pmid)) return { ok: false, why: `PMID ${pmid} not found on Europe PMC` };
  const doi = norm(hit.doi);
  if (doi) return { ok: false, why: `PMID ${pmid} has DOI ${doi}; cite that DOI instead of a non-DOI type` };
  return { ok: true };
}

export function createCrossrefClient({
  fetchImpl = globalThis.fetch,
  sleep = delay,
  maxAttempts = 5,
  gapMs = 200,
  cache = new Map(),
} = {}) {
  let rateLimited = false;
  let lastCall = 0;
  async function politeFetch(url, init) {
    const pause = Math.max(0, lastCall + gapMs - Date.now());
    if (pause) await sleep(pause);
    lastCall = Date.now();
    return fetchImpl(url, init);
  }
  async function cached(key, load) {
    if (cache.has(key)) return cache.get(key);
    const result = await load();
    cache.set(key, result);
    return result;
  }
  return {
    lookup(doi) {
      return cached(`doi:${doi}`, () => crossrefLookup(doi, {
        fetchImpl: politeFetch,
        sleep,
        maxAttempts: rateLimited ? 1 : maxAttempts,
      }).then((result) => {
        if (result.deferred && result.rateLimited) rateLimited = true;
        return result;
      }));
    },
    lookupPmid(pmid) {
      return cached(`pmid:${pmid}`, () => europePmcPmid(pmid, {
        fetchImpl: politeFetch,
        sleep,
        maxAttempts: rateLimited ? 1 : maxAttempts,
      }).then((result) => {
        if (result.deferred && result.rateLimited) rateLimited = true;
        return result;
      }));
    },
  };
}

export function loadFileCache(path, now = Date.now()) {
  let stored = {};
  try {
    stored = JSON.parse(readFileSync(path, "utf8"));
  } catch {
    stored = {};
  }
  const fresh = new Map();
  for (const [key, entry] of Object.entries(stored)) {
    if (!entry || typeof entry.at !== "number") continue;
    const ttl = entry.deferred ? RATE_LIMIT_TTL_MS : VERIFIED_TTL_MS;
    if (entry.ok && now - entry.at < ttl) fresh.set(key, entry);
  }
  const persist = () => {
    const out = {};
    for (const [key, entry] of fresh) out[key] = entry;
    writeFileSync(path, JSON.stringify(out));
  };
  return {
    has: (key) => fresh.has(key),
    get: (key) => fresh.get(key),
    set: (key, value) => {
      const { response, ...rest } = value || {};
      void response;
      fresh.set(key, { ...rest, at: Date.now() });
      try { persist(); } catch { /* a cache miss only repeats a lookup */ }
    },
  };
}

export async function evaluateSource(source, { onFile = "", lookupDoi, lookupPmid, offline = false } = {}) {
  const doi = norm(source?.doi);
  if (doi) {
    if (!onFile.toLowerCase().includes(doi)) return { failures: [`DOI ${doi} not in research/deposits or research/corpus`], warnings: [] };
    if (offline) return { failures: [], warnings: [] };
    const result = await lookupDoi(doi);
    if (result?.deferred) return { failures: [], warnings: [`DOI ${doi} was not failed for a rate limit: ${result.why}`] };
    if (!result?.ok) return { failures: [`DOI ${doi} failed: ${result?.why || "Crossref check failed"}`], warnings: [] };
    return { failures: [], warnings: [] };
  }
  const kind = explicitNonDoiKind(source);
  if (!kind) return { failures: ["has no DOI"], warnings: [] };
  if (!publicHttpUrl(source)) return { failures: [`is typed ${kind} but has no public http(s) URL`], warnings: [] };
  if (kind !== "no-doi-article") return { failures: [], warnings: [] };
  const pmid = String(source?.pmid || "").trim();
  if (!/^\d{1,9}$/.test(pmid)) return { failures: ["is typed no-doi-article but has no PubMed id"], warnings: [] };
  if (!onFile.includes(pmid)) return { failures: [`PMID ${pmid} not in research/deposits or research/corpus`], warnings: [] };
  if (offline) return { failures: [], warnings: [] };
  const result = await lookupPmid(pmid);
  if (result?.deferred) return { failures: [], warnings: [`PMID ${pmid} was not failed for a rate limit: ${result.why}`] };
  if (!result?.ok) return { failures: [result?.why || `PMID ${pmid} could not be checked`], warnings: [] };
  return { failures: [], warnings: [] };
}

function failureLine(slug, id, failure) {
  if (failure.startsWith("DOI ") || failure.startsWith("PMID ")) return `${slug}: ${id} ${failure}`;
  return `${slug}: source ${id} ${failure}`;
}

function walkFiles(dir, out = []) {
  if (!existsSync(dir)) return out;
  for (const name of readdirSync(dir)) {
    const path = join(dir, name);
    const info = statSync(path);
    if (info.isDirectory()) walkFiles(path, out);
    else if (/\.(csv|json|jsonl|md|tsv)$/i.test(name) && info.size < 200e6) out.push(path);
  }
  return out;
}

function citedIds(guide) {
  const ids = new Set();
  const visit = (value) => {
    if (Array.isArray(value)) return value.forEach(visit);
    if (value && typeof value === "object") {
      if (Array.isArray(value.sources)) value.sources.forEach((source) => ids.add(typeof source === "string" ? source : source.id));
      Object.values(value).forEach(visit);
    }
  };
  visit([guide.sections, guide.faqs, guide.scopedSections]);
  (guide.sourceIds || []).forEach((id) => ids.add(id));
  return ids;
}

function resolveBase(args) {
  if (args.includes("--base")) return args[args.indexOf("--base") + 1];
  if (process.env.GATE_BASE_REF) return process.env.GATE_BASE_REF;
  const ok = (command) => { try { execSync(command, { stdio: "ignore" }); return true; } catch { return false; } };
  if (process.env.GITHUB_BASE_REF) {
    if (ok(`git fetch --no-tags --depth=1 origin ${process.env.GITHUB_BASE_REF}`)) return "FETCH_HEAD";
  }
  if (process.env.GITHUB_ACTIONS) {
    ok("git fetch --no-tags --deepen=1");
    if (ok("git rev-parse --verify HEAD~1")) return "HEAD~1";
  }
  if (ok("git rev-parse --verify origin/main")) return "origin/main";
  return null;
}

async function main() {
  const args = process.argv.slice(2);
  const baseRef = resolveBase(args);
  if (!baseRef) { console.log("gate: no base ref available; skipped"); process.exit(0); }
  const offline = args.includes("--offline");
  const read = (path) => JSON.parse(readFileSync(path, "utf8"));
  const content = read("data/content.json");
  let base = { guides: [] };
  try { base = JSON.parse(execSync(`git show ${baseRef}:data/content.json`, { maxBuffer: 1 << 30 }).toString()); }
  catch { console.log(`gate: base ${baseRef} unreadable; skipped`); process.exit(0); }
  const baseBySlug = new Map(base.guides.map((guide) => [guide.slug, JSON.stringify(guide)]));
  const changed = content.guides.filter((guide) => baseBySlug.get(guide.slug) !== JSON.stringify(guide));
  if (!changed.length) { console.log("gate: no new or changed guides; pass"); process.exit(0); }

  const sources = new Map(content.sources.map((source) => [source.id, source]));
  let onFile = "";
  for (const file of [...walkFiles("research/deposits"), ...walkFiles("research/corpus")]) onFile += `${readFileSync(file, "utf8").toLowerCase()}\n`;
  const client = offline ? null : createCrossrefClient({ cache: loadFileCache(join(tmpdir(), "remaprx-citation-gate-cache.json")) });
  const failures = [];
  const warnings = [];
  let checked = 0;
  for (const guide of changed) {
    for (const id of citedIds(guide)) {
      const source = sources.get(id);
      if (!source) { failures.push(`${guide.slug}: source ${id} not found in data/content.json sources`); continue; }
      const result = await evaluateSource(source, {
        onFile,
        offline,
        lookupDoi: async (doi) => { checked += 1; return client.lookup(doi); },
        lookupPmid: async (pmid) => client.lookupPmid(pmid),
      });
      result.failures.forEach((failure) => failures.push(failureLine(guide.slug, id, failure)));
      result.warnings.forEach((warning) => warnings.push(`${guide.slug}: ${id} ${warning}`));
    }
  }
  console.log(`gate: ${changed.length} changed guide(s): ${changed.map((guide) => guide.slug).join(", ")}; ${checked} DOI(s) checked on Crossref`);
  warnings.forEach((warning) => console.log(`gate: warning: ${warning}`));
  if (failures.length) { console.error(`gate: FAIL\n- ${failures.join("\n- ")}`); process.exit(1); }
  console.log("gate: PASS");
}

function isDirectRun() {
  const entry = process.argv[1];
  return Boolean(entry) && import.meta.url === pathToFileURL(entry).href;
}

if (isDirectRun()) await main();
