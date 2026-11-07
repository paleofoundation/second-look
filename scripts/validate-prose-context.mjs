import assert from 'node:assert/strict';
import {readFileSync, existsSync, statSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

const batch = resolve(import.meta.dirname, '../research/batches/RRX-PROSE-MINIMUM-20261104');
const schema = JSON.parse(readFileSync(resolve(batch, 'context-receipt-v3.schema.json'), 'utf8'));
export function validateContext(record, inventory, {synthetic = false, verifyBytes = true} = {}) {
  for (const field of schema.required) assert(Object.hasOwn(record, field), `Missing ${field}`);
  assert(typeof record.sourceId === 'string' && record.sourceId.length, 'Source ID required');
  assert(typeof record.url === 'string' && /^https:\/\//.test(record.url), 'HTTPS source URL required');
  assert(Number.isFinite(Date.parse(record.retrievedAt)), 'Actual retrieval timestamp required');
  assert(schema.properties.accessStatus.enum.includes(record.accessStatus), 'Invalid access state');
  if (!synthetic) {
    const input = inventory.find(source => source.sourceId === record.sourceId);
    assert(input && input.url === record.url, 'Source identity/URL outside accepted inventory');
  } else assert(record.sourceId.startsWith('SYNTHETIC-'), 'Synthetic examples must be clearly identified');
  assert(record.identity && schema.properties.identity.properties.kind.enum.includes(record.identity.kind), 'Identity kind required');
  assert(typeof record.identity.name === 'string' && record.identity.name.length, 'Actual identity name required');
  assert(record.identity.formulation === null || typeof record.identity.formulation === 'string', 'Formulation must be explicit');
  assert(typeof record.identity.verified === 'boolean', 'Identity verification state required');
  assert(Array.isArray(record.observations) && Array.isArray(record.gaps), 'Observation/gap arrays required');
  if (['full_text', 'partial_text'].includes(record.accessStatus)) {
    assert(typeof record.file === 'string' && record.file.length, 'Acquired bytes require actual private file');
    assert(typeof record.sha256 === 'string' && /^[a-f0-9]{64}$/.test(record.sha256), 'Acquired bytes require SHA-256');
    assert(typeof record.resolvedUrl === 'string' && /^https:\/\//.test(record.resolvedUrl), 'Resolved HTTPS URL required');
    assert(typeof record.mediaType === 'string' && record.mediaType.length, 'Media type required');
    if (verifyBytes) {
      assert(existsSync(record.file) && statSync(record.file).isFile(), 'Raw source file missing');
      assert.equal(createHash('sha256').update(readFileSync(record.file)).digest('hex'), record.sha256, 'Raw byte hash mismatch');
    }
  }
  if (record.observations.length) assert(record.identity.verified && !['not_accessible', 'identity_mismatch'].includes(record.accessStatus), 'Unverified or inaccessible sources cannot support claims');
  for (const observation of record.observations) {
    for (const field of ['claim', 'locator', 'scope']) assert(typeof observation[field] === 'string' && observation[field].trim(), `Observation ${field} required`);
    assert(schema.properties.observations.items.properties.kind.enum.includes(observation.kind), 'Invalid observation kind');
  }
  for (const gap of record.gaps) {
    assert(typeof gap.reason === 'string' && gap.reason.trim(), 'Gap reason required');
    assert(typeof gap.nextAction === 'string' && gap.nextAction.trim(), 'Gap next action required');
    assert(schema.properties.gaps.items.properties.status.enum.includes(gap.status), 'Invalid gap missingness');
  }
  assert(record.observations.length || record.gaps.length, 'No observations requires a documented gap');
  return true;
}
if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const files = process.argv.slice(2).filter(arg => arg !== '--synthetic');
  assert(files.length, 'Supply receipt JSON/JSONL files');
  const inventory = JSON.parse(readFileSync(resolve(batch, existsSync(resolve(batch, 'source-inventory-v3.1.json')) ? 'source-inventory-v3.1.json' : 'source-inventory-v3.json'), 'utf8'));
  let count = 0;
  for (const file of files) {
    const input = readFileSync(resolve(file), 'utf8').trim();
    const records = file.endsWith('.jsonl') ? input.split('\n').filter(Boolean).map(line => JSON.parse(line)) : [JSON.parse(input)];
    for (const record of records) {validateContext(record, inventory, {synthetic: process.argv.includes('--synthetic')}); count++;}
  }
  console.log(`PASS: ${count} context receipt(s), required schema fields, inventory scope, identity/observation boundaries and available raw hashes.`);
}
