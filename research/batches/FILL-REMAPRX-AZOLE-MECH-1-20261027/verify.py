from pathlib import Path
import json,hashlib,subprocess,re
P=Path(__file__).resolve().parent;R=P.parents[2];B='d118d305b59cac5e54ca7f9e5aa55cea682d2cee'
def original(f):return subprocess.check_output(['git','-C',str(R),'show',B+':'+f])
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def read(f):return json.loads((R/f).read_text())
changes=[];unchanged=[];added=[]
def rawspans(text,key,identity):
 match=re.search(r'"'+re.escape(key)+r'"\s*:\s*\[',text);assert match;idx=match.end();decoder=json.JSONDecoder();out={}
 while True:
  while text[idx].isspace() or text[idx]==',':idx+=1
  if text[idx]==']':break
  start=idx;obj,idx=decoder.raw_decode(text,idx);out[identity(obj)]=text[start:idx].encode()
 return out
def check(f,key,identity,allowed,additions=()):
 oldraw=original(f).decode();newraw=(R/f).read_text();ra=rawspans(oldraw,key,identity);rb=rawspans(newraw,key,identity);old=json.loads(oldraw)[key];new=read(f)[key];a={identity(x):x for x in old};b={identity(x):x for x in new};assert not set(a)-set(b),(f,key,'removed');assert set(b)-set(a)==set(additions),(f,key,'added')
 for k in a:
  entry={'file':f,'collection':key,'id':k,'beforeSha256':digest(a[k]),'afterSha256':digest(b[k])}
  if a[k]!=b[k]:assert k in allowed,entry;changes.append(entry)
  else:
   assert ra[k]==rb[k],('raw span changed',f,key,k);entry['rawSha256']=hashlib.sha256(ra[k]).hexdigest();unchanged.append(entry)
 for k in set(b)-set(a):added.append({'file':f,'collection':key,'id':k,'sha256':digest(b[k])})
 assert set(k for k in a if a[k]!=b[k])==set(allowed),(f,key,'expected exact changes')
proposal=json.loads((P/'PROPOSED-SOURCE-BINDINGS.json').read_text())['records'];newids=[s['proposedSourceId'] for s in proposal]
for f in ['data/content.json','data/public-content.json']:
 check(f,'sources',lambda x:x['id'],[],newids);check(f,'guides',lambda x:x['id'],['G-DRUG-D07']);check(f,'glossary',lambda x:x['slug'],['hedgehog-pathway','hyphae'])
 old=json.loads(original(f));new=read(f)
 for k in old:
  if k not in ['sources','guides','glossary']:assert old[k]==new[k],(f,k)
f='editorial/parent-guide-scopes.json';check(f,'parents',lambda x:x['guideId'],['G-DRUG-D07']);old=json.loads(original(f));new=read(f)
for x,y in zip(old['parents'],new['parents']):
 if x['guideId']=='G-DRUG-D07':assert {k:v for k,v in x.items() if k!='guide'}=={k:v for k,v in y.items() if k!='guide'}
f='data/public-mechanisms.json';old=json.loads(original(f));new=read(f);assert old['contexts']==new['contexts'] # explicit checks below
for x,y in zip(old['drugs'],new['drugs']):
 if x.get('drugId')=='D07':
  for k in x:
   if k=='pathways':assert y[k][:len(x[k])]==x[k]
   else:assert x[k]==y[k],('D07 mechanism preserved',k)
 else:assert x==y,('old mechanism changed',x)
assert len(new['drugs'])==len(old['drugs'])+2
assert [x['guideIds'] for x in new['drugs'][-2:]]==[['term-hedgehog-pathway'],['term-hyphae']]
assert not any('comparisonTables' in x for x in new['drugs'])
f='data/article-updates.json';old=json.loads(original(f));new=read(f);assert new['entries'][3:]==old['entries'];assert len(new['entries'])==len(old['entries'])+3
assert {e['pagePaths'][0] for e in new['entries'][:3]}=={'/drugs/itraconazole','/glossary/hedgehog-pathway','/glossary/hyphae'}
for e in new['entries'][:3]:assert e['changeType']=='evidence'
for f in ['docs/PROJECT-RULES.md','docs/RULE-CHANGELOG.md']:
 old=original(f).decode().rstrip();new=(R/f).read_text();assert new.startswith(old+'\n\n## October 27 azole mechanism scope and 10:43 gates\n');assert new.count('## October 27 azole mechanism scope and 10:43 gates')==1
for f in ['lib/mechanisms.ts','components/article.tsx','components/shared-theme/mechanisms.tsx']:assert (R/f).read_bytes()==original(f),('table revert exact base',f)
allowed={'data/content.json','data/public-content.json','editorial/parent-guide-scopes.json','data/public-mechanisms.json','data/article-updates.json','docs/PROJECT-RULES.md','docs/RULE-CHANGELOG.md'}
tracked=subprocess.check_output(['git','-C',str(R),'diff','--name-only',B],text=True).splitlines();assert all(f in allowed or f.startswith('research/batches/FILL-REMAPRX-AZOLE-MECH-1-20261027/') for f in tracked),tracked
for f in ['data/content.json','data/public-content.json','editorial/parent-guide-scopes.json','data/public-mechanisms.json','data/article-updates.json']:
 diff=subprocess.check_output(['git','-C',str(R),'diff','--unified=0',B,'--',f],text=True)
 bad=[s for s in diff.splitlines() if s.startswith('+') and not s.startswith('+++') and ('\u2013' in s or '\u2014' in s)];assert not bad,(f,bad)
report={'status':'PASS','base':B,'changedKeyedObjects':changes,'unchangedKeyedObjects':unchanged,'addedSourceObjects':added,'counts':{'changed':len(changes),'unchanged':len(unchanged),'added':len(added)},'sharedRenderer':'All three files byte-identical to fixed base after ordinary revert','oldMechanismObjects':'D07 original fields and pathway prefix preserved, all other original records/contexts identical','protectedGuides':'All 13 prior guides including D34, seven PR9 IDs and fenbendazole unchanged; only D07 changed','protectedBatches':'No RRX-INGEST-* or FILL-REMAPRX-2 path touched','addedPublicDashLines':0,'trackedAppPaths':[f for f in tracked if f in allowed]}
(P/'PER-ID-PRESERVATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['changedKeyedObjects','unchangedKeyedObjects','addedSourceObjects']}))
