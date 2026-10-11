"""Apply source-checked editorial corrections without projecting protected review bodies."""
from pathlib import Path
from copy import deepcopy
import argparse,json
ROOT=Path(__file__).resolve().parents[1]
def read(name):return json.loads((ROOT/name).read_text())
def save(name,value):(ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
PUBLIC_SOURCE_KEYS=set('id title url doi year authors design population n randomizedN sampleDescription intervention comparator sourceType familyId pmid preview decisiveLimit locators correction status'.split())
def unique(v):return list(dict.fromkeys(v))
def ids_in(v):
 if isinstance(v,list):return [x for e in v for x in ids_in(e)]
 if isinstance(v,dict):return [x for k,e in v.items() for x in (e if k in ['sources','sourceIds'] and isinstance(e,list) else ids_in(e))]
 return []
def apply(files):
 raw=read('data/content.json'); public=read('data/public-content.json');discovery=read('data/discovery-pages.json');mechanisms=read('data/public-mechanisms.json');scope=read('editorial/parent-guide-scopes.json')
 source_ids={s['id'] for s in raw['sources']}; corrected=[]
 batches=[json.loads(Path(f).read_text()) for f in files]
 for batch in batches:
  for source in batch.get('sources',[]):
   source=deepcopy(source)
   old=next((s for s in raw['sources'] if s['id']==source['id']),None)
   if old:old.update(source)
   else:raw['sources'].append(source)
   projection={k:v for k,v in source.items() if k in PUBLIC_SOURCE_KEYS}
   # Retraction notices are scientific source properties; production states are private.
   if projection.get('status')!='Quarantined':projection.pop('status',None)
   old=next((s for s in public['sources'] if s['id']==source['id']),None)
   if old:old.update(projection)
   else:public['sources'].append(projection)
   source_ids.add(source['id'])
 for batch in batches:
  for record in batch.get('mechanisms',[]):
   target=record.get('drugId') or record.get('conditionId') or record['guideIds'][0]
   records=mechanisms.setdefault('drugs',[])
   records[:]=[r for r in records if (r.get('drugId') or r.get('conditionId') or r.get('guideIds',[None])[0])!=target]
   records.append(deepcopy(record))
  for update in batch.get('guides',[]):
   gid=update['guideId'];g=next((g for g in raw['guides']+discovery if g['id']==gid),None)
   if g is None:raise ValueError('Unknown guide '+gid)
   preserved=set(g.get('sourceIds',[]))
   # Preserve sources supporting existing results, not obsolete authored sentences.
   rows=read('data/reader-evidence.json')['synthesisRows']
   row_ids=[i for r in rows if r['id'] in g.get('synthesisIds',[]) for i in r['sourceIds']]
   g.update({k:deepcopy(v) for k,v in update.items() if k!='guideId'})
   for section in g['sections']:
    if section['id'] in ['research','mechanisms','faqs','references','studies','edition'] or section['id'].startswith('section-'):
     section['id']='authored-'+section['id']
   g.update(coverageLabel='',scope=update.get('scope',update['description']),scopedSections=[])
   g.pop('originalUse',None)
   for link in g.get('candidateLinks',[]):link['state']=''
   mechanism=next((m for m in mechanisms.get('drugs',[]) if m.get('drugId')==g.get('entityId') or m.get('conditionId')==g.get('entityId') or gid in m.get('guideIds',[])),None)
   g['sourceIds']=unique(ids_in(g['sections'])+ids_in(g['faqs'])+ids_in(mechanism)+row_ids)
   missing=set(g['sourceIds'])-source_ids
   if missing:raise ValueError(gid+': unresolved sources '+str(missing))
   pub=next((p for p in public['guides'] if p['id']==gid),None)
   if pub:pub.update(deepcopy(g));pub.pop('status',None);pub.pop('route',None)
   if g in raw['guides']:
    p=next((p for p in scope['parents'] if p['guideId']==gid),None)
    if p:p['guide']=deepcopy(g)
    else:scope['parents'].append(dict(guideId=gid,entityId=g['entityId'],route=g['slug'],scopeType=g['type'].lower(),guide=deepcopy(g),conditionCoverage=[]))
   corrected.append(gid)
 scope['version']='2026-10-11-reader-correction-2'
 save('data/content.json',raw);save('data/public-content.json',public);save('data/discovery-pages.json',discovery);save('data/public-mechanisms.json',mechanisms);save('editorial/parent-guide-scopes.json',scope)
 print(json.dumps(dict(updated=len(corrected),sources=len(raw['sources']),mechanisms=len(mechanisms['drugs']))))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('files',nargs='+');apply(p.parse_args().files)
