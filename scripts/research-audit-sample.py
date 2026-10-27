#!/usr/bin/env python3
"""Select a reproducible audit queue. Selection never certifies an extraction.

Input is a JSON object with seed, records and optional materialErrors. Records
identify a report/version, worker, design, format, and explicit boolean flags
calibration, publicNumericalClaim, launchSupporting, fullTextExtraction. A
material error requires worker/design/format fields (null means unknown) and a
recordId. Every matching known dimension expands the audit, conservatively;
an error with no known dimensions expands to every record.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path


def select(data):
    if not isinstance(data.get('seed'), str) or not data['seed'].strip() or data['seed'] != data['seed'].strip():
        raise ValueError('A recorded nonempty sampling seed is required')
    records = data['records']
    if not isinstance(records, list):
        raise ValueError('records must be an array')
    by_id = {}
    flags = ('calibration', 'publicNumericalClaim', 'launchSupporting', 'fullTextExtraction')
    dimensions = ('worker', 'design', 'format')
    for row in records:
        for key in ('id', 'reportId', 'sourceSha256', *dimensions):
            if not isinstance(row.get(key), str) or not row[key].strip() or row[key] != row[key].strip():
                raise ValueError('Missing record identity/dimension: ' + key)
        if len(row['sourceSha256']) != 64 or any(c not in '0123456789abcdef' for c in row['sourceSha256']):
            raise ValueError('Invalid source SHA-256')
        if row['id'] in by_id:
            raise ValueError('Duplicate audit record ID')
        if any(type(row.get(key)) is not bool for key in flags):
            raise ValueError('All audit flags must be explicit booleans')
        by_id[row['id']] = row
    # Different reports may share bytes; only duplicate report-version entries
    # are prohibited. Study-family overlap is not resolved by this selector.
    versions = [(r['reportId'], r['sourceSha256']) for r in records]
    if len(versions) != len(set(versions)):
        raise ValueError('Duplicate report-version audit obligation')
    reasons = {r['id']: {flag for flag in flags[:3] if r[flag]} for r in records}
    strata = {}
    for row in records:
        if row['fullTextExtraction'] and not reasons[row['id']]:
            key = tuple(row[d] for d in dimensions)
            strata.setdefault(key, []).append(row)
    def rank(row):
        value = [data['seed'], row['reportId'], row['sourceSha256'], row['id']]
        return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()
    sampling = []
    for key, rows in sorted(strata.items()):
        count = math.ceil(len(rows) / 10)
        chosen = sorted(rows, key=lambda row: (rank(row), row['id']))[:count]
        for row in chosen:
            reasons[row['id']].add('stratified_10_percent')
        sampling.append({'stratum': dict(zip(dimensions, key)), 'eligible': len(rows),
                         'required': count, 'selectedIds': sorted(r['id'] for r in chosen)})
    for error in data.get('materialErrors', []):
        if error.get('recordId') not in by_id or any(d not in error for d in dimensions):
            raise ValueError('Material error requires an existing record and all three dimensions')
        known = {d: error[d] for d in dimensions if error[d] is not None}
        if any(not isinstance(v, str) or not v.strip() or v != v.strip() for v in known.values()):
            raise ValueError('Invalid error dimension')
        origin = by_id[error['recordId']]
        if any(origin[d] != v for d, v in known.items()):
            raise ValueError('Material error dimensions differ from the affected record')
        for row in records:
            if row['id'] == error['recordId'] or not known or any(row[d] == v for d, v in known.items()):
                reasons[row['id']].add('material_error:' + error['recordId'])
    selected = [{'id': row['id'], 'reportId': row['reportId'], 'sourceSha256': row['sourceSha256'],
                 'reasons': sorted(reasons[row['id']])} for row in sorted(records, key=lambda r: r['id']) if reasons[row['id']]]
    return {'schemaVersion': 'remaprx-audit-selection-v1', 'seed': data['seed'],
            'algorithm': 'sha256-ranked report versions; ceil(10%) per worker/design/format stratum; mandatory and expanded obligations',
            'records': len(records), 'selectedCount': len(selected), 'selected': selected, 'strata': sampling,
            'auditPerformed': False, 'scientificApproval': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    print(json.dumps(select(json.loads(args.input.read_text())), indent=2, sort_keys=True))
