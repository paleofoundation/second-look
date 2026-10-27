"""Add located trial findings without collapsing distinct outcome scopes.

This is a legacy app projection tool, not the RRX batch accept/apply workflow.
It never updates an existing finding's prose or removes an alias row implicitly.
Use --export-identities for a read-only identity audit (no app writes).
"""
from pathlib import Path
import argparse
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
IDENTITY_VERSION = 'remaprx-synthesis-identity/1.0'
DIMENSIONS = ('drugId', 'conditionId', 'population', 'comparison', 'endpoint', 'formulation', 'route', 'timepoint')


def read(name):
    return json.loads((ROOT / name).read_text())


def save(name, value):
    target = ROOT / name
    encoded = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if not target.exists() or target.read_text() != encoded:
        target.write_text(encoded)


def unique(values):
    return list(dict.fromkeys(values))


def clean(value):
    value = str(value)
    value = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', value)
    value = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', value)
    value = re.sub(r'([,;])(?=\S)', r'\1 ', value)
    return value.replace('CI−', 'CI −').replace('CI–', 'CI –').replace('group−', 'group −').replace('difference−', 'difference −').replace('group~', 'group ~')


def canonical_source(source_id, aliases):
    seen = set()
    while source_id in aliases:
        if source_id in seen:
            raise ValueError('Source alias cycle: ' + source_id)
        seen.add(source_id)
        source_id = aliases[source_id]
    return source_id


def exact_scope(record, aliases=None):
    """Null is unknown, never a wildcard or an inferred route/formulation."""
    aliases = aliases or {}
    result = {}
    for key in DIMENSIONS:
        value = record.get(key)
        if value is not None and not isinstance(value, str):
            raise ValueError('Synthesis scope field must be text or null: ' + key)
        result[key] = value.strip() or None if isinstance(value, str) else None
    ids = record.get('sourceIds') or [record.get('sourceId')]
    if not ids or any(not isinstance(value, str) or not value for value in ids):
        raise ValueError('Synthesis scope requires explicit source identities.')
    result['sourceIds'] = sorted({canonical_source(value, aliases) for value in ids})
    return result


def scope_hash(scope):
    return hashlib.sha256(json.dumps(scope, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def remember_identity(mapping, row, registry, aliases):
    scope = exact_scope(row, aliases)
    digest = scope_hash(scope)
    same = [entry for entry in mapping['entries'] if entry['scopeSha256'] == digest]
    if any(entry['synthesisId'] != row['id'] or entry['scope'] != scope for entry in same):
        raise ValueError('Ambiguous synthesis scope: ' + row['id'])
    if any(entry['synthesisId'] == row['id'] and entry['scopeSha256'] != digest for entry in mapping['entries']):
        raise ValueError('Existing synthesis ID has changed scope: ' + row['id'])
    if not same:
        mapping['entries'].append({
            'scopeSha256': digest, 'scope': scope, 'synthesisId': row['id'],
            'outcomeId': registry.get('rowOutcomeMap', {}).get(row['id']),
            'resultIds': row.get('resultIds', []), 'answerRoutes': row.get('answerRoutes', []),
            'identityDisposition': 'preserved_exact_scope',
        })
        mapping['entries'].sort(key=lambda entry: entry['synthesisId'])


def build_identity_map(rows, registry, aliases=None):
    mapping = {'schemaVersion': IDENTITY_VERSION, 'entries': [], 'rowAliases': {}}
    for row in rows:
        remember_identity(mapping, row, registry, aliases or {})
    return mapping


def load_identity_map(root, rows, registry, aliases):
    target = root / 'editorial/synthesis-identity-map.json'
    if not target.exists():
        return build_identity_map(rows, registry, aliases)
    mapping = json.loads(target.read_text())
    if mapping.get('schemaVersion') != IDENTITY_VERSION:
        raise ValueError('Unsupported synthesis identity-map version.')
    for entry in mapping.get('entries', []):
        if scope_hash(entry['scope']) != entry['scopeSha256']:
            raise ValueError('Invalid synthesis identity scope hash.')
    for row in rows:
        remember_identity(mapping, row, registry, aliases)
    return mapping


def resolve_synthesis_identity(fact, rows, aliases=None, mapping=None):
    """Preserve an established exact scope; mint a scope-derived ID only for a new scope."""
    aliases = aliases or {}
    scope = exact_scope(fact, aliases)
    digest = scope_hash(scope)
    matches = [row for row in rows if exact_scope(row, aliases) == scope]
    if len(matches) > 1:
        raise ValueError('Ambiguous existing exact-scope rows: ' + ', '.join(row['id'] for row in matches))
    entries = [entry for entry in (mapping or {}).get('entries', []) if entry['scopeSha256'] == digest]
    if any(entry['scope'] != scope for entry in entries) or len({entry['synthesisId'] for entry in entries}) > 1:
        raise ValueError('Ambiguous or corrupt explicit synthesis identity mapping.')
    if matches:
        if entries and entries[0]['synthesisId'] != matches[0]['id']:
            raise ValueError('Explicit mapping conflicts with existing synthesis ID.')
        return matches[0]['id']
    if entries:
        raise ValueError('Mapped synthesis is absent from current records; reconcile before reimport.')
    # Partially described legacy scopes must be resolved explicitly, not overwritten
    # or silently multiplied when an incoming packet fills an unknown dimension.
    for row in rows:
        prior = exact_scope(row, aliases)
        if prior['sourceIds'] != scope['sourceIds']:
            continue
        if all(prior[key] == scope[key] or prior[key] is None or scope[key] is None for key in DIMENSIONS):
            raise ValueError('Ambiguous incomplete scope overlaps existing synthesis ' + row['id'])
    if not scope['drugId'] or not scope['conditionId'] or not scope['endpoint']:
        raise ValueError('A new synthesis requires drug, condition and exact endpoint.')
    source_label = re.sub('[^A-Z0-9-]', '', '-'.join(scope['sourceIds']).upper())[:64]
    synthesis_id = 'SYN-' + scope['drugId'] + '-' + scope['conditionId'] + '-' + source_label + '-' + digest[:20].upper()
    if any(row['id'] == synthesis_id for row in rows):
        raise ValueError('Synthesis ID collision; do not overwrite existing record.')
    return synthesis_id


def apply_batches(filenames):
    raw=read('data/content.json');pub=read('data/public-content.json');reader=read('data/reader-evidence.json');view=read('data/public-reader-evidence.json');registry=read('data/outcome-registry.json');scope=read('editorial/parent-guide-scopes.json');source={s['id']:s for s in raw['sources']};aliases=read('editorial/reader-source-aliases.json');new=[]
    identity_map=load_identity_map(ROOT, reader['synthesisRows'], registry, aliases)
    def resolved(id):return canonical_source(id,aliases)
    for filename in filenames:
     batch=json.loads(Path(filename).read_text())
     for fact in batch.get('evidenceRecords',[]):
      sid=resolved(fact['sourceId']);src=source[sid];did=fact['drugId'];cid=fact['conditionId']
      val={k:clean(fact.get(k,'')) for k in ['population','comparison','endpoint','timepoint','finding','magnitude','limits']}
      normalized={**fact, **val, 'sourceId':sid}
      rid=resolve_synthesis_identity(normalized, reader['synthesisRows'], aliases, identity_map)
      existing=next((r for r in reader['synthesisRows'] if r['id']==rid), None)
      oid=registry['rowOutcomeMap'].get(rid) or 'OUT-'+rid.removeprefix('SYN-');fid=src.get('familyId') or 'STUDY-'+sid
      limits=val['limits'];finding=val['finding'];ss=[sid]
      if not finding.endswith('.'):finding+='.'
      row=dict(id=rid,version='reader-correction-2026-10-11',drugId=did,conditionId=cid,title=val['endpoint'],use=val['comparison'],population=val['population'],comparison=val['comparison'],endpoint=val['endpoint'],timepoint=val['timepoint'],status='reported_result',finding=dict(text=finding,sources=ss),magnitudeText=val['magnitude'],certainty=dict(label='Not appraised',rationale=''),evidenceBase=src['design'],limitations=[dict(text=limits,sources=ss)],sourceIds=ss,resultIds=[rid+'-R1'],studyFamilyIds=[fid],countsAsPrimaryEvidence=True,answerRoutes=[],coverage=dict(complete=False,pending=[]),effects=[dict(sourceId=sid,design=src['design'],population=val['population'],timepoint=val['timepoint'],sampleDescription=('Reported sample: '+str(fact['N'])) if fact.get('N') else val['population'],locators=src.get('locators',[]))],sourceLocators=[dict(sourceId=sid,label=l.get('section','Study results')) for l in src.get('locators',[])],publicationState='private_ai_draft',humanApproval='pending')
      for dimension in ['route','formulation']:
       if dimension in fact:row[dimension]=fact[dimension]
      # Preserve unrelated existing fields and protected integrity status. Do not silently
      # rewrite the same scope or its prose: substantive replacement needs a separately
      # reviewed candidate under the current ingest contract.
      if existing:
       fields=['endpoint','population','comparison','timepoint','finding','magnitudeText','limitations','effects']
       if any(existing.get(key) != row.get(key) for key in fields):
        raise ValueError('Existing synthesis '+rid+' differs: use the reviewed candidate importer for content changes.')
       new.append(rid)
       continue
      for target in [reader,view]:
       target['synthesisRows']=[r for r in target['synthesisRows'] if r['id']!=rid];target['synthesisRows'].append({k:v for k,v in row.items() if target is reader or k not in ['publicationState','humanApproval']})
      for target in [raw,pub]:
       for g in target['guides']:
        if g.get('entityId') in [did,cid]:g['synthesisIds']=unique(g.get('synthesisIds',[])+[rid]);g['sourceIds']=unique(g['sourceIds']+ss)
      def field(v):return dict(value=v,status='reported' if v else 'not_reported',reason=None,sources=ss if v else [])
      outcome=dict(id=oid,label=val['endpoint'],aliases=[val['endpoint']],definition=dict(text=val['endpoint']+' in '+val['population']+'.',sources=ss),registryState='source_defined',instrument=field(val['endpoint']),endpointHierarchy=field(None),clinicalOrSurrogateRole=field(None),measuredDirection=field(finding),favorableScaleDirection=field(None),meaningfulChange=field(None),clinicalInterpretation=field(None))
      registry['outcomes']=[o for o in registry['outcomes'] if o['id']!=oid]+[outcome];registry['rowOutcomeMap'][rid]=oid;new.append(rid)
      remember_identity(identity_map, row, registry, aliases)
    # Retirement and source-alias merges require a separately reviewed candidate.
    # Importing a new outcome never removes unrelated canonical/editorial records.
    for p in scope['parents']:
     g=next((g for g in raw['guides'] if g['id']==p['guideId']),None)
     if g:p['guide']=g
    for n,v in [('data/content.json',raw),('data/public-content.json',pub),('data/reader-evidence.json',reader),('data/public-reader-evidence.json',view),('data/outcome-registry.json',registry),('editorial/parent-guide-scopes.json',scope)]:save(n,v)
    save('editorial/synthesis-identity-map.json',identity_map)
    print(json.dumps(dict(addedOrPreserved=len(new),retiredSecondaryRows=0,sharedOutcomes=len(reader['synthesisRows']))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('batches', nargs='*')
    parser.add_argument('--export-identities', type=Path, metavar='OUTPUT')
    args = parser.parse_args()
    if args.export_identities:
        if args.batches:
            parser.error('--export-identities cannot be combined with imports.')
        output = args.export_identities.resolve()
        for directory in ('data', 'public', 'dist', 'editorial'):
            if output.is_relative_to(ROOT / directory):
                parser.error('Identity audit output must be outside canonical/public/editorial data.')
        mapping = load_identity_map(ROOT, read('data/reader-evidence.json')['synthesisRows'], read('data/outcome-registry.json'), read('editorial/reader-source-aliases.json'))
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'output': str(output), 'preservedSynthesisIds': len(mapping['entries'])}))
    elif not args.batches:
        parser.error('Provide a batch or --export-identities OUTPUT; an empty run never mutates the app.')
    else:
        apply_batches(args.batches)


if __name__ == '__main__':
    main()
