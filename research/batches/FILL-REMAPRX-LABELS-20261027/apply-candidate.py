import json,copy,subprocess
from pathlib import Path
B=Path(__file__).parent;c=json.loads((B/'CANDIDATE.json').read_text());base=c['base'];targets={g['entityId']:g for g in c['guides']};mt={m['drugId']:m for m in c['mechanisms']}
def read(f):return json.loads(Path(f).read_text())
def original(f):return json.loads(subprocess.check_output(['git','show',base+':'+f]))
def write(f,d):Path(f).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def guard(old,new,before):assert old==new or old==before,'Concurrent target edit; reconcile before application.'
for f in ['data/content.json','data/public-content.json']:
 d=read(f);old={g.get('entityId'):g for g in original(f)['guides']}
 for i,g in enumerate(d['guides']):
  if g.get('entityId') in targets:guard(g,targets[g['entityId']],old[g['entityId']]);d['guides'][i]=copy.deepcopy(targets[g['entityId']])
 write(f,d)
f='data/public-mechanisms.json';d=read(f);old={m.get('drugId'):m for m in original(f)['drugs']}
for i,m in enumerate(d['drugs']):
 if m.get('drugId') in mt:guard(m,mt[m['drugId']],old[m['drugId']]);d['drugs'][i]=copy.deepcopy(mt[m['drugId']])
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
 drug=g['entityId'];label=drug in mt;id='2026-10-27-label-coverage-'+drug.lower();entry={'id':id,'date':'2026-10-27','title':g['title']+(' label context expanded' if label else ' human-evidence coverage clarified'),'changeType':'evidence','summary':('Expanded the cited product label\'s mechanism, safety and dosing context and distinguished it from the selected repurposing evidence. Added scoped Low clinical-confidence explanations; existing outcome assessments and source reviews retain their prior state.' if label else 'Clarified whether the cited primary papers describe human treatment or laboratory work, with a scoped Low clinical-confidence explanation. Existing outcome and source-review states are unchanged.'),'pagePaths':[g['slug']],'affectedSections':[{'id':s['id'],'label':s['label']} for s in g['sections'] if s['label'] in (['Overview','Benefits','Safety','Dosing','Evidence'] if label else ['Benefits','Evidence'])]}
 d['entries']=[entry]+[x for x in d['entries'] if x['id']!=id]
write(f,d);print('Applied 8 bounded guide updates and 6 mechanism contexts.')
