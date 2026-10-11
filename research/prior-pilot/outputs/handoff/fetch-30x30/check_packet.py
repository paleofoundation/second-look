"""Offline packet/return preflight. Python 3 standard library; never dispatches or imports."""
import argparse, hashlib, json, pathlib, sys
from urllib.parse import urlsplit, parse_qs

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path): return json.loads(path.read_text())

def check_packet(root):
    failures=[]
    def check(ok,why):
        if not ok: failures.append(why)
    plan=load(root/'ingestion-plan-v3.1.json')
    check(plan['plan_id']=='SL-INGEST-3.1-FETCH30','Wrong plan identity')
    check(plan['applicable_rule']['version']=='1.11','Wrong applicable rule')
    t=load(root/'transfer-contract.json')
    check(t['input_archive']=='second-look-fetch-30x30-v2.1-input.zip','Missing concrete input archive')
    check(all((root/n).is_file() for n in t['input_files'] if n not in ['readiness.json','packet-manifest.json']),'Missing transfer dependency')
    query_rows=load(root/'query-locations.json')['requests']
    check(len(query_rows)==98,'Question-specific query location coverage lost')
    for row in query_rows:
        seeds=row['query_seeds'];urls=row['pubmed_seed_urls']
        check(len(seeds)==len(urls),row['request_id']+' query/URL alignment mismatch')
        for seed,url in zip(seeds,urls):
            parsed=urlsplit(url)
            check(parsed.scheme=='https' and parsed.netloc=='pubmed.ncbi.nlm.nih.gov' and parse_qs(parsed.query).get('term')==[seed],row['request_id']+' executable URL does not match query seed')
            check(not seed.startswith(('Run exact-title/printed-DOI lookups','Resolve all named recovery-targets.json')),row['request_id']+' retrieval instruction encoded as search query')
        for instruction in row.get('retrieval_instructions',[]):
            check(instruction.get('kind')=='retrieval_instruction' and bool(instruction.get('text')) and instruction.get('executable_search_url') is None,row['request_id']+' instruction must have no executable search URL')
    for instruction_id in ['ITRACONAZOLE-CANCER','RECOVERY']:
        row=next((r for r in query_rows if r['request_id']==instruction_id),{})
        check(bool(row.get('retrieval_instructions')),instruction_id+' retrieval instruction label missing')
    check('CHATGPT-INGEST-PROMPT.txt' in t['reverse_prompt'],'Reverse ingest prompt contract missing')
    catalogue=load(root/'coverage-catalogue.json')
    requests=load(root/'requests.json')['requests']
    for f in plan['inputs']:
        p=root/f['path'];check(p.is_file() and sha(p)==f['sha256'],'Input changed: '+f['path'])
    drugs=catalogue['drugs'];conditions=catalogue['conditions']
    check(len(drugs)==30 and len({d['id'] for d in drugs})==30,'Exactly30 distinct drug IDs required')
    check(len(conditions)==30 and len({d['id'] for d in conditions})==30,'Exactly30 distinct condition IDs required')
    check(len({d['name'].casefold() for d in drugs})==30,'Drug names duplicated')
    check(len({d['name'].casefold() for d in conditions})==30,'Condition names duplicated')
    ids={r['id'] for r in requests};check(len(ids)==len(requests),'Duplicate request IDs')
    expected={d['request_id'] for d in drugs+conditions}|{f'DR{i:03d}' for i in range(1,37)}|{'RECOVERY','ITRACONAZOLE-CANCER'}
    check(ids==expected,'Request catalogue must cover both30-entity axes, all36 Reddit questions, recovery and itraconazole')
    drugids={d['id'] for d in drugs};condids={d['id'] for d in conditions};demandids={f'DR{i:03d}' for i in range(1,37)}
    for r in requests:
        for field in ['question','population','intervention','comparator','outcomes','inclusions','exclusions','queries','directness_pitfalls','completion']:
            check(bool(r.get(field)),r['id']+' missing '+field)
        check(set(r['drug_ids'])<=drugids,r['id']+' unknown drug')
        check(set(r['condition_ids'])<=condids,r['id']+' unknown condition')
        check(set(r['demand_ids'])<=demandids,r['id']+' unknown Reddit question')
    for edge in catalogue['pairs']:
        check(edge['drug_id'] in drugids and edge['condition_id'] in condids,'Orphan condition–drug edge')
    for c in conditions: check(any(e['condition_id']==c['id'] for e in catalogue['pairs']),c['id']+' has no candidate drug search')
    for d in drugs: check(any(e['drug_id']==d['id'] for e in catalogue['pairs']),d['id']+' has no condition search')
    itra=[d for d in drugs if d['name'].casefold()=='itraconazole'];check(len(itra)==1,'Itraconazole missing/duplicated')
    ir=next((r for r in requests if r['id']=='ITRACONAZOLE-CANCER'),{})
    check(ir.get('priority')=='mandatory_first_wave','Itraconazole not mandatory first wave')
    check(len(load(root/'itraconazole-primary-leads.json')['primary_report_candidates'])>=5,'Printed itraconazole leads missing')
    workers=load(root/'worker-packets.json')['packets']
    assigned=[i for p in workers for i in p['request_ids']]
    check(set(assigned)==ids,'Some requests lack a worker')
    check(len(assigned)==len(set(assigned)),'Request has multiple primary owners')
    return {'status':'PASS' if not failures else 'FAIL','plan_id':plan['plan_id'],'plan_sha256':sha(root/'ingestion-plan-v3.1.json'),
            'drug_count':len(drugs),'condition_count':len(conditions),'request_count':len(requests),'worker_count':len(workers),
            'failures':failures,'performed_acquisition':False,'performed_ingestion':False}

def check_return(root,path):
    r=load(path);fail=[]
    def ck(ok,why):
        if not ok: fail.append(why)
    plan=load(root/'ingestion-plan-v3.1.json');reqs={x['id'] for x in load(root/'requests.json')['requests']}
    catalogue=load(root/'coverage-catalogue.json');drugids={x['id'] for x in catalogue['drugs']};condids={x['id'] for x in catalogue['conditions']};demandids={f'DR{i:03d}' for i in range(1,37)}
    ck(r['plan_sha256']==sha(root/'ingestion-plan-v3.1.json'),'Wrong plan hash')
    ck(r['schema_version']=='SL-ACQUISITION-3.1' and r['plan_id']==plan['plan_id'] and r['packet_version']=='2.1','Wrong schema/plan/packet identity')
    ck(r['synthetic'] is False,'Synthetic fixture cannot be received as evidence')
    ck(r['extraction_status']=='not_started','This contract accepts acquisition only')
    ck(set(r['scope_request_ids'])<=reqs and bool(r['scope_request_ids']),'Unknown/empty scope')
    worker=next((w for w in load(root/'worker-packets.json')['packets'] if w['id']==r['batch_id']),None)
    ck(worker is not None,'Unknown batch')
    if worker: ck(set(r['scope_request_ids'])==set(worker['request_ids']),'Batch requests silently omitted/changed')
    cov=r['coverage'];ck(len(cov)==len({c['request_id'] for c in cov}),'Duplicate coverage')
    ck({c['request_id'] for c in cov}==set(r['scope_request_ids']),'Coverage omissions')
    sids={s['source_id'] for s in r['sources']};qids={s['search_id'] for s in r['searches']}
    ck(len(sids)==len(r['sources']) and len(qids)==len(r['searches']),'Duplicate source/search IDs')
    gids={g['gap_id'] for g in r['gaps']}
    for s in r['sources']:
        ck(set(s['request_ids'])<=reqs and bool(s['request_ids']),'Source missing/unknown request')
        ck(set(s['drug_ids'])<=drugids and set(s['condition_ids'])<=condids and set(s['demand_ids'])<=demandids,'Source has unknown drug/condition/demand ID')
        ck(set(s['related_source_ids'])<=sids,'Source has unknown related-source reference')
        ck(all(s[k] is None or s[k] in sids for k in ['duplicate_of','version_of']),'Source has unknown duplicate/version target; include identity stub for cross-batch references')
        ck(all(s[k]!=s['source_id'] for k in ['duplicate_of','version_of']),'Source cannot be its own duplicate/version')
        ck(not s['fulltext_read'] and s['result_extraction_status']=='not_started','Acquisition record claims scientific reading/extraction')
        ck((s['collection']=='PRIMARY')==(s['context_tier'] is None),'Tier collection mismatch')
        ck(s['report_role'] not in ['review','textbook','official_context'] or s['collection']=='CONTEXT','Background promoted to primary')
        if s['doi_verified']: ck(bool(s['doi_verification_source']),'DOI lacks verification provenance')
        if s['filename']:
            p=(path.parent/s['filename']).resolve()
            ck(p.is_relative_to(path.parent.resolve()),'Unsafe source path')
            ck(p.is_file(),'Missing source file')
            if p.is_file() and p.is_relative_to(path.parent.resolve()):
                ck(sha(p)==s['sha256'] and p.stat().st_size==s['bytes'],'Source bytes/hash mismatch')
                if s['access_state']=='full_pdf': ck(p.read_bytes()[:5]==b'%PDF-','PDF is a challenge page/wrong format')
        else: ck(s['access_state'] not in ['full_pdf','full_html'],'Acquired full text has no file')
    for c in cov:
        ck(set(c['source_ids'])<=sids and set(c['search_ids'])<=qids,'Coverage has orphan source/search')
        ck(set(c['remaining_gaps'])<=gids,'Coverage has orphan gap')
        if c['status']=='complete_against_declared_search':
            ck(bool(c['search_ids']) and not c['remaining_gaps'],'Complete coverage lacks search or still has gaps')
        ss=[s for s in r['sources'] if s['source_id'] in c['source_ids']]
        ck(all(c['request_id'] in s['request_ids'] for s in ss),'Coverage cites source assigned only to another request')
        ck(all(c['request_id'] in s['request_ids'] for s in r['searches'] if s['search_id'] in c['search_ids']),'Coverage cites search assigned only to another request')
        ck(all(c['request_id'] in g['request_ids'] for g in r['gaps'] if g['gap_id'] in c['remaining_gaps']),'Coverage cites unrelated gap')
        ck(c['primary_fulltexts']==sum(s['collection']=='PRIMARY' and s['report_role']=='original_report' and s['access_state'] in ['full_pdf','full_html'] and not s['duplicate_of'] for s in ss),'Primary counts include duplicates/background/access gaps')
        ck(c['background_sources']==sum(s['collection']=='CONTEXT' and not s['duplicate_of'] for s in ss),'Background counts mismatch')
        if c['independent_study_families'] is not None:
            eligible=[s for s in ss if s['collection']=='PRIMARY' and s['report_role']=='original_report' and not s['duplicate_of']]
            ck(all(s['family_identity_status']=='verified' and s['study_family_id'] for s in eligible),'Unresolved families cannot yield verified independent-study count')
            ck(c['independent_study_families']==len({s['study_family_id'] for s in eligible}),'Independent-study count mismatch')
    for g in r['gaps']: ck(set(g['request_ids'])<=reqs and set(g['source_ids'])<=sids,'Gap has orphan request/source reference')
    for s in r['searches']: ck(set(s['request_ids'])<=reqs and bool(s['request_ids']),'Search has missing/unknown request')
    for s in r['screening']: ck(s['search_id'] in qids and (s['source_id'] is None or s['source_id'] in sids),'Screening has orphan reference')
    rc=r['reconciliation'];sc=r['screening']
    ck(rc['candidates_screened']==len(sc),'Screening count mismatch')
    for label,decision in [('excluded_candidates','exclude'),('duplicate_candidates','duplicate'),('uncertain_candidates','uncertain')]: ck(rc[label]==sum(s['decision']==decision for s in sc),'Reconciliation mismatch: '+label)
    ck(rc['included_sources']==len(r['sources']),'Source count mismatch')
    ck(rc['files_received']==sum(bool(s['filename']) for s in r['sources']),'File count mismatch')
    ck(rc['unavailable_sources']==sum(s['access_state'] in ['inaccessible','unreadable','metadata_only','abstract_only','partial','registry_only'] for s in r['sources']),'Unavailable count mismatch')
    return {'status':'PASS' if not fail else 'FAIL','failures':fail,'schema_validation':'Required separately against acquisition-return.schema.json; this command checks semantic/file invariants','imported':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--return-file',type=pathlib.Path);p.add_argument('--delivery-receipt',type=pathlib.Path);a=p.parse_args()
    root=pathlib.Path(__file__).resolve().parent
    try:
        result=check_return(root,a.return_file) if a.return_file else check_packet(root)
        if a.return_file:
            if not a.delivery_receipt: result['failures'].append('Missing --delivery-receipt: data-only checks cannot accept transfer')
            else:
                from check_delivery import check_delivery
                transfer=check_delivery(root,a.return_file,a.delivery_receipt)
                result['delivery']=transfer
                result['failures']+=transfer['failures']
            result['status']='PASS' if not result['failures'] else 'FAIL'
    except (OSError,ValueError,KeyError,TypeError) as e: result={'status':'FAIL','failures':[str(e)]}
    print(json.dumps(result,indent=2));sys.exit(result['status']!='PASS')
