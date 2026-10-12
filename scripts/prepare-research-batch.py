#!/usr/bin/env python3
"""Prepare a prospective continuity plan; stage byte-preserving recovery after GP.

No source extraction, accepted-science promotion or canonical writes occur here.
Actual canonical writes go through scripts.research_ingest and its audit gate.
"""
import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.research_ingest.cli import safe_path, decode
BATCH = ROOT / 'research/batches/RRX-INGEST-001'
DEFAULT_PLAN_ID = 'RRX-INGEST-001-1.3'

def read(path):
    return decode(path.read_bytes())

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n')

def relative(path):
    return path.relative_to(ROOT).as_posix()

def prepare(args):
    plan_id = args.plan_id
    snapshot_version = plan_id.rsplit('-', 1)[-1]
    if not snapshot_version or any(c not in '0123456789.' for c in snapshot_version):
        raise SystemExit('Plan identity must end in a numeric dotted snapshot version.')
    if (BATCH / 'plan.json').exists():
        raise SystemExit('Plan exists. Preserve it in history with its disposition before explicitly preparing a new version.')
    locations = read(BATCH / 'inventory/source-locations.json')
    research = Path(locations['roots']['RESEARCH']['path'])
    historical = Path(args.historical_contract)
    schemas = BATCH / 'schemas'
    lineage = []
    for name in ['candidate.schema.json', 'results.schema.json']:
        source = historical / name
        data = read(source)
        data['$id'] = 'urn:remaprx:rrx-ingest-001:' + name
        if name == 'candidate.schema.json':
            data['properties']['schema_version']['const'] = 'RRX-SCIENTIFIC-CANDIDATE-1.0'
            data['properties']['plan_id']['const'] = plan_id
        write(schemas / name, data)
        lineage.append({'source': str(source), 'sourceSha256': sha(source),
                        'destination': relative(schemas / name), 'sha256': sha(schemas / name),
                        'adaptation': 'New namespace and prospective plan identity; draft, missingness and provenance restrictions retained.'})
    question_map = ROOT / 'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json'
    (schemas / question_map.name).write_bytes(question_map.read_bytes())
    write(schemas / 'provenance.json', {'sources': lineage, 'questionMapSha256': sha(question_map)})
    recovery = []
    for collection in ['acquisition', 'draft-science']:
        directory = research / 'outputs/research/evidence' / collection
        for path in sorted(directory.iterdir()):
            if path.is_file() and path.suffix in {'.json', '.jsonl'}:
                recovery.append({'rootId': 'RESEARCH', 'path': path.relative_to(research).as_posix(),
                                 'sha256': sha(path), 'bytes': path.stat().st_size,
                                 'target': f'research/corpus/RRX-INGEST-001/{collection}/{path.name}'})
    prior_names = ['corpus.json','results.jsonl','claims.jsonl','reviews.jsonl','papers.jsonl','studies.jsonl',
                   'context.jsonl','pages.jsonl','coverage.json','identity-map.json','open-flags.json',
                   'quarantine.json','numerical-audit.json','source-manifest.json','validation.json','evidence.schema.json']
    for name in prior_names:
        path = research / 'outputs/research/evidence' / name
        recovery.append({'rootId':'RESEARCH','path':path.relative_to(research).as_posix(),
                         'sha256':sha(path),'bytes':path.stat().st_size,
                         'target':f'research/corpus/RRX-INGEST-001/prior-evidence/{name}'})
    write(BATCH / 'recovery-inputs.json', {'scope': 'byte-preserving private checkpoint; no scientific reacceptance', 'files': recovery})
    inputs = [ROOT / 'AGENTS.md', ROOT / 'docs/RESEARCH-INGEST.md', ROOT / 'docs/PROJECT-RULES.md',
              ROOT / 'docs/RULE-CHANGELOG.md',
              ROOT / 'rules/one-match-rule/ONE-MATCH-RULE.md', BATCH / 'PLAN.md',
              BATCH / 'recovery-inputs.json', BATCH / 'cited-paper-ledger.json',
              BATCH / 'synthesis-identity-map.json', BATCH / 'calibration/assignments.json']
    ledger = read(BATCH / 'cited-paper-ledger.json')
    for name, expected in ledger['inputHashes'].items():
        source = safe_path(ROOT, name)
        if sha(source) != expected:
            raise SystemExit('Citation ledger input changed; regenerate before planning: '+name)
        inputs.append(source)
    inputs += [ROOT / 'scripts/prepare-research-batch.py', ROOT / 'scripts/research_inventory.py',
               ROOT / 'scripts/research-review-coverage.mjs', ROOT / 'scripts/apply-reader-outcomes.py',
               ROOT / 'editorial/mechanism-expansion/mechanism-extraction-schema.json']
    inputs += sorted((ROOT/'scripts/research_ingest').glob('*.py'))
    inputs += [ROOT/'scripts/research_ingest/README.md', ROOT/'scripts/research_ingest/requirements.txt']
    inputs += [ROOT/'tests/research_ingest'/name for name in
               ['test_engine.py','test_inventory.py','test_recovery_audit.py',
                'test_source_validation.py','test_mechanism_schema.py']]
    inputs += sorted(schemas.glob('*.json'))
    inputs += sorted((BATCH / 'inventory').glob('*.json')) + sorted((BATCH / 'inventory').glob('*.jsonl'))
    inputs += [ROOT / 'data' / f for f in ['content.json','reader-evidence.json','review-envelopes.json','private-reviews.json']]
    inputs += [ROOT / 'editorial' / f for f in ['reader-source-aliases.json','reader-source-corrections.json']]
    if args.source_continuation:
        disposition = BATCH/'history/plan-1.2-preserved/disposition.json'
        previous = read(disposition)
        if not previous['completedRecovery']['currentRecoveredFilesMatch']:
            raise SystemExit('Prior recovery has not been reconciled.')
        for item in recovery:
            if sha(safe_path(ROOT,item['target'])) != item['sha256']:
                raise SystemExit('Recovered checkpoint changed: '+item['target'])
        inputs += [disposition] + [ROOT/item['target'] for item in recovery]
    # Keep all shared app, rule and legacy inputs portable even when another
    # chat owns their uncommitted bytes. Core tools/tests are committed directly.
    snapshot_root = BATCH/'app-inputs'/snapshot_version
    if args.snapshot_revision is not None:
        if args.snapshot_revision < 2:
            raise SystemExit('A replacement proposal snapshot revision must be at least2.')
        snapshot_root = snapshot_root/f'revision-{args.snapshot_revision}'
    snapshot_map = []
    for source in sorted(set(inputs)):
        name = relative(source)
        if name.startswith(('research/', 'scripts/', 'tests/')):
            continue
        snapshot = snapshot_root/name
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        if snapshot.exists() and snapshot.read_bytes() != source.read_bytes():
            raise SystemExit('Preserved snapshot differs; create a new prospective version: '+name)
        if not snapshot.exists():
            snapshot.write_bytes(source.read_bytes())
        snapshot_map.append({'originalPath':name,'snapshotPath':relative(snapshot),
                             'sha256':sha(snapshot),'bytes':snapshot.stat().st_size})
        inputs.append(snapshot)
    source_map = snapshot_root/'source-map.json'
    write(source_map, {'schemaVersion':'remaprx-app-input-snapshots-v1','planId':plan_id,
                      'files':snapshot_map,
                      'replay':'Overlay verified snapshot bytes at originalPath in an isolated replay checkout only. Never overwrite the active shared app. A fresh clone may require this overlay before plan-input validation can pass.'})
    inputs.append(source_map)
    plan = {
        'schemaVersion': 'remaprx-ingest-plan-v1', 'planId': plan_id,
        'createdAt': dt.datetime.now(dt.timezone.utc).isoformat(),
        'operations': ['validate'] if args.source_continuation else ['validate','stage','diff','apply'],
        'allowedTargets': [item['target'] for item in recovery],
        'inputs': [{'path': relative(p), 'sha256': sha(p)} for p in sorted(set(inputs))],
        'contract': {
            'batchId': 'RRX-INGEST-001', 'ownerInstructionDate': '2026-10-12',
            'fullPlan': relative(BATCH / 'PLAN.md'),
            'scope': ('Validate and continue isolated draft source candidates after completed private checkpoint recovery. No stage/apply, new acquisition or public mutation is authorized by this continuation.' if args.source_continuation else 'Reconcile and recover private checkpoint; calibrated source extraction and content proposals under pinned schemas. Reader data application requires an explicit new allowlist and acceptance.'),
            'mode': 'historical_closed_packet_reuse; separately planned future gap acquisition',
            'sourceResolver': relative(BATCH / 'inventory/source-locations.json'),
            'targetRegistry': relative(BATCH / 'inventory/target-registry.json'),
            'sourceInventory': relative(BATCH / 'inventory/source-records.jsonl'),
            'identityLedger': relative(BATCH / 'inventory/identity-groups.jsonl'),
            'sourceSchema': relative(schemas / 'candidate.schema.json'),
            'resultSchema': relative(schemas / 'results.schema.json'),
            'mechanismSchema': relative(schemas / 'mechanism-candidate.schema.json'),
            'mechanismContract': 'RRX-MECHANISM-CANDIDATE-1.0 is the enforcing payload schema with source/result semantic checks. The legacy mechanism-extraction-schema.json remains a descriptive historical field contract only. Existing null payloads stay incomplete and are not silently promoted.',
            'appInputSnapshots': relative(source_map),
            'replayBoundary': 'Current active inputs and immutable snapshots are both pinned. Shared uncommitted app bytes may differ in a fresh clone; use the documented isolated overlay before validation, never alter the active app for replay.',
            'completedRecovery': relative(BATCH/'history/plan-1.2-preserved/disposition.json') if args.source_continuation else None,
            'inactiveRecoveryTargets': args.source_continuation,
            'currentActivation': 'CAL-07 binding-only continuation after independent GP; no further CAL-01/CAL-03 extraction in this operation.' if args.source_continuation else 'Only first tranche after matching GP readiness.',
            'separateConditionBatch': 'RRX-CONDITION-001 is a separate condition-led operation owned elsewhere. This historical repair/current-target MOA continuation neither imports that batch nor establishes condition-research completeness.',
            'reviewInputMap': relative(schemas / question_map.name),
            'calibrationAssignments': relative(BATCH / 'calibration/assignments.json'),
            'citedPaperLedger': relative(BATCH / 'cited-paper-ledger.json'),
            'synthesisIdentityMap': relative(BATCH / 'synthesis-identity-map.json'),
            'mechanismTargets': ['D01','D06','D07','D08','D10','D26','D31','D34'],
            'moaScope': 'existing targets only; extra drug names remain leads',
            'fanout': {'integrators':1,'workerSlots':3,'ownership':'canonical report plus companions and coordinated family',
                       'calibrationReportPackets':24,'calibrationTranches':3,'packetsPerTranche':8,
                       'initialBatchSize':20,'largerBatchSize':30,'largerBatchAfterAcceptedBatches':2,
                       'acceptOwnWork':False},
            'verification': {'calibrationIndependentAudit':1.0,'publicNumericalClaims':1.0,
                             'launchSources':1.0,'otherFulltextAuditMinimum':0.1,
                             'materialError':'expand affected worker/design/format audit'},
            'delivery': {'externalWorker':'Grok gap-only acquisition via downloadable attachments',
                         'dispatchRequires':'separate filled request, packet and GP readiness',
                         'returnRequires':['actual files','hash manifest','searches','screening','gaps','review-inputs.jsonl','CHATGPT-INGEST-PROMPT.txt'],
                         'receiver':'this project; manual attachment transfer then independent receipt verification'},
            'release': {'technicalAcceptanceIsScientificApproval':False,'publication':False,
                        'humanReview':'pending unless separately documented for exact version','reviewAccess':'free_authenticated'},
        },
    }
    write(BATCH / 'plan.json', plan)
    print(json.dumps({'planId':plan_id,'planSha256':sha(BATCH/'plan.json'),'targets':len(recovery),'readiness':'NOT_YET_RECORDED'}))

def checkpoint(args):
    plan = read(BATCH / 'plan.json')
    if 'stage' not in plan['operations']:
        raise SystemExit('Checkpoint staging is outside this prospective plan.')
    gate = read(BATCH / 'readiness.json')
    if gate.get('status') != 'PASS' or gate.get('scope') != 'GP_PLAN' or gate.get('planSha256') != sha(BATCH / 'plan.json'):
        raise SystemExit('Matching prospective GP Plan PASS is required before checkpoint staging.')
    for item in plan['inputs']:
        if sha(safe_path(ROOT,item['path'])) != item['sha256']:
            raise SystemExit('Pinned input changed: '+item['path'])
    locations = read(BATCH / 'inventory/source-locations.json')
    raw_packet = Path(args.packet).absolute()
    if raw_packet.is_symlink():
        raise SystemExit('Packet root cannot be a symlink.')
    packet = raw_packet.resolve()
    private_staging = safe_path(ROOT,'work/research-ingest').resolve()
    if packet == private_staging or not packet.is_relative_to(private_staging):
        raise SystemExit('Packet must be a dedicated attempt directory under work/research-ingest, outside public assets and canonical stores.')
    entries = []
    for item in read(BATCH/'recovery-inputs.json')['files']:
        source = safe_path(Path(locations['roots'][item['rootId']]['path']), item['path'])
        data = source.read_bytes()
        if hashlib.sha256(data).hexdigest() != item['sha256']:
            raise SystemExit('Source changed: '+str(source))
        if item['target'] not in plan['allowedTargets']:
            raise SystemExit('Target outside prospective plan: '+item['target'])
        target = safe_path(ROOT,item['target'])
        path = 'candidate/' + item['target']
        destination = safe_path(packet,path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and destination.read_bytes() != data:
            raise SystemExit('Existing packet bytes differ; use a new attempt directory: '+str(destination))
        if not destination.exists():
            destination.write_bytes(data)
        entries.append({'target':item['target'],'path':path,'sha256':item['sha256'],
                        'baseSha256':sha(target) if target.exists() else None})
    manifest = {'schemaVersion':'remaprx-candidate-v1','planId':plan['planId'],'planSha256':sha(BATCH/'plan.json'),
                'batchId':'RRX-INGEST-001-RECOVERY','author':'codex/root','files':entries}
    manifest_path=safe_path(packet,'manifest.json')
    if manifest_path.exists() and read(manifest_path) != manifest:
        raise SystemExit('Existing candidate manifest differs; use a new attempt directory.')
    if not manifest_path.exists():
        write(manifest_path,manifest)
    print(json.dumps({'status':'STAGED_CANDIDATE','files':len(entries),'canonicalImport':False,'packet':str(packet)}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare');p.add_argument('--historical-contract',required=True);p.add_argument('--plan-id',default=DEFAULT_PLAN_ID);p.add_argument('--source-continuation',action='store_true');p.add_argument('--snapshot-revision',type=int)
    p = sub.add_parser('checkpoint');p.add_argument('--packet',required=True)
    args = parser.parse_args()
    (prepare if args.command == 'prepare' else checkpoint)(args)
