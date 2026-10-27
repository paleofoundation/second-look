#!/usr/bin/env python3
from pathlib import Path
from copy import deepcopy
import json,hashlib,subprocess,re,datetime
P=Path(__file__).resolve().parent;R=P.parents[3];B='d118d305b59cac5e54ca7f9e5aa55cea682d2cee'
def git(*a):return subprocess.check_output(['git','-C',str(R),*a],text=True)
def h(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def before(n):return json.loads(git('show',B+':'+n))
selected={'G-CONDITION-C31','G-CONDITION-C23','G-CONDITION-C08','G-CONDITION-C22','G-CONDITION-C05','G-DRUG-D02','G-DRUG-D26'}
changed=set(json.loads((P/'CANDIDATE.json').read_text())['changedGuideIds']);allowed={'data/content.json','data/public-content.json','editorial/parent-guide-scopes.json','data/article-updates.json','docs/PROJECT-RULES.md','docs/RULE-CHANGELOG.md'};prefix='research/batches/FILL-REMAPRX-2-20261027/'
tracked=git('diff','--name-only',B).splitlines();untracked=git('ls-files','--others','--exclude-standard').splitlines();assert all(n in allowed or n.startswith(prefix) for n in tracked+untracked)
initial=json.loads((P.parent/'OUTPUT-HASHES.json').read_text())
for f in initial['files']:assert sha(P.parent/f['path'])==f['sha256'],'Historical initial checkpoint changed: '+f['path']
report=[]
def compare(n,key,idkey,allowids=()):
 old=before(n);new=json.loads((R/n).read_text());oldlist=old[key];newlist=new[key];om={str(x[idkey]):x for x in oldlist};nm={str(x[idkey]):x for x in newlist};assert set(om)==set(nm),n
 for i,x in om.items():
  delta=x!=nm[i];assert not delta or i in allowids,(n,key,i)
  report.append({'file':n,'collection':key,'id':i,'baseSha256':h(x),'candidateSha256':h(nm[i]),'changed':delta})
 unchangedold=deepcopy(old);unchangednew=deepcopy(new);unchangedold[key]=[];unchangednew[key]=[]
 if key=='guides' and n in ['data/content.json','data/public-content.json']:
  for k in ['sources','glossary']:
   assert old[k]==new[k],(n,k)
  assert unchangedold==unchangednew,n
for n in ['data/content.json','data/public-content.json']:
 compare(n,'guides','id',changed);compare(n,'sources','id');compare(n,'glossary','slug')
compare('editorial/parent-guide-scopes.json','parents','guideId',changed)
for n in ['data/content.json','data/public-content.json']:
 d=json.loads((R/n).read_text());assert {g['id'] for g in d['guides'] if g['id'] in selected-changed}==selected-changed
 for g in d['guides']:
  if g['id'] in changed:
   # New text is checked below against the authored claim ledger; inherited exact titles remain preserved.
   assert g['sourceIds']==next(x for x in before(n)['guides'] if x['id']==g['id'])['sourceIds']
# Compare parent wrappers, permitting only guide field changes.
o=before('editorial/parent-guide-scopes.json');n=json.loads((R/'editorial/parent-guide-scopes.json').read_text());assert set(o)==set(n)
for k in o:
 if k!='parents':assert o[k]==n[k]
for old,new in zip(o['parents'],n['parents']):
 a=deepcopy(old);b=deepcopy(new);a.pop('guide');b.pop('guide');assert a==b
updatesOld=before('data/article-updates.json');updatesNew=json.loads((R/'data/article-updates.json').read_text());added=updatesNew['entries'][:4];assert updatesNew['entries'][4:]==updatesOld['entries'];assert all(len(x['pagePaths'])==1 and x['pagePaths'][0] in {g['slug'] for g in json.loads((P/'CANDIDATE.json').read_text())['guides']} for x in added)
for n in ['docs/PROJECT-RULES.md','docs/RULE-CHANGELOG.md']:
 old=git('show',B+':'+n).rstrip();new=(R/n).read_text();assert new.startswith(old);assert new[len(old):].count('## ')==1;assert '09:43' in new[len(old):]
claims=json.loads((P/'CLAIMS.json').read_text())['records'];schema=json.loads((P/'CLAIM-SCHEMA.json').read_text());sourceIds={x['id'] for x in before('data/content.json')['sources']};ids=set()
for c in claims:
 assert set(schema['required'])<=set(c);assert c['claimId'] not in ids;ids.add(c['claimId']);assert c['page'] in changed;assert set(c['sourceIds'])<=sourceIds
 assert set(c['domains'])=={'Study methods','Directness','Precision','Consistency','Source integrity'}
 for d in c['domains'].values():assert len(d['rationale'])>=15 and set(d['sourceIds'])<=set(c['sourceIds'])
 assert c['grade'] in schema['properties']['grade']['enum'];assert not re.search('[\u2013\u2014]',c['statement']);assert c['reviewState']=='AI_assisted_draft_not_independently_or_human_approved'
 assert all(re.fullmatch('[0-9a-f]{64}',b['sha256']) for b in c['sourceBindings'])
 assert all(x['locator'] for x in c['locators'])
# Idempotence of the actual bounded projector, not a synthesized duplicate importer.
paths=sorted(allowed);snapshot={f:sha(R/f) for f in paths};subprocess.run(['python3',str(P/'apply-candidate.py')],cwd=R,check=True,capture_output=True);assert snapshot=={f:sha(R/f) for f in paths}
allforbidden=(P.parent/'FORBIDDEN-PATHS.txt').read_text().splitlines();unchangedForbidden=[]
for f in allforbidden:
 if f not in allowed:
  b=subprocess.check_output(['git','-C',str(R),'show',B+':'+f]);assert (R/f).read_bytes()==b;unchangedForbidden.append(f)
result={'status':'PASS_bounded_source_candidate_and_preservation','base':B,'changedGuideIds':sorted(changed),'heldGuideIds':sorted(selected-changed),'claims':len(claims),'grades':{g:sum(x['grade']==g for x in claims) for g in sorted({c['grade'] for c in claims})},'objectsCompared':len(report),'objectsUnchanged':sum(not r['changed'] for r in report),'unchangedForbiddenFiles':len(unchangedForbidden),'newSourceObjects':0,'newOutcomeRows':0,'initialCheckpointFilesUnchanged':len(initial['files']),'repeatApplication':'zero_diff','scientificOrHumanApproval':False}
(P/'PER-ID-DIFF.json').write_text(json.dumps({'serialization':'SHA256 of UTF-8 canonical JSON with sorted keys and compact separators; all source values and their pretty-printed source arrays are unchanged.','records':report},indent=2)+'\n');(P/'PRESERVATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
