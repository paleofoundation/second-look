import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import {
  createCrossrefClient,
  crossrefLookup,
  evaluateSource,
  europePmcPmid,
  explicitNonDoiKind,
  loadFileCache,
  parseRetryAfter,
} from '../scripts/check-citation-gate.mjs';

function response(status, body, headers = {}) {
  return {
    status,
    headers: { get: (name) => headers[name.toLowerCase()] ?? null },
    json: async () => body,
  };
}

const work = { message: { DOI: '10.1000/example', relation: {}, 'updated-by': [] } };
const notices = { message: { items: [] } };

function scriptedFetch(script) {
  const calls = [];
  const sleeps = [];
  const fetchImpl = async (url) => {
    calls.push(url);
    const next = script.shift();
    if (!next) throw new Error(`unexpected fetch ${url}`);
    if (next instanceof Error) throw next;
    return next;
  };
  return { calls, sleeps, fetchImpl, sleep: async (ms) => { sleeps.push(ms); } };
}

test('parseRetryAfter reads seconds and HTTP dates, and caps a long wait', () => {
  assert.equal(parseRetryAfter('2'), 2000);
  assert.equal(parseRetryAfter('0'), 0);
  assert.equal(parseRetryAfter(''), null);
  assert.equal(parseRetryAfter('999'), 15000);
  const soon = new Date(Date.now() + 3000).toUTCString();
  const wait = parseRetryAfter(soon);
  assert.ok(wait >= 2000 && wait <= 4000, String(wait));
});

test('Crossref HTTP 429 retries with backoff and then accepts the work', async () => {
  const fetch = scriptedFetch([
    response(429, {}, { 'retry-after': '3' }),
    response(200, work),
    response(200, notices),
  ]);
  const result = await crossrefLookup('10.1000/example', fetch);
  assert.equal(result.ok, true);
  assert.equal(result.deferred, undefined);
  assert.equal(fetch.calls.length, 3);
  assert.deepEqual(fetch.sleeps, [3000]);
  assert.match(fetch.calls[0], /api\.crossref\.org\/works\/10\.1000%2Fexample$/);
});

test('Crossref HTTP 429 after the retry budget does not fail the citation', async () => {
  const fetch = scriptedFetch(Array.from({ length: 5 }, () => response(429, {})));
  const result = await crossrefLookup('10.1000/limited', { ...fetch, maxAttempts: 5 });
  assert.equal(result.ok, true);
  assert.equal(result.deferred, true);
  assert.equal(result.rateLimited, true);
  assert.match(result.why, /429/);
  assert.equal(fetch.calls.length, 5);
  assert.equal(fetch.sleeps.length, 4);
  assert.deepEqual(fetch.sleeps, [1000, 2000, 4000, 8000]);
});

test('a later DOI does not repeat the full 429 backoff after one identifier stays limited', async () => {
  const first = Array.from({ length: 5 }, () => response(429, {}));
  const fetch = scriptedFetch([...first, response(429, {})]);
  const client = createCrossrefClient({ ...fetch, gapMs: 0, maxAttempts: 5 });
  const limited = await client.lookup('10.1000/first');
  const next = await client.lookup('10.1000/second');
  assert.equal(limited.deferred, true);
  assert.equal(next.deferred, true);
  assert.equal(fetch.calls.length, 6);
  const again = await client.lookup('10.1000/first');
  assert.equal(again.deferred, true);
  assert.equal(fetch.calls.length, 6);
});

test('HTTP 404 and a retraction fail without a retry, and HTTP 500 retries', async () => {
  const missing = scriptedFetch([response(404, {})]);
  const notFound = await crossrefLookup('10.1000/missing', missing);
  assert.equal(notFound.ok, false);
  assert.match(notFound.why, /404/);
  assert.equal(missing.calls.length, 1);
  assert.equal(missing.sleeps.length, 0);

  const retracted = scriptedFetch([
    response(200, { message: { relation: { 'is-retracted-by': [{}] } } }),
  ]);
  const pulled = await crossrefLookup('10.1000/retracted', retracted);
  assert.equal(pulled.ok, false);
  assert.match(pulled.why, /is-retracted-by/);
  assert.equal(retracted.calls.length, 1);

  const noticed = scriptedFetch([
    response(200, work),
    response(200, { message: { items: [{ DOI: '10.1000/notice', 'update-to': [{ DOI: '10.1000/example', type: 'retraction' }] }] } }),
  ]);
  const notice = await crossrefLookup('10.1000/example', noticed);
  assert.equal(notice.ok, false);
  assert.match(notice.why, /retraction/);

  const flaky = scriptedFetch([
    response(503, {}),
    response(200, work),
    response(200, notices),
  ]);
  const recovered = await crossrefLookup('10.1000/example', flaky);
  assert.equal(recovered.ok, true);
  assert.equal(flaky.sleeps.length, 1);
  assert.equal(flaky.sleeps[0], 1000);

  const down = scriptedFetch(Array.from({ length: 5 }, () => response(502, {})));
  const failed = await crossrefLookup('10.1000/down', down);
  assert.equal(failed.ok, false);
  assert.match(failed.why, /502/);
  assert.equal(failed.deferred, undefined);
});

test('a verified Crossref result is reused from the file cache', async () => {
  const dir = mkdtempSync(join(tmpdir(), 'citation-gate-'));
  const path = join(dir, 'cache.json');
  const cache = loadFileCache(path);
  const fetch = scriptedFetch([response(200, work), response(200, notices)]);
  const client = createCrossrefClient({ ...fetch, cache, gapMs: 0, maxAttempts: 2 });
  assert.equal((await client.lookup('10.1000/example')).ok, true);
  const reloaded = loadFileCache(path);
  const again = createCrossrefClient({
    fetchImpl: async () => { throw new Error('cache miss'); },
    sleep: async () => {},
    cache: reloaded,
    gapMs: 0,
  });
  assert.equal((await again.lookup('10.1000/example')).ok, true);
  const saved = JSON.parse(readFileSync(path, 'utf8'));
  assert.equal(saved['doi:10.1000/example'].ok, true);
  assert.equal(saved['doi:10.1000/example'].deferred, undefined);
});

test('explicit regulatory and agency sources pass without a DOI or a Crossref call', async () => {
  assert.equal(explicitNonDoiKind({ sourceTier: 'official_label' }), 'regulatory-label');
  assert.equal(explicitNonDoiKind({ sourceTier: 'regulatory_guidance' }), 'agency-page');
  assert.equal(explicitNonDoiKind({ nonDoiSourceType: 'regulatory-label' }), 'regulatory-label');
  const lookupDoi = async () => { throw new Error('DOI lookup should not run'); };
  for (const source of [
    { id: 'MF-LABEL-2025', sourceTier: 'official_label', url: 'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=example' },
    { id: 'MF-FDA-GENERICS', sourceTier: 'regulatory_guidance', url: 'https://www.fda.gov/drugs/generic-drugs/generic-drug-facts' },
    { id: 'CTX-D08-LABEL', nonDoiSourceType: 'agency-page', url: 'https://www.fda.gov/drugs/example' },
  ]) {
    const result = await evaluateSource(source, { lookupDoi });
    assert.deepEqual(result.failures, [], source.id);
  }
});

test('a non-DOI type still needs a public URL, and a host name is not a type', async () => {
  const unlabeled = await evaluateSource({
    id: 'CTX-D08-LABEL',
    sourceType: 'context',
    url: 'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=example',
  }, {});
  assert.deepEqual(unlabeled.failures, ['has no DOI']);

  const missingUrl = await evaluateSource({
    id: 'LABEL',
    nonDoiSourceType: 'regulatory-label',
    url: '/research/local',
  }, {});
  assert.deepEqual(missingUrl.failures, ['is typed regulatory-label but has no public http(s) URL']);
});

test('a DOI is still checked when a non-DOI type is also set', async () => {
  const calls = [];
  const result = await evaluateSource({
    id: 'PAPER',
    nonDoiSourceType: 'regulatory-label',
    url: 'https://dailymed.nlm.nih.gov/example',
    doi: 'https://doi.org/10.1000/fake',
  }, {
    onFile: '10.1000/fake\n',
    lookupDoi: async (doi) => { calls.push(doi); return { ok: false, why: 'Crossref HTTP 404' }; },
  });
  assert.deepEqual(calls, ['10.1000/fake']);
  assert.deepEqual(result.failures, ['DOI 10.1000/fake failed: Crossref HTTP 404']);
});

test('missing, retracted, and rate-limited DOI results keep their own outcomes', async () => {
  const absent = await evaluateSource({ id: 'P', doi: '10.1000/absent' }, {
    onFile: '',
    lookupDoi: async () => { throw new Error('missing DOI should not call Crossref'); },
  });
  assert.match(absent.failures[0], /not in research\/deposits or research\/corpus/);

  const retracted = await evaluateSource({ id: 'P', doi: '10.1000/bad' }, {
    onFile: '10.1000/bad',
    lookupDoi: async () => ({ ok: false, why: 'Crossref relation is-retracted-by' }),
  });
  assert.match(retracted.failures[0], /is-retracted-by/);

  const limited = await evaluateSource({ id: 'P', doi: '10.1000/limited' }, {
    onFile: '10.1000/limited',
    lookupDoi: async () => ({ ok: true, deferred: true, rateLimited: true, why: 'Crossref HTTP 429 after retries' }),
  });
  assert.deepEqual(limited.failures, []);
  assert.match(limited.warnings[0], /429/);
});

test('a no-DOI article passes only when Europe PMC has that PubMed id and no DOI', async () => {
  const source = {
    id: 'P-D08-OVARIAN-2009',
    nonDoiSourceType: 'no-doi-article',
    pmid: '22495656',
    url: 'https://pubmed.ncbi.nlm.nih.gov/22495656/',
  };
  const unfiled = await evaluateSource(source, {
    onFile: '',
    lookupPmid: async () => { throw new Error('unfiled PMID should not call Europe PMC'); },
  });
  assert.match(unfiled.failures[0], /PMID 22495656 not in research/);

  const pass = await evaluateSource(source, {
    onFile: 'pmid 22495656 DOI NOT PRINTED',
    lookupPmid: async () => ({ ok: true }),
  });
  assert.deepEqual(pass.failures, []);

  const hidden = await evaluateSource(source, {
    onFile: '22495656',
    lookupPmid: async () => ({ ok: false, why: 'PMID 22495656 has DOI 10.5582/ddt.3.243; cite that DOI instead of a non-DOI type' }),
  });
  assert.match(hidden.failures[0], /cite that DOI/);

  const limited = await evaluateSource(source, {
    onFile: '22495656',
    lookupPmid: async () => ({ ok: true, deferred: true, why: 'Europe PMC HTTP 429 after retries' }),
  });
  assert.deepEqual(limited.failures, []);

  const fetch = scriptedFetch([
    response(200, { resultList: { result: [{ pmid: '22495656', title: 'Ivermectin inactivates the kinase PAK1' }] } }),
  ]);
  const live = await europePmcPmid('22495656', fetch);
  assert.equal(live.ok, true);
  assert.match(fetch.calls[0], /EXT_ID%3A22495656/);

  const withDoi = scriptedFetch([
    response(200, { resultList: { result: [{ pmid: '36070710', doi: '10.1056/NEJMoa2201662' }] } }),
  ]);
  const found = await europePmcPmid('36070710', withDoi);
  assert.equal(found.ok, false);
  assert.match(found.why, /10\.1056\/nejmoa2201662/);
});
