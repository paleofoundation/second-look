#!/usr/bin/env python3
"""Validate one private report review across its primary and companion assets.

This is read-only validation of bytes, declared inspection and provenance, not
proof that a person read a source or that scientific interpretation is correct.
"""
import argparse
from datetime import datetime
from decimal import Decimal
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.research_ingest.cli import Hold, canonical, check_inputs, check_readiness, load, require, resolve_source, safe_path, sha
from scripts.research_ingest.source_validation import reported_scalar, schema_errors

SCHEMA_DIR = 'research/batches/RRX-INGEST-001/continuations/CAL-T1-20261012/schemas'
QUESTION_MAP = 'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json'
TEXT = {'type': 'string', 'minLength': 1, 'pattern': r'\S'}
PROSE = {**TEXT, 'minLength': 30}
HASH = {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}
NULL_TEXT = {'anyOf': [TEXT, {'type': 'null'}]}
NULL_PROSE = {'anyOf': [PROSE, {'type': 'null'}]}
STRINGS = {'type': 'array', 'items': TEXT, 'uniqueItems': True}
CLOSED = {'reported', 'not_reported', 'not_applicable', 'assessed'}
UNFINISHED = {'partial', 'not_extracted', 'not_accessible', 'not_checked', 'not_identifiable', 'conflicting'}
KINDS = ['pdf_page', 'html_section', 'image', 'text_section']
INTEGRITY_KINDS = ['version', 'access', 'supplements', 'registration', 'corrections_retractions']


def obj(properties, required=None):
    return {'type': 'object', 'properties': properties,
            'required': list(properties) if required is None else required, 'additionalProperties': False}


def array(items, minimum=0):
    return {'type': 'array', 'items': items, 'minItems': minimum}


UNIT = obj({'id': TEXT, 'kind': {'enum': KINDS}, 'locator': TEXT})
LOCATOR = obj({'sourceId': TEXT, 'sourceSha256': HASH, 'unitId': TEXT,
               'kind': {'enum': KINDS}, 'locator': TEXT, 'quote': TEXT,
               'figureTable': NULL_TEXT})
LOCATORS = array(LOCATOR)
PIN = obj({'path': TEXT, 'sha256': HASH})
ASSET = obj({'sourceId': TEXT, 'role': {'enum': ['primary', 'companion', 'protocol', 'correction', 'integrity_check', 'other']},
             'required': {'type': 'boolean'}, 'mediaType': {'enum': ['application/pdf', 'text/html', 'image/png', 'image/jpeg', 'image/webp', 'text/plain', 'application/json']},
             'availability': {'enum': ['available', 'not_accessible', 'pending']},
             'sha256': {'anyOf': [HASH, {'type': 'null'}]}, 'bytes': {'type': ['integer', 'null'], 'minimum': 1},
             'path': NULL_TEXT, 'expectedUnits': array(UNIT), 'reason': PROSE})
ASSIGNMENT_SCHEMA = obj({'schemaVersion': {'const': 'remaprx-full-review-assignment-v1'}, 'assignmentId': TEXT,
                         'planId': TEXT, 'canonicalReportId': TEXT, 'reviewId': TEXT, 'assets': array(ASSET, 1)})
INSPECTION = obj({'sourceId': TEXT, 'sourceSha256': {'anyOf': [HASH, {'type': 'null'}]},
                  'status': {'enum': ['full', 'partial', 'not_checked', 'not_accessible']},
                  'unitIdsRead': STRINGS, 'visualUnitIds': STRINGS,
                  'readLog': array(obj({'unitId': TEXT, 'inspectedAt': TEXT, 'method': {'enum': ['native_read', 'text_read', 'visual_read']}, 'notes': PROSE})),
                  'limitations': STRINGS, 'nextAction': NULL_TEXT})
FIELD = obj({'questionId': TEXT, 'field': TEXT, 'status': {'enum': sorted(CLOSED | UNFINISHED)},
             'value': {}, 'reason': PROSE, 'basis': {'enum': ['reported', 'appraisal', 'absence_check', 'design_applicability', 'unfinished']},
             'sourceLocators': LOCATORS, 'assessedAssetIds': STRINGS, 'experimentIds': STRINGS,
             'numericClaimIds': STRINGS, 'nextAction': NULL_TEXT})
ANSWER = obj({'questionId': TEXT, 'status': {'enum': ['answered', 'draft']}, 'answer': NULL_PROSE,
              'appraisalRationale': NULL_PROSE, 'inputFields': STRINGS, 'experimentIds': STRINGS,
              'sourceLocators': LOCATORS, 'limitations': STRINGS})
EXPERIMENT = obj({'id': TEXT, 'label': TEXT, 'design': TEXT, 'experimentalUnit': TEXT,
                  'studyIds': STRINGS, 'sourceLocators': array(LOCATOR, 1)})
INTEGRITY = obj({'kind': {'enum': INTEGRITY_KINDS}, 'status': {'enum': ['checked', 'not_applicable', 'partial', 'not_checked', 'not_accessible', 'conflicting']},
                 'checkedAt': NULL_TEXT, 'scope': PROSE, 'rationale': PROSE,
                 'sourceLocators': LOCATORS, 'limitations': STRINGS, 'nextAction': NULL_TEXT})
NUMBER = obj({'id': TEXT, 'questionId': TEXT, 'field': TEXT, 'value': {'type': ['number', 'null']},
              'units': TEXT, 'basis': {'enum': ['exact_reported', 'calculated', 'graph_estimate']},
              'reportedText': NULL_TEXT, 'precision': PROSE, 'sourceLocators': array(LOCATOR, 1),
              'calculationProvenance': NULL_PROSE, 'limitation': NULL_PROSE})
ARM = obj({'id': TEXT, 'label': TEXT, 'role': TEXT, 'sampleSizeNumericClaimId': NULL_TEXT})
RESULT = obj({'id': TEXT, 'experimentId': TEXT, 'endpoint': TEXT, 'population': TEXT,
              'comparison': TEXT, 'arms': array(ARM), 'timepoint': TEXT,
              'outcomeType': {'enum': ['continuous', 'binary', 'time_to_event', 'mechanistic', 'qualitative', 'other']},
              'numericClaimIds': STRINGS, 'sourceLocators': array(LOCATOR, 1),
              'interpretation': PROSE, 'limitations': STRINGS})
CLAIM = obj({'id': TEXT, 'text': PROSE, 'basis': {'enum': ['observed_result', 'author_conclusion', 'reviewer_interpretation']},
             'resultIds': {**STRINGS, 'minItems': 1}, 'sourceLocators': array(LOCATOR, 1)})
COVERAGE = obj({'sourceId': TEXT, 'unitId': TEXT, 'disposition': {'enum': ['results_recorded', 'no_applicable_result', 'unfinished']},
                'resultIds': STRINGS, 'rationale': PROSE, 'sourceLocators': LOCATORS})
REVIEW_SCHEMA = obj({'schemaVersion': {'const': 'remaprx-full-review-v1'}, 'reviewId': TEXT, 'canonicalReportId': TEXT,
                     'assignmentId': TEXT, 'assignmentSha256': HASH, 'planId': TEXT, 'planSha256': HASH,
                     'questionMapSha256': HASH, 'questionSetVersion': TEXT, 'author': TEXT,
                     'processingState': {'enum': ['draft', 'candidate_complete']},
                     'inspection': array(INSPECTION, 1), 'studyIds': STRINGS, 'familyIds': STRINGS,
                     'experiments': array(EXPERIMENT), 'results': array(RESULT), 'claims': array(CLAIM),
                     'resultCoverage': array(COVERAGE), 'identityRationale': PROSE,
                     'relatedReports': array(obj({'canonicalReportId': TEXT, 'relationship': TEXT, 'rationale': PROSE})),
                     'inputs': {**array(FIELD), 'minItems': 67, 'maxItems': 67},
                     'answers': {**array(ANSWER), 'minItems': 15, 'maxItems': 15},
                     'sourceIntegrity': {**array(INTEGRITY), 'minItems': 5, 'maxItems': 5},
                     'numericClaims': array(NUMBER), 'sourceLimitations': STRINGS,
                     'humanApproval': {'const': False}, 'released': {'const': False}})
REVIEW_SCHEMA['allOf'] = [{'if': {'properties': {'processingState': {'const': 'candidate_complete'}}},
                          'then': {'properties': {key: {'minItems': 1} for key in ('experiments', 'results', 'claims', 'resultCoverage')}}}]
AUDIT_CHECKS = ['sourceIdentity', 'allRequiredAssetsInspected', 'allQuestionInputs', 'allAnswers',
                'numericClaims', 'studyExperimentIdentity', 'appraisalRationale', 'sourceIntegrity', 'limitations']
AUDIT_SCHEMA = obj({'schemaVersion': {'const': 'remaprx-full-review-audit-v1'}, 'status': {'const': 'PASS'},
                    'scope': {'const': 'independent_full_report_review'}, 'author': TEXT, 'auditor': TEXT,
                    'reviewedAt': TEXT, 'candidateSha256': HASH, 'planSha256': HASH, 'assignmentSha256': HASH,
                    'questionMapSha256': HASH, 'sourceHashes': array(obj({'sourceId': TEXT, 'sha256': HASH}), 1),
                    'checks': obj({name: {'const': True} for name in AUDIT_CHECKS}),
                    'evidence': array(PIN, 1), 'limitations': STRINGS,
                    'humanApproval': {'const': False}, 'released': {'const': False}})
SCHEMAS = {'full-review.schema.json': REVIEW_SCHEMA, 'full-review-assignment.schema.json': ASSIGNMENT_SCHEMA,
           'full-review-audit.schema.json': AUDIT_SCHEMA}
for _schema in SCHEMAS.values():
    _schema['$schema'] = 'https://json-schema.org/draft/2020-12/schema'


def dated(value):
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return parsed.tzinfo is not None
    except (ValueError, AttributeError, TypeError):
        return False


def question_fields(question_map):
    questions = question_map.get('questions', [])
    require(len(questions) == 15 and {q['id'] for q in questions} == {f'Q{i:02}' for i in range(1, 16)}, 'Question map must contain unique Q01-Q15')
    fields = [(q['id'], field) for q in questions for field in q['inputFields']]
    require(len(fields) == len(set(fields)) == 67, 'Question map must contain exactly 67 unique required fields')
    return set(fields)


def make_template(assignment, assignment_sha, plan_sha, question_map, question_map_sha, author):
    """Create an honestly uninspected draft; calling code chooses its private path."""
    fields, answers, inspection, coverage = [], [], [], []
    for question in question_map['questions']:
        for field in question['inputFields']:
            fields.append(dict(questionId=question['id'], field=field, status='not_checked', value=None,
                               reason='This required input awaits actual source inspection and appraisal.', basis='unfinished',
                               sourceLocators=[], assessedAssetIds=[], experimentIds=[], numericClaimIds=[],
                               nextAction='Inspect assigned sources and record this field with exact source locators.'))
        answers.append(dict(questionId=question['id'], status='draft', answer=None, appraisalRationale=None,
                            inputFields=question['inputFields'], experimentIds=[], sourceLocators=[], limitations=[]))
    for asset in assignment['assets']:
        inspection.append(dict(sourceId=asset['sourceId'], sourceSha256=asset['sha256'], status='not_checked',
                               unitIdsRead=[], visualUnitIds=[], readLog=[], limitations=[],
                               nextAction='Inspect every assigned unit and record the actual reading method and timestamp.'))
        if asset['required']:
            for unit in asset['expectedUnits']:
                coverage.append(dict(sourceId=asset['sourceId'], unitId=unit['id'], disposition='unfinished',
                                     resultIds=[], rationale='This source unit awaits result accounting or an explicit no-result disposition.', sourceLocators=[]))
    return dict(schemaVersion='remaprx-full-review-v1', reviewId=assignment['reviewId'], canonicalReportId=assignment['canonicalReportId'],
                assignmentId=assignment['assignmentId'], assignmentSha256=assignment_sha, planId=assignment['planId'], planSha256=plan_sha,
                questionMapSha256=question_map_sha, questionSetVersion=question_map['questionSetVersion'], author=author,
                processingState='draft', inspection=inspection, studyIds=[], familyIds=[], experiments=[], results=[], claims=[], resultCoverage=coverage,
                identityRationale='Study and experiment identities await inspection; no identity has been invented by this template.', relatedReports=[],
                inputs=fields, answers=answers, sourceIntegrity=[dict(kind=kind, status='not_checked', checkedAt=None,
                    scope='Prospective integrity scope awaits its actual dated source checks and explicit limitations.',
                    rationale='This required integrity check has not yet been performed.', sourceLocators=[], limitations=[],
                    nextAction='Perform the declared source integrity check and record evidence within its permitted scope.') for kind in INTEGRITY_KINDS],
                numericClaims=[], sourceLimitations=[], humanApproval=False, released=False)


def validate_review(candidate, assignment, question_map):
    """Pure structural/semantic validation; filesystem checks are in validate()."""
    errors = schema_errors(REVIEW_SCHEMA, candidate) + schema_errors(ASSIGNMENT_SCHEMA, assignment)
    if errors:
        return {'errors': errors, 'gaps': []}
    gaps = []
    def check(condition, message):
        if not condition:
            errors.append(message)
    required_fields = question_fields(question_map)
    for name in ('assignmentId', 'planId', 'canonicalReportId', 'reviewId'):
        check(candidate[name] == assignment[name], 'Assignment identity mismatch: ' + name)
    check(candidate['questionSetVersion'] == question_map['questionSetVersion'], 'Question-set version mismatch')
    check(candidate['author'] == candidate['author'].strip(), 'Author identity must not have outer whitespace')
    assets = {a['sourceId']: a for a in assignment['assets']}
    check(len(assets) == len(assignment['assets']), 'Duplicate source asset identity')
    check(sum(a['role'] == 'primary' for a in assets.values()) == 1, 'Exactly one primary report asset is required')
    check(all(a['required'] for a in assets.values() if a['role'] == 'primary'), 'Primary report asset must be required')
    units = {}
    for asset in assets.values():
        units[asset['sourceId']] = {u['id']: u for u in asset['expectedUnits']}
        check(len(units[asset['sourceId']]) == len(asset['expectedUnits']), 'Duplicate expected inspection unit')
        available = asset['availability'] == 'available'
        check(bool(asset['path'] and asset['sha256'] and asset['bytes'] and asset['expectedUnits']) if available else
              all(asset[k] is None for k in ('path', 'sha256', 'bytes')) and not asset['expectedUnits'], 'Availability/asset metadata contradiction: ' + asset['sourceId'])
        expected_kind = {'application/pdf': 'pdf_page', 'text/html': 'html_section', 'text/plain': 'text_section', 'application/json': 'text_section'}.get(asset['mediaType'], 'image')
        check(all(u['kind'] == expected_kind for u in asset['expectedUnits']), 'Media/inspection unit mismatch')
        if expected_kind == 'pdf_page' and available:
            check([u['locator'] for u in asset['expectedUnits']] == [str(i) for i in range(1, len(asset['expectedUnits']) + 1)], 'PDF expected units must enumerate consecutive physical pages')
    inspections = {i['sourceId']: i for i in candidate['inspection']}
    check(len(inspections) == len(candidate['inspection']) and set(inspections) == set(assets), 'Inspection must cover each assigned asset exactly once')
    fully_read = set()
    for sid, inspection in inspections.items():
        if sid not in assets:
            continue
        asset = assets[sid]
        check(inspection['sourceSha256'] == asset['sha256'], 'Inspection source hash mismatch: ' + sid)
        read = set(inspection['unitIdsRead'])
        visual = set(inspection['visualUnitIds'])
        logs = inspection['readLog']
        check(read <= units[sid].keys() and visual <= read, 'Inspection unit outside assigned/read coverage')
        check({log['unitId'] for log in logs} == read and len(logs) == len(read), 'Exactly one actual read-log entry per read unit is required')
        check(all(dated(log['inspectedAt']) for log in logs), 'Read log needs dated inspection timestamps')
        check({log['unitId'] for log in logs if log['method'] == 'visual_read'} == visual, 'Visual unit/read method mismatch')
        if asset['availability'] != 'available':
            check(not read and inspection['status'] in ('not_checked', 'not_accessible'), 'Unavailable asset cannot be inspected')
        if inspection['status'] == 'full':
            check(asset['availability'] == 'available' and read == units[sid].keys(), 'Full inspection must cover every expected unit')
            if asset['mediaType'].startswith('image/'):
                check(visual == read, 'Image inspection must be visual')
            if asset['availability'] == 'available' and read == units[sid].keys():
                fully_read.add(sid)
        elif asset['required']:
            gaps.append('Required asset not fully inspected: ' + sid)
            check(bool(inspection['nextAction']), 'Unfinished required asset needs next action')
    required_assets = {sid for sid, a in assets.items() if a['required']}
    if not required_assets <= fully_read:
        gaps.append('Report/required companion coverage incomplete')
    experiment_ids = {e['id'] for e in candidate['experiments']}
    check(len(experiment_ids) == len(candidate['experiments']), 'Duplicate experiment identity')
    for experiment in candidate['experiments']:
        check(set(experiment['studyIds']) <= set(candidate['studyIds']), 'Experiment references an unknown study identity')
    reports = [r['canonicalReportId'] for r in candidate['relatedReports']]
    check(len(reports) == len(set(reports)) and candidate['canonicalReportId'] not in reports, 'Duplicate or self-related report identity')
    def locators(items):
        for locator in items:
            sid = locator['sourceId']
            if sid not in assets:
                errors.append('Locator references unassigned source'); continue
            unit = units[sid].get(locator['unitId'])
            inspection = inspections.get(sid, {})
            check(locator['sourceSha256'] == assets[sid]['sha256'], 'Locator source hash mismatch')
            check(unit is not None and locator['kind'] == unit['kind'] and locator['locator'] == unit['locator'], 'Locator kind/location differs from assigned unit')
            check(locator['unitId'] in inspection.get('unitIdsRead', []), 'Locator unit was not inspected')
    for experiment in candidate['experiments']:
        locators(experiment['sourceLocators'])
    keys = [(f['questionId'], f['field']) for f in candidate['inputs']]
    check(len(keys) == len(set(keys)) and set(keys) == required_fields, 'Review must include each of the 67 question/field inputs exactly once')
    numeric_ids = {n['id'] for n in candidate['numericClaims']}
    check(len(numeric_ids) == len(candidate['numericClaims']), 'Duplicate numeric claim identity')
    result_ids = {r['id'] for r in candidate['results']}
    result_by_id = {r['id']: r for r in candidate['results']}
    check(len(result_ids) == len(candidate['results']), 'Duplicate result identity')
    check({r['experimentId'] for r in candidate['results']} == experiment_ids, 'Every experiment needs results; result experiment references must resolve')
    used_numbers = set()
    for result in candidate['results']:
        check(set(result['numericClaimIds']) <= numeric_ids, 'Result references unknown numeric claim')
        used_numbers.update(result['numericClaimIds'])
        check(len({a['id'] for a in result['arms']}) == len(result['arms']), 'Duplicate arm identity within result')
        check(all(a['sampleSizeNumericClaimId'] is None or a['sampleSizeNumericClaimId'] in result['numericClaimIds'] for a in result['arms']), 'Arm sample size must reference its result numeric claims')
        locators(result['sourceLocators'])
    check(used_numbers == numeric_ids, 'Every numeric claim needs a scoped experiment/result')
    check(len({c['id'] for c in candidate['claims']}) == len(candidate['claims']), 'Duplicate claim identity')
    claimed_results = set()
    for claim in candidate['claims']:
        check(set(claim['resultIds']) <= result_ids, 'Claim references unknown result')
        claimed_results.update(claim['resultIds'])
        locators(claim['sourceLocators'])
    check(claimed_results == result_ids, 'Every scoped result must reach an explicit claim')
    coverage_keys = [(c['sourceId'], c['unitId']) for c in candidate['resultCoverage']]
    expected_coverage = {(sid, unit) for sid in required_assets for unit in units[sid]}
    check(len(coverage_keys) == len(set(coverage_keys)) and set(coverage_keys) == expected_coverage, 'Result coverage must account for each required source unit exactly once')
    covered_results = set()
    for coverage in candidate['resultCoverage']:
        check(set(coverage['resultIds']) <= result_ids, 'Coverage references unknown result')
        locators(coverage['sourceLocators'])
        if coverage['disposition'] == 'unfinished':
            gaps.append('Unfinished result coverage: ' + coverage['sourceId'] + '/' + coverage['unitId'])
        else:
            check(any(l['sourceId'] == coverage['sourceId'] and l['unitId'] == coverage['unitId'] for l in coverage['sourceLocators']), 'Coverage disposition needs its own source-unit locator')
            check(bool(coverage['resultIds']) == (coverage['disposition'] == 'results_recorded'), 'Result coverage disposition/references mismatch')
            check(all(any(l['sourceId'] == coverage['sourceId'] and l['unitId'] == coverage['unitId'] for l in result_by_id[rid]['sourceLocators'])
                      for rid in coverage['resultIds'] if rid in result_by_id), 'Covered result lacks this source-unit locator')
            covered_results.update(coverage['resultIds'])
    check(covered_results == result_ids, 'Every result must occur in the source-unit coverage accounting')
    field_by_key = {key: field for key, field in zip(keys, candidate['inputs'])}
    for field in candidate['inputs']:
        key = field['questionId'] + '/' + field['field']
        check(set(field['assessedAssetIds']) <= fully_read, 'Field assessment names an asset not fully inspected: ' + key)
        check(set(field['experimentIds']) <= experiment_ids, 'Unknown field experiment reference')
        check(set(field['numericClaimIds']) <= numeric_ids, 'Unknown field numeric claim reference')
        locators(field['sourceLocators'])
        state = field['status']
        if state in UNFINISHED:
            gaps.append('Unfinished input: ' + key + ' (' + state + ')')
            check(bool(field['nextAction']) and field['basis'] == 'unfinished', 'Unfinished input needs its own basis/next action')
        else:
            check(field['nextAction'] is None, 'Closed input cannot retain an unfinished next action')
            check(bool(field['sourceLocators']) and bool(field['assessedAssetIds']), 'Closed input needs source-located assessment')
            if state in ('reported', 'assessed'):
                check(field['value'] is not None and field['value'] not in ('', [], {}), 'Reported/assessed input needs a substantive value')
                check(field['basis'] == ('reported' if state == 'reported' else 'appraisal'), 'Closed field basis mismatch')
            else:
                check(field['value'] is None, 'Absent/inapplicable input must keep value null')
                check(field['basis'] == ('absence_check' if state == 'not_reported' else 'design_applicability'), 'Absence/applicability basis mismatch')
                if state == 'not_reported':
                    check(required_assets <= set(field['assessedAssetIds']) and required_assets <= fully_read, 'Not-reported input must assess every required asset')
    question_ids = [a['questionId'] for a in candidate['answers']]
    check(len(set(question_ids)) == 15 and set(question_ids) == {q for q, _ in required_fields}, 'Exactly one answer per Q01-Q15 is required')
    for answer in candidate['answers']:
        expected = {field for q, field in required_fields if q == answer['questionId']}
        check(set(answer['inputFields']) == expected, 'Answer must reference all its required input fields')
        check(set(answer['experimentIds']) <= experiment_ids, 'Unknown answer experiment reference')
        locators(answer['sourceLocators'])
        if answer['status'] == 'answered':
            check(bool(answer['answer'] and answer['appraisalRationale'] and answer['sourceLocators']), 'Answered question needs substantive prose, appraisal rationale and source locators')
        else:
            gaps.append('Draft answer: ' + answer['questionId'])
    check(len({i['kind'] for i in candidate['sourceIntegrity']}) == 5, 'Each integrity check kind must occur exactly once')
    for integrity in candidate['sourceIntegrity']:
        locators(integrity['sourceLocators'])
        if integrity['status'] in ('checked', 'not_applicable'):
            check(dated(integrity['checkedAt']) and bool(integrity['sourceLocators']) and integrity['nextAction'] is None, 'Closed integrity check needs date, source-located scope and no next action')
        else:
            gaps.append('Unfinished integrity check: ' + integrity['kind'])
            check(bool(integrity['nextAction']), 'Unfinished integrity check needs next action')
    for number in candidate['numericClaims']:
        key = (number['questionId'], number['field'])
        check(key in field_by_key and number['id'] in field_by_key[key]['numericClaimIds'], 'Numeric claim must resolve to its exact input field')
        locators(number['sourceLocators'])
        if number['basis'] == 'exact_reported':
            scalar = reported_scalar(number['reportedText'])
            if number['value'] is None:
                check(bool(number['limitation']), 'Qualified/ambiguous reported quantity needs explicit scalar limitation')
            else:
                check(scalar is not None and scalar == Decimal(str(number['value'])), 'Numeric value differs from exact reported scalar')
            check(number['calculationProvenance'] is None, 'Reported scalar cannot hide a calculation')
            check(bool(number['reportedText']) and any(number['reportedText'] in loc['quote'] for loc in number['sourceLocators']), 'Reported scalar absent from source quotation')
        else:
            check(number['value'] is None and bool(number['limitation']), 'Graph estimates/calculated numeric values are not supported by this contract; retain null and explicit limitation')
            if number['basis'] == 'calculated':
                check(bool(number['calculationProvenance']), 'Calculation intent needs explicit provenance')
        for locator in number['sourceLocators']:
            if locator['kind'] == 'image' or locator['figureTable']:
                check(locator['unitId'] in inspections.get(locator['sourceId'], {}).get('visualUnitIds', []), 'Consequential figure/table number lacks visual inspection')
    if candidate['processingState'] == 'candidate_complete':
        check(not gaps, 'Candidate claims completeness with unfinished required work')
    return {'errors': errors, 'gaps': sorted(set(gaps))}


def validate(args):
    root = Path(args.root).resolve()
    plan_path, gp_path, candidate_path = map(Path, (args.plan, args.readiness, args.candidate))
    controls = {p.resolve(): sha(p) for p in (plan_path, gp_path, candidate_path)}
    plan, candidate = load(plan_path), load(candidate_path)
    require('full-review-validate' in plan.get('operations', []), 'Full review validation is outside prospective plan')
    check_readiness(gp_path, plan, controls[plan_path.resolve()])
    check_inputs(root, plan)
    pins = {safe_path(root, p['path']).resolve(): p['sha256'] for p in plan['inputs']}
    def pinned(path):
        path = Path(path).resolve()
        require(path in pins and sha(path) == pins[path], 'Missing/stale full-review control pin: ' + str(path))
        controls[path] = pins[path]
        return load(path)
    schema_path = Path(args.schema)
    require(pinned(schema_path) == REVIEW_SCHEMA, 'Use the executable full-review schema matching this validator')
    for name, expected in SCHEMAS.items():
        require(pinned(schema_path.parent / name) == expected, 'Full-review companion schema mismatch: ' + name)
    for name in ('scripts/research_full_review.py', 'scripts/research_ingest/cli.py', 'scripts/research_ingest/source_validation.py'):
        path = root / name
        require(path.resolve() in pins and sha(path) == pins[path.resolve()], 'Validator code must be pinned: ' + name)
    assignment_path, map_path = Path(args.assignment), Path(args.question_map)
    assignment, question_map = pinned(assignment_path), pinned(map_path)
    require(not schema_errors(ASSIGNMENT_SCHEMA, assignment), 'Invalid full-review assignment schema')
    require(candidate.get('planId') == plan['planId'] and candidate.get('planSha256') == controls[plan_path.resolve()], 'Candidate plan mismatch')
    require(candidate.get('assignmentSha256') == sha(assignment_path) and candidate.get('questionMapSha256') == sha(map_path), 'Candidate assignment/question map hash mismatch')
    result = validate_review(candidate, assignment, question_map)
    require(not result['errors'], '\n'.join(result['errors']))
    source_hashes = []
    source_map = Path(args.source_map) if getattr(args, 'source_map', None) else None
    if source_map:
        # A local resolver is relocatable; assigned identities/hashes remain the
        # authority. Record its exact version and detect concurrent changes.
        controls[source_map.resolve()] = sha(source_map)
    for asset in assignment['assets']:
        if asset['availability'] != 'available':
            continue
        path = Path(resolve_source(source_map, asset['sourceId'])['path'] if source_map else asset['path'])
        if not path.is_absolute():
            path = safe_path(root, asset['path'])
        require(path.is_file() and path.stat().st_size == asset['bytes'] and sha(path) == asset['sha256'], 'Assigned source bytes/hash mismatch: ' + asset['sourceId'])
        head = path.read_bytes()[:512]
        media = asset['mediaType']
        signatures = {'application/pdf': head.startswith(b'%PDF-'), 'image/png': head.startswith(b'\x89PNG\r\n\x1a\n'),
                      'image/jpeg': head.startswith(b'\xff\xd8\xff'), 'image/webp': head.startswith(b'RIFF') and head[8:12] == b'WEBP',
                      'text/html': b'<' in head}
        require(signatures.get(media, True), 'Asset media signature mismatch: ' + asset['sourceId'])
        controls[path.resolve()] = asset['sha256']
        source_hashes.append({'sourceId': asset['sourceId'], 'sha256': asset['sha256']})
    complete = candidate['processingState'] == 'candidate_complete' and not result['gaps']
    state = 'candidate_complete' if complete else 'draft'
    if args.audit:
        audit_path = Path(args.audit)
        controls[audit_path.resolve()] = sha(audit_path)
        audit = load(audit_path)
        require(not schema_errors(AUDIT_SCHEMA, audit), 'Invalid independent full-review audit schema')
        require(complete, 'Incomplete candidate cannot be independently accepted')
        require(audit['author'] == candidate['author'] and audit['auditor'].strip().casefold() != candidate['author'].strip().casefold() and audit['auditor'] == audit['auditor'].strip(), 'Independent auditor must differ from candidate author')
        require(dated(audit['reviewedAt']), 'Audit needs dated review timestamp')
        for key, expected in {'candidateSha256': controls[candidate_path.resolve()], 'planSha256': controls[plan_path.resolve()],
                              'assignmentSha256': sha(assignment_path), 'questionMapSha256': sha(map_path)}.items():
            require(audit[key] == expected, 'Independent audit hash mismatch: ' + key)
        require(sorted(audit['sourceHashes'], key=lambda x: x['sourceId']) == sorted(source_hashes, key=lambda x: x['sourceId']), 'Independent audit must bind every available source asset exactly once')
        for evidence in audit['evidence']:
            path = safe_path(root, evidence['path'])
            require(path.is_file() and sha(path) == evidence['sha256'], 'Independent audit evidence changed')
            controls[path.resolve()] = evidence['sha256']
        state = 'accepted_private'
    check_inputs(root, plan)
    require(all(path.is_file() and sha(path) == expected for path, expected in controls.items()), 'A review control or source changed during validation')
    return {'schemaVersion': 'remaprx-full-review-validation-v1', 'status': 'PASS', 'scope': 'read_only_private_full_report_validation',
            'reviewId': candidate['reviewId'], 'canonicalReportId': candidate['canonicalReportId'], 'completionState': state,
            'candidateSha256': controls[candidate_path.resolve()], 'planSha256': controls[plan_path.resolve()],
            'assignmentSha256': sha(assignment_path), 'questionMapSha256': sha(map_path),
            'sourceMapSha256': controls[source_map.resolve()] if source_map else None,
            'requiredAssets': sum(a['required'] for a in assignment['assets']), 'verifiedAvailableAssets': len(source_hashes),
            'inputs': len(candidate['inputs']), 'answers': len(candidate['answers']), 'gaps': result['gaps'],
            'independentAuditAccepted': state == 'accepted_private', 'scientificApproval': False,
            'humanApproval': False, 'released': False, 'performedImport': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('root', 'plan', 'readiness', 'assignment', 'candidate', 'schema', 'question-map'):
        parser.add_argument('--' + flag, required=True)
    parser.add_argument('--audit')
    parser.add_argument('--source-map')
    try:
        print(json.dumps(validate(parser.parse_args()), indent=2, sort_keys=True))
    except (Hold, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'status': 'HOLD', 'errors': [str(error)], 'humanApproval': False, 'released': False, 'performedImport': False}, indent=2))
        sys.exit(2)
