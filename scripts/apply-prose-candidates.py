"""Apply reviewed prose fields by stable IDs; preserve scientific records and questions."""
import argparse
import copy
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument('--kind', choices=['Drug', 'Condition'], required=True)
parser.add_argument('--report', required=True)
parser.add_argument('--audit')
parser.add_argument('--draft-base')
parser.add_argument('files', nargs='+')
args = parser.parse_args()
paths = [ROOT / name for name in ['data/content.json', 'data/public-content.json', 'data/discovery-pages.json', 'editorial/parent-guide-scopes.json', 'data/public-mechanisms.json']]
data = [json.loads(path.read_text()) for path in paths]
internal, public, discovery, scopes, mechanisms = data
public_guides = public['guides'] + [g for g in discovery if not any(c['id'] == g['id'] or c['slug'] == g['slug'] for c in public['guides'])]
by_id = {g['id']: g for g in public_guides}
all_sources = {s['id'] for s in public['sources']}
report = {'kind': args.kind, 'sections': [], 'mechanisms': [], 'skippedCompliant': [], 'sourceGaps': []}
report['skippedChangedSinceDraft'] = []
needed = None
if args.audit:
    needed = {(item['guideId'], item['sectionId']) for item in json.loads((ROOT / args.audit).read_text())['failures']}
base_guides = {}
if args.draft_base:
    for file in ['data/public-content.json', 'data/discovery-pages.json']:
        old = json.loads(subprocess.check_output(['git', 'show', f'{args.draft_base}:{file}'], cwd=ROOT))
        base_guides.update({guide['id']: guide for guide in old['guides'] if isinstance(old, dict)} if isinstance(old, dict) else {guide['id']: guide for guide in old})
replacements = {}
new_labels = {'contraindications': 'Contraindications', 'interactions': 'Interactions', 'quality': 'Quality', 'status': 'Status', 'safety': 'Safety', 'dosing': 'Dosing', 'evidence': 'Evidence'}


def normalized(value):
    return ' '.join(value.split())


def validate(prose, source_key, guide, prefix=''):
    text = normalized(prose.get('paragraph', prose.get('text', '')))
    counted = normalized(prefix + ' ' + text)
    assert len(counted.split()) >= 113 and len(counted) >= 845, (guide['id'], len(counted.split()), len(counted))
    assert text == normalized(' '.join(sentence['text'] for sentence in prose['sentences'])), guide['id']
    ids = set(prose[source_key]) | {sid for sentence in prose['sentences'] for sid in sentence['sources']}
    assert ids and ids <= all_sources, (guide['id'], ids - all_sources)
    assert ids <= set(guide['sourceIds']), (guide['id'], 'source outside existing page', ids - set(guide['sourceIds']))
    inherited_notices = {sentence['text'] for section in guide['sections'] for sentence in section.get('sentences', []) if not sentence['sources']}
    assert all(sentence['sources'] or sentence['text'] in inherited_notices for sentence in prose['sentences']), (guide['id'], 'new uncited candidate sentence')
    assert '\u2014' not in text and '\u2013' not in text, (guide['id'], 'dash')


for file in args.files:
    candidate = json.loads((ROOT / file).read_text())
    report['sourceGaps'].extend(candidate.get('gaps', []))
    for entry in candidate.get('guides', []):
        guide = by_id[entry['guideId']]
        if guide['type'] != args.kind:
            continue
        if args.draft_base and set(guide['sourceIds']) != set(base_guides.get(guide['id'], {}).get('sourceIds', [])):
            report['skippedChangedSinceDraft'].append({'guideId': guide['id'], 'reason': 'Page source identities changed; requires current-source review'})
            continue
        for section in entry['sections']:
            if needed is not None and (guide['id'], section['id']) not in needed:
                continue
            original = next((s for s in guide['sections'] if s['id'] == section['id']), None)
            baseline = next((s for s in base_guides.get(guide['id'], {}).get('sections', []) if s['id'] == section['id']), None)
            if args.draft_base and original and baseline and original.get('paragraph') != baseline.get('paragraph'):
                report['skippedChangedSinceDraft'].append({'guideId': guide['id'], 'sectionId': section['id']})
                continue
            if original and len(normalized(original.get('paragraph', '')).split()) >= 113 and len(normalized(original.get('paragraph', ''))) >= 845:
                report['skippedCompliant'].append({'guideId': guide['id'], 'sectionId': section['id']})
                continue
            validate(section, 'sources', guide)
            replacement = {key: copy.deepcopy(section[key]) for key in ['paragraph', 'sources', 'sentences']}
            if original is None:
                assert section['id'] in new_labels, (guide['id'], 'unrecognized new section')
                replacement.update(id=section['id'], label=new_labels[section['id']], title='', questions=[])
            replacements[(guide['id'], section['id'])] = replacement
    for record in candidate.get('mechanisms', []):
        key = 'conditionId' if record.get('conditionId') else 'drugId'
        guide = next((g for g in public_guides if g['type'] == args.kind and g.get('entityId') == record.get(key)), None)
        if not guide:
            continue
        if args.draft_base and set(guide['sourceIds']) != set(base_guides.get(guide['id'], {}).get('sourceIds', [])):
            continue
        if needed is not None and (guide['id'], 'mechanisms') not in needed:
            continue
        existing = next((item for item in mechanisms['drugs'] if item.get(key) == record[key]), None)
        assert existing is not None, (guide['id'], 'mechanism identity missing')
        validate(record['summary'], 'sourceIds', guide, existing.get('originalAction', {}).get('text', ''))
        current = normalized(' '.join(existing.get(field, {}).get('text', '') for field in ['originalAction', 'summary']))
        if len(current.split()) >= 113 and len(current) >= 845:
            report['skippedCompliant'].append({'guideId': guide['id'], 'sectionId': 'mechanisms'})
            continue
        existing['summary'] = copy.deepcopy(record['summary'])
        report['mechanisms'].append({'guideId': guide['id'], key: record[key]})

collections = [internal['guides'], public['guides'], discovery, [parent['guide'] for parent in scopes['parents']]]
for collection in collections:
    for guide in collection:
        for (identity, section_id), replacement in replacements.items():
            if identity != guide['id']:
                continue
            original = next((s for s in guide['sections'] if s['id'] == section_id), None)
            if original is None:
                guide['sections'].append(copy.deepcopy(replacement))
            else:
                original.update(copy.deepcopy(replacement))
for (guide_id, section_id) in replacements:
    report['sections'].append({'guideId': guide_id, 'sectionId': section_id})
for path, value in zip(paths, data):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
(ROOT / args.report).write_text(json.dumps(report, indent=2) + '\n')
print(f"Applied {len(report['sections'])} {args.kind} sections and {len(report['mechanisms'])} mechanism summaries; {len(report['skippedCompliant'])} already-compliant fields preserved.")
