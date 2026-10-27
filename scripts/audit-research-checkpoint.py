#!/usr/bin/env python3
"""Independently audit the exact 47-file recovery plus one private CAL-07 bundle.

No canonical writes. Requires a matching GP PASS; replays the pinned read-only
fanout, verifies historical bytes and preserved identities, then emits a distinct
technical evidence/report pair. Scientific source acceptance remains a separate,
bounded receipt; this audit never completes a review or approves publication.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
_spec = importlib.util.spec_from_file_location('recovery_audit_utilities', ROOT / 'scripts/audit-research-recovery.py')
recovery = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(recovery)
from scripts.research_fanout import fanout

AUDITOR = 'codex/identity_review'
BATCH = Path('research/batches/RRX-INGEST-001')
NEW_TARGET = 'research/corpus/RRX-INGEST-001/verified-batches/CAL-07.json'
REPLAY_OVERRIDE_PATHS = {'docs/PROJECT-RULES.md', 'docs/RULE-CHANGELOG.md'}
require, digest, canonical, decode, safe = recovery.require, recovery.digest, recovery.canonical, recovery.decode, recovery.safe


def expected_bundle(candidate, bindings, source_audit, proposals):
    return {'schemaVersion': 'remaprx-private-content-checkpoint-v1', 'batchId': 'RRX-INGEST-001-CAL-07',
            'scope': 'Independently verified bounded qualitative findings and private page proposals; incomplete scientific review',
            'candidate': candidate, 'bindings': bindings, 'independentAudit': source_audit, 'fanout': proposals,
            'humanReviewed': False, 'appraised': False, 'released': False, 'fullScientificReviewComplete': False}


def verify_bundle(data, candidate, bindings, source_audit, proposals):
    expected = expected_bundle(candidate, bindings, source_audit, proposals)
    require(data == canonical(expected), 'New bundle must exactly preserve the canonical verified candidate, bindings, independent audit, fanout and pending flags.')
    require(candidate['inspection']['scope'] == 'partial_source' and candidate['human_review_status'] == 'pending'
            and candidate['excluded_from_accepted_support'] is True and candidate['mechanism_payload'] is None,
            'The CAL-07 bounded source and incomplete mechanism/review status must be retained.')
    require(len(candidate['results']) == 3 and len(candidate['claims']) == 4 and len(candidate['questions']) == 15,
            'Unexpected bounded CAL-07 content counts.')
    require([q['id'] for q in candidate['questions']] == [f'Q{i:02}' for i in range(1, 16)], 'Q01-Q15 identities/order must be preserved.')
    require(Counter(q['status'] for q in candidate['questions']) == Counter({'located_candidate': 5, 'partial': 10}),
            'Missingness must not be relabeled as completed review inputs.')
    require(proposals['performedImport'] is False and proposals['humanApproval'] is False and proposals['releaseChanged'] is False,
            'Fanout must remain read-only and unreleased.')
    require(len(proposals['synthesisProposals']) == 0 and len(proposals['mechanismProposals']) == 2
            and len(proposals['pageProposals']) == len(proposals['historyProposals']) == 3,
            'Unexpected scientific/page proposal count or clinical efficacy synthesis.')
    require(proposals['reviewProposal']['reviewCompletion'] == proposals['reviewProposal']['humanApproval'] == proposals['reviewProposal']['release'] == 'pending',
            'Review approval/completion/release must remain pending.')
    require(proposals['reviewProposal']['accessPolicy'] == 'free_authenticated', 'Preserve review access policy.')
    require(all(p['publicationState'] == 'private_ai_draft' and p['humanApproval'] == p['scientificAssessment'] == 'pending'
                and p['clinicalBenefitEstablished'] is False for p in proposals['mechanismProposals']), 'Unexpected public mechanism approval.')
    condition = [p for p in proposals['pageProposals'] if p['guideId'] == 'G-CONDITION-C19']
    require(len(condition) == 1 and condition[0]['sections'] == [{'id': 'interventions', 'label': 'Interventions'}]
            and condition[0]['destinationStatus'] == 'private_proposal' and condition[0]['renderedTargetVerified'] is False
            and condition[0]['layoutStatus'] in ('pending_layout', 'pending_rendered_verification'), 'Condition target must preserve pending Interventions layout.')
    require(proposals['invalidations']['applyAutomatically'] is False, 'Invalidation proposal cannot mutate current approvals.')
    return expected


def select_replay_inputs(root, historical_pins, checkpoint_plan, read):
    """Only exact, explicitly adopted appended visual-doc changes may be isolated."""
    current_pins = {i['path']: i['sha256'] for i in checkpoint_plan['inputs']}
    overrides = checkpoint_plan['contract'].get('isolatedReplayOverrides', [])
    require(isinstance(overrides, list) and len(overrides) <= 2, 'At most two explicit documentation replay overrides are permitted.')
    by_path = {}
    for item in overrides:
        require(isinstance(item, dict) and set(item) == {'path', 'historicalSha256', 'snapshotPath', 'currentSha256', 'reason'}, 'Invalid isolated replay override contract.')
        name = item['path']
        require(name in REPLAY_OVERRIDE_PATHS and name not in by_path, 'Only distinct PROJECT-RULES/RULE-CHANGELOG visual documentation overrides are permitted.')
        require(isinstance(item['reason'], str) and len(item['reason'].strip()) >= 30, 'Override requires the independently reviewed visual-only reason.')
        require(historical_pins.get(name) == item['historicalSha256'], 'Override does not match the archived fanout pin.')
        require(current_pins.get(name) == item['currentSha256'] and current_pins.get(item['snapshotPath']) == item['historicalSha256'], 'Both current document and historical snapshot must be checkpoint-plan-pinned.')
        current = read(safe(root, name), item['currentSha256'])
        historical = read(safe(root, item['snapshotPath']), item['historicalSha256'])
        require(current != historical and current.startswith(historical.rstrip(b'\r\n')), 'Replay isolation is limited to append-only documentation changes preserving the prior contract.')
        by_path[name] = item
    selected, evidence = {}, []
    for name, checksum in historical_pins.items():
        if name in by_path:
            item = by_path[name]
            selected[name] = read(safe(root, item['snapshotPath']), checksum)
            evidence.append({**item, 'currentDocumentPreserved': True, 'historicalContractPreservedAsPrefix': True})
        else:
            require(current_pins.get(name) == checksum or name.startswith('research/corpus/RRX-INGEST-001/'), 'Every other archived fanout input must remain current or be an unchanged preserved checkpoint target: ' + name)
            selected[name] = read(safe(root, name), checksum)
    return selected, evidence


def replay_archived_fanout(root, fanout_dir, checkpoint_plan, read):
    historical_plan = decode(read(safe(root, str(fanout_dir / 'plan.json'))))
    historical_pins = {i['path']: i['sha256'] for i in historical_plan['inputs']}
    require(len(historical_pins) == len(historical_plan['inputs']), 'Duplicate archived fanout pins.')
    selected, evidence = select_replay_inputs(root, historical_pins, checkpoint_plan, read)
    for name in ['plan.json', 'readiness.json']:
        relative = str(fanout_dir / name)
        selected[relative] = read(safe(root, relative))
    with tempfile.TemporaryDirectory(prefix='remaprx-checkpoint-replay-') as temporary:
        isolated = Path(temporary)
        for name, data in selected.items():
            target = safe(isolated, name); target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
        args = argparse.Namespace(root=str(isolated), plan=str(isolated/fanout_dir/'plan.json'), readiness=str(isolated/fanout_dir/'readiness.json'),
            candidate=str(isolated/BATCH/'calibration/candidates/CAL-07/CAL-07-S01.candidate.json'), bindings=str(isolated/fanout_dir/'bindings.json'), verification=str(isolated/fanout_dir/'independent-audit.json'),
            authorship=str(isolated/BATCH/'calibration/candidates/CAL-07/source-authorship.json'), schema=str(isolated/BATCH/'schemas/candidate.schema.json'),
            assignment=str(isolated/BATCH/'calibration/assignments.json'), source_plan=str(isolated/BATCH/'plan.json'), source_readiness=str(isolated/BATCH/'readiness.json'),
            source_file=None, mechanism_schema=None, identity_map=str(isolated/BATCH/'synthesis-identity-map.json'))
        result = fanout(args)
    return result, {'mode': 'temporary_isolated_archived_fanout', 'copiedInputCount': len(selected), 'overrides': evidence,
                    'activeFilesOverwritten': False, 'temporaryCopyRemoved': True,
                    'purpose': 'Archive previously verified bounded private proposals; any reader/application integration requires a new current plan.'}


def audit(packet, plan_path, readiness_path, fanout_dir):
    packet = Path(packet).resolve()
    private_work = safe(ROOT, 'work/research-ingest').resolve()
    require(packet != private_work and packet.is_relative_to(private_work), 'Dedicated private candidate directory required.')
    pins = {}
    def read(path, checksum=None):
        return recovery.read_pinned(path, pins, checksum)
    plan_path, readiness_path = Path(plan_path).resolve(), Path(readiness_path).resolve()
    plan_bytes = read(plan_path); plan = decode(plan_bytes); plan_hash = digest(plan_bytes)
    gate = decode(read(readiness_path))
    require(plan.get('schemaVersion') == 'remaprx-ingest-plan-v1' and plan.get('operations') == ['validate', 'stage', 'diff', 'apply'], 'Exact private checkpoint operation plan required.')
    require(gate.get('schemaVersion') == 'remaprx-gp-readiness-v1' and gate.get('scope') == 'GP_PLAN'
            and gate.get('status') == 'PASS' and gate.get('planId') == plan['planId'] and gate.get('planSha256') == plan_hash,
            'Current matching prospective GP Plan PASS required.')
    plan_pins = {i['path']: i['sha256'] for i in plan['inputs']}
    require(len(plan_pins) == len(plan['inputs']), 'Duplicate plan pins.')
    for name, value in plan_pins.items(): read(safe(ROOT, name), value)
    def pinned(name):
        name = str(name); require(name in plan_pins, 'Unpinned checkpoint input: ' + name)
        return decode(read(safe(ROOT, name), plan_pins[name]))
    for name in ['scripts/audit-research-checkpoint.py', 'scripts/audit-research-recovery.py', 'scripts/research_fanout.py']:
        require(name in plan_pins, 'Auditing implementation must be plan-pinned: ' + name)
    manifest = decode(read(safe(packet, 'manifest.json')))
    require(manifest.get('schemaVersion') == 'remaprx-candidate-v1' and manifest.get('planId') == plan['planId'] and manifest.get('planSha256') == plan_hash
            and manifest.get('batchId') == 'RRX-INGEST-001-PRIVATE-CHECKPOINT', 'Candidate must match this checkpoint plan.')
    require(manifest.get('author', '').strip() and manifest['author'].strip().casefold() != AUDITOR.casefold(), 'Independent candidate author required.')
    historical = pinned(BATCH / 'recovery-inputs.json'); locations = pinned(BATCH / 'inventory/source-locations.json')
    expected = {item['target']: item for item in historical['files']}
    require(len(expected) == len(historical['files']) == 47 and NEW_TARGET not in expected, 'Exactly 47 distinct historical files required.')
    target_set = set(expected) | {NEW_TARGET}; entries = manifest.get('files', [])
    require(len(entries) == len({x['target'] for x in entries}) == len({x['path'] for x in entries}) == 48, 'Exactly 48 unique targets and payloads required.')
    require({x['target'] for x in entries} == set(plan['allowedTargets']) == target_set, 'Checkpoint target set differs from the exact 47+1 scope.')
    require(plan['contract']['expectedChangedTargets'] == [NEW_TARGET], 'Only new private content target may change.')
    fanout_dir = Path(fanout_dir)
    controls = {name: pinned(fanout_dir / name) for name in ['plan.json', 'readiness.json', 'proposals.json', 'bindings.json', 'independent-audit.json']}
    candidate_path = BATCH / 'calibration/candidates/CAL-07/CAL-07-S01.candidate.json'
    candidate = pinned(candidate_path)
    require(candidate['plan_sha256'] == digest(read(safe(ROOT, str(BATCH / 'plan.json')))), 'Source plan binding mismatch.')
    replay, replay_evidence = replay_archived_fanout(ROOT, fanout_dir, plan, read)
    require(replay == controls['proposals.json'], 'Pinned read-only fanout does not reproduce the proposed content bundle.')
    source_audit = controls['independent-audit.json']
    require(source_audit['status'] == 'PASS' and source_audit['candidateSha256'] == digest(read(ROOT/candidate_path)), 'Exact independently audited candidate required.')
    files, collections, states, bases = [], {}, {}, {}
    for entry in entries:
        target = entry['target']; value = read(safe(packet, entry['path']), entry['sha256'])
        destination = safe(ROOT, target); current = read(destination) if destination.exists() else None
        current_hash = digest(current) if current is not None else None; bases[target] = current_hash
        require(current_hash in (entry['baseSha256'], entry['sha256']), 'Current target changed from declared base: ' + target)
        if target in expected:
            receipt = expected[target]
            source = safe(Path(locations['roots'][receipt['rootId']]['path']).resolve(), receipt['path'])
            original = read(source, receipt['sha256'])
            require(value == original and len(value) == receipt['bytes'] and entry['sha256'] == receipt['sha256'], 'Historical bytes changed: ' + target)
            require(current_hash == receipt['sha256'], 'Completed recovery target must already exist unchanged: ' + target)
            records = [decode(line) for line in value.splitlines() if line.strip()] if target.endswith('.jsonl') else decode(value)
            relative = target.removeprefix('research/corpus/RRX-INGEST-001/')
            values = recovery.state_values(records); states[relative] = {'fieldCount': len(values), 'sha256': digest(canonical(values))}
            if relative in recovery.EXPECTED_COLLECTIONS:
                identity_field, count = recovery.EXPECTED_COLLECTIONS[relative]; ids = [r.get(identity_field) for r in records]
                require(len(records) == count and all(isinstance(i, str) and i for i in ids) and len(set(ids)) == count, 'Historical identities/count mismatch: ' + relative)
                collections[relative] = {'records': count, 'identityField': identity_field, 'orderedIdsSha256': digest(canonical(ids))}
                if relative == 'draft-science/reviews.jsonl':
                    require(all(r.get('full_review_complete') is not True for r in records), 'Historical full-review promotion forbidden.')
        else:
            verify_bundle(value, candidate, controls['bindings.json'], source_audit, replay)
        files.append({'target': target, 'candidatePath': entry['path'], 'sha256': entry['sha256'], 'bytes': len(value),
                      'targetState': 'absent' if current_hash is None else 'same_candidate' if current_hash == entry['sha256'] else 'declared_base'})
    for path, checksum in pins.items(): require(Path(path).is_file() and digest(Path(path).read_bytes()) == checksum, 'Input changed during audit: ' + path)
    for target, checksum in bases.items():
        path = safe(ROOT, target); require((digest(path.read_bytes()) if path.exists() else None) == checksum, 'Target changed during audit: ' + target)
    checks = dict.fromkeys(['matching_prospective_GP_plan','all_plan_inputs_current','exact_48_private_targets','historical_47_bytes_counts_identities_holds_preserved',
        'new_bundle_exactly_matches_separate_scientific_audit_and_source','fanout_reproduces_from_archived_pins_in_isolated_copy','qualitative_partial_source_limits_preserved',
        'zero_clinical_synthesis_or_full_review_or_human_approval_or_release','condition_interventions_layout_pending','current_base_or_unchanged_candidate_verified','inputs_rehashed_after_inspection'], True)
    candidate_digest = digest(canonical(manifest))
    evidence = {'schemaVersion':'remaprx-private-checkpoint-independent-evidence-v1','status':'PASS','scope':'Exact private 47+1 technical continuity/content checkpoint; separate partial scientific audit retained',
        'candidateDigest':candidate_digest,'planId':plan['planId'],'planSha256':plan_hash,'author':manifest['author'],'auditor':AUDITOR,
        'reviewedAt':datetime.now(timezone.utc).isoformat(),'checks':checks,'files':files,'collections':collections,'stateFingerprints':states,
        'contentCounts':{'reports':1,'qualitativeResults':3,'claims':4,'QInputs':15,'locatedQInputs':5,'partialQInputs':10,'mechanismProposals':2,'parentPageProposals':3,'clinicalSynthesisProposals':0,'fullScientificReviews':0,'appraised':0,'humanReviewed':0,'released':0},
        'sourceAuditSha256':digest(read(ROOT/fanout_dir/'independent-audit.json')),'isolatedReplay':replay_evidence,'pinnedArtifacts':pins,
        'limitations':['Remote figure pixels, supplement, numerical graph effects, formal appraisal and external integrity checks remain unfinished.',
                       'No canonical app content, approval, grade, layout or release is changed; integration is restricted to the private corpus.',
                       'Archived fanout replay isolates only explicitly pinned append-only visual documentation changes; current shared documents are preserved. Reader/application integration requires a new current plan.',
                       'Integrator must apply and verify unchanged second import separately.'],'scientificApproval':False,'performedImport':False}
    report={'status':'PASS','candidateDigest':candidate_digest,'targets':sorted(target_set),'inputHashes':{x['path']:x['sha256'] for x in entries},'checks':checks,'author':manifest['author'],'auditor':AUDITOR,'evidence':[]}
    return evidence, report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['packet','plan','readiness']:parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--fanout-dir',default=str(BATCH/'fanout/CAL-07'))
    args=parser.parse_args()
    try:
        evidence,report=audit(args.packet,args.plan,args.readiness,args.fanout_dir)
        ep=safe(args.packet.resolve(),'audit/independent-evidence.json');rp=safe(args.packet.resolve(),'audit/independent_audit.json')
        require(not ep.exists() and not rp.exists(),'Preserve previous audit evidence; use a fresh candidate attempt.')
        data=canonical(evidence);report['evidence']=[{'path':'audit/independent-evidence.json','sha256':digest(data)}]
        recovery.write_new_or_same(ep,data);recovery.write_new_or_same(rp,canonical(report))
        print(json.dumps({'status':'PASS','candidateDigest':report['candidateDigest'],'files':len(evidence['files']),'report':str(rp),'reportSha256':digest(rp.read_bytes()),'evidence':str(ep),'evidenceSha256':digest(data),'performedImport':False}))
        return 0
    except (ValueError,KeyError,OSError,TypeError) as error:
        print(json.dumps({'status':'HOLD','error':str(error),'performedImport':False}));return 1

if __name__=='__main__':raise SystemExit(main())
