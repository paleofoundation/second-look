#!/usr/bin/env python3
"""Prepare one independently audited private review; never approve or apply it."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from types import SimpleNamespace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('root', 'review-dir', 'candidate', 'audit', 'source-map', 'packet', 'plan-dir', 'plan-id'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--check-script', help='Pin the integration replay/report implementation before GP')
    args = parser.parse_args()
    root = Path(args.root).resolve()
    sys.path.insert(0, str(root))
    from scripts.research_full_review import validate
    from scripts.research_ingest.cli import canonical, check_inputs, digest, require, safe_path, sha

    here = Path(__file__).resolve().parent
    review_dir = safe_path(root, args.review_dir)
    candidate = safe_path(root, args.candidate)
    audit = safe_path(root, args.audit)
    source_map = safe_path(root, args.source_map)
    schema = here / 'schemas/full-review.schema.json'
    question_map = root / 'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json'
    captured = {}
    def capture(path, expected=None):
        name = path.relative_to(root).as_posix()
        data = path.read_bytes()
        value = digest(data)
        require(expected is None or value == expected, 'Control differs from its approved pin: ' + name)
        require(name not in captured or captured[name][0] == value, 'Control changed during preparation: ' + name)
        captured[name] = (value, data)
        return data
    source_plan = json.loads(capture(review_dir / 'plan.json'))
    pins = {x['path']: x['sha256'] for x in source_plan['inputs']}
    for name, expected in pins.items():
        capture(safe_path(root, name), expected)
    baseline_path = here / 'integration-baseline.json'
    paths = [candidate, audit, source_map, baseline_path, Path(__file__).resolve(),
        review_dir / 'readiness.json', review_dir / 'assignment.json',
        root / 'AGENTS.md', root / 'docs/PROJECT-RULES.md', root / 'docs/RESEARCH-INGEST.md',
        root / 'docs/RULE-CHANGELOG.md', root / 'scripts/research_ingest/contracts.py',
        root / 'scripts/research_ingest/__main__.py']
    if args.check_script:
        paths.append(safe_path(root, args.check_script))
    for path in paths:
        capture(path, pins.get(path.relative_to(root).as_posix()))
    source_audit = json.loads(captured[audit.relative_to(root).as_posix()][1])
    for item in source_audit['evidence']:
        capture(safe_path(root, item['path']), item['sha256'])
    baseline = json.loads(captured[baseline_path.relative_to(root).as_posix()][1])
    for item in baseline['files']:
        capture(safe_path(root, item['path']), item['sha256'])
    # Freeze all bytes before validation; never refresh an approved pin afterward.
    pins = {name: value[0] for name, value in captured.items()}
    check_inputs(root, {'inputs': [{'path': p, 'sha256': h} for p, h in pins.items()]})
    validation = validate(SimpleNamespace(root=str(root), plan=str(review_dir / 'plan.json'),
        readiness=str(review_dir / 'readiness.json'), assignment=str(review_dir / 'assignment.json'),
        candidate=str(candidate), schema=str(schema), question_map=str(question_map),
        audit=str(audit), source_map=str(source_map)))
    require(validation['completionState'] == 'accepted_private', 'Independent full-review acceptance required')
    candidate_data = captured[candidate.relative_to(root).as_posix()][1]
    review = json.loads(candidate_data)
    report_id = review['canonicalReportId']
    require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', report_id), 'Unsafe canonical report identity')
    require(report_id.casefold() != 'index', 'Reserved review identity')

    destination = safe_path(root, args.plan_dir)
    packet = safe_path(root, args.packet)
    require(destination.is_relative_to(here) and not destination.exists(), 'Use a fresh continuation plan directory')
    require(packet.is_relative_to(root / 'work/research-ingest') and not packet.exists(), 'Use a fresh isolated work packet')
    target = 'research/corpus/RRX-INGEST-001/full-reviews/' + report_id + '.json'
    index_target = 'research/corpus/RRX-INGEST-001/full-reviews/index.json'
    require(target != index_target, 'Reserved review identity')
    old_index = safe_path(root, index_target)
    index_data = old_index.read_bytes() if old_index.exists() else None
    old_review = safe_path(root, target)
    base_hashes = {index_target: digest(index_data) if index_data is not None else None,
                   target: sha(old_review) if old_review.exists() else None}
    def check_bases():
        for name, expected in base_hashes.items():
            current = safe_path(root, name)
            require((sha(current) if current.exists() else None) == expected, 'Canonical base changed during preparation: ' + name)
    index = json.loads(index_data) if index_data is not None else {
        'schemaVersion': 'remaprx-private-full-review-index-v1', 'reviews': []}
    require(index.get('schemaVersion') == 'remaprx-private-full-review-index-v1', 'Unknown private review index')
    require(len({x['canonicalReportId'].casefold() for x in index['reviews']}) == len(index['reviews']), 'Duplicate/case-colliding canonical review index')
    for item in index['reviews']:
        identity = item['canonicalReportId']
        require(identity.casefold() != report_id.casefold() or identity == report_id, 'Case-colliding review identity')
        require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', identity) and identity.casefold() != 'index', 'Invalid indexed review identity')
        expected_path = 'research/corpus/RRX-INGEST-001/full-reviews/' + identity + '.json'
        require(item['path'] == expected_path, 'Index path differs from canonical review identity')
        capture(safe_path(root, expected_path), item['sha256'])
        pins[expected_path] = item['sha256']
    if old_review.parent.exists():
        require(all(p.name.casefold() != old_review.name.casefold() or p.name == old_review.name
                    for p in old_review.parent.iterdir()), 'Case-colliding review filename')
    # This continuation permits new reviews and exact repeats. Replacing a
    # completed review needs a separate version-preservation/invalidation plan.
    previous = next((x for x in index['reviews'] if x['canonicalReportId'] == report_id), None)
    require(previous is not None or base_hashes[target] is None, 'Unindexed existing review body; reconcile before preparation')
    entry = {'canonicalReportId': report_id, 'reviewId': review['reviewId'], 'path': target,
        'sha256': digest(candidate_data), 'sourcePlanSha256': validation['planSha256'],
        'independentAuditPath': audit.relative_to(root).as_posix(), 'independentAuditSha256': pins[audit.relative_to(root).as_posix()],
        'processingState': 'independently_verified_ai_review', 'fullScientificReviewComplete': True,
        'appraisalMethod': 'source-bound qualitative design-specific appraisal; not formal GRADE',
        'humanReviewed': False, 'scientificReleaseApproved': False, 'released': False,
        'previousReview': previous}
    if previous and all(previous.get(k) == v for k, v in entry.items() if k != 'previousReview'):
        entry = previous
    elif previous:
        require(False, 'Review revision requires a separate preservation/invalidation contract')
    index['reviews'] = sorted([x for x in index['reviews'] if x['canonicalReportId'] != report_id] + [entry],
                              key=lambda x: x['canonicalReportId'])
    payloads = {target: candidate_data, index_target: canonical(index)}
    require(digest(candidate_data) == validation['candidateSha256'], 'Validated candidate differs from captured bytes')
    for path in payloads:
        pins.pop(path, None)
    plan = {'schemaVersion': 'remaprx-ingest-plan-v1', 'planId': args.plan_id,
        'createdAt': datetime.now(timezone.utc).isoformat(), 'operations': ['validate', 'stage', 'diff', 'apply'],
        'allowedTargets': sorted(payloads), 'inputs': [{'path': p, 'sha256': h} for p, h in sorted(pins.items())],
        'contract': {'scope': 'One independently audited complete AI review in the private corpus and canonical review index',
            'canonicalReportId': report_id, 'author': 'codex/root', 'sourceValidation': validation,
            'historicalFilesPreserved': len(baseline['files']), 'humanApproval': False, 'released': False,
            'nextGate': 'New GP Plan PASS and independent technical acceptance before integrator apply'}}
    check_inputs(root, plan)
    check_bases()
    destination.mkdir(parents=True)
    packet.mkdir(parents=True)
    plan_path = destination / 'plan.json'
    plan_path.write_bytes(canonical(plan))
    entries = []
    for path, data in sorted(payloads.items()):
        relative = 'candidate/' + path
        output = safe_path(packet, relative)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
        entries.append({'target': path, 'path': relative, 'sha256': sha(output),
                        'baseSha256': base_hashes[path]})
    manifest = {'schemaVersion': 'remaprx-candidate-v1', 'planId': args.plan_id,
        'planSha256': sha(plan_path), 'batchId': 'RRX-CAL-T1-' + report_id, 'author': 'codex/root', 'files': entries}
    for output in (packet / 'manifest.json', destination / 'manifest.json'):
        output.write_bytes(canonical(manifest))
    (destination / 'source-validation.json').write_bytes(canonical(validation))
    check_inputs(root, plan)
    check_bases()
    print(json.dumps({'status': 'PREPARED_REQUIRES_GP_AND_TECHNICAL_ACCEPTANCE', 'files': len(entries),
        'plan': str(plan_path), 'planSha256': sha(plan_path), 'packet': str(packet), 'performedImport': False}))


if __name__ == '__main__':
    main()
