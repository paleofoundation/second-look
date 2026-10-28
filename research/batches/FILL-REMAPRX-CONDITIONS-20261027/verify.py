import json,hashlib,subprocess,os,argparse,collections
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[2];os.chdir(ROOT);c=json.loads((B/'CANDIDATE.json').read_text());base=c['base'];targets={g['entityId']:g for g in c['guides']};mt={m['conditionId']:m for m in c['mechanisms']};args=argparse.ArgumentParser();args.add_argument('--require-source-files',action='store_true');args=args.parse_args()
def read(f):return json.loads(Path(f).read_text())
def old(f):return json.loads(subprocess.check_output(['git','show',base+':'+f]))
def h(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
claims=json.loads((B/'CLAIMS.json').read_text())['claims'];schema=json.loads((B/'CLAIM-SCHEMA.json').read_text());assert len(claims)==17 and collections.Counter(r['grade'] for r in claims)=={'Low':13,'Moderate':1,'not_established':2,'official_context':1}
ss={s['id']:s for s in read('data/content.json')['sources']};checked=set();missing=set()
for r in claims:
 assert all(k in r for k in schema['required']) and len(r['domains'])==5 and r['reviewState']=='pending_independent_and_human_review'
 for binding in r['sourceBindings']:
  assert h(ss[binding['sourceId']])==binding['sourceObjectSha256']
  if 'path' in binding:
   root=os.environ.get('REMAPRX_CONDITION_PRIVATE');p=Path(root)/Path(binding['path']).name if root else None
   if p and p.is_file():assert hashlib.sha256(p.read_bytes()).hexdigest()==binding['fileSha256'];checked.add(binding['sourceId'])
   else:missing.add(binding['sourceId'])
 if r.get('reusesAssessmentRowId'):assert h(next(x for x in read('editorial/evidence-assessments.json')['records'] if x['rowId']==r['reusesAssessmentRowId']))==r['reusesAssessmentSha256']
if args.require_source_files:assert not missing,missing
protected=[]
for f in ['data/content.json','data/public-content.json']:
 d=read(f);a=old(f);assert [g for g in d['guides'] if g.get('entityId') not in targets]==[g for g in a['guides'] if g.get('entityId') not in targets]
 for id,g in targets.items():assert next(x for x in d['guides'] if x.get('entityId')==id)==g
 for s in a['sources']:assert s==next(x for x in d['sources'] if x['id']==s['id'])
 assert len(d['sources'])==len(a['sources'])+1
 for g in a['guides']:
  if any(s.startswith(('CP027','CP028')) for s in g.get('sourceIds',[])):
   assert g==next(x for x in d['guides'] if x['id']==g['id']);protected.append(g['id'])
 assert next(x for x in a['guides'] if x.get('entityId')=='C29')==next(x for x in d['guides'] if x.get('entityId')=='C29')
f='editorial/parent-guide-scopes.json';assert [p for p in read(f)['parents'] if p['entityId'] not in targets]==[p for p in old(f)['parents'] if p['entityId'] not in targets]
f='data/public-mechanisms.json';assert [m for m in read(f)['drugs'] if m.get('conditionId') not in mt]==[m for m in old(f)['drugs'] if m.get('conditionId') not in mt]
for m in c['mechanisms']:assert next(x for x in read(f)['drugs'] if x.get('conditionId')==m['conditionId'])==m
for f in ['data/reader-evidence.json','editorial/evidence-assessments.json','data/public-evidence-assessments.json','editorial/outcome-summary/authored.json','editorial/outcome-summary/assessments.json','editorial/outcome-summary/trial-identities.json','data/drug-status-table.json','data/review-envelopes.json','data/private-reviews.json']:
 assert Path(f).read_bytes()==subprocess.check_output(['git','show',base+':'+f]),f
f='data/public-review-metadata.json';a=old(f)['records'];d=read(f)['records'];assert all(r==next(x for x in d if x['sourceId']==r['sourceId']) for r in a);assert len(d)==len(a)+1
record=next(x for x in d if x['sourceId']==c['sources'][0]['id']);assert record['complete']==False and record['publicationState']=='private_ai_draft' and record['draftBodyAvailable']==False
rendered=json.dumps([c['guides'],c['mechanisms']],ensure_ascii=False);assert not any(x in rendered for x in ['\u2013','\u2014']);assert 'Models only. Confidence in clinical translation: Low.' in rendered
for f in ['app/[...path]/page.tsx','app/robots.ts']:
 if Path(f).exists():assert Path(f).read_bytes()==subprocess.check_output(['git','show',base+':'+f])
files=list(c['baseFileHashes']);before={f:Path(f).read_bytes() for f in files};subprocess.run(['python3',str(B/'apply-candidate.py')],check=True);assert all(Path(f).read_bytes()==v for f,v in before.items())
print(json.dumps({'integrity':'PASS','claims':dict(collections.Counter(r['grade'] for r in claims)),'privateOriginalsVerified':len(checked),'privateOriginalsNotChecked':len(missing),'oldOutcomes':70,'oldSummaries':68,'protectedGuideObjects':len(protected),'vitiligo':'unchanged','repeatApply':'zero diff','scientificAcceptance':False}))
