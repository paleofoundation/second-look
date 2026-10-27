from pathlib import Path
import json,re,hashlib,sys
P=Path(__file__).resolve().parent;R=P.parents[2];htmlroot=Path(sys.argv[1]);content=json.loads((R/'data/public-content.json').read_text());known={s['id'] for s in content['sources']}|{s['id'] for s in json.loads((R/'data/treatment-suitability.json').read_text())['sources']};records=[]
for slug in ['_drugs_itraconazole','_glossary_hedgehog-pathway','_glossary_hyphae']:
 s=(htmlroot/(slug+'.html')).read_text();ids=re.findall(r'(?<![-\w])id="([^"]+)"',s);assert len(ids)==len(set(ids)),slug+' duplicate ids';sources=set(re.findall(r'data-source-id="([^"]+)"',s));assert sources<=known,(slug,sources-known)
 refs=set(re.findall(r'href="#(source-ref-[^"]+)"',s));assert refs<=set(ids),(slug,refs-set(ids));assert 'citation-missing' not in s
 seen={}
 for id,n in re.findall(r'data-source-id="([^"]+)"[^>]*><a[^>]*aria-label="Citation (\d+):',s):
  if id in seen:assert seen[id]==int(n)
  else:seen[id]=int(n)
 assert list(seen.values())==list(range(1,len(seen)+1)),slug+' first-appearance order'
 records.append({'routeFile':slug+'.html','status':'PASS','citationSourceIds':sorted(sources),'referenceTargets':len(refs),'uniqueElementIds':len(ids),'firstAppearanceCitationOrder':'PASS sequential, stable repeated citations','sha256':hashlib.sha256(s.encode()).hexdigest()})
(P/'SCOPED-SSR-CITATIONS.json').write_text(json.dumps({'status':'PASS','method':'Actual Article SSR. Every cited source exists in public content or unchanged treatment-suitability sources, all reference targets resolve, all element IDs unique, first appearance sequential, no missing-citation sentinel. No table renderer present.','records':records},indent=2)+'\n');print('PASS3 scoped actual-Article citation checks')
