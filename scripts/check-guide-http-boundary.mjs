import assert from 'node:assert/strict';

const origin = new URL(process.argv[2] ?? 'http://127.0.0.1:5184').origin;
const results = [];
for (const path of ['/drugs/metformin', '/conditions/long-covid', '/guides/products/metformin', '/guides/products/long-covid', '/guides/read/SL-METFORMIN-1']) {
  const response = await fetch(origin + path, { redirect: 'error' });
  const body = await response.text();
  assert.equal(response.status, 200, path);
  assert.match(response.headers.get('content-type') ?? '', /text\/html/, path);
  if (path.includes('/products/')) {
    assert.match(body, /In development/, path);
    assert.doesNotMatch(body, /href="https:\/\/checkout\.stripe\.com/, path);
  }
  if (path.includes('/read/')) {
    assert.match(body, /noindex/, path);
    assert.doesNotMatch(body, /"manuscript"\s*:/, path);
  }
  results.push({ path, status: response.status, bytes: body.length });
}
for (const [path, method, status] of [
  ['/api/profile', 'GET', 401], ['/api/library/guides', 'GET', 401], ['/api/purchases', 'GET', 401],
  ['/api/guides/SL-METFORMIN-1/reader', 'GET', 401], ['/api/guides/SL-METFORMIN-1/download', 'GET', 401],
  ['/api/checkout', 'POST', 401], ['/api/billing/portal', 'POST', 401], ['/api/stripe/webhook', 'POST', 400],
]) {
  const response = await fetch(origin + path, { method, redirect: 'error', ...(method === 'POST' ? { headers: { 'Content-Type': 'application/json', Origin: origin }, body: '{}' } : {}) });
  assert.equal(response.status, status, path);
  assert.match(response.headers.get('cache-control') ?? '', /private/, path);
  assert.match(response.headers.get('cache-control') ?? '', /no-store/, path);
  const body = await response.json();
  assert.deepEqual(Object.keys(body), ['error'], path);
  results.push({ path, status: response.status, cache: response.headers.get('cache-control') });
}
console.log(JSON.stringify({ checkedAt: new Date().toISOString(), origin, result: 'PASS', checks: results }, null, 2));
