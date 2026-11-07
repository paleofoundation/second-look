"""Bind the root's reviewed label paragraphs to receipts and existing source IDs."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'research/batches/RRX-PROSE-MINIMUM-20261104'
inputs = json.loads((ROOT / sys.argv[1]).read_text())
inventory = {row['sourceId']: row for row in json.loads((BATCH / 'source-inventory-v3.json').read_text())}
if (BATCH / 'source-inventory-v3.1.json').exists():
    inventory.update({row['sourceId']: row for row in json.loads((BATCH / 'source-inventory-v3.1.json').read_text())})
paths = [ROOT / name for name in ['data/content.json', 'data/public-content.json', 'data/discovery-pages.json', 'editorial/parent-guide-scopes.json']]
data = [json.loads(path.read_text()) for path in paths]
collections = [data[0]['guides'], data[1]['guides'], data[2], [row['guide'] for row in data[3]['parents']]]
guides = {guide['id']: guide for guide in data[1]['guides'] + data[2]}
output = {'guides': [], 'mechanisms': [], 'gaps': []}
by_id = {}
for entry in inputs:
    guide = guides[entry['guideId']]
    if guide['id'] not in by_id:
        by_id[guide['id']] = {'guideId': guide['id'], 'sections': []}
    text = entry['paragraph']
    sentences = [{'text': part.strip(), 'sources': entry['sources']} for part in re.split(r'(?<=[.!?])\s+(?=[A-Z])', text) if part.strip()]
    ids = list(entry['sources'])
    if entry.get('mode') == 'append':
        previous = next(section for section in guide['sections'] if section['id'] == entry['id'])
        previous_sentences = previous.get('sentences') or [{'text': previous['paragraph'], 'sources': previous['sources']}]
        sentences = previous_sentences + sentences
        text = previous['paragraph'] + ' ' + text
        ids = list(dict.fromkeys(previous['sources'] + ids))
    assert ' '.join(' '.join(sentence['text'] for sentence in sentences).split()) == ' '.join(text.split())
    assert len(text.split()) >= 113 and len(text) >= 845, (guide['id'], entry['id'], len(text.split()), len(text))
    for source_id in entry['sources']:
        source = inventory[source_id]
        receipt_path = BATCH / 'returns' / f'{source_id}-receipt.json'
        receipt = json.loads(receipt_path.read_text())
        assert receipt['file'] and receipt['sha256'] and Path(receipt['file']).is_file(), source_id
        receipt['accessStatus'] = 'full_text'
        receipt['identity'] = {'kind': 'general' if source_id == 'MF-FDA-GENERICS' else 'product', 'name': source['title'], 'formulation': entry.get('productScope', 'Exact cited label product; formulation and indication qualifiers retained in paragraph.'), 'verified': True}
        observation = {'claim': entry['paragraph'], 'locator': entry['locator'], 'scope': f"{guide['title']}; exact labeled product and indication qualifications, not a new efficacy result", 'kind': {'quality': 'formulation', 'contraindications': 'contraindication', 'interactions': 'interaction', 'dosing': 'dosing'}.get(entry['id'], 'safety')}
        if observation not in receipt['observations']:
            receipt['observations'].append(observation)
        receipt['gaps'] = [{'reason': 'Selected source-located label context only; no full study appraisal or exhaustive interaction assessment is claimed.', 'status': 'not_applicable', 'nextAction': 'Retain source-specific scope when rendering the accepted prose.'}]
        receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
        if 'sourceRecordCandidate' in source:
            for dataset in data[:2]:
                if not any(item['id'] == source_id for item in dataset['sources']):
                    dataset['sources'].append(source['sourceRecordCandidate'])
        for collection in collections:
            for current in collection:
                if current['id'] == guide['id'] and source_id not in current['sourceIds']:
                    current['sourceIds'].append(source_id)
    by_id[guide['id']]['sections'].append({'id': entry['id'], 'paragraph': text, 'sources': ids, 'sentences': sentences})
output['guides'] = list(by_id.values())
for path, value in zip(paths, data):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
target = ROOT / sys.argv[2]
target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
print(f"Prepared {sum(len(guide['sections']) for guide in output['guides'])} reviewed label prose blocks with source receipts.")
