"""Deterministic editorial parent projection; never extracts or alters source/results."""
from copy import deepcopy
from pathlib import Path
import argparse
import json

DEFAULT_SCOPE = Path(__file__).resolve().parents[1] / 'editorial/parent-guide-scopes.json'


def read_scope(path=DEFAULT_SCOPE):
    return json.loads(Path(path).read_text())


def apply_parent_scopes(content, scope=None):
    """Apply maintained parent composition after a legacy seed/projection.

    Additional sources or FAQ additions require deliberate scope reconciliation,
    rather than being erased by a stale editorial configuration.
    """
    scope = scope or read_scope()
    output = deepcopy(content)
    source_ids = {s['id'] for s in output['sources']}
    for parent in scope['parents']:
        desired = parent['guide']
        existing = next((g for g in output['guides'] if g['id'] == parent['guideId']), None)
        if existing is None:
            continue
        if existing['slug'] != parent['route'] or desired['slug'] != parent['route']:
            raise ValueError('Parent route/identity conflict: ' + parent['guideId'])
        missing = set(desired['sourceIds']) - source_ids
        if missing:
            raise ValueError('Historical input lacks parent sources; use the current accepted projection: ' + ', '.join(sorted(missing)))
        if set(existing['sourceIds']) - set(desired['sourceIds']):
            raise ValueError('New parent sources require explicit scope reconciliation: ' + parent['guideId'])
        if len(existing.get('faqs', [])) > len(desired['faqs']):
            raise ValueError('New parent questions require explicit scope reconciliation: ' + parent['guideId'])
        # Only fields explicitly maintained in the versioned editorial config.
        existing.update(deepcopy(desired))
    assert output['sources'] == content['sources']
    return output


def apply_reader_metadata(reader, scope=None):
    """Correct D01 metadata in future reader-view generation, leaving rows intact."""
    output = deepcopy(reader)
    for parent in (scope or read_scope())['parents']:
        entity = next((e for e in output.get('entities', []) if e['id'] == parent['entityId']), None)
        if entity is None:
            continue
        guide = parent['guide']
        overview = next(s for s in guide['sections'] if s['id'] == 'overview')
        entity.update(coverageLabel=guide['coverageLabel'], scope=guide['scope'],
                      overview={k:deepcopy(overview[k]) for k in ('paragraph', 'sentences')},
                      conditionIds=[c['conditionId'] for c in parent['conditionCoverage']],
                      topicIds=list(guide['topicIds']), parentScopeVersion=(scope or read_scope())['version'])
    assert output.get('synthesisRows') == reader.get('synthesisRows')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--scope', default=DEFAULT_SCOPE, type=Path)
    parser.add_argument('--reader-metadata', action='store_true')
    args = parser.parse_args()
    transform = apply_reader_metadata if args.reader_metadata else apply_parent_scopes
    result = transform(json.loads(args.input.read_text()), read_scope(args.scope))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
