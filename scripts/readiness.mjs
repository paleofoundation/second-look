/** Node CLI and file loader. Browser-safe readiness rules live in lib/readiness.mjs. */
import {readFileSync} from 'node:fs';
import {dirname, resolve} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {assessLibrary, deepenQueue, formatReadinessReport, readinessContext} from '../lib/readiness.mjs';
export * from '../lib/readiness.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');

export function loadReadinessInputs() {
  const read = name => JSON.parse(readFileSync(resolve(root, name), 'utf8'));
  const content = read('data/public-content.json');
  return {
    guides: content.guides,
    sources: content.sources,
    context: readinessContext({
      sources: content.sources,
      mechanisms: read('data/public-mechanisms.json'),
      suitability: read('data/treatment-suitability.json'),
      synthesisRows: read('data/public-reader-evidence.json'),
      outcomeSummaries: read('data/outcome-summaries.json'),
      status: read('data/drug-status-table.json'),
    }),
  };
}

function main() {
  const {guides, context} = loadReadinessInputs();
  const results = assessLibrary(guides, context);
  if (process.argv.includes('--json')) {
    console.log(JSON.stringify({
      passing: results.filter(result => result.pass).map(result => result.path),
      queue: deepenQueue(results).map(result => ({path: result.path, failing: result.failing, words: result.words, distinctDois: result.distinctDois})),
      pages: results,
    }, null, 2));
    return;
  }
  console.log(formatReadinessReport(results));
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
