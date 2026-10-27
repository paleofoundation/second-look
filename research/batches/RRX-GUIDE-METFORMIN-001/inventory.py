"""Metadata/byte reconciliation only. Never extracts medical source contents."""
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
APP = HERE.parents[2]
NOW = '2026-10-12'
INPUTS = [
    'AGENTS.md', 'docs/PROJECT-RULES.md', 'docs/RULE-CHANGELOG.md',
    'docs/RESEARCH-INGEST.md', 'rules/one-match-rule/ONE-MATCH-RULE.md',
    'research/batches/RRX-INGEST-001/PLAN.md', 'research/batches/RRX-INGEST-001/HANDOFF.md',
    'research/batches/RRX-INGEST-001/continuations/CAL-T1-20261012/PLAN.md',
    'research/batches/RRX-INGEST-001/inventory/source-records.jsonl',
    'research/batches/RRX-INGEST-001/inventory/source-locations.json',
    'research/batches/RRX-INGEST-001/calibration/assignments.json',
    'research/batches/RRX-INGEST-001/schemas/review-questions-and-inputs.json',
    'research/batches/RRX-INGEST-001/continuations/CAL-T1-20261012/schemas/full-review.schema.json',
    'data/content.json', 'data/reader-evidence.json', 'data/private-reviews.json',
    'data/review-envelopes.json', 'data/ingestion-status.json', 'data/acquisition-status.json',
    'editorial/reader-source-corrections.json', 'editorial/reader-source-aliases.json',
    'editorial/evidence-assessments.json', 'editorial/EVIDENCE-GRADING.md',
    'editorial/metformin-source-additions.json', 'editorial/metformin-additional-evidence.json',
]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read(path):
    return json.loads((APP / path).read_text())

def write(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

def doi(s):
    return (s or '').lower().removeprefix('https://doi.org/')

# Explicit existing-metadata identity leads. These are not automatic merges.
LEADS = {
    'COND-C02-COVIDOUT-2022': ['acquisition:A-F01-R031-F01', 'acquisition:B-R0018-F00'],
    'COND-C15-MA32-2022': ['acquisition:B-R0007-F00'],
    'COND-C17-MET-2015': ['acquisition:B-R0040-F00'],
    'MF-MYELOMA-MODELS-2018': ['moa:MOA-T-autophagy-001@row-1214'],
}
CHAPTER = {
    'MF-LABEL-2025': 'safety-formulations', 'MF-FDA-GENERICS': 'safety-formulations',
    'CP016': 'parkinson', 'CP017': 'schizophrenia', 'CP018': 'physical-function',
    'MF-PD-MECHANISM-2016': 'parkinson', 'MF-SCHIZOPHRENIA-PARENT-2023': 'schizophrenia',
    'MF-METPREVENT-2025': 'physical-function', 'MF-MASTERS-2019': 'physical-function',
    'MF-STAMPEDE-2025': 'prostate-cancer', 'MF-NRG-LU001-2021': 'lung-cancer',
    'MF-ALMERA-2021': 'lung-cancer', 'MF-ADENOMA-2016': 'colorectal-prevention',
    'MF-COLON-MECHANISM-2010': 'colorectal-prevention', 'MF-MYELOMA-MODELS-2018': 'myeloma-preclinical',
    'COND-C15-MA32-2022': 'breast-cancer', 'COND-C15-MA32-METABOLIC': 'breast-cancer',
    'COND-C17-MET-2015': 'pancreatic-cancer',
}
FAMILY = {
    'P-COVIDOUT-2023': 'COVID-OUT', 'COND-C02-COVIDOUT-2022': 'COVID-OUT', 'MF-COVID-VIRAL-2024': 'COVID-OUT',
    'P-ACTIV6-2026': 'ACTIV-6', 'CP017': 'NCT03271866', 'MF-SCHIZOPHRENIA-PARENT-2023': 'NCT03271866',
    'COND-C15-MA32-2022': 'MA.32', 'COND-C15-MA32-METABOLIC': 'MA.32',
}

def build():
    c = read('data/content.json')
    ids = next(g for g in c['guides'] if g['id'] == 'G-METFORMIN')['sourceIds']
    source_map = {s['id']: s for s in c['sources']}
    records = [json.loads(line) for line in (APP / INPUTS[8]).read_text().splitlines()]
    locations = read(INPUTS[9])
    corrections = read('editorial/reader-source-corrections.json')
    envelopes = read('data/review-envelopes.json')
    evidence = read('data/reader-evidence.json')
    rows = evidence['synthesisRows']
    qmap = read('research/batches/RRX-INGEST-001/schemas/review-questions-and-inputs.json')
    asset_cache = {}

    def assets(hash_value):
        if not hash_value:
            return []
        if hash_value in asset_cache:
            return asset_cache[hash_value]
        found = []
        for f in locations['files']:
            if f.get('sha256') != hash_value:
                continue
            path = Path(locations['roots'][f['rootId']]['path']) / f['path']
            exists = path.is_file()
            b = path.read_bytes() if exists else None
            found.append({'logicalRoot': f['rootId'], 'relativePath': f['path'], 'archiveMember': None,
                'expectedSha256': hash_value, 'observedSha256': sha(b) if b is not None else None,
                'bytes': len(b) if b is not None else None, 'status': 'hash_verified' if b is not None and sha(b) == hash_value else 'missing_or_mismatch',
                'declaredKind': f['kind'], 'formatSignature': 'pdf' if b and b.startswith(b'%PDF-') else 'not_inspected_as_medical_text'})
        for m in locations['archiveMembers']:
            if m.get('sha256') != hash_value:
                continue
            af = next((f for f in locations['files'] if f['id'] == m['archiveFileId']), None)
            if not af:
                continue
            ap = Path(locations['roots'][af['rootId']]['path']) / af['path']
            try:
                with zipfile.ZipFile(ap) as z:
                    b = z.read(m['path'])
                found.append({'logicalRoot': af['rootId'], 'relativePath': af['path'], 'archiveMember': m['path'],
                    'expectedSha256': hash_value, 'observedSha256': sha(b), 'bytes': len(b),
                    'status': 'hash_verified' if sha(b) == hash_value else 'missing_or_mismatch',
                    'declaredKind': m['kind'], 'formatSignature': 'pdf' if b.startswith(b'%PDF-') else 'not_inspected_as_medical_text'})
            except (OSError, KeyError, zipfile.BadZipFile):
                found.append({'logicalRoot': af['rootId'], 'relativePath': af['path'], 'archiveMember': m['path'],
                    'expectedSha256': hash_value, 'observedSha256': None, 'bytes': None,
                    'status': 'missing_or_mismatch', 'declaredKind': m['kind'], 'formatSignature': 'not_accessible'})
        asset_cache[hash_value] = found
        return found

    coverage = []
    for sid in ids:
        s = source_map[sid]
        pmid = str(s.get('pmid') or '')
        if not pmid:
            match = re.search(r'pubmed.ncbi.nlm.nih.gov/(\d+)', s.get('url', ''))
            pmid = match.group(1) if match else ''
        matches = []
        for r in records:
            basis = None
            if r['canonicalId'] == sid or r['sourceId'] == sid:
                basis = 'existing_source_identity'
            elif doi(s.get('doi')) and doi(s.get('doi')) == doi(r.get('doi')):
                basis = 'exact_doi_metadata_match'
            elif pmid and pmid == str(r.get('pmid') or ''):
                basis = 'exact_pmid_metadata_match'
            elif r['id'] in LEADS.get(sid, []):
                basis = 'explicit_title_url_lead_requires_source_identity_check'
            if basis:
                matches.append({'recordId': r['id'], 'sourceId': r['sourceId'], 'canonicalId': r['canonicalId'],
                    'matchBasis': basis, 'title': r.get('title'), 'doi': r.get('doi'), 'pmid': r.get('pmid'),
                    'states': r.get('states', {}), 'previousScientificDisposition': r.get('priorScientificDisposition'),
                    'assets': assets(r.get('sha256'))})
        holdings = [a for m in matches for a in m['assets'] if a['status'] == 'hash_verified']
        exact_holdings = [a for m in matches if m['matchBasis'] != 'explicit_title_url_lead_requires_source_identity_check' for a in m['assets'] if a['status'] == 'hash_verified']
        primary_holds = sid in ['P-REVIVE-2026', 'P-COVIDOUT-2023', 'P-ACTIV6-2026']
        action = 'Reuse verified local report; verify identity, all companions and Q01–Q15 before full assessment.' if holdings else 'Locate/download lawful exact full report and required companions; existing page metadata is not a received complete source.'
        if sid == 'P-REVIVE-2026':
            action = 'Keep quarantined; reuse RRX-GAP-001 request for notice, corrected republication and complete change trail; no efficacy support from original.'
        elif sid == 'P-COVIDOUT-2023':
            action = 'Reuse original PDF and existing family/protocol holdings. Acquire actual correction text (PMID 37666258) and reconcile exact amended values before absolute-effect synthesis.'
        elif sid == 'P-ACTIV6-2026':
            action = 'Reuse RRX-GAP-001 journal-source request and CAL-04/05 version hold; preprint PDF is not this journal report. Obtain journal body, supplements and relevant SAP versions.'
        if sid in ['MF-LABEL-2025', 'MF-FDA-GENERICS']:
            action = 'Locate exact versioned official source; inspect existing IR/ER label holdings first, then verify current product/jurisdiction and all safety sections.'
        coverage.append({'sourceId': sid, 'title': s['title'], 'url': s.get('url'), 'doi': s.get('doi'),
            'pmid': pmid or None, 'chapter': CHAPTER.get(sid, 'infection-long-covid'),
            'tier': 'CONTEXT' if sid in ['MF-LABEL-2025', 'MF-FDA-GENERICS', 'CP018'] else 'PRIMARY',
            'existingAppAccess': s.get('access', 'not_recorded'), 'familyGroup': FAMILY.get(sid, s.get('familyId')),
            'familyStatus': 'preserved_overlap_coordination_not_independence_acceptance',
            'matches': matches, 'localAssetHashes': sorted(set(a['expectedSha256'] for a in holdings)),
            'assetMatchConfidence': 'exact_metadata_identity_not_source_verified' if exact_holdings else 'title_or_url_lead_requires_adjudication' if holdings else 'no_matched_local_asset',
            'integrityState': 'quarantined' if sid == 'P-REVIVE-2026' else 'unresolved_correction_or_version' if primary_holds else 'current_external_check_not_performed',
            'preservedCorrection': corrections.get(sid, {}).get('correction', s.get('correction')),
            'existingReviewEnvelope': {'present': sid in envelopes, 'state': envelopes.get(sid, {}).get('releaseState', s.get('reviewState', 'pending'))},
            'synthesisIds': [r['id'] for r in rows if sid in r.get('sourceIds', [])],
            'newFullAssessment': 'not_completed', 'humanReview': 'pending', 'release': 'not_released',
            'questionCoverage': [{'id': q['id'], 'status': 'not_checked', 'requiredInputs': q['inputFields'],
                'nextAction': 'Reconcile existing source-located extraction, then inspect exact source/companions and author substantive answer; this inventory does not infer completion.'} for q in qmap['questions']] if sid not in ['MF-LABEL-2025', 'MF-FDA-GENERICS'] else [],
            'nextAction': action})
    write('coverage-ledger.json', {'schemaVersion': '1.0', 'batchId': 'RRX-GUIDE-METFORMIN-001', 'date': NOW,
        'scope': 'Current 24 article references; not an exhaustive literature search', 'sources': coverage})
    leads = [r for r in records if 'D01' in r.get('acquisitionTags', {}).get('drug_ids', [])]
    write('existing-metformin-leads.json', {'status': 'metadata_inventory_not_eligibility_or_independent_study_count',
        'originRecordCount': len(leads), 'records': [{k: r.get(k) for k in ['id', 'canonicalId', 'sourceId', 'title', 'doi', 'pmid', 'sha256', 'states', 'identityMetadata', 'sourceLocation']} for r in leads]})
    extras = [r for r in leads if any(t in r['sourceId'] for t in ['OFF-b01-dailymed-metformin', 'REG-NCT04510194', 'REG-NCT04885530', 'A-F01-R004', 'A-F01-R029', 'B-R0057'])]
    write('companion-and-safety-holdings.json', {'basis': 'Existing metadata relationships, pending exact source/version and eligibility audit',
        'records': [{'recordId': r['id'], 'sourceId': r['sourceId'], 'title': r['title'], 'states': r.get('states'), 'assets': assets(r.get('sha256'))} for r in extras]})
    write('source-access.json', {'roots': locations['roots'], 'portability': 'Raw papers are external private dependencies. On another host bind matching logical roots and reverify each exact hash; no source redistribution is implied.'})
    input_files = []
    for p in INPUTS:
        b = (APP / p).read_bytes()
        record = {'path': p, 'sha256': sha(b)}
        if p.endswith('.md'):
            snap = HERE / 'instruction-snapshots' / p
            snap.parent.mkdir(parents=True, exist_ok=True)
            snap.write_bytes(b)
            record['snapshot'] = str(snap.relative_to(HERE))
        input_files.append(record)
    write('input-manifest.json', {'date': NOW, 'gitRevision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=APP, text=True).strip(),
        'workingTreeWarning': 'Inputs include concurrent uncommitted work. Exact file hashes, not Git HEAD alone, define this inventory.',
        'files': input_files})
    print(json.dumps({'references': len(coverage), 'withLocatedAsset': sum(bool(r['localAssetHashes']) for r in coverage),
        'locatedDistinctHashes': len({h for r in coverage for h in r['localAssetHashes']}), 'existingD01OriginRecords': len(leads), 'completedFullReviews': 0}))

if __name__ == '__main__':
    build()
