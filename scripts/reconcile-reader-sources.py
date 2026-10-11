"""Merge duplicate source identities and reconcile reader citations, never protected reviews."""
import json,re
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_text())
def save(n,v):(ROOT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def keys(s):
 out=[]
 if s.get('sourceType')=='textbook' or s['id'].startswith(('CP027','CP028')):return ['chapter:'+s['id']]
 if s.get('doi'):out.append('doi:'+s['doi'].lower().removeprefix('https://doi.org/'))
 if s.get('pmid'):out.append('pmid:'+str(s['pmid']))
 u=urlsplit(s['url']);host=u.netloc.removeprefix('www.');p=u.path.rstrip('/');q=parse_qs(u.query)
 if host=='pubmed.ncbi.nlm.nih.gov':out.append('pmid:'+p.strip('/'))
 if host=='doi.org':out.append('doi:'+p.strip('/').lower())
 if host=='dailymed.nlm.nih.gov' and q.get('setid'):out.append('label:'+q['setid'][0])
 if s.get('sourceType') not in ['textbook','review']:out.append('url:'+host+p+('?'+'&'.join(k+'='+','.join(v) for k,v in sorted(q.items()) if k in ['setid']) if q.get('setid') else ''))
 return out
raw=read('data/content.json');bykey={};aliases=read('editorial/reader-source-aliases.json') if (ROOT/'editorial/reader-source-aliases.json').exists() else {};aliases['CTX-GUIDE-3']='CTX-off-label-1';canonical={}
for source in raw['sources']:
 matches=[bykey[k] for k in keys(source) if k in bykey]
 target=matches[0] if matches else source['id']
 if target!=source['id']:
  aliases[source['id']]=target
  for k,v in source.items():
   if k not in canonical[target] or canonical[target][k] in ['',None,[]]:canonical[target][k]=v
 else:canonical[target]=source
 for k in keys(source):bykey[k]=target
# Only exact known source IDs are remapped. Narrative strings are not rewritten.
def remap(v):
 if isinstance(v,str):return aliases.get(v,v)
 if isinstance(v,list):
  out=[remap(i) for i in v]
  return list(dict.fromkeys(out)) if all(isinstance(i,str) for i in out) else out
 if isinstance(v,dict):return {k:remap(x) for k,x in v.items()}
 return v
raw['sources']=list(canonical.values());raw=remap(raw);save('data/content.json',raw)
public=read('data/public-content.json');public['sources']=[s for s in public['sources'] if s['id'] not in aliases];public=remap(public);save('data/public-content.json',public)
for name in ['data/discovery-pages.json','data/public-mechanisms.json','data/reader-evidence.json','data/public-reader-evidence.json','data/outcome-registry.json','data/outcome-sentence-maps.json','editorial/parent-guide-scopes.json']:
 save(name,remap(read(name)))
save('editorial/reader-source-aliases.json',aliases)
print(json.dumps(dict(aliases=aliases,uniqueSources=len(canonical))))
