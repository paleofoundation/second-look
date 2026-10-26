"""Apply only the inspected FILL2 candidates; refuse changes to already applied rows."""
from pathlib import Path
import json,hashlib,copy,importlib.util
ROOT=Path(__file__).resolve().parents[4];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads((ROOT/p).read_text())
def save(p,x):
 path=ROOT/p;out=json.dumps(x,indent=2,ensure_ascii=False)+'\n'
 if not path.exists() or path.read_text()!=out:path.write_text(out)
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def append_exact(arr,item,key):
 old=next((x for x in arr if x[key]==item[key]),None)
 if old is None:arr.append(item)
 else:assert old==item,'Changed previously projected input: '+item[key]
def unique(v):return list(dict.fromkeys(v))
cs=json.loads((BASE/'candidates.json').read_text());raw=read('data/content.json');pub=read('data/public-content.json');reader=read('data/reader-evidence.json');view=read('data/public-reader-evidence.json');registry=read('data/outcome-registry.json');parents=read('editorial/parent-guide-scopes.json');assessed=read('editorial/evidence-assessments.json');authored=read('editorial/outcome-summary/authored.json');trials=read('editorial/outcome-summary/trial-identities.json');discovery=read('data/discovery-pages.json')
# Retain the existing goal identity/route/content, now a canonical synthesis parent.
aging=next((g for g in discovery if g.get('entityId')=='GOAL-AGING'),None)
if aging:
 for store in [raw,pub]:append_exact(store['guides'],copy.deepcopy(aging),'id')
 discovery=[g for g in discovery if g['id']!=aging['id']]
# Carry the explicit retraction attached to the exact existing original, not a new source lookup.
correction=dict(status='Quarantined',preview='This preclinical ivermectin–sorafenib report is retracted and excluded from efficacy conclusions.',correction='The locally delivered full-text XML links “RETRACTION: Ivermectin Synergizes Sorafenib in Hepatocellular Carcinoma via Targeting Multiple Oncogenic Pathways” (2026; DOI 10.1002/prp2.70222; PMID 41689298). The original is excluded from efficacy assessment.',decisiveLimit='Retracted original report; no efficacy inference or benefit grade.')
sourceCorrections=read('editorial/reader-source-corrections.json');sourceCorrections['P-D08-HCC-2022']=correction
for store in [raw,pub]:
 next(s for s in store['sources'] if s['id']=='P-D08-HCC-2022').update(correction)
 for g in store['guides']:
  if g.get('entityId')=='D02':
   for sec in g['sections']:
    if sec['id']=='dosing':
     text='ACTIV-6 studied 50 mg twice daily on day 1, followed by 100 mg twice daily for 12 additional days; that experimental course did not improve sustained recovery.'
     sec['paragraph']=text;sec['sentences']=[dict(text=text,sources=sec['sources'])]
  if g.get('entityId')!='D08':continue
  for sec in g['sections']:
   if sec['id']=='benefits':
    text='Six days of higher-dose ivermectin did not improve sustained recovery from acute COVID-19. Ovarian, brain, breast and colorectal cancer experiments reported effects in cells or animals, without a patient benefit estimate from those experiments. The liver-cancer combination report is retracted and excluded from efficacy conclusions.'
    sec['paragraph']=text;sec['sentences']=[dict(text=text,sources=sec['sources'])]
    for q in sec.get('questions',[]):
     if q.get('id')=='hcc-benefit':q['answer']='This preclinical ivermectin–sorafenib report is retracted and cannot support a liver-cancer benefit conclusion.';q['sentences']=[dict(text=q['answer'],sources=q['sources'])]
  for q in g['faqs']:
   if 'P-D08-HCC-2022' in q.get('sources',[]) and ('liver' in q.get('question','').lower() or 'sorafenib' in q.get('answer','').lower()):q['answer']='The preclinical ivermectin–sorafenib report is retracted and excluded from efficacy conclusions; it does not establish a patient benefit.';q['sentences']=[dict(text=q['answer'],sources=q['sources'])]
for c in cs:
 for b in c['sourceBindings']:assert hashlib.sha256(Path(b['path']).read_bytes()).hexdigest()==b['expectedSha256'],b['path']
 r=c['row'];p=c['publicRow'];ss=r['sourceIds'];append_exact(reader['synthesisRows'],r,'id');append_exact(view['synthesisRows'],p,'id')
 for store in [raw,pub]:
  for entity in [r['drugId'],r['conditionId']]:
   g=next(g for g in store['guides'] if g.get('entityId')==entity);g['synthesisIds']=unique(g.get('synthesisIds',[])+[r['id']]);g['sourceIds']=unique(g['sourceIds']+ss)
 oid='OUT-'+r['id'].removeprefix('SYN-');registry['rowOutcomeMap'][r['id']]=oid
 def field(v):return dict(value=v,status='reported' if v else 'not_extracted',reason=None if v else 'Not separately established in this bounded selected-source appraisal.',sources=ss if v else [])
 outcome=dict(id=oid,label=r['endpoint'],aliases=[r['endpoint']],definition=dict(text=r['endpoint']+' in '+r['population']+'.',sources=ss),registryState='source_defined',instrument=field(r['endpoint']),endpointHierarchy=field('secondary' if c['row']['id'].endswith('AGING-LEAN') else 'primary' if c['trial'] else None),clinicalOrSurrogateRole=field('Nonclinical experimental outcome' if c['assessment']['integrity']=='preclinical_only' else 'Body-composition measure; not a lifespan endpoint' if r['conditionId']=='GOAL-AGING' else 'Clinical symptom-recovery or acute-event endpoint'),measuredDirection=field(c['finding']),favorableScaleDirection=field(None),meaningfulChange=field(None),clinicalInterpretation=field(None));append_exact(registry['outcomes'],outcome,'id')
 a=copy.deepcopy(c['assessment']);a['inputSha256']=sha(dict(row=r,publicRow=p,sources=[next(s for s in raw['sources'] if s['id']==sid) for sid in ss],publicSources=[next(s for s in pub['sources'] if s['id']==sid) for sid in ss]));append_exact(assessed['records'],a,'rowId')
 item=copy.deepcopy(c['summary']);item['assessedInputSha256']=sha(dict(rows=[r],publicRows=[p],priorAssessments=[a],sources=[next(s for s in pub['sources'] if s['id']==sid) for sid in ss]));append_exact(authored,item,'id')
 t=c['trial']
 if t:
  found=next((x for x in trials['trials'] if x['id']==t['id']),None)
  if t.get('comparisonId'):
   assert found is not None
   comp=dict(drugId=c['drugId'],participants=t['participants'],participantBasis=t['participantBasis'],sourceIds=ss,synthesisIds=[r['id']]);prev=found.setdefault('comparisons',{}).get(t['comparisonId']);assert prev is None or prev==comp;found['comparisons'][t['comparisonId']]=comp
  elif found is None:
   found=dict(id=t['id'],sourceIds=ss,participants=t['participants'],participantBasis=t['participantBasis'],synthesisIds=[],sourceBasis=c['assessment']['basis'][0]['locator'],identityRationale='Exact report-specific randomized comparison; not another agent/dose comparison in the same platform. Actual local source inspection on 2026-10-26.');trials['trials'].append(found)
  found['synthesisIds']=unique(found['synthesisIds']+[r['id']])
for entry in parents['parents']:
 g=next((g for g in raw['guides'] if g['id']==entry['guideId']),None)
 if g:entry['guide']=copy.deepcopy(g)
if not any(p['entityId']=='GOAL-AGING' for p in parents['parents']):
 g=next(g for g in raw['guides'] if g.get('entityId')=='GOAL-AGING');parents['parents'].append(dict(guideId=g['id'],entityId=g['entityId'],route=g['slug'],scopeType='condition',guide=copy.deepcopy(g)))
spec=importlib.util.spec_from_file_location('identity',ROOT/'scripts/apply-reader-outcomes.py');identity=importlib.util.module_from_spec(spec);spec.loader.exec_module(identity)
imap=read('editorial/synthesis-identity-map.json')
for c in cs:identity.remember_identity(imap,c['row'],registry,{})
for file,value in [('data/content.json',raw),('data/public-content.json',pub),('data/reader-evidence.json',reader),('data/public-reader-evidence.json',view),('data/outcome-registry.json',registry),('data/discovery-pages.json',discovery),('editorial/parent-guide-scopes.json',parents),('editorial/evidence-assessments.json',assessed),('editorial/outcome-summary/authored.json',authored),('editorial/outcome-summary/trial-identities.json',trials),('editorial/synthesis-identity-map.json',imap),('editorial/reader-source-corrections.json',sourceCorrections)]:save(file,value)
save('research/batches/FILL-REMAPRX-1-STEP2/appraisal/assessments.json',dict(method=assessed['method'],records=[a for a in assessed['records'] if a['rowId'] in [c['row']['id'] for c in cs]],independentReview='pending',humanApproval='pending',release='not authorized'))
print(json.dumps(dict(newRows=len(cs),domainJudgments=sum(len(c['assessment']['domains']) for c in cs),sourceQuarantines=['P-D08-HCC-2022'],humanApprovals=0)))
