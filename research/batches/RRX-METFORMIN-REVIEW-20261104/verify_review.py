"""Check the review's exact bindings and the rendered private edition, without conferring approval."""
import collections, datetime, hashlib, json
from pathlib import Path
from pypdf import PdfReader
import pdfplumber

B = Path(__file__).resolve().parent
ROOT = B.parents[2]
def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def schema_check(value, schema, where='$'):
    if 'const' in schema: assert value == schema['const'], where
    if 'enum' in schema: assert value in schema['enum'], where
    typ = schema.get('type')
    if typ: assert isinstance(value, {'object':dict,'array':list,'string':str,'integer':int}[typ]), where
    if typ == 'object':
        assert set(schema.get('required',[])) <= value.keys(), where
        for k,v in value.items():
            if k in schema.get('properties',{}): schema_check(v,schema['properties'][k],where+'.'+k)
    if typ == 'array':
        for i,v in enumerate(value): schema_check(v,schema.get('items',{}),where+f'[{i}]')

plan,review,artifact = map(read,[B/'plan.json',B/'review.json',B/'guide-artifacts.json'])
readiness=read(B/'readiness.json')
assert readiness['status']=='GP Plan PASS'
for name,digest in readiness['files'].items(): assert sha(B/name)==digest
schema_check(review,read(B/'review.schema.json'))
assert review['inputHashes'] == plan['inputs']
for a in plan['inputs']: assert sha(a['path']) == a['sha256'], a['path']
assert [{'chapterId':a['chapterId'],'block':a['block'],'sourceIds':a['sourceIds']} for a in review['blockAudits']] == plan['reviewUnits']
assert len({(a['chapterId'],a['block']) for a in review['blockAudits']}) == len(plan['reviewUnits'])
assert {s['sourceId'] for s in review['sourceChecks']} == set(plan['sourceIds'])
for a in review['blockAudits']:
    assert {s['sourceId'] for s in a['sourceLocators']} == set(a['sourceIds'])
    assert len(a['rationale']) > 40
assert all(f['status']=='resolved_in_candidate_2' for f in review['findings'])

previous = B.parent/'RRX-METFORMIN-COMPLETE-20261103'
original_manifest = read(previous/'guide-artifacts.json')
for a in original_manifest['assets']: assert sha(a['file'])==a['sha256']
assets = {}
for source in read(previous/'source-access.json')['sources']:
    for a in source['assets']:
        assert sha(a['path'])==a['sha256']; assets[a['path']]=a['sha256']
        if a.get('textPath'): assert sha(a['textPath'])==a['textSha256']
states=collections.Counter(read(f)['completion'] for f in (previous/'assessments').glob('*.json'))

source_path = Path(artifact['source']['path'])
private = source_path.parent
assert not private.is_relative_to(ROOT)
assert artifact['source']['sha256']==sha(source_path)
source=read(source_path); m=source['manuscript']; old=read(plan['inputs'][0]['path'])['manuscript']
assert m['references']==old['references']
assert m['editionId']!=old['editionId'] and m['version']!=old['version']
assert datetime.datetime.fromisoformat(m['updatedAt'].replace('Z','+00:00')) <= datetime.datetime.now(datetime.timezone.utc)
refs={r['id'] for r in m['references']}
assert refs=={s for c in m['chapters'] for block in c['blocks'] for s in block['sourceIds']}==set(plan['sourceIds'])
assert not refs & {'P-REVIVE-2026','ABRILLA-2021','EL-MIR-2000'}
assert len(review['blockAudits'])+len(review['newBlockAudits'])==sum(len(c['blocks']) for c in m['chapters'])
old_chapters={c['id']:c for c in old['chapters']}
for c in m['chapters']:
    for a in [a for a in review['blockAudits'] if a['chapterId']==c['id']]:
        if a['decision'] not in ['corrected','qualified']:
            assert c['blocks'][a['outputBlock']-1]==old_chapters[c['id']]['blocks'][a['block']-1],(c['id'],a['block'])
manifest=read(private/'output/build-manifest.json')
assert artifact['buildManifest']['sha256']==sha(private/'output/build-manifest.json')
assert manifest['sourceSha256']==sha(source_path)
assert manifest['releaseState']=='private_draft' and manifest['sampleApproval']=='pending'
for name,a in manifest['assets'].items(): assert sha(private/'output'/name)==a['sha256']
assert artifact['modelReview']['sha256']==sha(B/'review.json')
assert read(private/'output/web-manuscript.json')==m
for k in ['independentClinicalReview','humanEditorialApproval','commercialLegalApproval']: assert artifact[k]=='pending'

normalize=lambda x:' '.join(x.split())
pdf_results=[]
for variant,a in manifest['pdf']['assets'].items():
    path=private/'output'/a['file']; pdf=PdfReader(path)
    page_text=[p.extract_text() or '' for p in pdf.pages]
    assert all(t.startswith('REMAPRX\nPRIVATE EDITORIAL DRAFT\n') for t in page_text)
    compact=normalize('\n'.join('\n'.join(t.splitlines()[4:]) for t in page_text))
    scoped=m if variant=='full' else read(private/'output'/('sample-candidate.json' if variant=='preview' else 'summary-candidate.json'))
    assert normalize(m['medicalNotice']) in compact
    for c in scoped['chapters']:
        for block in c['blocks']:
            phrases=[block['text']] if block['type'] in ['paragraph','callout'] else block['items'] if block['type'] in ['questions','list'] else [block['caption'],*block['columns'],*(v for row in block['rows'] for v in row)]
            for phrase in phrases: assert normalize(phrase) in compact,(variant,c['id'],phrase[:65])
    assert len(pdf.outline)==len(a['bookmarks'])
    for mark in pdf.outline: assert 0 <= pdf.get_destination_page_number(mark) < len(pdf.pages)
    for link in a['linkAnnotations']: assert link['uri'].startswith('https://') or 1<=link['destinationPage']<=len(pdf.pages)
    with pdfplumber.open(path) as pp:
        for page in pp.pages:
            assert page.chars
            assert all(0<=ch['x0'] and ch['x1']<=page.width+.5 and 0<=ch['top'] and ch['bottom']<=page.height+.5 for ch in page.chars)
            assert all(ch['text']!='\ufffd' for ch in page.chars)
    pdf_results.append({'variant':variant,'pages':len(pdf.pages),'links':len(a['linkAnnotations']),'bookmarks':len(pdf.outline),'sha256':sha(path),'tagged':bool(pdf.trailer['/Root'].get('/StructTreeRoot'))})
report={
    'status':'PASS','inputHashesVerified':len(plan['inputs']),'priorPrivateAssetsPreserved':len(original_manifest['assets']),
    'verifiedSourceFiles':len(assets),'sourceAssessmentStates':dict(states),
    'originalBlocksReviewed':len(review['blockAudits']),'newBlocksReviewed':len(review['newBlockAudits']),
    'references':len(refs),'resolvedFindings':len(review['findings']),'pdfs':pdf_results,
    'checks':['Input/source byte identity','Historical candidate preservation','All original and new block audit bindings','Reference and excluded-source closure','Only declared blocks changed','UTC timestamp not in future','Web and PDF text parity for all variants','PDF text bounds and replacement-glyph check','Bookmark/link destination checks','Private location and pending approval states'],
    'limits':'Deterministic verification supports the authored review; it does not replace scientific judgment, visual inspection, a real reader test or human/legal approval.'
}
(B/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
