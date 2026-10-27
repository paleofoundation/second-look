"""Publish the already-rendered sample locally and check its PDF structure."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
from pypdf import PdfReader, PdfWriter

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parents[3]
ART = ROOT / 'artifacts/physician-packet-nsclc'
OUT = ART / 'output'
NAME = 'remaprx-nsclc-physician-packet-sample'
rendered = ART / 'render' / (NAME + '.pdf')
final = OUT / (NAME + '.pdf')
manuscript = json.loads((BATCH / 'manuscript.json').read_text())
candidate = json.loads((BATCH / 'candidate.json').read_text())
reader = PdfReader(rendered)
assert len(reader.pages) == 5
writer = PdfWriter(clone_from=rendered)
writer._root_object.pop('/Outlines', None)
for i, page in enumerate(manuscript['pages']):
    writer.add_outline_item(page['title'], i)
writer.add_metadata({'/Title': 'Non-small-cell lung cancer physician discussion packet',
                     '/Author': 'RemapRx sample preparation',
                     '/Subject': 'Educational sample; independent clinical review pending'})
with final.open('wb') as output:
    writer.write(output)
result = PdfReader(final)
assert len(result.pages) == 5 and len(result.outline) == 5
external, internal = [], 0
words = []
for index, (before, page) in enumerate(zip(reader.pages, result.pages)):
    assert before.get_contents().get_data() == page.get_contents().get_data()
    text = page.extract_text()
    assert len(text.split()) > 150
    assert 'Sample 1.0' in text and 'Clinical review pending' in text
    for token in ('{{', 'PP-CLAIM-', 'RRX-PHYSICIAN', 'turn11view', 'PLACEHOLDER'):
        assert token not in text
    words.append(len(text.split()))
    for ref in page.get('/Annots', []):
        annotation = ref.get_object()
        if '/Dest' in annotation:
            internal += 1
            assert annotation['/Dest'][0] == result.pages[3].indirect_reference
            assert 0 <= float(annotation['/Dest'][3]) <= 792
        elif '/A' in annotation:
            action = annotation['/A']
            assert action['/S'] == '/URI'
            external.append(str(action['/URI']))
assert internal == 17
assert sorted(external) == sorted(s['url'] for s in candidate['sources'])
ids = [s['id'] for s in candidate['sources']]
assert len(set(ids)) == len(ids) == 6
claim_ids = [c['id'] for c in candidate['claims']]
assert len(set(claim_ids)) == len(claim_ids) == 14
for claim in candidate['claims']:
    assert claim['sourceIds'] and set(claim['sourceIds']).issubset(ids)
    assert claim['humanReview'] == 'pending'

def fingerprint(path):
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

manifest_path = BATCH / 'source-manifest.json'
manifest = json.loads(manifest_path.read_text())
manifest['updatedAt'] = datetime.now(timezone.utc).isoformat()
captures = sorted((ART / 'research').glob('web-*.txt'), key=lambda p: int(p.stem.split('-')[1]))
manifest['sourceCaptures'] = [fingerprint(p) for p in captures]
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')

validation = {
    'checkedAt': datetime.now(timezone.utc).isoformat(),
    'scope': 'Local product sample only; no canonical import, clinical approval or subscriber release',
    'pdf': {'pages': 5, 'bookmarks': 5, 'selectableText': True, 'wordsPerPage': words,
            'internalCitationsToSourcePage': internal, 'externalSourceLinks': len(external),
            'finalPageContentIdenticalToInspectedRender': True},
    'sourceMapping': {'uniqueSources': len(ids), 'uniqueClaimBlocks': len(claim_ids),
                      'orphanSources': 0, 'pendingHumanReview': 14},
    'artifacts': [fingerprint(OUT / f) for f in (NAME+'.pdf', NAME+'.docx', 'physician-email-template.txt')],
    'remaining': ['Full Q01-Q15 scientific appraisals and required companions',
                  'Independent qualified clinical review',
                  'Authenticated portal implementation, sharing and subscriber release checks']
}
(BATCH / 'validation.json').write_text(json.dumps(validation, indent=2) + '\n')
print(json.dumps({'finalPdf': str(final), 'pages': 5, 'citations': internal, 'externalLinks': len(external)}))
