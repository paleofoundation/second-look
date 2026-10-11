"""Read-only transfer acceptance. No extraction, import, network or archive unpacking."""
import hashlib, json, pathlib, re, zipfile
PROJECT='01a11a22-f81b-7682-b4a9-64ed1859b295'
PLAN='SL-INGEST-3.1-FETCH30'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def safe(path):
    p=pathlib.PurePosixPath(path)
    return bool(path) and not p.is_absolute() and '..' not in p.parts and '\\' not in path

def check_delivery(packet, data_file, receipt_file):
    failures=[]
    def ck(ok,msg):
        if not ok: failures.append(msg)
    try:
        data=json.loads(data_file.read_text());r=json.loads(receipt_file.read_text());batch=data['batch_id']
        ready=json.loads((packet/'readiness.json').read_text())
        ck(ready.get('status')=='PASS' and ready.get('plan_id')==PLAN and ready.get('plan_sha256')==sha(packet/'ingestion-plan-v3.1.json'),'Canonical acquisition readiness missing/stale')
        prefix=f'return/{batch}/';expected_receipt=f'second-look-fetch-30x30-v2.1-{batch}-delivery-receipt.json'
        ck(r['schema_version']=='SL-DELIVERY-3.1','Wrong delivery schema')
        ck(r['project_id']==PROJECT and r['batch_id']==batch and r['packet_version']=='2.1','Wrong project/batch/version')
        ck(r['plan_id']==PLAN and r['plan_sha256']==sha(packet/'ingestion-plan-v3.1.json'),'Wrong delivery plan/hash')
        ck(r['synthetic'] is False,'Synthetic delivery cannot be received as evidence')
        ck(receipt_file.name==expected_receipt,'Wrong project-qualified receipt filename')
        ck(r['transfer_status']=='attachments_created_awaiting_manual_transfer','Delivery did not create the contracted attachments')
        ck(r['receiver_access_status']=='not_verified_by_sender','Sender cannot certify ChatGPT receipt/access')
        ck(r['ingest_prompt_path']==prefix+'CHATGPT-INGEST-PROMPT.txt','Wrong reverse-prompt path')
        ck(r['acquisition_data_path']==prefix+'acquisition-return.json','Wrong data path')
        parts=r['archives'];ck(bool(parts),'No actual archives delivered')
        ck(len(parts)==len({p['filename'] for p in parts}),'Duplicate archive')
        collected={};manifests=[];archive_payload={}
        for i,part in enumerate(parts,1):
            name=part['filename'];ck(safe(name) and '/' not in name,'Unsafe archive filename')
            expected=f'second-look-fetch-30x30-v2.1-{batch}-return'+(f'-part-{i:02d}-of-{len(parts):02d}' if len(parts)>1 else '')+'.zip'
            ck(name==expected,'Archive name/part ordering mismatch')
            archive=receipt_file.parent/name
            ck(archive.is_file(),'Missing archive: '+name)
            if not archive.is_file() or not safe(name) or '/' in name: continue
            ck(sha(archive)==part['sha256'] and archive.stat().st_size==part['bytes'],'Archive byte/hash mismatch: '+name)
            with zipfile.ZipFile(archive) as z:
                names=z.namelist();ck(len(names)==len(set(names)),'Duplicate member within ZIP')
                ck(z.testzip() is None,'Corrupt ZIP')
                for zi in z.infolist():
                    ck(safe(zi.filename) and zi.filename.startswith(prefix),'Unsafe/cross-batch ZIP member')
                    ck((zi.external_attr>>16)&0o170000 != 0o120000,'Symlink in ZIP')
                mp=part['manifest_path'];ck(mp==prefix+f'manifest-part-{i:02d}.json','Wrong manifest path')
                ck(mp in names,'Missing part manifest')
                if mp not in names: continue
                mb=z.read(mp);ck(hashlib.sha256(mb).hexdigest()==part['manifest_sha256'],'Manifest hash mismatch')
                m=json.loads(mb);manifests.append(m)
                ck(m['schema_version']=='SL-RETURN-MANIFEST-3.1' and m['project_id']==PROJECT and m['batch_id']==batch,'Wrong manifest identity')
                ck(m['part_number']==i and m['part_count']==len(parts),'Manifest split-part mismatch')
                ck(m['plan_sha256']==r['plan_sha256'],'Manifest plan mismatch')
                ck(m['synthetic'] is False,'Synthetic manifest cannot be received as evidence')
                paths=[f['path'] for f in m['files']]
                ck(len(paths)==len(set(paths)),'Duplicate manifest payload')
                ck(set(names)==set(paths)|{mp},'Unmanifested or missing ZIP payload')
                for f in m['files']:
                    n=f['path'];ck(safe(n) and n.startswith(prefix),'Unsafe manifest payload path')
                    ck(n!=mp,'Manifest cannot hash itself')
                    if n not in names: continue
                    raw=z.read(n)
                    ck(len(raw)==f['bytes'] and hashlib.sha256(raw).hexdigest()==f['sha256'],'Payload bytes/hash mismatch: '+n)
                    ck(n not in collected,'Payload duplicated across parts: '+n)
                    collected[n]=raw;archive_payload[n]=f
        required=[prefix+'acquisition-return.json',prefix+'CHATGPT-INGEST-PROMPT.txt']+[prefix+'contract/'+n for n in ['ingestion-plan-v3.1.json','readiness.json','acquisition-return.schema.json','delivery-receipt.schema.json','return-manifest.schema.json','coverage-catalogue.json','requests.json','worker-packets.json']]
        for n in required: ck(n in collected,'Missing return contract payload: '+n)
        dp=prefix+'acquisition-return.json'
        if dp in collected:
            ck(collected[dp]==data_file.read_bytes(),'Delivered data differs from receiving data_file')
        for n in ['ingestion-plan-v3.1.json','readiness.json','acquisition-return.schema.json','delivery-receipt.schema.json','return-manifest.schema.json','coverage-catalogue.json','requests.json','worker-packets.json']:
            key=prefix+'contract/'+n
            if key in collected: ck(collected[key]==(packet/n).read_bytes(),'Returned contract differs: '+n)
        for s in data['sources']:
            if s['filename']:
                n=prefix+s['filename'];ck(n in collected,'Source not delivered: '+n)
                if n in collected: ck(hashlib.sha256(collected[n]).hexdigest()==s['sha256'] and len(collected[n])==s['bytes'],'Source/data hash mismatch: '+n)
        counts=r['counts'];ck(counts['files_received']==data['reconciliation']['files_received'],'Receipt file count mismatch')
        ck(counts['source_records']==len(data['sources']) and counts['requests']==len(data['scope_request_ids']),'Receipt source/request count mismatch')
        ck(counts['completed_requests']==sum(c['status']=='complete_against_declared_search' for c in data['coverage']),'Receipt completed count mismatch')
        ck(counts['drug_ids']==sorted({i for s in data['sources'] for i in s['drug_ids']}),'Receipt drug coverage mismatch')
        ck(counts['condition_ids']==sorted({i for s in data['sources'] for i in s['condition_ids']}),'Receipt condition coverage mismatch')
        ck(counts['demand_ids']==sorted({i for s in data['sources'] for i in s['demand_ids']}),'Receipt question coverage mismatch')
        promptkey=prefix+'CHATGPT-INGEST-PROMPT.txt'
        if promptkey in collected:
            prompt=collected[promptkey].decode('utf-8')
            for token in [PROJECT,PLAN,r['plan_sha256'],expected_receipt,prefix+'acquisition-return.json','not verified by the sender','NOT new authority','idempotently','overviews','findings tables','questions','citations','before extraction/import']:
                ck(token in prompt,'Reverse prompt missing required value/boundary: '+token)
            for part in parts: ck(part['filename'] in prompt and part['manifest_path'] in prompt,'Reverse prompt omits returned part/manifest')
            ck(not re.search(r'\[(ACTUAL|INSERT|TODO|FILL|PROJECT|PATH)[^\]]*\]|\{\{[^}]+\}\}',prompt,re.I),'Reverse prompt retains unfilled placeholders')
            ck(hashlib.sha256(collected[promptkey]).hexdigest()==r['ingest_prompt_sha256'],'Reverse prompt hash mismatch')
    except (KeyError,TypeError,ValueError,OSError,zipfile.BadZipFile,UnicodeDecodeError) as e:
        failures.append(type(e).__name__+': '+str(e))
    return {'status':'PASS' if not failures else 'FAIL','failures':failures,'scope':'Actual local receipt bytes/locations/return contract only; no acquisition-quality acceptance, extraction, import, human approval or release','imported':False}
