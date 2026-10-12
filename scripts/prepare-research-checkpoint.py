#!/usr/bin/env python3
"""Prepare a private continuity+content candidate. Does not approve or apply it."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.research_ingest.cli import canonical, check_inputs, check_readiness, digest, load, require, safe_path, sha


def write_new(path, value):
    require(not path.exists(), 'Preserve existing attempts; destination exists: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value))


def prepare(args):
    batch = ROOT / 'research/batches/RRX-INGEST-001'
    fanout_dir = safe_path(ROOT, args.fanout_dir)
    controls = {name: load(fanout_dir / name) for name in ['plan.json', 'readiness.json', 'proposals.json', 'bindings.json', 'independent-audit.json']}
    plan, proposals = controls['plan.json'], controls['proposals.json']
    check_readiness(fanout_dir / 'readiness.json', plan, sha(fanout_dir / 'plan.json'))
    historical_pins = {item['path']: item['sha256'] for item in plan['inputs']}
    pins = dict(historical_pins)
    overrides = load(safe_path(ROOT, args.replay_overrides)) if args.replay_overrides else []
    require(len({item['path'] for item in overrides}) == len(overrides), 'Duplicate replay override')
    for item in overrides:
        require(item['path'] in {'docs/PROJECT-RULES.md', 'docs/RULE-CHANGELOG.md'}, 'Only explicitly reviewed document divergence may use archived replay')
        require(item['historicalSha256'] == historical_pins.get(item['path']), 'Historical document hash mismatch')
        require(historical_pins.get(item['snapshotPath']) == item['historicalSha256'], 'Historical snapshot must already be fanout-pinned')
        require(sha(safe_path(ROOT, item['snapshotPath'])) == item['historicalSha256'], 'Historical snapshot changed')
        require(sha(safe_path(ROOT, item['path'])) == item['currentSha256'] and item['reason'], 'Current document or reviewed divergence reason missing')
        pins[item['path']] = item['currentSha256']
    check_inputs(ROOT, {'inputs': [{'path': k, 'sha256': v} for k, v in pins.items()]})
    require(proposals['status'] == 'PASS' and proposals['scope'] == 'read_only_private_draft_proposals', 'Verified private fanout required')
    require(proposals['planSha256'] == sha(fanout_dir / 'plan.json') and proposals['inputHashes'] == historical_pins, 'Proposal inputs/plan changed')
    require(proposals['sourceValidation']['status'] == 'PASS', 'Source validation required')
    require(proposals['humanApproval'] is False and proposals['releaseChanged'] is False, 'Unexpected approval/release')
    candidate_path = safe_path(ROOT, args.candidate)
    candidate = load(candidate_path)
    require(sha(candidate_path) == proposals['sourceValidation']['candidateSha256'], 'Candidate differs from verified fanout')
    require(sha(fanout_dir / 'independent-audit.json') == proposals['verificationSha256'], 'Independent audit changed')
    packet = safe_path(ROOT, args.packet)
    work = safe_path(ROOT, 'work/research-ingest')
    require(packet != work and packet.is_relative_to(work), 'Use a dedicated private work packet')
    require(not packet.exists(), 'Use a fresh packet directory')
    destination = safe_path(ROOT, args.plan_dir)
    require(destination.is_relative_to(batch) and not destination.exists(), 'Use a fresh plan directory in this batch')
    recovery = load(batch / 'recovery/manifest.json')['files']
    require(len(recovery) == 47, 'Expected exact preserved 47-file checkpoint')
    payloads = {}
    for old in recovery:
        path = safe_path(ROOT, old['target'])
        require(sha(path) == old['sha256'], 'Historical checkpoint changed: ' + old['target'])
        payloads[old['target']] = path.read_bytes()
    target = 'research/corpus/RRX-INGEST-001/verified-batches/CAL-07.json'
    require(target not in payloads, 'Target collision')
    bundle = {'schemaVersion': 'remaprx-private-content-checkpoint-v1', 'batchId': 'RRX-INGEST-001-CAL-07',
              'scope': 'Independently verified bounded qualitative findings and private page proposals; incomplete scientific review',
              'candidate': candidate, 'bindings': controls['bindings.json'], 'independentAudit': controls['independent-audit.json'],
              'fanout': proposals, 'humanReviewed': False, 'appraised': False, 'released': False,
              'fullScientificReviewComplete': False}
    payloads[target] = canonical(bundle)
    for name in controls:
        path = fanout_dir / name
        pins[path.relative_to(ROOT).as_posix()] = sha(path)
    for path in [Path(__file__), ROOT / 'scripts/check-research-checkpoint.py', ROOT / 'scripts/audit-research-checkpoint.py',
                 ROOT / 'scripts/audit-research-recovery.py', ROOT / 'tests/research_ingest/test_checkpoint_audit.py',
                 batch / 'recovery/manifest.json', batch / 'recovery/acceptance.json']:
        pins[path.relative_to(ROOT).as_posix()] = sha(path)
    if args.replay_overrides:
        pins[args.replay_overrides] = sha(safe_path(ROOT, args.replay_overrides))
    # Target hashes are bound by the manifest, not simultaneously protected inputs.
    for name in payloads:
        pins.pop(name, None)
    snapshots = []
    previous_map = load(batch / 'app-inputs/1.3/revision-2/source-map.json')['files']
    known = {(p['originalPath'], p['sha256']): p for p in previous_map}
    for name, value in sorted(pins.items()):
        if not (name.startswith(('data/', 'editorial/', 'docs/', 'lib/', 'components/')) or name == 'AGENTS.md'):
            continue
        existing = known.get((name, value))
        if existing:
            require(sha(safe_path(ROOT, existing['snapshotPath'])) == value, 'Preserved snapshot changed')
            snapshots.append(existing)
        else:
            snapshot = destination / 'input-snapshots' / name
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            snapshot.write_bytes(safe_path(ROOT, name).read_bytes())
            require(sha(snapshot) == value, 'Snapshot raced a current edit')
            snapshots.append({'originalPath': name, 'snapshotPath': snapshot.relative_to(ROOT).as_posix(),
                              'sha256': value, 'bytes': snapshot.stat().st_size})
    source_map = destination / 'source-map.json'
    write_new(source_map, {'scope': 'Isolated replay only; never overwrite current app inputs', 'files': snapshots})
    pins[source_map.relative_to(ROOT).as_posix()] = sha(source_map)
    for item in snapshots:
        pins[item['snapshotPath']] = item['sha256']
    current_plan = {'schemaVersion': 'remaprx-ingest-plan-v1', 'planId': args.plan_id,
        'createdAt': datetime.now(timezone.utc).isoformat(), 'operations': ['validate', 'stage', 'diff', 'apply'],
        'allowedTargets': sorted(payloads), 'inputs': [{'path': k, 'sha256': v} for k, v in sorted(pins.items())],
        'contract': {'scope': 'Preserve 47 recovered files unchanged and add exactly one verified private CAL07 bundle',
                     'author': 'codex/root', 'scientificApproval': False, 'publication': False,
                     'fullScientificReviewComplete': False, 'sourcePlanId': candidate['plan_id'],
                     'sourcePlanSha256': candidate['plan_sha256'], 'fanoutPlanSha256': sha(fanout_dir / 'plan.json'),
                     'isolatedReplayOverrides': overrides,
                     'expectedChangedTargets': [target], 'nextGate': 'Independent technical acceptance before integrator apply'}}
    plan_path = destination / 'plan.json'
    write_new(plan_path, current_plan)
    entries = []
    for name, data in sorted(payloads.items()):
        relative = 'candidate/' + name
        output = safe_path(packet, relative)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
        current = safe_path(ROOT, name)
        entries.append({'target': name, 'path': relative, 'sha256': digest(data),
                        'baseSha256': sha(current) if current.exists() else None})
    manifest = {'schemaVersion': 'remaprx-candidate-v1', 'planId': args.plan_id, 'planSha256': sha(plan_path),
                'batchId': 'RRX-INGEST-001-PRIVATE-CHECKPOINT', 'author': 'codex/root', 'files': entries}
    write_new(packet / 'manifest.json', manifest)
    write_new(destination / 'manifest.json', manifest)
    check_inputs(ROOT, current_plan)
    print(json.dumps({'status': 'PREPARED_REQUIRES_GP_AND_ACCEPTANCE', 'files': len(entries),
        'plan': str(plan_path), 'planSha256': sha(plan_path), 'candidateDigest': digest(canonical(manifest)),
        'packet': str(packet), 'canonicalImportPerformed': False}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['fanout-dir', 'candidate', 'packet', 'plan-dir', 'plan-id']:
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--replay-overrides', help='Explicit independently reviewed document-only historical replay map')
    prepare(parser.parse_args())
