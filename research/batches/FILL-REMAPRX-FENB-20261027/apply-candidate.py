"""Bounded, idempotent projection of the reviewed D10 candidate. No corpus generator."""
import json,hashlib,copy,subprocess
from pathlib import Path
B=Path(__file__).parent; candidate=json.loads((B/'CANDIDATE.json').read_text())
def original(f):return json.loads(subprocess.check_output(['git','show','1dc68285d499d6f4f8ddcef2c1ff873883f0ed7d:'+f]))
def guard(old,new,baseline):assert old==new or old==baseline, 'Concurrent target edit; stop for reconciliation.'
def read(f):return json.loads(Path(f).read_text())
def write(f,d):Path(f).write_text(json.dumps(d,indent=1 if f=='data/drug-status-table.json' else 2,ensure_ascii=False)+'\n')
def public_source(s):return {k:v for k,v in s.items() if k not in ['access','reviewState','hasReviewDraft','status']}
for f in ['data/content.json','data/public-content.json']:
 d=read(f)
 for s in candidate['sources']:
  target=public_source(s) if f=='data/public-content.json' else s
  old=next((x for x in d['sources'] if x['id']==s['id']),None)
  if old is not None:assert old==target, 'Concurrent source change: '+s['id']
  else:d['sources'].append(target)
 guard(next(g for g in d['guides'] if g.get('entityId')=='D10'),candidate['guide'],next(g for g in original(f)['guides'] if g.get('entityId')=='D10'))
 d['guides']=[copy.deepcopy(candidate['guide']) if g.get('entityId')=='D10' else g for g in d['guides']];write(f,d)
f='editorial/parent-guide-scopes.json';d=read(f)
for p in d['parents']:
 if p.get('entityId')=='D10':
  old=p['guide'];p['guide']=copy.deepcopy(candidate['guide'])
  for key in old:
   if key not in p['guide']:p['guide'][key]=old[key]
write(f,d)
f='data/public-mechanisms.json';d=read(f);guard(next(x for x in d['drugs'] if x.get('drugId')=='D10'),candidate['mechanism'],next(x for x in original(f)['drugs'] if x.get('drugId')=='D10'));d['drugs']=[candidate['mechanism'] if x.get('drugId')=='D10' else x for x in d['drugs']];write(f,d)
f='data/drug-status-table.json';d=read(f);guard(d['drugs']['/drugs/fenbendazole'],candidate['status'],original(f)['drugs']['/drugs/fenbendazole']);d['drugs']['/drugs/fenbendazole']=candidate['status'];write(f,d)
f='data/article-updates.json';d=read(f);entry={'id':'2026-10-27-fenbendazole-evidence-correction','date':'2026-10-27','title':'Fenbendazole evidence and status corrected','changeType':'correction','summary':'Expanded the selected-source cancer evidence with conflicting mouse findings, cell-only mechanisms, an uncontrolled human combination case and liver-injury reports. Added claim-specific clinical evidence labels and explicit human dosing gaps. Corrected the Status table to cite the FDA veterinary approval record.','pagePaths':['/drugs/fenbendazole'],'affectedSections':[{'id':id,'label':label} for id,label in [('overview','Overview'),('mechanisms','Mechanism of Action'),('benefits','Benefits'),('safety','Safety'),('dosing','Dosing'),('status','Status'),('evidence','Evidence')]]};d['entries']=[entry]+[x for x in d['entries'] if x['id']!=entry['id']];write(f,d)
print('Applied bounded D10 candidate.')
