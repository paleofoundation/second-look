#!/usr/bin/env python3
"""Integrator checks for a byte-preserving private recovery, never scientific approval.

Exercises the actual candidate twice in a disposable store through the transaction
core. The production CLI's acceptance gate is deliberately separate and remains
mandatory; this isolated test cannot write the application store.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.research_ingest.cli import (canonical, decode, digest, load, safe_path, sha,
    require, preflight, check_readiness, store_lock, apply_context, atomic, summary)


def run(packet, plan_path, readiness_path):
    raw_packet=Path(packet).absolute()
    require(not raw_packet.is_symlink(),'Packet cannot be a symlink')
    packet=raw_packet.resolve()
    private=safe_path(ROOT,'work/research-ingest').resolve()
    require(packet != private and packet.is_relative_to(private),'Packet must be a dedicated private staging directory')
    plan_path=Path(plan_path).resolve()
    context=preflight(ROOT,packet,plan_path,packet/'manifest.json','validate')
    check_readiness(readiness_path,context['plan'],context['planHash'])
    batch=plan_path.parent
    inputs=load(batch/'recovery-inputs.json')['files']
    locations=load(batch/'inventory/source-locations.json')
    by_target={i['target']:i for i in inputs}
    require(len(by_target)==47 and set(by_target)=={w['target'] for w in context['writes']},'Recovery set differs')
    checks=[]
    for item in context['writes']:
        expected=by_target[item['target']]
        historical=safe_path(Path(locations['roots'][expected['rootId']]['path']),expected['path'])
        source=historical.read_bytes()
        require(digest(source)==expected['sha256']==item['sha256'],'Historical hash differs')
        require(len(source)==expected['bytes'] and source==item['data'],'Bytes differ')
        values=([load(historical)] if historical.suffix=='.json' else
                [decode(line) for line in source.splitlines() if line.strip()])
        checks.append({'target':item['target'],'bytes':len(source),'sha256':digest(source),
                       'jsonDocuments':len(values),'exactHistoricalBytes':True})
    # This is an isolated transaction-core test, not production acceptance.
    with tempfile.TemporaryDirectory(prefix='rrx-recovery-test-') as temporary:
        scratch=Path(temporary)
        for pin in context['plan']['inputs']:
            target=safe_path(scratch,pin['path']);target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(safe_path(ROOT,pin['path']),target)
        for item in context['writes']:
            if item['beforeData'] is not None:
                atomic(safe_path(scratch,item['target']),item['beforeData'])
        scratch_plan=scratch/'test-plan.json'
        scratch_plan.write_bytes(plan_path.read_bytes())
        with store_lock(scratch):
            first=apply_context(preflight(scratch,packet,scratch_plan,packet/'manifest.json','validate'))
        with store_lock(scratch):
            second=apply_context(preflight(scratch,packet,scratch_plan,packet/'manifest.json','validate'))
        require(second['changedFiles']==0 and second['status']=='UNCHANGED','Second import changed bytes')
        require(all(sha(safe_path(scratch,w['target']))==w['sha256'] for w in context['writes']),'Scratch output mismatch')
        for result in (first,second):
            if result.get('journal'):result['journal']='temporary-store/journals/'+Path(result['journal']).name
    evidence={'status':'PASS','candidateDigest':context['candidateDigest'],
              'checkedAt':dt.datetime.now(dt.timezone.utc).isoformat(),
              'scope':'byte-preserving private checkpoint; historical dispositions unchanged',
              'historicalByteChecks':checks,'isolatedTransactionFirstImport':first,
              'isolatedTransactionSecondImport':second,'scientificApproval':False,'canonicalImportPerformed':False}
    audit=safe_path(packet,'audit');audit.mkdir(parents=True,exist_ok=True)
    def save(name,value):
        path=safe_path(packet,'audit/'+name)
        data=canonical(value)
        require(not path.exists() or path.read_bytes()==data,'Existing report differs; use a fresh attempt directory')
        if not path.exists():atomic(path,data)
    save('integrator-evidence.json',evidence)
    base={'status':'PASS','candidateDigest':context['candidateDigest'],
          'targets':sorted(by_target),'inputHashes':{w['path']:w['sha256'] for w in context['writes']},
          'evidence':[{'path':'audit/integrator-evidence.json','sha256':sha(audit/'integrator-evidence.json')}]}
    kinds={
        'schema':{'strict_json_and_jsonl_parse':True,'exact_47_file_manifest_and_hashes':True,'historical_schema_bytes_preserved':True},
        'identity':{'every_historical_identity_preserved_byte_for_byte':True,'no_report_or_study_merge':True},
        'source_integrity':{'all_47_historical_sources_rehashed':True,'candidate_bytes_equal_source_bytes':True},
        'preservation':{'all_prose_statuses_corrections_and_exclusions_unchanged':True,'no_scientific_or_human_approval_promotion':True},
        'idempotence':{'actual_candidate_transaction_core_exercised_in_disposable_store':True,'repeat_changed_files_zero':True,'all_final_hashes_match':True},
    }
    for kind, verified in kinds.items():
        save(kind+'.json',{**base,'checks':verified,'scope':'private continuity recovery only'})
    print(json.dumps({'status':'PASS','candidateDigest':context['candidateDigest'],'files':len(checks),
                      'isolatedFirstChanged':first['changedFiles'],'isolatedSecondChanged':second['changedFiles'],
                      'canonicalImportPerformed':False}))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet',required=True);p.add_argument('--plan',required=True);p.add_argument('--readiness',required=True)
    a=p.parse_args();run(a.packet,a.plan,a.readiness)
