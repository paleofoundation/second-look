#!/usr/bin/env python3
"""Independently audit the RRX-INGEST-001 byte-preserving private checkpoint.

Reads historical source files, candidate files, GP readiness and pinned app inputs.
Writes only an independent evidence/report pair beneath the candidate's audit
directory. Does not apply a candidate, appraise science, or author other reports.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / 'research/batches/RRX-INGEST-001'
AUDITOR = 'codex/identity_review'
EXPECTED_FILES = 47
EXPECTED_COLLECTIONS = {
    'acquisition/sources.jsonl': ('source_id', 2765),
    'acquisition/reports.jsonl': ('id', 1990),
    'acquisition/assets.jsonl': ('id', 1930),
    'draft-science/results.jsonl': ('id', 570),
    'draft-science/claims.jsonl': ('id', 525),
    'draft-science/reviews.jsonl': ('id', 1152),
}
STATE_FIELDS = ('full_review_complete', 'publication_state', 'human_review_status',
                'quarantined', 'verification_state', 'processing_state', 'status',
                'retraction_status', 'numerical_extraction_allowed', 'excluded_from_accepted_support')


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n').encode()


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def decode(data):
    return json.loads(data, object_pairs_hook=unique_keys,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Invalid JSON constant: ' + value)))


def safe(root, relative):
    require(isinstance(relative, str) and relative and '\\' not in relative and '\0' not in relative,
            'Unsafe audit-relative path')
    parts = relative.split('/')
    require(not PurePosixPath(relative).is_absolute() and all(part not in ('', '.', '..') for part in parts),
            'Unsafe audit-relative path: ' + relative)
    path = Path(root)
    for part in parts:
        path /= part
        require(not path.is_symlink(), 'Symlink audit input/output is not allowed: ' + str(path))
    require(path.resolve().is_relative_to(Path(root).resolve()), 'Audit path escapes its root')
    return path


def read_pinned(path, pins, expected=None):
    path = Path(path)
    data = path.read_bytes()
    actual = digest(data)
    require(expected is None or actual == expected, 'Pinned artifact changed: ' + str(path))
    pins[str(path.resolve())] = actual
    return data


def state_values(value, pointer=''):
    result = []
    if isinstance(value, dict):
        for key, item in value.items():
            child = pointer + '/' + key.replace('~', '~0').replace('/', '~1')
            if key in STATE_FIELDS:
                result.append({'pointer': child, 'value': item})
            result.extend(state_values(item, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            result.extend(state_values(item, pointer + '/' + str(index)))
    return result


def audit(packet, plan_path=None, readiness_path=None):
    packet = Path(packet).resolve()
    private_staging = safe(ROOT, 'work/research-ingest').resolve()
    require(packet != private_staging and packet.is_relative_to(private_staging),
            'Candidate must be a dedicated private work/research-ingest attempt directory.')
    pins = {}
    plan_path = Path(plan_path or BATCH / 'plan.json').resolve()
    readiness_path = Path(readiness_path or BATCH / 'readiness.json').resolve()
    plan_bytes = read_pinned(plan_path, pins)
    plan = decode(plan_bytes)
    require(plan.get('schemaVersion') == 'remaprx-ingest-plan-v1', 'Unsupported prospective plan schema.')
    plan_hash = digest(plan_bytes)
    gate = decode(read_pinned(readiness_path, pins))
    require(gate.get('schemaVersion') == 'remaprx-gp-readiness-v1'
            and gate.get('status') == 'PASS' and gate.get('scope') == 'GP_PLAN'
            and gate.get('planId') == plan['planId'] and gate.get('planSha256') == plan_hash,
            'A matching prospective GP Plan PASS is required.')
    require('apply' in plan['operations'], 'Plan does not authorize private checkpoint integration.')
    for pin in plan['inputs']:
        read_pinned(safe(ROOT, pin['path']), pins, pin['sha256'])
    manifest_path = safe(packet, 'manifest.json')
    manifest = decode(read_pinned(manifest_path, pins))
    require(manifest.get('schemaVersion') == 'remaprx-candidate-v1'
            and manifest.get('planId') == plan['planId'] and manifest.get('planSha256') == plan_hash,
            'Candidate does not match this prospective plan.')
    require(manifest.get('batchId') == 'RRX-INGEST-001-RECOVERY', 'This auditor is limited to the private recovery checkpoint.')
    require(manifest.get('author', '').strip() and manifest['author'].strip().casefold() != AUDITOR.casefold(),
            'The auditor must be independent from the candidate author.')
    require(len(manifest.get('files', [])) == EXPECTED_FILES, 'Unexpected recovery file count.')
    recovery = decode(read_pinned(BATCH / 'recovery-inputs.json', pins))
    locations = decode(read_pinned(BATCH / 'inventory/source-locations.json', pins))
    expected = {item['target']: item for item in recovery['files']}
    require(len(expected) == len(recovery['files']) == EXPECTED_FILES, 'Duplicate/missing historical recovery targets.')
    targets = [item['target'] for item in manifest['files']]
    payload_paths = [item['path'] for item in manifest['files']]
    require(len(set(targets)) == len(targets) and set(targets) == set(expected) == set(plan['allowedTargets']),
            'Recovery target set differs from the exact historical plan.')
    require(len(set(payload_paths)) == len(payload_paths), 'Candidate payload is reused for multiple targets.')
    plan_inputs = {item['path']: item['sha256'] for item in plan['inputs']}
    for filename in ['recovery-inputs.json', 'inventory/source-locations.json']:
        relative = (BATCH / filename).relative_to(ROOT).as_posix()
        require(plan_inputs.get(relative) == pins[str((BATCH / filename).resolve())], 'Recovery inputs must be pinned by the plan: ' + filename)

    files, collections, observed_states, bases = [], {}, {}, {}
    private_prefix = 'research/corpus/RRX-INGEST-001/'
    for item in manifest['files']:
        target = item['target']
        require(target.startswith(private_prefix), 'Candidate target is outside the private checkpoint.')
        historical = expected[target]
        require(item['sha256'] == historical['sha256'], 'Candidate rewrites historical source bytes: ' + target)
        source = safe(Path(locations['roots'][historical['rootId']]['path']).resolve(), historical['path'])
        original_bytes = read_pinned(source, pins, historical['sha256'])
        candidate_bytes = read_pinned(safe(packet, item['path']), pins, item['sha256'])
        require(candidate_bytes == original_bytes and len(candidate_bytes) == historical['bytes'],
                'Candidate differs from verified historical bytes: ' + target)
        destination = safe(ROOT, target)
        current = read_pinned(destination, pins) if destination.exists() else None
        current_hash = digest(current) if current is not None else None
        bases[target] = current_hash
        require(current_hash in (item['baseSha256'], item['sha256']), 'Current target differs from the declared base: ' + target)
        if target.endswith('.jsonl'):
            value = [decode(line) for line in candidate_bytes.splitlines() if line.strip()]
        else:
            value = decode(candidate_bytes)
        relative = target.removeprefix(private_prefix)
        states = state_values(value)
        observed_states[relative] = {'fieldCount': len(states), 'sha256': digest(canonical(states))}
        entry = {'target': target, 'candidatePath': item['path'], 'sha256': item['sha256'], 'bytes': len(candidate_bytes),
                 'historicalSource': {'rootId': historical['rootId'], 'path': historical['path']},
                 'targetState': 'absent' if current_hash is None else 'same_candidate' if current_hash == item['sha256'] else 'declared_base',
                 'recordCount': len(value) if isinstance(value, list) else None}
        if relative in EXPECTED_COLLECTIONS:
            identity_key, expected_count = EXPECTED_COLLECTIONS[relative]
            require(isinstance(value, list) and len(value) == expected_count, 'Historical count mismatch: ' + relative)
            ids = [record.get(identity_key) for record in value]
            require(all(isinstance(identity, str) and identity for identity in ids) and len(set(ids)) == len(ids),
                    'Missing or duplicate stable IDs: ' + relative)
            collections[relative] = {'records': len(value), 'uniqueIds': len(ids), 'identityField': identity_key,
                                     'orderedIdsSha256': digest(canonical(ids))}
        if relative == 'draft-science/reviews.jsonl':
            completed = sum(record.get('full_review_complete') is True for record in value)
            require(completed == 0, 'Recovery must not promote draft records to completed reviews.')
            collections[relative]['completedFullReviews'] = completed
            collections[relative]['humanReviewStates'] = dict(Counter(str(record.get('human_review_status')) for record in value))
        files.append(entry)
    # Re-read every input after the full pass, including targets that already exist.
    for pathname, checksum in pins.items():
        require(Path(pathname).is_file() and digest(Path(pathname).read_bytes()) == checksum,
                'Audit input changed during inspection: ' + pathname)
    for target, checksum in bases.items():
        pathname = safe(ROOT, target)
        observed = digest(pathname.read_bytes()) if pathname.exists() else None
        require(observed == checksum, 'Canonical target changed during audit: ' + target)
    candidate_digest = digest(canonical(manifest))
    checks = {'matching_prospective_GP_plan': True, 'all_plan_inputs_current': True,
              'exact_47_file_target_set': True, 'all_candidate_bytes_equal_historical_sources': True,
              'current_base_or_unchanged_candidate_verified': True, 'all_json_and_jsonl_parse_without_duplicate_keys': True,
              'six_collection_counts_and_stable_ids_preserved': True, 'all_record_fields_and_holds_preserved_byte_for_byte': True,
              'zero_completed_full_review_promotions': True, 'all_targets_private_and_no_app_data_targets': True,
              'inputs_rehashed_after_inspection': True, 'no_apply_or_scientific_acceptance_performed': True}
    evidence = {'schemaVersion': 'remaprx-recovery-independent-evidence/1.0', 'status': 'PASS',
                'scope': 'byte-preserving private continuity recovery only', 'candidateDigest': candidate_digest,
                'author': manifest['author'], 'auditor': AUDITOR, 'planId': plan['planId'], 'planSha256': plan_hash,
                'reviewedAt': datetime.now(timezone.utc).isoformat(), 'checks': checks,
                'files': files, 'collections': collections, 'stateFingerprints': observed_states,
                'pinnedArtifacts': pins, 'auditScriptSha256': digest(Path(__file__).read_bytes()),
                'scientificApproval': False, 'fullScientificReviewCompleted': False, 'publicationPerformed': False,
                'limitations': ['Byte continuity preserves historical defects and pending work; it does not reappraise research.',
                                'No new paper acquisition, substantive source extraction, application-data import or release was performed.',
                                'Actual integration and unchanged second-apply verification belong to the integrator.']}
    report = {'status': 'PASS', 'candidateDigest': candidate_digest, 'targets': sorted(targets),
              'inputHashes': {item['path']: item['sha256'] for item in manifest['files']}, 'checks': checks,
              'author': manifest['author'], 'auditor': AUDITOR, 'evidence': []}
    return evidence, report


def write_new_or_same(path, data):
    if path.exists():
        require(path.read_bytes() == data, 'Existing audit differs; preserve it and use a new candidate attempt: ' + str(path))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        os.chmod(path, 0o600)
        stream.write(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', type=Path, required=True)
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--readiness', type=Path)
    args = parser.parse_args()
    try:
        evidence, report = audit(args.packet, args.plan, args.readiness)
        packet = args.packet.resolve()
        evidence_path = safe(packet, 'audit/independent-evidence.json')
        evidence_bytes = canonical(evidence)
        report['evidence'] = [{'path': 'audit/independent-evidence.json', 'sha256': digest(evidence_bytes)}]
        report_path = safe(packet, 'audit/independent_audit.json')
        # An existing output is never silently replaced with a new acceptance date.
        require(not evidence_path.exists() and not report_path.exists(), 'Independent audit already exists; preserve it and use a new attempt for changed inputs.')
        write_new_or_same(evidence_path, evidence_bytes)
        write_new_or_same(report_path, canonical(report))
        print(json.dumps({'status': 'PASS', 'candidateDigest': report['candidateDigest'], 'files': len(evidence['files']),
                          'report': str(report_path), 'reportSha256': digest(report_path.read_bytes()),
                          'evidence': str(evidence_path), 'evidenceSha256': digest(evidence_bytes), 'scientificApproval': False}))
        return 0
    except (ValueError, KeyError, OSError, TypeError) as error:
        print(json.dumps({'status': 'HOLD', 'error': str(error), 'scientificApproval': False, 'performedImport': False}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
