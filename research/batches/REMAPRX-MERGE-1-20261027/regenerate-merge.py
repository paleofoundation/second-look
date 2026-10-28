from pathlib import Path
from copy import deepcopy
import json,subprocess,hashlib
R=Path(__file__).resolve().parents[3]
P=R/'research/batches/REMAPRX-MERGE-1-20261027';P.mkdir(exist_ok=True)
O='82189fb66be796db935c12d96b4adb477ff7a77a';M='4ca37b7e433aebcb2fdcc4fe39801b8f527e0bea';B='d118d305b59cac5e54ca7f9e5aa55cea682d2cee'
def raw(ref,f):return subprocess.check_output(['git','show',ref+':'+f],cwd=R)
def read(ref,f):return json.loads(raw(ref,f))
def write(f,j):(R/f).write_text(json.dumps(j,indent=2,ensure_ascii=False)+'\n')
c=json.loads((R/'research/batches/FILL-REMAPRX-AZOLE-MECH-1-20261027/CANDIDATE.json').read_text())
proof={'ours':O,'main':M,'fixedCandidateBase':B,'method':'Replay exact saved PR10 candidate onto main authoritative records; never run historical fixed-base generator','collections':[]}
for f in ['data/content.json','data/public-content.json']:
 j=read(M,f);before=deepcopy(j);base=read(B,f);ours=read(O,f)
 ids={s['id'] for s in j['sources']};assert not ids.intersection(s['id'] for s in c['newSources'])
 j['sources']+=deepcopy(c['newSources'])
 assert sum(g['id']=='G-DRUG-D07' for g in j['guides'])==1
 j['guides']=[deepcopy(c['guide']) if g['id']=='G-DRUG-D07' else g for g in j['guides']]
 terms={t['slug']:t for t in c['glossary']};j['glossary']=[deepcopy(terms.get(t['slug'],t)) for t in j['glossary']]
 for key,identity,changed in [('sources','id',set()),('guides','id',{'G-DRUG-D07'}),('glossary','slug',set(terms))]:
  old={x[identity]:x for x in before[key]};out={x[identity]:x for x in j[key]};pr={x[identity]:x for x in ours[key]}
  assert all(out[k]==v for k,v in old.items() if k not in changed)
  assert all(k in out for k in pr)
  # Every original PR10 object survives, except PR9 legitimately changes independent guides.
  b={x[identity]:x for x in base[key]}
  delta={k:v for k,v in pr.items() if k not in b or b[k]!=v}
  assert all(out[k]==v for k,v in delta.items())
  proof['collections'].append({'file':f,'collection':key,'mainCount':len(old),'mergedCount':len(out),'pr10DeltaIdsPreserved':list(delta),'allMainIdsPreserved':True,'mainOtherObjectsUnchanged':True})
 write(f,j)
f='editorial/parent-guide-scopes.json';j=read(M,f)
for p in j['parents']:
 if p['guideId']=='G-DRUG-D07':p['guide']=deepcopy(c['guide'])
assert {p['guideId'] for p in read(M,f)['parents']}=={p['guideId'] for p in j['parents']};write(f,j)
f='data/article-updates.json';j=read(M,f);ours=read(O,f);baseids={e['id'] for e in read(B,f)['entries']};new=[e for e in ours['entries'] if e['id'] not in baseids];assert len(new)==3
ids={e['id'] for e in j['entries']};assert not ids.intersection(e['id'] for e in new);j['entries']=deepcopy(new)+j['entries'];write(f,j)
heading='## October 27 azole mechanism scope and 10:43 gates'
newheading='## October 27 main integration and authorized publication gate'
text="Source: Elon's October 27, 17:15 Asia/Nicosia REMAPRX-MERGE-1 order, relaying Karen's 16:47 merge and deploy GO. Resolve PR10 with a normal origin/main merge, preserving all PR9 guide IDs and every PR10 candidate object. Rebuild canonical and public content from main records plus the exact saved azole candidate, rather than editing generated conflict hunks or rerunning the historical fixed-base generator. Preserve all historical research packets and scientific-review states. Run production build, governance and relevant content checks; plain push the merge head for Elon's green-check squash merge. This supersedes the earlier no-merge/no-publication boundary only for this integration and one normal Sites publish of main 4ca37b7 or main after PR10, project appgprj_6ac734459a508191a425263c7645a0be, rollback version 46. Root verification of head, main and staging precedes publication. No other publish, DNS, secrets, audience or indexing changes. Technical integration is not scientific or human review approval. Implementation and validation: research/batches/REMAPRX-MERGE-1-20261027/."
for f in ['docs/PROJECT-RULES.md','docs/RULE-CHANGELOG.md']:
 main=raw(M,f).decode().rstrip();azole=raw(O,f).decode().split(heading,1)[1].strip();assert heading not in main
 (R/f).write_text(main+'\n\n'+heading+'\n\n'+azole+'\n\n'+newheading+'\n\n'+text+'\n')
# Assert automatic mechanisms merge retained every main and exact PR10 delta object.
f='data/public-mechanisms.json';j=json.loads((R/f).read_text());main=read(M,f);ours=read(O,f);base=read(B,f)
assert j['contexts']==main['contexts']
for x in ours['drugs']:
 if x.get('drugId')=='D07' or x.get('guideIds') in [['term-hedgehog-pathway'],['term-hyphae']]:assert x in j['drugs']
for x in main['drugs']:
 if x.get('drugId')!='D07':assert x in j['drugs']
# All prior PR10 packet bytes and main frozen research bytes remain byte identical.
for ref in [O,M]:
 files=subprocess.check_output(['git','ls-tree','-r','--name-only',ref,'research'],cwd=R,text=True).splitlines()
 for f in files:assert (R/f).read_bytes()==raw(ref,f),(ref,f)
proof['allHistoricalResearchBytesPreserved']=True
proof['allMainGuideIds']= [g['id'] for g in read(M,'data/content.json')['guides']]
(P/'PRESERVATION.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof,indent=2))
