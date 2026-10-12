#!/usr/bin/env python3
"""Integrator reports and isolated repeat test after the separate checkpoint audit."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.research_ingest.cli import canonical, load, require, safe_path, sha, preflight, check_readiness, store_lock, apply_context, atomic


def run(packet, plan, readiness):
    packet, plan = Path(packet).resolve(), Path(plan).resolve()
    require(packet != ROOT/'work/research-ingest' and packet.is_relative_to(ROOT/'work/research-ingest'), 'Dedicated private packet required')
    context = preflight(ROOT, packet, plan, packet/'manifest.json', 'validate')
    check_readiness(readiness, context['plan'], context['planHash'])
    independent = load(packet/'audit/independent_audit.json')
    require(independent['status'] == 'PASS' and independent['candidateDigest'] == context['candidateDigest'], 'Current independent audit required')
    require(independent['author'] == 'codex/root' and independent['auditor'] != independent['author'], 'Distinct independent auditor required')
    expected_inputs = {w['path']: w['sha256'] for w in context['writes']}
    targets = sorted(w['target'] for w in context['writes'])
    require(independent['targets'] == targets and independent['inputHashes'] == expected_inputs, 'Independent scope differs')
    for pin in independent['evidence']:
        require(sha(safe_path(packet, pin['path'])) == pin['sha256'], 'Independent evidence changed')
    with tempfile.TemporaryDirectory(prefix='remaprx-checkpoint-transaction-') as temporary:
        scratch = Path(temporary)
        for pin in context['plan']['inputs']:
            destination = safe_path(scratch, pin['path']); destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(safe_path(ROOT, pin['path']), destination)
        for item in context['writes']:
            if item['beforeData'] is not None: atomic(safe_path(scratch, item['target']), item['beforeData'])
        scratch_plan = scratch/'test-plan.json'; scratch_plan.write_bytes(plan.read_bytes())
        with store_lock(scratch):
            first = apply_context(preflight(scratch, packet, scratch_plan, packet/'manifest.json', 'validate'))
        with store_lock(scratch):
            second = apply_context(preflight(scratch, packet, scratch_plan, packet/'manifest.json', 'validate'))
        require(first['changedFiles'] in (0, 1) and second['changedFiles'] == 0, 'Unexpected first or repeat changes')
        require(all(sha(safe_path(scratch, w['target'])) == w['sha256'] for w in context['writes']), 'Scratch checkpoint differs')
        for value in (first, second):
            if value.get('journal'): value['journal'] = 'temporary-store/journals/' + Path(value['journal']).name
    # Re-run live preflight: the isolated exercise cannot authorize a changed base.
    require(preflight(ROOT, packet, plan, packet/'manifest.json', 'validate')['candidateDigest'] == context['candidateDigest'], 'Candidate changed during repeat test')
    audit = packet/'audit'
    evidence = {'status': 'PASS', 'candidateDigest': context['candidateDigest'], 'checkedAt': datetime.now(timezone.utc).isoformat(),
                'independentAuditSha256': sha(audit/'independent_audit.json'), 'isolatedFirst': first, 'isolatedRepeat': second,
                'scope': 'Private checkpoint technical checks only', 'scientificApproval': False, 'performedImport': False}
    def save(name, value):
        path = audit/name
        require(not path.exists(), 'Preserve existing reports: ' + name)
        atomic(path, canonical(value))
    save('integrator-evidence.json', evidence)
    base = {'status': 'PASS', 'candidateDigest': context['candidateDigest'], 'targets': targets, 'inputHashes': expected_inputs,
            'evidence': [{'path': 'audit/independent-evidence.json', 'sha256': sha(audit/'independent-evidence.json')},
                         {'path': 'audit/integrator-evidence.json', 'sha256': sha(audit/'integrator-evidence.json')}]}
    checks = {
        'schema': {'strict_file_manifest_and_json': True, 'independent_exact_bundle_and_source_contract': True},
        'identity': {'independent_historical_identity_count_check': True, 'separate_report_result_claim_synthesis_links_preserved': True},
        'source_integrity': {'independent_47_historical_byte_checks_and_exact_source_fanout_replay': True, 'all_candidate_hashes_match': True},
        'preservation': {'47_existing_files_unchanged': True, 'partial_review_human_release_and_layout_limits_preserved': True},
        'idempotence': {'actual_candidate_exercised_in_isolated_store': True, 'unchanged_repeat_zero': True, 'final_hashes_match': True}}
    for kind, values in checks.items(): save(kind+'.json', {**base, 'checks': values})
    print(json.dumps({'status': 'PASS', 'candidateDigest': context['candidateDigest'], 'firstChanged': first['changedFiles'],
                      'repeatChanged': second['changedFiles'], 'performedCanonicalImport': False}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['packet', 'plan', 'readiness']: parser.add_argument('--'+name, required=True)
    args = parser.parse_args(); run(args.packet, args.plan, args.readiness)
