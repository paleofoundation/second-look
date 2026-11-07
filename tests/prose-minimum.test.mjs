import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import test from 'node:test';

const benchmark = readFileSync(new URL('../docs/PROSE-SECTIONS.md', import.meta.url), 'utf8')
  .split('\n').find(line => line.startsWith('> ')).slice(2);
function audit(html, required = false) {
  const result = spawnSync('python3', [fileURLToPath(new URL('../scripts/prose-minimum-html.py', import.meta.url))], {
    input: JSON.stringify([{guideId: 'fixture', slug: '/fixture', hasMechanismProse: false, sections: [{id: 'overview', label: 'Overview', required}], html}]), encoding: 'utf8',
  });
  assert.equal(result.status, 0, result.stderr);
  return JSON.parse(result.stdout);
}
test('exact canonical benchmark passes with inline links and citations excluded', () => {
  const linked = benchmark.replace('mTOR', '<a href="/glossary/mtor">mTOR</a>');
  const result = audit(`<section id="overview"><p>${linked}<sup>[1][2]</sup></p></section>`);
  assert.equal(result.sections[0].words, 113);
  assert.equal(result.sections[0].characters, 845);
  assert.equal(result.failures.length, 0);
});
test('closed and open disclosures, table cells and hidden text cannot pad prose', () => {
  const padding = benchmark.repeat(3);
  const result = audit(`<section id="overview"><p>Short text.</p><details open><p>${padding}</p></details><table><tr><td><p>${padding}</p></td></tr></table><p aria-hidden="true">${padding}</p></section>`);
  assert.equal(result.sections[0].words, 2);
  assert.equal(result.failures.length, 1);
});
test('word and character floors independently prevent a false pass', () => {
  for (const text of [benchmark.split(' ').slice(0, -1).join(' '), Array(113).fill('a').join(' ')]) {
    assert.equal(audit(`<section id="overview"><p>${text}</p></section>`).failures.length, 1);
  }
});
test('visible empty narrative module fails; omitted legacy prose is reported separately', () => {
  const empty = audit('<section id="overview"><h2>Overview</h2></section>', true);
  assert.equal(empty.sections[0].words, 0);
  assert.equal(empty.failures.length, 1);
  const omitted = audit('<span id="overview" aria-hidden="true"></span>');
  assert.equal(omitted.sections.length, 0);
  assert.equal(omitted.omittedStructuredOrHiddenSections.length, 1);
});
