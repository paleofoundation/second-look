#!/usr/bin/env python3
"""Materialize one exact PASTIS DOCX, with no scientific reading or rendering."""
import argparse
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))
from scripts.research_ingest.cli import check_inputs, check_readiness, digest, load, require, sha

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--readiness', type=Path, required=True)
    args = parser.parse_args()
    plan_hash, gp_hash = sha(args.plan), sha(args.readiness)
    plan = load(args.plan)
    check_readiness(args.readiness, plan, plan_hash)
    inputs = check_inputs(ROOT, plan)
    require(plan['operations'] == ['materialize-docx', 'prepare-reading-representation'], 'Wrong preparation scope')
    require(inputs.get(Path(__file__).relative_to(ROOT).as_posix()) == sha(Path(__file__)), 'Unpinned executable')
    helper = HERE.parent / 'next-tranche-preflight/materialize_zip.py'
    require(inputs.get(helper.relative_to(ROOT).as_posix()) == sha(helper), 'Unpinned safe file helper')
    spec = importlib.util.spec_from_file_location('safe_materializer', helper)
    safe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(safe)
    inventory_path = ROOT / plan['archiveInventory']
    require(inputs.get(plan['archiveInventory']) == sha(inventory_path), 'Unpinned manifest')
    inventory = load(inventory_path)
    archive = Path(inventory['archive']['path'])
    safe.absolute_without_links(archive)
    data = archive.read_bytes()
    require(len(data) == inventory['archive']['bytes'] and digest(data) == inventory['archive']['sha256'], 'Archive bytes mismatch')
    require(len(inventory['members']) == 9 and sum(x['bytes'] for x in inventory['members']) < 10_000_000, 'Unbounded archive')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = [x.filename for x in z.infolist()]
        require(len(names) == len(set(n.casefold() for n in names)) == 9, 'Archive identity collision')
        require(set(names) == {x['name'] for x in inventory['members']}, 'Archive member-set mismatch')
        bodies = {}
        for m in inventory['members']:
            require('/' not in m['name'] and '\\' not in m['name'] and not m['name'].startswith('.'), 'Unsafe member name')
            info = z.getinfo(m['name'])
            require(not info.flag_bits & 1 and info.compress_type in (0, 8) and not info.is_dir(), 'Unsupported entry')
            require(info.external_attr >> 16 in (0, 0o100644, 0o100600), 'Nonregular entry')
            require(info.file_size == m['bytes'] and info.compress_size == m['compressedBytes'] and info.file_size / max(1, info.compress_size) < 200, 'Size or compression mismatch')
            require(format(info.CRC, '08x') == m['crc32'], 'CRC mismatch')
            body = z.read(info)
            require(digest(body) == m['sha256'], 'Member hash mismatch')
            bodies[m['name']] = body
    body = bodies['ALZ-18-2393-s001.docx']
    with zipfile.ZipFile(io.BytesIO(body)) as doc:
        entries = doc.infolist()
        require(len(entries) <= 500 and sum(x.file_size for x in entries) < 20_000_000, 'Unbounded Word package')
        require(len(entries) == len(set(x.filename.casefold() for x in entries)), 'Duplicate Word part')
        require({'[Content_Types].xml', 'word/document.xml'} <= set(doc.namelist()), 'Invalid Word package')
        for part in entries:
            require(not part.flag_bits & 1 and part.compress_type in (0, 8) and part.file_size / max(1, part.compress_size) < 200, 'Unsupported Word part')
            require(not part.filename.startswith('/') and '..' not in Path(part.filename).parts and '\\' not in part.filename, 'Unsafe Word part')
            require(not any(x in part.filename.casefold() for x in ('vbaproject', 'activex', 'embeddings/')), 'Active or embedded object requires separate disposition')
            doc.read(part)  # CRC validation, never execution or scientific text extraction.
    output = Path(plan['privateOutputRoot'])
    relative = plan['destination']
    require(relative == 'CAL-08/ALZ-18-2393-s001.docx', 'Output outside exact member destination')
    safe.private_root(ROOT, output, [relative])
    require(sha(archive) == inventory['archive']['sha256'], 'Archive changed')
    check_inputs(ROOT, plan)
    fd = os.open(output, safe.DIRECTORY)
    lock = '.rrx-materialization.lock'
    locked = False
    try:
        lockfd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600, dir_fd=fd)
        with os.fdopen(lockfd, 'w') as h:
            h.write(json.dumps({'pid': os.getpid(), 'planSha256': plan_hash}))
        locked = True
        old = safe.existing_bytes(fd, relative)
        require(old is None or old == body, 'Occupied destination differs')
        if old is None:
            safe.install_exclusive(fd, relative, body)
        require(safe.existing_bytes(fd, relative) == body, 'Output changed')
        check_inputs(ROOT, plan)
        require(sha(args.plan) == plan_hash and sha(args.readiness) == gp_hash, 'Preparation controls changed')
        print(json.dumps({'status':'PASS', 'changedFiles': int(old is None), 'sourceId':'CAL08-supplement-original-docx', 'path':str(output / relative), 'sha256':digest(body), 'bytes':len(body), 'archiveSha256':inventory['archive']['sha256'], 'archiveMember':'ALZ-18-2393-s001.docx', 'planSha256':plan_hash, 'scientificInspectionPerformed':False, 'sourceReadinessGranted':False}))
    finally:
        if locked:
            os.unlink(lock, dir_fd=fd)
        os.close(fd)

if __name__ == '__main__':
    main()
