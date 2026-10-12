#!/usr/bin/env python3
"""Package an already approved gap request locally; no transmission/acquisition."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.research_ingest.cli import check_inputs, check_readiness, load, require, safe_path, sha


def package(plan_path, readiness_path, output):
    plan_path, readiness_path = Path(plan_path).resolve(), Path(readiness_path).resolve()
    output = Path(output).absolute()
    require(not output.is_symlink(), 'Output cannot be a symlink')
    require(output.suffix == '.zip', 'Output must be a ZIP')
    require(not output.exists(), 'Output exists; preserve prior deliveries and use a new destination')
    # Delivery files stay in ignored private work. Raw full texts are not inputs.
    work = safe_path(ROOT, 'work/research-ingest').resolve()
    require(output.resolve().is_relative_to(work), 'Use a private work/research-ingest output directory')
    plan = load(plan_path)
    require(plan.get('schemaVersion') == 'remaprx-gap-acquisition-plan-v1', 'Wrong plan kind')
    check_readiness(readiness_path, plan, sha(plan_path))
    pins = check_inputs(ROOT, plan)
    paths = [safe_path(ROOT, name) for name in pins]
    paths += [plan_path, readiness_path, plan_path.parent / 'gp-review.json']
    entries = {}
    for path in sorted(set(paths)):
        require(path.is_relative_to(ROOT), 'Input is outside the repository')
        name = path.relative_to(ROOT).as_posix()
        data = path.read_bytes()
        require(path.suffix.lower() in {'.json', '.jsonl', '.md', '.txt', '.py', '.mjs'}, 'Only request metadata/code is deliverable')
        entries[name] = data
    manifest = [{'path': name, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)} for name, data in entries.items()]
    folder = plan_path.parent.relative_to(ROOT).as_posix()
    entries['START-HERE.txt'] = (f'RemapRx {plan["planId"]}\nOpen {folder}/REQUEST.txt and plan.json in that same folder.\n'
        'All plan input paths resolve from this archive root. Read readiness and gp-review before acquisition.\n'
        'This attachment contains only request metadata and code, not a received research collection.\n'
        'The owner must attach this ZIP and paste the request into Grok manually; no transfer is performed.\n').encode()
    entries['DELIVERY-MANIFEST.json'] = (json.dumps({'planId': plan['planId'], 'planSha256': sha(plan_path),
        'files': manifest, 'scope': 'Prepared metadata request only; not dispatched', 'rawPapers': 0}, indent=2) + '\n').encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    with zipfile.ZipFile(output) as archive:
        require(set(archive.namelist()) == set(entries), 'Delivery member count differs')
        require(all(archive.read(name) == data for name, data in entries.items()), 'Delivery bytes differ')
    check_inputs(ROOT, plan)
    require(all(sha(safe_path(ROOT, item['path'])) == item['sha256'] for item in manifest), 'Delivery controls changed while packaging')
    require(sha(plan_path) == next(x['sha256'] for x in manifest if x['path'] == plan_path.relative_to(ROOT).as_posix()), 'Plan changed while packaging')
    result = {'status': 'PREPARED_NOT_DISPATCHED', 'planId': plan['planId'], 'planSha256': sha(plan_path),
              'path': str(output), 'sha256': sha(output), 'bytes': output.stat().st_size,
              'files': len(entries), 'verifiedReadableLocally': True, 'receiverAccessVerified': False,
              'rawPapers': 0, 'performedAcquisition': False}
    output.with_suffix('.zip.receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True)
    parser.add_argument('--readiness', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    print(json.dumps(package(args.plan, args.readiness, args.out), indent=2))
