import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync} from 'node:fs';
import {validateContext} from '../scripts/validate-prose-context.mjs';
const example = JSON.parse(readFileSync(new URL('../research/batches/RRX-PROSE-MINIMUM-20261104/synthetic-context-example-v3.json', import.meta.url)));
test('synthetic example validates only as synthetic', () => {
  assert(validateContext(example, [], {synthetic: true}));
  assert.throws(() => validateContext(example, []), /outside accepted inventory/);
});
test('full text cannot claim missing bytes or identity-unsafe observations', () => {
  assert.throws(() => validateContext({...example, accessStatus: 'full_text'}, [], {synthetic: true}), /actual private file/);
  assert.throws(() => validateContext({...example, observations: [{claim: 'Invented', locator: 'None', scope: 'None', kind: 'safety'}]}, [], {synthetic: true}), /Unverified or inaccessible/);
});
test('receipt cannot omit resolved URL, media type or product identity', () => {
  for (const field of ['resolvedUrl', 'mediaType', 'identity']) {
    const invalid = {...example}; delete invalid[field];
    assert.throws(() => validateContext(invalid, [], {synthetic: true}), /Missing/);
  }
});
test('restored mechanism identities remain unique and cover condition parents', () => {
  const records = JSON.parse(readFileSync(new URL('../data/public-mechanisms.json', import.meta.url))).drugs;
  const identities = records.map(record => record.drugId ? `drug:${record.drugId}` : record.conditionId ? `condition:${record.conditionId}` : `guides:${[...(record.guideIds || [])].sort().join(',')}`);
  assert.equal(new Set(identities).size, identities.length, 'A drug-only key must not collapse condition/glossary records');
  assert.equal(records.filter(record => record.conditionId).length, 32);
});
