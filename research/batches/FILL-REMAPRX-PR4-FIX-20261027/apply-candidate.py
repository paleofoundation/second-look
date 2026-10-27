import json,copy,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;c=json.loads((B/'CANDIDATE.json').read_text());base=c['base']
def read(f):return json.loads((ROOT/f).read_text())
def old(f):return json.loads(subprocess.check_output(['git','show',base+':'+f],cwd=ROOT))
def write(f,d):(ROOT/f).write_text(json.dumps(d,indent=1 if f=='data/drug-status-table.json' else 2,ensure_ascii=False)+'\n')
def guard(a,b,z):assert a==b or a==z,'Concurrent target edit; reconcile first.'
for f in ['data/content.json','data/public-content.json']:
 d=read(f);before=next(g for g in old(f)['guides'] if g.get('entityId')=='D10')
 for i,g in enumerate(d['guides']):
  if g.get('entityId')=='D10':guard(g,c['guide'],before);d['guides'][i]=copy.deepcopy(c['guide'])
 if f=='data/public-content.json':d['sources']=[s for s in d['sources'] if s['id'] not in c['hidePublicSourceIds']]
 write(f,d)
f='data/public-mechanisms.json';d=read(f);before=next(x for x in old(f)['drugs'] if x.get('drugId')=='D10')
for i,m in enumerate(d['drugs']):
 if m.get('drugId')=='D10':guard(m,c['mechanism'],before);d['drugs'][i]=copy.deepcopy(c['mechanism'])
write(f,d)
f='editorial/parent-guide-scopes.json';d=read(f);before=next(x for x in old(f)['parents'] if x.get('entityId')=='D10')['guide'];target=copy.deepcopy(c['guide'])
for k,v in before.items():
 if k not in target:target[k]=v
for p in d['parents']:
 if p.get('entityId')=='D10':guard(p['guide'],target,before);p['guide']=copy.deepcopy(target)
write(f,d)
f='data/drug-status-table.json';d=read(f);guard(d['drugs']['/drugs/fenbendazole'],c['status'],old(f)['drugs']['/drugs/fenbendazole']);d['drugs']['/drugs/fenbendazole']=c['status'];write(f,d)
f='data/public-review-metadata.json';d=read(f);d['records']=[r for r in d['records'] if r['sourceId'] not in c['hidePublicSourceIds']];write(f,d)
f='data/article-updates.json';d=read(f)
for e in d['entries']:
 if e['id']=='2026-10-27-fenbendazole-evidence-correction':e['summary']='Expanded mixed cancer-model findings, model-only mechanism explanations and human liver-injury reports. Added scoped clinical-translation confidence and explicit human dosing gaps. Corrected the FDA veterinary approval citation and clarified that fenbendazole is not approved for human use.'
write(f,d);print('Applied PR4 review correction; internal-only case/mechanism notes excluded from reader projections.')
