"""Validate operational packet and synthetic negative fixtures, not science."""
import copy
import hashlib
import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parent

def load(name):
    return json.loads((ROOT / name).read_text())

def file_hash(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()

def validate_return(data, synthetic=False):
    jsonschema.Draft202012Validator(load('return.schema.json'), format_checker=jsonschema.FormatChecker()).validate(data)
    assignment = load('assignment.json')
    expected = {a['assignmentId']: a['targetSourceId'] for a in assignment['assignments']}
    assert data['inputPlanSha256'] == file_hash('PLAN.md'), 'Input plan hash does not match accepted packet'
    assert data['inputSchemaSha256'] == file_hash('return.schema.json'), 'Input schema hash does not match accepted packet'
    assert synthetic or not data['fixture'], 'Synthetic fixture cannot be received as research'
    assert len({x['assignmentId'] for x in data['assignments']}) == len(expected), 'Duplicate/missing assignment'
    assert {x['assignmentId'] for x in data['assignments']} == set(expected)
    for x in data['assignments']:
        assert x['targetSourceId'] == expected[x['assignmentId']], 'Wrong target source'
    asset_ids = [x['assetId'] for x in data['assets']]
    assert len(asset_ids) == len(set(asset_ids)), 'Duplicate asset ID'
    assert data['fileCount'] == len(data['assets']), 'Count mismatch'
    assert data['totalSourceBytes'] == sum(x['bytes'] for x in data['assets']), 'Byte mismatch'
    for x in data['assets']:
        assert '..' not in Path(x['path']).parts, 'Traversal source path'
        assert x['targetSourceId'] == expected[x['assignmentId']], 'Wrong asset assignment'
        assert x['doi'] or x['pmid'] or x['identifierMissingReason'], 'Missing identifier reason'
        assert x['sourceVersion'] or x['versionMissingReason'], 'Missing version reason'
    for x in data['assignments']:
        assert all(i in asset_ids for i in x['assetIds']), 'Unresolved asset link'
        assert all(a['assignmentId'] == x['assignmentId'] for a in data['assets'] if a['assetId'] in x['assetIds']), 'Cross-assignment asset'
        linked=[a for a in data['assets'] if a['assetId'] in x['assetIds']]
        if x['status'] in ['acquired','partially_acquired']:
            assert linked, 'Acquired status requires actual delivered source files'
        if x['status']=='acquired':
            operation=next(a for a in assignment['assignments'] if a['assignmentId']==x['assignmentId'])
            required_role='full_report' if operation['tier']=='PRIMARY' else 'correction_notice' if x['assignmentId']=='MF-GAP-12' else 'official_label' if x['assignmentId']=='MF-GAP-13' else 'regulatory_context'
            assert any(a['role']==required_role and a['accessBasis']!='metadata_only' for a in linked), 'Metadata or companion-only receipt cannot complete original-source acquisition'
            assert not x['missingArtifacts'], 'Acquired assignment cannot retain missing artifacts'

def validate_inputs():
    a = load('assignment.json')['assignments']
    assert len(a) == 14 and len({x['targetSourceId'] for x in a}) == 14
    assert not {'P-ACTIV6-2026','P-REVIVE-2026'} & {x['targetSourceId'] for x in a}
    assert sum(x['tier']=='PRIMARY' for x in a)==11
    qids = [f'Q{i:02}' for i in range(1,16)]
    assert [x['id'] for x in load('review-questions-and-inputs.json')['questions']] == qids
    planned=load('inputs/planned-review-inputs.json')['papers']
    assert len(planned)==11
    assert {x['targetSourceId'] for x in planned} == {x['targetSourceId'] for x in a if x['tier']=='PRIMARY'}
    assert all([q['id'] for q in p['questions']]==qids for p in planned)
    assert all(x['queries'] and x['knownIdentifiers']['url'] and x['requestedRoles'] for x in a)
    receipt=load('coordination/upstream-delivery-receipt.json')
    b=(ROOT/'coordination/RRX-GAP-001-1.1-request.zip').read_bytes()
    assert hashlib.sha256(b).hexdigest()==receipt['sha256']
    for f in load('INPUT-MANIFEST.json')['files']:
        assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'], 'Input changed: '+f['path']

def main():
    validate_inputs()
    example=load('example-return.synthetic.json')
    validate_return(example, True)
    probes=[]
    x=copy.deepcopy(example);x['assignments'][1]=x['assignments'][0];probes.append(x)
    x=copy.deepcopy(example);x['inputPlanSha256']='bad hash';probes.append(x)
    x=copy.deepcopy(example);x['scientificAssessmentComplete']=True;probes.append(x)
    x=copy.deepcopy(example);x['assignments'].pop();probes.append(x)
    x=copy.deepcopy(example);x['assignments'][0]['targetSourceId']='MF-MASTERS-2019';probes.append(x)
    x=copy.deepcopy(example);x['inputPlanSha256']='0'*64;probes.append(x)
    x=copy.deepcopy(example);x['inputSchemaSha256']='0'*64;probes.append(x)
    x=copy.deepcopy(example);x['assignments'][0]['status']='acquired';x['assignments'][0]['missingArtifacts']=[];probes.append(x)
    asset_example=copy.deepcopy(example)
    first=asset_example['assignments'][0]
    asset={'assetId':'SYNTHETIC-NOT-EVIDENCE','assignmentId':first['assignmentId'],'targetSourceId':first['targetSourceId'],
        'canonicalReportId':'SYNTHETIC-REPORT','role':'full_report','relationshipToTarget':'synthetic test only',
        'title':'Synthetic example, never source evidence','doi':None,'pmid':None,'identifierMissingReason':'synthetic fixture',
        'originalUrl':'https://example.invalid/fixture','resolvedUrl':'https://example.invalid/fixture',
        'retrievedAt':'2026-10-12T00:00:00Z','sourceVersion':None,'versionMissingReason':'synthetic fixture',
        'path':'sources/PRIMARY/synthetic.pdf','mediaType':'application/pdf','bytes':1,'sha256':'0'*64,
        'rights':'synthetic fixture; no actual source','accessBasis':'lawful_full_text','scientificExtraction':'not_performed','quarantine':False}
    asset_example['assets']=[asset];asset_example['fileCount']=1;asset_example['totalSourceBytes']=1
    first['assetIds']=[asset['assetId']]
    validate_return(asset_example,True)
    x=copy.deepcopy(asset_example);x['assets'].append(x['assets'][0]);x['fileCount']=2;x['totalSourceBytes']=2;probes.append(x)
    x=copy.deepcopy(asset_example);x['assets'][0]['sha256']='incorrect';probes.append(x)
    x=copy.deepcopy(asset_example);x['assets'][0]['path']='sources/PRIMARY/../../outside.pdf';probes.append(x)
    x=copy.deepcopy(asset_example);x['assignments'][0]['status']='acquired';x['assignments'][0]['missingArtifacts']=[];x['assets'][0]['accessBasis']='metadata_only';probes.append(x)
    rejected=0
    for probe in probes:
        try:validate_return(probe, True)
        except (AssertionError,jsonschema.ValidationError):rejected+=1
    assert rejected==len(probes)
    try:validate_return(example, False)
    except AssertionError:rejected+=1
    assert rejected==13
    print(json.dumps({'status':'PASS','scope':'prospective exact-gap packet only','assignments':14,'scholarlyReports':11,'questionInputs':165,'negativeProbesRejected':rejected,'dispatched':False,'sourcesAcquired':0}))

if __name__=='__main__':main()
