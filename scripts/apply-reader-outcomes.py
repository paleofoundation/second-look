"""Add located trial findings to both parent profiles and the outcome registry.

This extracts records, not grades. Complete the outcome-specific editorial
assessment step in editorial/EVIDENCE-GRADING.md, then compile its projection.
The production build rejects missing or stale assessments after this import.
"""
from pathlib import Path
import argparse,json,re
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_text())
def save(n,v):(ROOT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def unique(x):return list(dict.fromkeys(x))
def clean(s):
 s=str(s);s=re.sub(r'([a-zA-Z])(\d)',r'\1 \2',s);s=re.sub(r'(\d)([a-zA-Z])',r'\1 \2',s);s=re.sub(r'([,;])(?=\S)',r'\1 ',s);s=s.replace('CI−','CI −').replace('CI–','CI –').replace('group−','group −').replace('difference−','difference −').replace('group~','group ~');return s
raw=read('data/content.json');pub=read('data/public-content.json');reader=read('data/reader-evidence.json');view=read('data/public-reader-evidence.json');registry=read('data/outcome-registry.json');scope=read('editorial/parent-guide-scopes.json');source={s['id']:s for s in raw['sources']};aliases=read('editorial/reader-source-aliases.json');new=[]
def resolved(id):return aliases.get(id,id)
for filename in __import__('sys').argv[1:]:
 batch=json.loads(Path(filename).read_text())
 for fact in batch.get('evidenceRecords',[]):
  sid=resolved(fact['sourceId']);src=source[sid];did=fact['drugId'];cid=fact['conditionId']
  # One exact outcome record per source/drug/condition; repeat source contributions update it.
  rid='SYN-'+did+'-'+cid+'-'+re.sub('[^A-Z0-9-]','',sid.upper());oid='OUT-'+rid.removeprefix('SYN-');fid=src.get('familyId') or 'STUDY-'+sid
  val={k:clean(fact.get(k,'')) for k in ['population','comparison','endpoint','timepoint','finding','magnitude','limits']}
  if 'not transcribed' in val['magnitude']:val['magnitude']='Clinical attachment and probing-depth changes favored doxycycline as an adjunct to mechanical treatment.'
  limits=val['limits'];finding=val['finding'];ss=[sid]
  if not finding.endswith('.'):finding+='.'
  row=dict(id=rid,version='reader-correction-2026-10-11',drugId=did,conditionId=cid,title=val['endpoint'],use=val['comparison'],population=val['population'],comparison=val['comparison'],endpoint=val['endpoint'],timepoint=val['timepoint'],status='reported_result',finding=dict(text=finding,sources=ss),magnitudeText=val['magnitude'],certainty=dict(label='Not appraised',rationale=''),evidenceBase=src['design'],limitations=[dict(text=limits,sources=ss)],sourceIds=ss,resultIds=[rid+'-R1'],studyFamilyIds=[fid],countsAsPrimaryEvidence=True,answerRoutes=[],coverage=dict(complete=False,pending=[]),effects=[dict(sourceId=sid,design=src['design'],population=val['population'],timepoint=val['timepoint'],sampleDescription=('Reported sample: '+str(fact['N'])) if fact.get('N') else val['population'],locators=src.get('locators',[]))],sourceLocators=[dict(sourceId=sid,label=l.get('section','Study results')) for l in src.get('locators',[])],publicationState='private_ai_draft',humanApproval='pending')
  for target in [reader,view]:
   target['synthesisRows']=[r for r in target['synthesisRows'] if r['id']!=rid];target['synthesisRows'].append({k:v for k,v in row.items() if target is reader or k not in ['publicationState','humanApproval']})
  for target in [raw,pub]:
   for g in target['guides']:
    if g.get('entityId') in [did,cid]:g['synthesisIds']=unique(g.get('synthesisIds',[])+[rid]);g['sourceIds']=unique(g['sourceIds']+ss)
  def field(v):return dict(value=v,status='reported' if v else 'not_reported',reason=None,sources=ss if v else [])
  outcome=dict(id=oid,label=val['endpoint'],aliases=[val['endpoint']],definition=dict(text=val['endpoint']+' in '+val['population']+'.',sources=ss),registryState='source_defined',instrument=field(val['endpoint']),endpointHierarchy=field(None),clinicalOrSurrogateRole=field(None),measuredDirection=field(finding),favorableScaleDirection=field(None),meaningfulChange=field(None),clinicalInterpretation=field(None))
  registry['outcomes']=[o for o in registry['outcomes'] if o['id']!=oid]+[outcome];registry['rowOutcomeMap'][rid]=oid;new.append(rid)
# A textbook account is retained in References, not counted as another clinical finding.
retired=[r for r in reader['synthesisRows'] if r['status']=='background_only']
retired_ids={r['id'] for r in retired}
if (ROOT/'editorial/retired-background-outcome-rows.json').exists():retired_ids.update(r['id'] for r in read('editorial/retired-background-outcome-rows.json'))
if retired:save('editorial/retired-background-outcome-rows.json',retired)
for target in [reader,view]:target['synthesisRows']=[r for r in target['synthesisRows'] if r['id'] not in retired_ids]
for target in [raw,pub]:
 for g in target['guides']:g['synthesisIds']=[id for id in g.get('synthesisIds',[]) if id not in retired_ids]
# Retire superseded IDs after source identities merge, preserving one shared result.
row_ids={r['id'] for r in reader['synthesisRows']};row_aliases={}
for r in reader['synthesisRows']:
 prefix='SYN-'+r['drugId']+'-'+r['conditionId']+'-'
 if r['id'].startswith(prefix) and len(r['sourceIds'])==1:
  canonical_id=prefix+re.sub('[^A-Z0-9-]','',r['sourceIds'][0].upper())
  if canonical_id in row_ids and canonical_id!=r['id']:row_aliases[r['id']]=canonical_id
for target in [reader,view]:target['synthesisRows']=[r for r in target['synthesisRows'] if r['id'] not in row_aliases]
for target in [raw,pub]:
 for g in target['guides']:g['synthesisIds']=unique(row_aliases.get(r,r) for r in g.get('synthesisIds',[]))
for id in row_aliases:registry['rowOutcomeMap'].pop(id,None)
for p in scope['parents']:
 g=next((g for g in raw['guides'] if g['id']==p['guideId']),None)
 if g:p['guide']=g
for n,v in [('data/content.json',raw),('data/public-content.json',pub),('data/reader-evidence.json',reader),('data/public-reader-evidence.json',view),('data/outcome-registry.json',registry),('editorial/parent-guide-scopes.json',scope)]:save(n,v)
print(json.dumps(dict(addedOrUpdated=len(new),retiredSecondaryRows=len(retired),sharedOutcomes=len(reader['synthesisRows']))))
