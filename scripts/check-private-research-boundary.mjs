import assert from 'node:assert/strict';
import {privateSourceBoundary} from '../build/private-source-boundary.ts';

let handler;
privateSourceBoundary().configureServer({middlewares:{use(value){handler=value;}}});
const privatePaths = [
  '/research/corpus/RRX-INGEST-001/sources.jsonl',
  '/research/batches/RRX-INGEST-001/PLAN.md',
  '/.research-ingest/journal.json',
  '/@fs/tmp/site/research/corpus/results.jsonl?raw',
  '/research%2Fcorpus%2Fresults.jsonl',
  '/research%252Fbatches%252Fplan.json',
  '/research%5Ccorpus%5Creviews.jsonl',
  '/data/private-reviews.json',
  '/research/x/../corpus/private.json',
  '/@fs/tmp/site/research/x/../corpus/private.json',
  '/research%252525252Fcorpus%252525252Fprivate.json',
  '/research/CORPUS/results.jsonl',
  '/data/private-reviews.json%3Fraw',
  '/work/research-ingest/RRX-INGEST-001/recovery/candidate/reviews.jsonl',
];
for (const url of privatePaths) {
  const headers = {};
  const res = {setHeader(k,v){headers[k]=v;},end(){this.ended=true;}};
  handler({url},res,()=>assert.fail(`Private path passed: ${url}`));
  assert.equal(res.statusCode,404,url);
  assert.equal(headers['Cache-Control'],'no-store');
}
for (const url of ['/research/P-COVIDOUT-2023','/research','/drugs/itraconazole','/data/public-content.json']) {
  let next=false;
  handler({url},{end(){assert.fail(`Public route blocked: ${url}`);}},()=>{next=true;});
  assert.equal(next,true,url);
}
const bad={end(){}};
handler({url:'/%ZZ'},bad,()=>assert.fail('Malformed URL passed'));
assert.equal(bad.statusCode,400);
console.log(JSON.stringify({status:'PASS',privatePaths:privatePaths.length,publicPaths:4,malformed:1}));
