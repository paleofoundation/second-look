#!/usr/bin/env python3
"""Fetch only a GP-ready exact request manifest, retaining honest media receipts."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('root', 'plan', 'readiness', 'receipt'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    sys.path.insert(0, str(root))
    from scripts.research_ingest.cli import check_inputs, check_readiness, digest, load, require, safe_path, sha
    plan_path, gp_path = Path(args.plan), Path(args.readiness)
    plan_hash, gp_hash = sha(plan_path), sha(gp_path)
    plan = load(plan_path)
    check_readiness(gp_path, plan, plan_hash)
    check_inputs(root, plan)
    require(plan['status'] == 'READY_FOR_NARROW_ACQUISITION', 'Acquisition plan is not active')
    require(any(x['path'] == Path(__file__).resolve().relative_to(root).as_posix() and x['sha256'] == sha(Path(__file__))
                for x in plan['inputs']), 'Fetch implementation must be pinned')
    base = Path(plan['rawDestination']).resolve()
    require(not base.is_relative_to(root), 'Raw sources must be outside application Git/public')
    require(base.is_relative_to(root.parent / 'private-research'), 'Use the declared external private research root')
    receipt = safe_path(root, args.receipt)
    require(not receipt.exists(), 'Preserve prior acquisition receipts')
    require(len({r['filename'] for r in plan['requests']}) == len(plan['requests']), 'Duplicate receipt destination')
    base.mkdir(parents=True, exist_ok=True)

    def fetch(request):
        row = {**request, 'retrievedAt': datetime.now(timezone.utc).isoformat(), 'planSha256': plan_hash}
        temporary = None
        try:
            require(request['url'].startswith('https://'), 'Only declared public HTTPS requests are supported')
            output = safe_path(base, request['filename'])
            require(not output.exists(), 'Existing source must not be overwritten')
            output.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=base, delete=False) as handle:
                temporary = Path(handle.name)
            result = subprocess.run(['curl', '-sS', '-L', '--proto', '=https', '--proto-redir', '=https',
                '--max-time', '45', '--max-filesize', '30000000', '-o', str(temporary), '-w', '%{json}', request['url']],
                capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(result.stderr.strip())
            metadata = json.loads(result.stdout)
            data = temporary.read_bytes()
            media = request['mediaType']
            valid = metadata['http_code'] == 200 and metadata['ssl_verify_result'] == 0
            if media == 'application/json':
                try:
                    json.loads(data)
                except (ValueError, UnicodeError):
                    valid = False
            elif media == 'image/jpeg':
                valid = valid and data.startswith(b'\xff\xd8\xff')
            elif media.endswith('wordprocessingml.document'):
                try:
                    with zipfile.ZipFile(io.BytesIO(data)) as archive:
                        valid = valid and {'[Content_Types].xml', 'word/document.xml'} <= set(archive.namelist())
                except zipfile.BadZipFile:
                    valid = False
            elif media == 'application/pdf':
                valid = valid and data.startswith(b'%PDF-')
            elif media == 'application/xml':
                valid = valid and data.lstrip().startswith((b'<?xml', b'<OA'))
            else:
                raise ValueError('Uncontracted expected media type: ' + media)
            if not valid:
                output = output.with_name(output.name + '.failed-download')
            require(not output.exists(), 'Preserve existing failed-source diagnostics')
            with output.open('xb') as handle:
                handle.write(data)
            row.update(status='RECEIVED' if valid else 'ACCESS_OR_MEDIA_HOLD', path=str(output),
                bytes=len(data), sha256=digest(data), finalUrl=metadata['url_effective'],
                httpStatus=metadata['http_code'], contentType=metadata.get('content_type'),
                tlsVerifyResult=metadata['ssl_verify_result'], scientificBodyInspected=False)
        except Exception as error:
            row.update(status='FAILED', error=str(error), scientificBodyInspected=False)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        return row

    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(fetch, plan['requests']))
    unchanged = sha(plan_path) == plan_hash and sha(gp_path) == gp_hash
    try:
        check_inputs(root, plan)
    except Exception:
        unchanged = False
    value = {'schemaVersion': 'remaprx-narrow-acquisition-receipt-v1', 'planId': plan['planId'],
        'planSha256': plan_hash, 'controlHashesUnchanged': unchanged,
        'status': 'RECEIPT_REQUIRES_IDENTITY_RECONCILIATION' if unchanged else 'HOLD_CONTROL_CHANGED',
        'requests': rows, 'sourceExtractionPerformed': False, 'performedImport': False}
    receipt.parent.mkdir(parents=True, exist_ok=True)
    with receipt.open('x') as handle:
        json.dump(value, handle, indent=2)
        handle.write('\n')
    print(json.dumps({'status': value['status'], 'requests': len(rows),
        'received': sum(r['status'] == 'RECEIVED' for r in rows), 'receipt': str(receipt)}))


if __name__ == '__main__':
    main()
