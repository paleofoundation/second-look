/**
 * Decide whether evidence-gate may auto-merge.
 *
 * The separate "Rules and research continuity" workflow reports a status
 * check named governance (the job id). Auto-merge waits for the latest
 * governance check on this pull request and merges only after it succeeds.
 */
import {execFileSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';

export function latestGovernanceCheck(checks) {
  const named = (checks || []).filter(check => check?.name === 'governance');
  if (!named.length) return null;
  return named.slice().sort((a, b) => stamp(b) - stamp(a))[0];
}

function stamp(check) {
  const value = Date.parse(check?.startedAt || check?.completedAt || '');
  return Number.isFinite(value) ? value : 0;
}

/** @returns {{action: 'merge' | 'wait' | 'fail', reason: string}} */
export function governanceMergeDecision(checks) {
  const latest = latestGovernanceCheck(checks);
  if (!latest) return {action: 'wait', reason: 'The governance check has not been reported yet.'};
  const status = String(latest.status || '').toUpperCase();
  const conclusion = String(latest.conclusion || latest.state || '').toUpperCase();
  if (status && status !== 'COMPLETED') return {action: 'wait', reason: `The governance check is ${status}.`};
  if (conclusion === 'SUCCESS') return {action: 'merge', reason: 'The governance check passed.'};
  const finished = conclusion || status || 'no conclusion';
  return {action: 'fail', reason: `The governance check finished with ${finished}.`};
}

export function readChecksFromPullRequest(pr, repo) {
  const raw = execFileSync('gh', ['pr', 'view', String(pr), '--repo', repo, '--json', 'statusCheckRollup'], {
    encoding: 'utf8',
  });
  const payload = JSON.parse(raw);
  return payload.statusCheckRollup || [];
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export async function waitForGovernance({
  pr,
  repo,
  attempts = 60,
  intervalMs = 15000,
  readChecks = readChecksFromPullRequest,
  pause = sleep,
} = {}) {
  let last = {action: 'wait', reason: 'The governance check has not been reported yet.'};
  for (let attempt = 1; attempt <= attempts; attempt++) {
    last = governanceMergeDecision(await readChecks(pr, repo));
    if (last.action !== 'wait') return last;
    if (attempt < attempts) await pause(intervalMs);
  }
  return {action: 'fail', reason: `Timed out waiting for the governance check. ${last.reason}`};
}

async function main() {
  const args = process.argv.slice(2);
  if (args.includes('--decide')) {
    const checks = JSON.parse(readFileSync(args[args.indexOf('--decide') + 1], 'utf8'));
    const decision = governanceMergeDecision(checks);
    console.log(`${decision.action}: ${decision.reason}`);
    process.exit(decision.action === 'merge' ? 0 : decision.action === 'wait' ? 2 : 1);
  }
  const pr = process.env.PR;
  const repo = process.env.GITHUB_REPOSITORY;
  if (!pr || !repo) {
    console.error('PR and GITHUB_REPOSITORY are required.');
    process.exit(1);
  }
  const decision = await waitForGovernance({pr, repo});
  console.log(decision.reason);
  if (decision.action !== 'merge') process.exit(1);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}
