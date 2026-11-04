import test from 'node:test';
import assert from 'node:assert/strict';
import {governanceMergeDecision, latestGovernanceCheck, waitForGovernance} from '../scripts/require-governance-check.mjs';

test('a later governance failure blocks merge after an older success', () => {
  const checks = [
    {name: 'governance', status: 'COMPLETED', conclusion: 'SUCCESS', startedAt: '2026-11-04T20:14:00Z'},
    {name: 'gate', status: 'COMPLETED', conclusion: 'SUCCESS', startedAt: '2026-11-04T20:15:00Z'},
    {name: 'governance', status: 'COMPLETED', conclusion: 'FAILURE', startedAt: '2026-11-04T20:15:10Z'},
  ];
  assert.equal(latestGovernanceCheck(checks).conclusion, 'FAILURE');
  const decision = governanceMergeDecision(checks);
  assert.equal(decision.action, 'fail');
});

test('in-progress governance waits, and success allows merge', () => {
  assert.equal(governanceMergeDecision([]).action, 'wait');
  assert.equal(governanceMergeDecision([
    {name: 'governance', status: 'IN_PROGRESS', startedAt: '2026-11-04T20:15:10Z'},
    {name: 'governance', status: 'COMPLETED', conclusion: 'FAILURE', startedAt: '2026-11-04T20:14:00Z'},
  ]).action, 'wait');
  assert.equal(governanceMergeDecision([
    {name: 'governance', status: 'COMPLETED', conclusion: 'SUCCESS', startedAt: '2026-11-04T20:16:00Z'},
    {name: 'governance', status: 'COMPLETED', conclusion: 'FAILURE', startedAt: '2026-11-04T20:14:00Z'},
  ]).action, 'merge');
});

test('cancelled, skipped, and timed-out governance checks fail closed', () => {
  for (const conclusion of ['CANCELLED', 'SKIPPED', 'TIMED_OUT', 'STALE']) {
    assert.equal(governanceMergeDecision([
      {name: 'governance', status: 'COMPLETED', conclusion, startedAt: '2026-11-04T20:15:10Z'},
    ]).action, 'fail', conclusion);
  }
});

test('the waiter merges only after the check succeeds', async () => {
  const reads = [
    [{name: 'governance', status: 'QUEUED', startedAt: '2026-11-04T20:15:00Z'}],
    [{name: 'governance', status: 'COMPLETED', conclusion: 'SUCCESS', startedAt: '2026-11-04T20:15:00Z'}],
  ];
  const decision = await waitForGovernance({
    pr: '42',
    repo: 'example/repo',
    attempts: 3,
    intervalMs: 1,
    readChecks: async () => reads.shift(),
    pause: async () => {},
  });
  assert.equal(decision.action, 'merge');
});

test('the waiter fails closed when governance never succeeds', async () => {
  const decision = await waitForGovernance({
    pr: '42',
    repo: 'example/repo',
    attempts: 2,
    intervalMs: 1,
    readChecks: async () => [],
    pause: async () => {},
  });
  assert.equal(decision.action, 'fail');
  assert.match(decision.reason, /Timed out/);
});
