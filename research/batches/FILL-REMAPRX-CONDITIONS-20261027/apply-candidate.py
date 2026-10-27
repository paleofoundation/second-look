import json,copy,subprocess,os
from pathlib import Path
B=Path(__file__).resolve().parent;os.chdir(B.parents[2]);c=json.loads((B/'CANDIDATE.json').read_text());base=c.get('projectionBase',c['base']);targets={g['entityId']:g for g in c['guides']};mt={m['conditionId']:m for m in c['mechanisms']}
def read(f):return json.loads(Path(f).read_text())
def original(f):return json.loads(subprocess.check_output(['git','show',base+':'+f]))
def write(f,d):Path(f).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def guard(old,new,before):assert old==new or old==before,'Concurrent target edit; reconcile before application.'
for f in ['data/content.json','data/public-content.json']:
 d=read(f)
 for source in c['sources']:
  value={k:v for k,v in source.items() if k not in ['access','reviewState','hasReviewDraft']} if f=='data/public-content.json' else source
  existing=next((s for s in d['sources'] if s['id']==source['id']),None)
  if existing is None:d['sources'].append(value)
  else:assert existing==value, 'Concurrent new source edit'
 old={g.get('entityId'):g for g in original(f)['guides']}
 for i,g in enumerate(d['guides']):
  if g.get('entityId') in targets:guard(g,targets[g['entityId']],old[g['entityId']]);d['guides'][i]=copy.deepcopy(targets[g['entityId']])
 write(f,d)
f='data/public-mechanisms.json';d=read(f);old={m.get('conditionId'):m for m in original(f)['drugs']}
for i,m in enumerate(d['drugs']):
 if m.get('conditionId') in mt:guard(m,mt[m['conditionId']],old[m['conditionId']]);d['drugs'][i]=copy.deepcopy(mt[m['conditionId']])
write(f,d)
f='editorial/parent-guide-scopes.json';d=read(f);old={p['entityId']:p for p in original(f)['parents']}
for p in d['parents']:
 if p['entityId'] in targets:
  target=copy.deepcopy(targets[p['entityId']])
  for key,val in old[p['entityId']]['guide'].items():
   if key not in target:target[key]=val
  guard(p['guide'],target,old[p['entityId']]['guide']);p['guide']=target
write(f,d)
f='data/article-updates.json';d=read(f)
for g in reversed(c['guides']):
 id='2026-10-27-condition-evidence-'+g['entityId'].lower();entry={'id':id,'date':'2026-10-27','title':g['title']+' evidence expanded','changeType':'evidence','summary':{'C21':'Expanded metformin, itraconazole-combination and simvastatin experimental findings. Distinguished these anticancer hypotheses from aspirin clot-prevention research and established myeloma-treatment context.','C06':'Added three uncontrolled naltrexone case reports, distinguished symptom histories from patient-derived immune-cell measurements, and added the cited naltrexone opioid-related label safety context.','C28':'Clarified the harmful primary functional result, its scoped Moderate confidence, and the separate uncertainty around mortality, adverse events and the proposed laboratory rationale.','C19':'Clarified the exploratory tumor-area result, primary pathway/proliferation biomarkers, limited duration and reported heart-failure safety signal.'}[g['entityId']],'pagePaths':[g['slug']],'affectedSections':[{'id':s['id'],'label':s['label']} for s in g['sections'] if s['label'] in ['Overview','Options','Safety','Comparisons','Evidence']]}
 d['entries']=[entry]+[x for x in d['entries'] if x['id']!=id]
write(f,d)
f='data/public-review-metadata.json';d=read(f);s=c['sources'][0]
if not any(x['sourceId']==s['id'] for x in d['records']):
 record=copy.deepcopy(d['records'][0]);record.update(sourceId=s['id'],paperId=s['id'],reviewId='REVIEW-'+s['id'],route='/research/'+s['id'],reviewState='pending',draftBodyAvailable=False,humanApproval='pending',publicationState='private_ai_draft',complete=False)
 for q in record['questions']:q.update(status='not_extracted',nextAction='Complete the source review before declaring this answer complete.')
 d['records'].append(record)
write(f,d);print('Applied four bounded condition guides; one source and pending review metadata. Vitiligo preserved.')
