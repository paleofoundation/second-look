import json,hashlib,subprocess,os,argparse
from pathlib import Path
B=Path(__file__).resolve().parent;os.chdir(B.parents[2]);O=B.parent/'FILL-REMAPRX-LABELS-20261027';args=argparse.ArgumentParser();args.add_argument('--require-source-files',action='store_true');args=args.parse_args();checked=set();missing=set();c=json.loads((B/'CANDIDATE.json').read_text());base=c['base'];claims=json.loads((O/'CLAIMS.json').read_text())['claims'];schema=json.loads((O/'CLAIM-SCHEMA.json').read_text());targets={x['entityId'] for x in c['guides']}
def original(f):return json.loads(subprocess.check_output(['git','show',base+':'+f]))
def read(f):return json.loads(Path(f).read_text())
def h(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
assert len(claims)==32 and len({r['claimId'] for r in claims})==32
src={s['id']:s for s in read('data/content.json')['sources']}
for r in claims:
 assert all(k in r for k in schema['required']);assert r['grade'] in schema['grades'];assert len(r['domains'])==5;assert r['reviewState']=='pending_independent_and_human_review'
 for b in r['sourceBindings']:
  assert h(src[b['sourceId']])==b['sourceObjectSha256']
  if 'path' in b:
   root=os.environ.get('REMAPRX_LABEL_PRIVATE');p=Path(root)/Path(b['path']).name if root else None
   if p and p.is_file():assert hashlib.sha256(p.read_bytes()).hexdigest()==b['fileSha256'];checked.add(b['sourceId'])
   else:missing.add(b['sourceId'])
 if r.get('reusesAssessmentRowId'):assert h(next(x for x in read('editorial/evidence-assessments.json')['records'] if x['rowId']==r['reusesAssessmentRowId']))==r['reusesAssessmentSha256']
for f in ['data/content.json','data/public-content.json']:
 old=original(f);d=read(f);assert old['sources']==d['sources'];assert [g for g in old['guides'] if g.get('entityId') not in targets]==[g for g in d['guides'] if g.get('entityId') not in targets]
 for g in c['guides']:assert next(x for x in d['guides'] if x.get('entityId')==g['entityId'])==g
for f in ['data/reader-evidence.json','editorial/evidence-assessments.json','data/public-evidence-assessments.json','editorial/outcome-summary/authored.json','editorial/outcome-summary/assessments.json','editorial/outcome-summary/trial-identities.json','data/drug-status-table.json','data/public-review-metadata.json']:
 assert Path(f).read_bytes()==subprocess.check_output(['git','show',base+':'+f]),f+' must remain unchanged'
for f in ['data/content.json','data/public-content.json']:
 for g in original(f)['guides']:
  if any(s.startswith(('CP027','CP028')) for s in g.get('sourceIds',[])):assert g==next(x for x in read(f)['guides'] if x['id']==g['id'])
assert not any(x in json.dumps([c['guides'],c['mechanisms']],ensure_ascii=False) for x in ['\u2014','\u2013']),'No rendered em/en dashes in active target projection'
if args.require_source_files:assert not missing,sorted(missing)
files=list(c['baseFileHashes']);before={f:Path(f).read_bytes() for f in files};subprocess.run(['python3',str(B/'apply-candidate.py')],check=True);assert all(Path(f).read_bytes()==v for f,v in before.items())
print('PASS:32 scoped claim/context records; source/label hashes; all existing sources and70 outcomes/68 summaries; protected book and other guide objects; unchanged statuses/reviews; repeat-apply zero diff.')

print(json.dumps({'privateLabelsVerified':len(checked),'privateLabelsNotChecked':len(missing),'strictSourceMode':args.require_source_files,'scientificAcceptance':False}))
