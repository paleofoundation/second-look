#!/usr/bin/env python3
"""GP-gated PDF-only archive materialization. Never performs scientific reading."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import uuid
import zipfile

HERE = Path(__file__).resolve().parent
APP = HERE.parents[5]
sys.path.insert(0, str(APP))
from scripts.research_ingest.cli import (Hold, canonical, check_inputs, check_readiness,
    digest, load, pinned_load, require, safe_path, sha)

spec = importlib.util.spec_from_file_location('zip_metadata_inventory', HERE / 'inventory.py')
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)
SCHEMA = HERE / 'materialization-plan.schema.json'
NOFOLLOW = os.O_NOFOLLOW
DIRECTORY = os.O_RDONLY | os.O_DIRECTORY | NOFOLLOW


def unchanged(pins):
    for path, checksum in pins.items():
        require(Path(path).is_file() and not Path(path).is_symlink() and sha(path) == checksum,
                'Control or archive changed: ' + path)


def absolute_without_links(path):
    path = Path(path)
    require(path.is_absolute() and str(path) == str(path.resolve()), 'Root must be absolute, canonical and symlink-free')
    for ancestor in [path, *path.parents]:
        require(not ancestor.is_symlink(), 'Symlink ancestor is forbidden')
    return path


def private_root(app, output, destinations):
    """Require an ignored raw root when an enclosing Git checkout exists."""
    absolute_without_links(output)
    require(not output.is_relative_to(app) and not app.is_relative_to(output),
            'Raw output must be outside and must not contain the application repository')
    require(not {'.git', 'public', 'dist'} & {p.casefold() for p in output.parts}, 'Public/build/Git destination forbidden')
    nearest = output
    while not nearest.exists():
        nearest = nearest.parent
    found = subprocess.run(['git', '-C', str(nearest), 'rev-parse', '--show-toplevel'], capture_output=True, text=True)
    if found.returncode:
        require(found.returncode == 128 and 'not a git repository' in found.stderr.lower(),
                'Could not establish enclosing Git boundary')
        return {'outsideApplication': True, 'enclosingGitRoot': None, 'ignored': None, 'trackedFiles': 0}
    git_root = Path(found.stdout.strip()).resolve()
    relative = output.relative_to(git_root).as_posix()
    tracked = subprocess.run(['git', '--literal-pathspecs', '-C', str(git_root), 'ls-files', '-z', '--', relative], capture_output=True)
    require(tracked.returncode == 0 and not tracked.stdout, 'Raw output root contains Git-tracked paths')
    for name in ['.rrx-materialization.lock', *destinations]:
        ignored = subprocess.run(['git', '-C', str(git_root), 'check-ignore', '--quiet', '--no-index', '--',
                                  relative + '/' + name], capture_output=True)
        require(ignored.returncode == 0, 'Raw output must be ignored by enclosing Git: ' + name)
    return {'outsideApplication': True, 'enclosingGitRoot': str(git_root), 'ignored': True, 'trackedFiles': 0}


def directory_fd(base, parts, create=False):
    """Walk only directories without following links, including during races."""
    fd = os.dup(base)
    try:
        for part in parts:
            if create:
                try:
                    os.mkdir(part, 0o700, dir_fd=fd)
                except FileExistsError:
                    pass
            next_fd = os.open(part, DIRECTORY, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        return fd
    except BaseException:
        os.close(fd)
        raise


def existing_bytes(base, relative):
    parts = relative.split('/')
    try:
        parent = directory_fd(base, parts[:-1])
    except FileNotFoundError:
        return None
    try:
        try:
            fd = os.open(parts[-1], os.O_RDONLY | os.O_NONBLOCK | NOFOLLOW, dir_fd=parent)
        except FileNotFoundError:
            return None
        with os.fdopen(fd, 'rb') as source:
            meta = os.fstat(source.fileno())
            require(stat.S_ISREG(meta.st_mode) and meta.st_nlink == 1, 'Destination must be a regular unlinked file')
            require(meta.st_size <= inventory.MAX_MEMBER_BYTES, 'Existing destination exceeds bounded size')
            return source.read(inventory.MAX_MEMBER_BYTES + 1)
    finally:
        os.close(parent)


def install_exclusive(base, relative, body):
    """Atomic no-clobber publication; no replace/rename of an existing file."""
    parts = relative.split('/')
    parent = directory_fd(base, parts[:-1], create=True)
    temporary = '.rrx-member-' + uuid.uuid4().hex
    try:
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | NOFOLLOW, 0o600, dir_fd=parent)
        with os.fdopen(fd, 'wb') as output:
            output.write(body)
            output.flush()
            os.fsync(output.fileno())
        try:
            os.link(temporary, parts[-1], src_dir_fd=parent, dst_dir_fd=parent, follow_symlinks=False)
        except FileExistsError:
            # A new external writer is not treated as an authorized repeat.
            raise Hold('Destination appeared during installation: ' + relative)
        os.unlink(temporary, dir_fd=parent)
        os.fsync(parent)
    finally:
        try:
            os.unlink(temporary, dir_fd=parent)
        except FileNotFoundError:
            pass
        os.close(parent)


def materialize(root, plan_path, readiness_path, manifest_path, archive_path, out_root):
    root = Path(root).resolve()
    require(root == APP, 'Use the application root containing this executable')
    controls = {}
    plan_path, readiness_path, manifest_path = map(Path, (plan_path, readiness_path, manifest_path))
    plan = pinned_load(plan_path, controls)
    try:
        from jsonschema import Draft202012Validator
    except ImportError as error:
        raise Hold('Install scripts/research_ingest/requirements.txt') from error
    schema = pinned_load(SCHEMA, controls)
    errors = list(Draft202012Validator(schema).iter_errors(plan))
    require(not errors, 'Materialization plan schema: ' + '; '.join(e.message for e in errors[:5]))
    plan_hash = controls[str(plan_path.resolve())]
    check_readiness(readiness_path, plan, plan_hash, controls)
    inputs = check_inputs(root, plan)
    for relative, checksum in inputs.items():
        absolute = str(safe_path(root, relative).resolve())
        require(controls.get(absolute, checksum) == checksum, 'Loaded control differs from its approved input pin')
        controls[absolute] = checksum
    required = [Path(__file__).resolve(), HERE / 'inventory.py', SCHEMA,
                HERE / 'ZIP-MEMBER-CONTRACT-DRAFT.md', HERE / 'test_materialize_zip.py',
                root / 'scripts/research_ingest/cli.py', root / 'scripts/research_ingest/contracts.py',
                root / 'AGENTS.md', root / 'docs/PROJECT-RULES.md', root / 'docs/RULE-CHANGELOG.md',
                root / 'docs/RESEARCH-INGEST.md', manifest_path.resolve()]
    for path in required:
        require(path.is_relative_to(root) and path.relative_to(root).as_posix() in inputs,
                'Required control absent from plan inputs: ' + str(path))
    require(safe_path(root, plan['manifestPath']).resolve() == manifest_path.resolve(), 'Manifest path mismatch')
    manifest = pinned_load(manifest_path, controls, inputs[plan['manifestPath']])
    require(manifest.get('schemaVersion') == 'remaprx-prospective-archive-members-v1', 'Wrong archive manifest version')
    rows = manifest.get('members')
    require(isinstance(rows, list) and rows, 'Expected nonempty archive manifest')
    archive_path = absolute_without_links(archive_path)
    require(archive_path.is_file() and archive_path.stat().st_size == plan['archive']['bytes'], 'Whole archive byte count mismatch')
    data = archive_path.read_bytes()
    require(len(data) == plan['archive']['bytes'] and digest(data) == plan['archive']['sha256'], 'Whole archive hash mismatch')
    controls[str(archive_path)] = digest(data)
    observed = inventory.archive_inventory(data)
    # Equality includes every filename, CRC, physical page count and member hash.
    expected, names, source_ids, destinations = [], set(), set(), []
    output = absolute_without_links(out_root)
    require(str(output) == plan['privateOutputRoot'], 'Output root differs from approved root')
    for row in rows:
        member = row['member']
        name = inventory.member_name(member['path'])
        source_id = row['sourceId']
        require(isinstance(source_id, str) and source_id.strip() == source_id and source_id, 'Invalid source identity')
        require(name.casefold() not in names and source_id.casefold() not in source_ids, 'Duplicate member or source identity')
        names.add(name.casefold()); source_ids.add(source_id.casefold())
        require(row['archiveSourceId'] == plan['archive']['sourceId'] and row['archiveSha256'] == digest(data)
                and row['canonicalReportId'] == plan['canonicalReportId'], 'Archive/report identity mismatch')
        destination = row['proposedMaterializationRelativePath']
        inventory.member_name(destination)
        require(destination == plan['memberDirectory'] + '/' + member['sha256'] + '.pdf', 'Destination must be the exact approved SHA-named PDF')
        safe_path(output, destination)
        require(destination.casefold() not in {d.casefold() for d in destinations}, 'Ambiguous destination identity')
        destinations.append(destination); expected.append(member)
        require(row['expectedUnits'] == [{'id': 'page-' + str(i), 'kind': 'pdf_page', 'locator': str(i)}
                                       for i in range(1, member['pages'] + 1)], 'Physical page-unit manifest mismatch')
    require(sorted(expected, key=lambda m: m['path']) == sorted(observed, key=lambda m: m['path']),
            'Complete archive member inventory differs from approved manifest')
    require(sorted(destinations) == sorted(plan['allowedDestinations']), 'Member destination allowlist mismatch')
    receipt_relative = plan['receiptRelativePath']
    inventory.member_name(receipt_relative)
    require(receipt_relative.endswith('.json') and receipt_relative.casefold() not in {d.casefold() for d in destinations}, 'Receipt path collision/type')
    safe_path(output, receipt_relative)
    output_names = [name.casefold() for name in destinations + [receipt_relative]]
    require(not any(a.startswith(b + '/') for a in output_names for b in output_names if a != b),
            'File/directory output collision')
    for destination in destinations + [receipt_relative]:
        require(not {'.git', 'public', 'dist'} & {p.casefold() for p in Path(destination).parts}, 'Public/build/Git destination forbidden')
    privacy = private_root(root, output, destinations + [receipt_relative])
    unchanged(controls)
    # Only now may the approved external directory be created.
    slash = os.open('/', DIRECTORY)
    try:
        output_fd = directory_fd(slash, output.parts[1:], create=True)
    finally:
        os.close(slash)
    locked = False
    changed = []
    lock_name = '.rrx-materialization.lock'
    lock_token = uuid.uuid4().hex
    try:
        try:
            lock_fd = os.open(lock_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | NOFOLLOW, 0o600, dir_fd=output_fd)
        except FileExistsError as error:
            raise Hold('Output root is locked; inspect a stale lock manually, never auto-clear it') from error
        locked = True
        with os.fdopen(lock_fd, 'wb') as lock:
            lock.write(canonical({'pid': os.getpid(), 'token': lock_token, 'planSha256': plan_hash}))
            lock.flush(); os.fsync(lock.fileno())
        unchanged(controls)
        privacy = private_root(root, output, destinations + [receipt_relative])
        actual = {d: existing_bytes(output_fd, d) for d in destinations}
        for row, destination in zip(rows, destinations):
            previous = actual[destination]
            require(previous is None or (digest(previous) == row['member']['sha256'] and len(previous) == row['member']['bytes']),
                    'Existing destination has different bytes: ' + destination)
        binding = {
            'schemaVersion': 'remaprx-zip-materialization-receipt-v1', 'status': 'PASS',
            'scope': 'private_archive_member_materialization_only', 'planId': plan['planId'], 'planSha256': plan_hash,
            'readinessSha256': controls[str(readiness_path.resolve())], 'manifestSha256': controls[str(manifest_path.resolve())],
            'archive': plan['archive'], 'canonicalReportId': plan['canonicalReportId'],
            'privateOutputRoot': str(output), 'preparer': plan['preparer'], 'inputHashes': inputs,
            'privacy': privacy, 'scientificInspectionPerformed': False, 'sourceReadinessGranted': False,
            'canonicalWrites': False, 'humanApproval': False, 'released': False,
        }
        prior_receipt = existing_bytes(output_fd, receipt_relative)
        if prior_receipt is not None:
            from scripts.research_ingest.cli import decode, timestamp
            receipt = decode(prior_receipt)
            require(set(receipt) == set(binding) | {'completedAt', 'members'}, 'Receipt fields differ from contract')
            require({k: receipt[k] for k in binding} == binding, 'Existing receipt binds different controls or scope')
            timestamp(receipt['completedAt'])
            require(all(actual[d] is not None for d in destinations), 'Receipt exists but materialized members are missing')
        else:
            receipt = dict(binding, completedAt=datetime.now(timezone.utc).isoformat(), members=[])
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = []
            for row, destination in zip(rows, destinations):
                if actual[destination] is None:
                    unchanged(controls)
                    private_root(root, output, destinations + [receipt_relative])
                    body = archive.read(row['member']['path'])
                    require(digest(body) == row['member']['sha256'] and len(body) == row['member']['bytes'], 'Member changed before write')
                    install_exclusive(output_fd, destination, body)
                    changed.append(destination)
                result = 'created' if destination in changed else 'reused_exact'
                members.append({'sourceId': row['sourceId'], 'archiveMember': row['member']['path'],
                                'sha256': row['member']['sha256'], 'bytes': row['member']['bytes'],
                                'pages': row['member']['pages'], 'relativePath': destination, 'result': result})
        if prior_receipt is not None:
            require(len(receipt['members']) == len(members), 'Existing receipt member count mismatch')
            for prior, current in zip(receipt['members'], members):
                require(prior.get('result') in ('created', 'reused_exact') and
                        {k: v for k, v in prior.items() if k != 'result'} == {k: v for k, v in current.items() if k != 'result'},
                        'Existing receipt member identity mismatch')
        else:
            receipt['members'] = members
        for row, destination in zip(rows, destinations):
            current = existing_bytes(output_fd, destination)
            require(current is not None and digest(current) == row['member']['sha256'] and len(current) == row['member']['bytes'], 'Final materialized bytes changed')
        unchanged(controls)
        private_root(root, output, destinations + [receipt_relative])
        if prior_receipt is None:
            receipt['completedAt'] = datetime.now(timezone.utc).isoformat()
            install_exclusive(output_fd, receipt_relative, canonical(receipt))
            changed.append(receipt_relative)
        unchanged(controls)
        expected_receipt = prior_receipt if prior_receipt is not None else canonical(receipt)
        require(existing_bytes(output_fd, receipt_relative) == expected_receipt, 'Final receipt changed')
        current_root = os.stat(output, follow_symlinks=False)
        opened_root = os.fstat(output_fd)
        require((current_root.st_dev, current_root.st_ino) == (opened_root.st_dev, opened_root.st_ino), 'Output root was replaced')
        for row, destination in zip(rows, destinations):
            final_path = safe_path(output, destination)
            require(final_path.is_file() and sha(final_path) == row['member']['sha256'], 'Final output path changed')
        return {'status': 'PASS', 'scope': binding['scope'], 'changedFiles': len(changed), 'changedPaths': changed,
                'memberCount': len(rows), 'receiptPath': str(output / receipt_relative),
                'receiptSha256': digest(existing_bytes(output_fd, receipt_relative)),
                'scientificInspectionPerformed': False, 'sourceReadinessGranted': False}
    except (ValueError, OSError, KeyError, TypeError, zipfile.BadZipFile) as error:
        failure = Hold(str(error))
        failure.receipt = {'status': 'HOLD', 'error': str(error), 'planId': plan['planId'], 'planSha256': plan_hash,
                           'privateOutputRoot': str(output), 'changedPaths': changed,
                           'scientificInspectionPerformed': False, 'sourceReadinessGranted': False,
                           'recovery': 'Preserve exact partial members; investigate changed controls/conflicts before an approved retry.'}
        raise failure from error
    finally:
        if locked:
            try:
                # Do not remove a lock another process replaced.
                from scripts.research_ingest.cli import decode
                if decode(existing_bytes(output_fd, lock_name)).get('token') == lock_token:
                    os.unlink(lock_name, dir_fd=output_fd)
                    os.fsync(output_fd)
            except (ValueError, OSError, TypeError):
                pass
        os.close(output_fd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('root', 'plan', 'readiness', 'manifest', 'archive', 'out-root'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    try:
        result = materialize(args.root, args.plan, args.readiness, args.manifest, args.archive, args.out_root)
    except (ValueError, OSError, KeyError, TypeError, zipfile.BadZipFile) as error:
        print(json.dumps(getattr(error, 'receipt', {'status': 'HOLD', 'error': str(error),
                                                  'scientificInspectionPerformed': False, 'sourceReadinessGranted': False})))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
