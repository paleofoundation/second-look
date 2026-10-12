#!/usr/bin/env python3
"""Verify a manually received Grok archive without extracting/importing sources."""
import argparse
import hashlib
import json
from pathlib import Path,PurePosixPath
import re
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.research_ingest.cli import decode,load,sha,require,check_inputs,check_readiness
from scripts.research_ingest.source_validation import schema_errors
CONTROL=['manifest.json','search-log.json','screening-log.json','gaps.json','review-inputs.jsonl','CHATGPT-INGEST-PROMPT.txt']
def member_name(name):
    require(isinstance(name,str) and name and '\\' not in name and not PurePosixPath(name).is_absolute() and all(p not in ('','.','..') for p in name.split('/')),'Unsafe archive member name')
def verify(archive,plan_path,readiness,schema_path):
    plan=load(plan_path);ph=sha(plan_path);rh=sha(readiness);check_readiness(readiness,plan,ph);pins=check_inputs(ROOT,plan)
    rel=Path(schema_path).resolve().relative_to(ROOT).as_posix();require(pins.get(rel)==sha(schema_path),'Return schema not plan-pinned')
    archive=Path(archive).resolve()
    require(archive.is_file(),'Downloadable attachment is not readable at receiving path')
    require(not archive.is_relative_to(ROOT),'Raw return archive must remain outside the application Git repository')
    with zipfile.ZipFile(archive) as z:
        infos=[i for i in z.infolist() if not i.is_dir()];names=[i.filename for i in infos]
        require(len(names)==len(set(names)),'Duplicate ZIP member names')
        for i in infos:
            member_name(i.filename)
            require((i.external_attr >> 16)&0o170000 != 0o120000,'ZIP symlinks are not accepted')
            require(i.file_size<=256*1024*1024,'Member exceeds bounded 256MiB intake; plan a separate large-asset receipt')
        require(all(n in names for n in CONTROL),'Missing required return control files')
        for n in CONTROL:require(z.getinfo(n).file_size<=16*1024*1024,'Control file too large')
        manifest=decode(z.read('manifest.json'));errors=schema_errors(load(schema_path),manifest);require(not errors,'Return schema: '+'; '.join(errors))
        require(manifest['planId']==plan['planId'] and manifest['planSha256']==ph,'Returned plan identity/hash differs')
        files=manifest['files'];paths=[f['path'] for f in files]
        require(manifest['fileCount']==len(files) and len(paths)==len(set(paths)),'Manifest count/path duplication')
        require(len({f['id'] for f in files})==len(files),'Duplicate asset IDs')
        require(len({f['sourceId'] for f in files})==len(files),'Duplicate source IDs make asset/hash mapping ambiguous')
        require(set(names)==set(CONTROL+paths),'Unlisted or missing source members')
        for f in files:
            require(f['path'].startswith('files/'),'Sources must live under files/')
            require(z.getinfo(f['path']).file_size==f['bytes'],'Source size mismatch')
            h=hashlib.sha256()
            with z.open(f['path']) as stream:
                first=stream.read(1024*1024);h.update(first)
                if f['mediaType']=='application/pdf':require(first.startswith(b'%PDF-'),'Mislabeled PDF/failed download')
                for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
            require(h.hexdigest()==f['sha256'],'Source hash mismatch')
        for n in ['search-log.json','screening-log.json','gaps.json']:
            require(isinstance(decode(z.read(n)),list),'Control log must be a JSON array: '+n)
        logs=decode(z.read('search-log.json'))
        planned={(q['location'],q['query']) for gap in plan['gaps'] for q in gap['queries']}
        executed={(q.get('location'),q.get('query')) for q in logs}
        require(planned <= executed,'Missing planned search queries or explicit execution-limit records')
        gaps=decode(z.read('gaps.json'))
        require(all(g.get('gapId') and g.get('reason') and g.get('nextAction') for g in gaps),'Gap records require identity, reason and next action')
        covered={gid for f in files for gid in f['gapIds']} | {g['gapId'] for g in gaps}
        require({g['id'] for g in plan['gaps']} <= covered,'Unaccounted requested gap')
        for log in logs:require(all(log.get(k) is not None for k in ['query','location','executedAt','resultCount','limits']),'Incomplete actual search log')
        review_rows=[decode(l) for l in z.read('review-inputs.jsonl').splitlines() if l.strip()]
        input_schema_path=Path(schema_path).parent/'review-inputs.schema.json'
        input_relative=input_schema_path.resolve().relative_to(ROOT).as_posix()
        require(pins.get(input_relative)==sha(input_schema_path),'Review-input schema not plan-pinned')
        input_schema=load(input_schema_path)
        question_map_path=Path(schema_path).parent/'review-questions-and-inputs.json'
        question_map_relative=question_map_path.resolve().relative_to(ROOT).as_posix()
        require(pins.get(question_map_relative)==sha(question_map_path),'Review question map not plan-pinned')
        question_map=load(question_map_path)
        require(len(question_map['questions'])==15 and {q['id'] for q in question_map['questions']}=={f'Q{i:02d}' for i in range(1,16)},'Question map must define exact Q01-Q15')
        required_fields={(q['id'],field) for q in question_map['questions'] for field in q['inputFields']}
        seen=set();by_paper={};source_files={f['sourceId']:f for f in files}
        for r in review_rows:
            errors=schema_errors(input_schema,r);require(not errors,'Review-input schema: '+'; '.join(errors))
            key=(r['paperId'],r['questionId'],r['field'])
            require(key not in seen,'Duplicate paper/question/field input');seen.add(key)
            by_paper.setdefault(r['paperId'],set()).add((r['questionId'],r['field']))
            require(r['sourceId'] in source_files,'Unknown review input source')
            source=source_files[r['sourceId']]
            require(r['paperId']==source['canonicalReportId'] and r['sourceHash']==source['sha256'],'Review source/report/hash mismatch')
            if r['status']=='answered':
                require(r['value_or_null'] is not None and r['nativeLocator'] is not None,'Answered input lacks value/locator')
            else:require(r['reason'] is not None,'Missing input state reason')
            if r['nativeLocator'] is not None and source['mediaType']=='application/pdf':
                require(r['nativeLocator']['kind']=='pdf','Review locator kind differs from PDF source')
        for f in files:
            if f['role'] in ['original_report','preprint','replacement','context']:
                require(by_paper.get(f['canonicalReportId'])==required_fields,'Missing exact Q01-Q15 required input fields')
        prompt=z.read('CHATGPT-INGEST-PROMPT.txt').decode('utf-8').strip()
        require(len(prompt)>100 and plan['planId'] in prompt and ph in prompt,'Filled receiving prompt must identify exact plan/hash')
        require(hashlib.sha256(z.read('manifest.json')).hexdigest() in prompt,'Receiving prompt manifest hash differs')
        require(sha(schema_path) in prompt and sha(input_schema_path) in prompt,'Receiving prompt schema hashes differ')
        require(re.search(r'^Manifest source file count:\s*'+str(len(files))+r'\s*$',prompt,re.MULTILINE),'Receiving prompt file count differs')
        require(not re.search(r'\[(?:actual|exact|hash of)\b',prompt,re.IGNORECASE),'Receiving prompt still has template tokens')
    check_inputs(ROOT,plan)
    require(sha(plan_path)==ph and sha(readiness)==rh,'Receipt plan/readiness changed during verification')
    return {'status':'PASS_RECEIPT_ONLY','archiveSha256':sha(archive),'archiveBytes':archive.stat().st_size,'sourceFiles':len(files),'planId':plan['planId'],'planSha256':ph,'receiverAccessVerified':True,'sourceExtractionPerformed':False,'canonicalImportPerformed':False,'scientificApproval':False,'nextAction':'Resolve identities and companions; create new source-pinned extraction assignments/readiness before extracting this newly acquired packet.'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['archive','plan','readiness','schema']:p.add_argument('--'+k,required=True)
    a=p.parse_args()
    try:r=verify(a.archive,a.plan,a.readiness,a.schema)
    except (ValueError,OSError,KeyError,TypeError,zipfile.BadZipFile) as e:r={'status':'HOLD','reason':str(e),'canonicalImportPerformed':False}
    print(json.dumps(r,indent=2));sys.exit(0 if r['status']=='PASS_RECEIPT_ONLY' else 1)
