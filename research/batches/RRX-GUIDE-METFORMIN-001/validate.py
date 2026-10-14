"""Validate inventory claims; no scientific acceptance is inferred."""
import copy
import hashlib
import json
import sys
from pathlib import Path

import jsonschema

HERE = Path(__file__).resolve().parent
APP = HERE.parents[2]

def read(name):
    return json.loads((HERE / name).read_text())

def check(data, check_inputs=True):
    jsonschema.Draft202012Validator(read('packet.schema.json')).validate(data)
    source_ids = [r['sourceId'] for r in data['sources']]
    assert len(set(source_ids)) == len(source_ids), 'Duplicate source identity'
    content = json.loads((APP / 'data/content.json').read_text())
    expected = next(g['sourceIds'] for g in content['guides'] if g['id'] == 'G-METFORMIN')
    assert source_ids == expected, 'Current article coverage/order mismatch'
    for r in data['sources']:
        qids = [q['id'] for q in r['questionCoverage']]
        assert qids == ([] if r['sourceId'] in ['MF-LABEL-2025', 'MF-FDA-GENERICS'] else [f'Q{i:02}' for i in range(1,16)]), 'Question map coverage mismatch'
        held = r['integrityState'] == 'quarantined'
        assert not held or r['sourceId'] == 'P-REVIVE-2026'
        for m in r['matches']:
            for a in m['assets']:
                if a['status'] == 'hash_verified':
                    assert a['observedSha256'] == a['expectedSha256'], 'Asset hash mismatch'
    if check_inputs:
        for f in read('input-manifest.json')['files']:
            source = HERE / f['snapshot'] if f.get('snapshot') else APP / f['path']
            assert hashlib.sha256(source.read_bytes()).hexdigest() == f['sha256'], 'Input changed: ' + f['path']

def main():
    data = read('coverage-ledger.json')
    check(data)
    mutations = []
    x = copy.deepcopy(data); x['sources'].pop(); mutations.append(x)
    x = copy.deepcopy(data); x['sources'][1]['questionCoverage'][1]['id']='Q01'; mutations.append(x)
    x = copy.deepcopy(data); x['sources'][1]['newFullAssessment']='complete'; mutations.append(x)
    x = copy.deepcopy(data)
    asset = next(a for r in x['sources'] for m in r['matches'] for a in m['assets'])
    asset['observedSha256']='0'*64; mutations.append(x)
    rejected=0
    for m in mutations:
        try: check(m, False)
        except (AssertionError,jsonschema.ValidationError): rejected+=1
    assert rejected==len(mutations)
    print(json.dumps({'status':'PASS', 'scope':'metadata reconciliation and preserved holds only', 'sources':len(data['sources']), 'negativeProbesRejected':rejected, 'scientificAssessment':'not_completed'}))

if __name__ == '__main__': main()
