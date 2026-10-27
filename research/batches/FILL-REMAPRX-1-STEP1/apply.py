"""Add checked existing-source associations only; never import or synthesize evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKET = Path(__file__).resolve().parent


def apply():
    ledger = json.loads((PACKET / 'source-mappings.json').read_text())
    paths = ['data/content.json', 'data/public-content.json',
             'data/discovery-pages.json', 'editorial/parent-guide-scopes.json']
    documents = {path: json.loads((ROOT / path).read_text()) for path in paths}
    source_ids = {s['id'] for s in documents[paths[0]]['sources']}
    changed = []
    for path, document in documents.items():
        if path.endswith('discovery-pages.json'):
            guides = document
        elif path.endswith('parent-guide-scopes.json'):
            guides = [parent['guide'] for parent in document['parents']]
        else:
            guides = document['guides']
        before = json.dumps(document)
        for mapping in ledger['candidates']:
            if mapping['decision'] != 'wire_existing_source':
                continue
            assert mapping['sourceId'] in source_ids, 'New sources are forbidden'
            for guide in guides:
                if guide['slug'] == mapping['route']:
                    assert guide['entityId'] == mapping['entityId']
                    if mapping['sourceId'] not in guide['sourceIds']:
                        guide['sourceIds'].append(mapping['sourceId'])
        if json.dumps(document) != before:
            (ROOT / path).write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n')
            changed.append(path)
    history_path = ROOT / 'data/article-updates.json'
    history = json.loads(history_path.read_text())
    existing_ids = {entry['id'] for entry in history['entries']}
    new_events = [event for event in ledger['historyEvents'] if event['id'] not in existing_ids]
    if new_events:
        history['entries'] = new_events + history['entries']
        history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n')
        changed.append('data/article-updates.json')
    print(json.dumps({'changedFiles': changed, 'newSources': 0, 'newOutcomeRows': 0}))


if __name__ == '__main__':
    apply()
