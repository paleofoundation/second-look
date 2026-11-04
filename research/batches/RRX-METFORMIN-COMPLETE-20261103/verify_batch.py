"""Verify identities, source bytes, explicit assessment fields and private guide parity."""
import argparse,collections,hashlib,json,re
from pathlib import Path
B=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def schema_check(value,schema,where='$'):
 if 'const' in schema:assert value==schema['const'],where
 if 'enum' in schema:assert value in schema['enum'],where
 t=schema.get('type')
 if t:assert isinstance(value,{'object':dict,'array':list,'string':str}[t]),where
 if t=='object':
  assert set(schema.get('required',[]))<=set(value),where
  props=schema.get('properties',{})
  if schema.get('additionalProperties') is False:assert set(value)<=set(props),where
  for k,v in value.items():
   if k in props:schema_check(v,props[k],where+'/'+k)
 if t=='array':
  assert len(value)>=schema.get('minItems',0) and len(value)<=schema.get('maxItems',float('inf')),where
  for n,v in enumerate(value):schema_check(v,schema.get('items',{}),where+'/'+str(n))
 if t=='string':
  assert len(value)>=schema.get('minLength',0),where
  if 'pattern' in schema:assert re.search(schema['pattern'],value),where

def verify(guide):
 sources=read(B/'source-access.json')['sources'];ids=[s['sourceId'] for s in sources];assert len(ids)==len(set(ids))==33
 coverage=read(B/'coverage.json');assert coverage['fixedSourceQuota'] is None
 assert {r['sourceId'] for r in coverage['coverage']}==set(ids)
 schema=read(B/'review.v3.schema.json');questions=read(B/'review-questions-and-inputs.json')['questions']
 expected={(q['id'],f) for q in questions for f in q['inputFields']};assert len(expected)==67
 assessed={};unique_assets={};states=collections.Counter()
 for s in sources:
  for asset in s['assets']:
   assert sha(asset['path'])==asset['sha256'],asset['path'];unique_assets[asset['path']]=asset['sha256']
 for f in sorted((B/'assessments').glob('*.json')):
  r=read(f);schema_check(r,schema);assert f.stem==r['sourceId'];assessed[f.stem]=r
  assert len(r['inputs'])==67 and {(i['questionId'],i['field']) for i in r['inputs']}==expected
  unresolved=[i['field'] for i in r['inputs'] if i['status'] in ['not_accessible','not_checked']]
  assert unresolved==r['unresolvedInputs'];assert (r['completion']=='partial')==bool(unresolved)
  for i in r['inputs']:assert i['value'].strip() and not re.search(r'GAP:|UNCHECKED:',i['value'])
  for q in questions:
   partial=any(i['status'] in ['not_accessible','not_checked'] for i in r['inputs'] if i['questionId']==q['id'])
   assert (r['questions'][q['id']]['status']=='partial')==partial
  for a in r['sourceAssets']:assert sha(a['path'])==a['sha256']
  cov=next(c for c in coverage['coverage'] if c['sourceId']==f.stem);assert cov['sha256']==sha(f)
  states[r['completion']]+=1
 assert len(assessed)==coverage['scientificAssessmentCount']==24
 source=read(guide/'manuscript-source.json');m=source['manuscript'];refs={r['id'] for r in m['references']};used={s for c in m['chapters'] for b in c['blocks'] for s in b['sourceIds']}
 assert refs==used and refs<=set(ids) and len(refs)==30
 assert not refs.intersection({'P-REVIVE-2026','ABRILLA-2021','EL-MIR-2000'})
 manifest=read(guide/'output/build-manifest.json');assert manifest['sourceSha256']==sha(guide/'manuscript-source.json')
 for file,a in manifest['assets'].items():assert sha(guide/'output'/file)==a['sha256']
 from pypdf import PdfReader
 import pdfplumber
 pdf_checks=[]
 normalize=lambda x:' '.join(x.split())
 for variant,a in manifest['pdf']['assets'].items():
  path=guide/'output'/a['file'];pdf=PdfReader(path);page_text=[p.extract_text() or '' for p in pdf.pages]
  assert all(t.startswith('REMAPRX\nPRIVATE EDITORIAL DRAFT\n') for t in page_text)
  text='\n'.join('\n'.join(t.splitlines()[4:]) for t in page_text);compact=normalize(text)
  scoped=m if variant=='full' else read(guide/'output'/('sample-candidate.json' if variant=='preview' else 'summary-candidate.json'))
  assert normalize(m['medicalNotice']) in compact
  for c in scoped['chapters']:
   for b in c['blocks']:
    phrases=[b['text']] if b['type'] in ['paragraph','callout'] else b['items'] if b['type'] in ['questions','list'] else [b['caption'],*b['columns'],*(v for row in b['rows'] for v in row)]
    for phrase in phrases:assert normalize(phrase) in compact,(variant,c['id'],phrase[:50])
  assert len(pdf.outline)==len(a['bookmarks'])
  for mark in pdf.outline:assert 0<=pdf.get_destination_page_number(mark)<len(pdf.pages)
  for link in a['linkAnnotations']:assert link['uri'].startswith('https://') or 1<=link['destinationPage']<=len(pdf.pages)
  with pdfplumber.open(path) as pp:
   for page in pp.pages:
    assert page.chars and all(0<=ch['x0'] and ch['x1']<=page.width+.5 and 0<=ch['top'] and ch['bottom']<=page.height+.5 for ch in page.chars)
    assert all(ch['text']!='\ufffd' for ch in page.chars)
  pdf_checks.append({'variant':variant,'pages':len(pdf.pages),'links':len(a['linkAnnotations']),'sha256':sha(path)})
 report={'status':'PASS','sourceDispositions':33,'scientificAssessments':24,'questions':360,'explicitInputs':1608,'assessmentStates':dict(states),'verifiedSourceFiles':len(unique_assets),'guideReferences':len(refs),'guideBlocks':sum(len(c['blocks']) for c in m['chapters']),'pdfs':pdf_checks,'limits':'Structural, byte, content-parity and geometry checks do not confer independent scientific or human release approval.'}
 (B/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guide',type=Path,required=True);verify(p.parse_args().guide)
