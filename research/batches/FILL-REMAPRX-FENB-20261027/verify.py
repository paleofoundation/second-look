import json,hashlib,subprocess
from pathlib import Path
B=Path(__file__).parent;base='1dc68285d499d6f4f8ddcef2c1ff873883f0ed7d'
def read(f):return json.loads(Path(f).read_text())
def h(o):return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def original(f):return json.loads(subprocess.check_output(['git','show',base+':'+f]))
c=read(B/'CANDIDATE.json');claims=read(B/'CLAIMS.json')['claims'];schema=read(B/'CLAIM-SCHEMA.json');sources={x['id']:x for x in read('data/content.json')['sources']}
assert len(claims)==13 and len({x['claimId'] for x in claims})==13
for row in claims:
 assert all(k in row for k in schema['required'])
 assert row['grade'] in schema['grades'] and row['reviewState']=='pending_independent_and_human_review'
 assert len(row['domains'])==5 and [d['domain'] for d in row['domains']]==schema['domains']
 assert row['rationale'] and row['locators'] and row['sourceIds']
 for bind in row['sourceBindings']:
  assert bind['sourceObjectSha256']==h(sources[bind['sourceId']]),'Stale claim source'
  if bind.get('path'):assert hashlib.sha256(Path(bind['path']).read_bytes()).hexdigest()==bind['fileSha256']
for f in ['data/content.json','data/public-content.json']:
 old=original(f);new=read(f);assert [g for g in old['guides'] if g.get('entityId')!='D10']==[g for g in new['guides'] if g.get('entityId')!='D10']
 ns={s['id']:s for s in new['sources']};assert all(s==ns[s['id']] for s in old['sources'])
 assert next(g for g in new['guides'] if g.get('entityId')=='D10')==c['guide']
 assert not any(x in json.dumps(c['guide']) for x in ['40605964','Makis','CP027','CP028'])
p=read(B/'PRESERVATION.json');assert all(hashlib.sha256(Path(f).read_bytes()).hexdigest()==v for f,v in p['files'].items())
for f,objects in p['protectedBookObjects'].items():
 now=read(f)
 for key,hashes in objects.items():
  current={o['id']:o for o in now[key]};assert all(h(current[id])==digest for id,digest in hashes.items())
assert read('data/drug-status-table.json')['drugs']['/drugs/fenbendazole']==c['status']
old=original('data/drug-status-table.json')['drugs'];now=read('data/drug-status-table.json')['drugs'];assert {k:v for k,v in old.items() if k!='/drugs/fenbendazole'}=={k:v for k,v in now.items() if k!='/drugs/fenbendazole'}
assert not any(p.suffix.lower()=='.pdf' for p in B.rglob('*'))
for text in [json.dumps(c['guide'],ensure_ascii=False),json.dumps(c['mechanism'],ensure_ascii=False),json.dumps(c['sources'],ensure_ascii=False)]:assert '\u2014' not in text
tracked=['data/content.json','data/public-content.json','data/public-mechanisms.json','data/drug-status-table.json','editorial/parent-guide-scopes.json','data/article-updates.json']
before={f:Path(f).read_bytes() for f in tracked};subprocess.run(['python3',str(B/'apply-candidate.py')],check=True);assert all(Path(f).read_bytes()==data for f,data in before.items())
print('PASS:13 scoped five-domain claims; exact source bindings; protected book and all other guide/source objects;70 prior outcomes and68 summaries; status citation; no public PDFs/new em dashes; repeat application zero diff.')
