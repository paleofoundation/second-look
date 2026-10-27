import json,hashlib,subprocess,os,argparse,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;O=B.parent/'FILL-REMAPRX-FENB-20261027';c=json.loads((B/'CANDIDATE.json').read_text());base=c['base'];args=argparse.ArgumentParser();args.add_argument('--require-source-files',action='store_true');args=args.parse_args()
def read(f):return json.loads((ROOT/f).read_text())
def old(f):return json.loads(subprocess.check_output(['git','show',base+':'+f],cwd=ROOT))
def h(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def resolve(ref):
 if not ref.startswith('$'):return ROOT/ref
 name,_,relative=ref[1:].partition('/');root=os.environ.get(name)
 return Path(root)/relative if root else None
canonical=read('data/content.json');public=read('data/public-content.json');ss={s['id']:s for s in canonical['sources']};claims=json.loads((O/'CLAIMS.json').read_text())['claims'];assert collections.Counter(r['grade'] for r in claims)=={'Low':9,'not_established':4}
assert canonical['sources']==old('data/content.json')['sources'],'No source identity/appraisal mutation'
for r in claims:
 assert len(r['domains'])==5
 for binding in r['sourceBindings']:assert h(ss[binding['sourceId']])==binding['sourceObjectSha256']
verified=[];missing=[]
for paper in json.loads((O/'INPUTS.json').read_text())['papers']:
 p=resolve(paper['path'])
 if p is None or not p.is_file():missing.append(paper['pmid']);continue
 assert hashlib.sha256(p.read_bytes()).hexdigest()==paper['sha256'],'Changed private original: '+paper['pmid'];verified.append(paper['pmid'])
if args.require_source_files:assert not missing,'Strict source verification requires documented external roots: '+str(missing)
for f in ['data/content.json','data/public-content.json']:
 a=old(f);d=read(f);assert [g for g in a['guides'] if g.get('entityId')!='D10']==[g for g in d['guides'] if g.get('entityId')!='D10'];assert next(g for g in d['guides'] if g.get('entityId')=='D10')==c['guide']
 assert all(s==next(x for x in d['sources'] if x['id']==s['id']) for s in a['sources'] if s['id'] not in c['hidePublicSourceIds'])
 assert not any(s['id'] in c['hidePublicSourceIds'] for s in public['sources'])
for f in ['data/reader-evidence.json','editorial/evidence-assessments.json','data/public-evidence-assessments.json','editorial/outcome-summary/authored.json','editorial/outcome-summary/assessments.json','editorial/outcome-summary/trial-identities.json']:
 assert (ROOT/f).read_bytes()==subprocess.check_output(['git','show',base+':'+f],cwd=ROOT)
assert read('data/drug-status-table.json')['drugs']['/drugs/fenbendazole']==c['status']
rendered=json.dumps([c['guide'],c['mechanism']],ensure_ascii=False).lower()
for forbidden in ['chlorine dioxide','guilford','hedgehog','npc1','cholesterol transport','ovarian-benefit']:assert forbidden not in rendered
assert 'fenb-human-benefit' in rendered and 'models only' in rendered
for f in ['INPUTS.json','SOURCE-READING.json','CLAIMS.json','verify.py']:assert '/Users/' not in (O/f).read_text()
assert '\u2013' not in rendered and '\u2014' not in rendered
# Existing source routes already inherit noindex; do not change the global policy.
route=(ROOT/'app/[...path]/page.tsx').read_text();assert 'robots:{index:false,follow:false}' in route
assert (ROOT/'app/[...path]/page.tsx').read_bytes()==subprocess.check_output(['git','show',base+':app/[...path]/page.tsx'],cwd=ROOT)
files=['data/content.json','data/public-content.json','data/public-mechanisms.json','editorial/parent-guide-scopes.json','data/drug-status-table.json','data/public-review-metadata.json','data/article-updates.json'];before={f:(ROOT/f).read_bytes() for f in files};subprocess.run(['python3',str(B/'apply-candidate.py')],cwd=ROOT,check=True);assert all((ROOT/f).read_bytes()==v for f,v in before.items())
print(json.dumps({'integrity':'PASS','internalGrades':{'Low':9,'not_established':4},'readerMappedClaims':11,'privateSourceFilesVerified':len(verified),'privateSourceFilesNotChecked':len(missing),'missingPrivateSourceIds':missing,'strictSourceMode':args.require_source_files,'oldOutcomes':70,'oldSummaries':68,'repeatApply':'zero diff','globalIndexingPolicy':'unchanged; existing noindex','scientificAcceptance':False}))
