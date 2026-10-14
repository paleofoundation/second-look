#!/usr/bin/env python3
"""Exercise the exact independently audited candidate in an isolated private store."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('root', 'packet', 'plan', 'readiness'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    sys.path.insert(0, str(root))
    from scripts.research_ingest.cli import canonical, load, require, safe_path, sha, preflight, check_readiness, store_lock, apply_context, atomic
    packet, plan = Path(args.packet).resolve(), Path(args.plan).resolve()
    require(packet != root / 'work/research-ingest' and packet.is_relative_to(root / 'work/research-ingest'), 'Dedicated private packet required')
    context = preflight(root, packet, plan, packet / 'manifest.json', 'validate')
    check_readiness(args.readiness, context['plan'], context['planHash'])
    pins = {p['path']: p['sha256'] for p in context['plan']['inputs']}
    require(pins.get(Path(__file__).resolve().relative_to(root).as_posix()) == sha(Path(__file__)), 'Pin the actual integration checker')
    independent = load(packet / 'audit/independent_audit.json')
    require(independent['status'] == 'PASS' and independent['candidateDigest'] == context['candidateDigest'], 'Current independent technical audit required')
    require(independent['author'] == 'codex/root' and independent['auditor'].casefold() != independent['author'].casefold(), 'Distinct independent auditor required')
    expected = {w['path']: w['sha256'] for w in context['writes']}
    targets = sorted(w['target'] for w in context['writes'])
    require(independent['targets'] == targets and independent['inputHashes'] == expected, 'Independent scope differs')
    for item in independent['evidence']:
        require(sha(safe_path(packet, item['path'])) == item['sha256'], 'Independent evidence changed')
    with tempfile.TemporaryDirectory(prefix='remaprx-full-review-replay-') as temporary:
        scratch = Path(temporary)
        for item in context['plan']['inputs']:
            destination = safe_path(scratch, item['path'])
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(safe_path(root, item['path']), destination)
        for item in context['writes']:
            if item['beforeData'] is not None:
                atomic(safe_path(scratch, item['target']), item['beforeData'])
        scratch_plan = scratch / 'test-plan.json'
        scratch_plan.write_bytes(plan.read_bytes())
        with store_lock(scratch):
            first = apply_context(preflight(scratch, packet, scratch_plan, packet / 'manifest.json', 'validate'))
        with store_lock(scratch):
            second = apply_context(preflight(scratch, packet, scratch_plan, packet / 'manifest.json', 'validate'))
        require(first['changedFiles'] == sum(w['beforeData'] != w['data'] for w in context['writes']) and second['changedFiles'] == 0,
                'Unexpected initial or repeat changes')
        require(all(sha(safe_path(scratch, w['target'])) == w['sha256'] for w in context['writes']), 'Isolated output differs')
        for value in (first, second):
            if value.get('journal'):
                value['journal'] = 'temporary-store/journals/' + Path(value['journal']).name
    require(preflight(root, packet, plan, packet / 'manifest.json', 'validate')['candidateDigest'] == context['candidateDigest'], 'Candidate changed during replay')
    audit = packet / 'audit'
    evidence = {'status': 'PASS', 'candidateDigest': context['candidateDigest'],
        'checkedAt': datetime.now(timezone.utc).isoformat(), 'independentAuditSha256': sha(audit / 'independent_audit.json'),
        'isolatedFirst': first, 'isolatedRepeat': second, 'scope': 'Exact private full-review technical checks',
        'scientificApproval': False, 'performedCanonicalImport': False}
    def save(name, value):
        path = audit / name
        require(not path.exists(), 'Preserve previous reports')
        atomic(path, canonical(value))
    save('integrator-evidence.json', evidence)
    base = {'status': 'PASS', 'candidateDigest': context['candidateDigest'], 'targets': targets, 'inputHashes': expected,
        'evidence': independent['evidence'] + [{'path': 'audit/integrator-evidence.json', 'sha256': sha(audit / 'integrator-evidence.json')}]}
    checks = {
        'schema': {'strict_manifest_and_json': True, 'independent_full_review_schema_and_completeness_checked': True},
        'identity': {'independent_canonical_report_review_and_result_identities_checked': True, 'one_index_entry_per_report': True},
        'source_integrity': {'separate_exact_candidate_scientific_audit_retained': True, 'all_pinned_files_current': True},
        'preservation': {'historical_corpus_and_preexisting_reviews_preserved': True, 'human_approval_and_release_false': True},
        'idempotence': {'actual_candidate_exercised_in_isolated_store': True, 'unchanged_repeat_zero': True, 'output_hashes_match': True}}
    for kind, values in checks.items():
        save(kind + '.json', {**base, 'checks': values})
    print(json.dumps({'status': 'PASS', 'candidateDigest': context['candidateDigest'],
        'firstChanged': first['changedFiles'], 'repeatChanged': second['changedFiles'], 'performedCanonicalImport': False}))


if __name__ == '__main__':
    main()
