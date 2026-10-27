#!/usr/bin/env python3
"""Metadata only: hashes, media signatures, PDF counts, ZIP and HTML structure.

Never extracts source body text, renders scientific figures, acquires URLs or
materializes archive members. Outputs stay beside this script.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import unicodedata
from urllib.parse import urljoin
import zipfile

OUT = Path(__file__).resolve().parent
MAX_MEMBER_BYTES = 100 * 1024 * 1024
MAX_TOTAL_BYTES = 300 * 1024 * 1024
MAX_MEMBERS = 1000
MAX_RATIO = 200


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pdf_pages(data):
    if not data.startswith(b'%PDF-'):
        raise ValueError('PDF signature mismatch')
    result = subprocess.run(['pdfinfo', '-'], input=data, capture_output=True, check=True, timeout=30)
    count = re.search(rb'^Pages:\s*(\d+)\s*$', result.stdout, re.M)
    if not count or int(count.group(1)) < 1:
        raise ValueError('PDF page count unavailable')
    return int(count.group(1))


def member_name(name):
    path = PurePosixPath(name)
    if (not name or '\\' in name or any(ord(char) < 32 for char in name) or path.is_absolute()
            or any(part in ('', '.', '..') for part in name.split('/'))
            or ':' in name or name != unicodedata.normalize('NFC', name)):
        raise ValueError('Unsafe or ambiguous ZIP member path: ' + name)
    return path.as_posix()


def archive_inventory(data, count_pages=pdf_pages):
    """Validate the entire archive directory before streaming allowlisted PDFs."""
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        infos = archive.infolist()
        if len(infos) > MAX_MEMBERS:
            raise ValueError('Archive member count exceeds limit')
        seen, total = set(), 0
        for info in infos:
            name = member_name(info.filename[:-1] if info.is_dir() else info.filename)
            collision = name.casefold()
            if collision in seen:
                raise ValueError('Duplicate/colliding ZIP member path')
            seen.add(collision)
            mode = (info.external_attr >> 16) & 0o170000
            if mode not in (0, stat.S_IFREG, stat.S_IFDIR) or info.flag_bits & 1:
                raise ValueError('Link/special/encrypted ZIP member is forbidden')
            if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                raise ValueError('Unsupported ZIP compression method')
            total += info.file_size
            if info.file_size > MAX_MEMBER_BYTES or total > MAX_TOTAL_BYTES:
                raise ValueError('ZIP uncompressed bytes exceed limit')
            if info.file_size / max(info.compress_size, 1) > MAX_RATIO:
                raise ValueError('ZIP compression ratio exceeds limit')
            if not info.is_dir() and PurePosixPath(name).suffix.lower() != '.pdf':
                raise ValueError('Only PDF files are allowed in this prospective archive contract')
        members = []
        for info in infos:
            if info.is_dir():
                continue
            checksum, chunks, count = hashlib.sha256(), [], 0
            with archive.open(info) as stream:
                while chunk := stream.read(1024 * 1024):
                    count += len(chunk)
                    if count > info.file_size or count > MAX_MEMBER_BYTES:
                        raise ValueError('Stream exceeds declared member bytes')
                    checksum.update(chunk); chunks.append(chunk)
            if count != info.file_size:
                raise ValueError('ZIP member byte count mismatch')
            body = b''.join(chunks)
            if not body.startswith(b'%PDF-'):
                raise ValueError('ZIP PDF member signature mismatch')
            members.append(dict(path=info.filename, sha256=checksum.hexdigest(), bytes=count,
                                compressedBytes=info.compress_size, crc32=f'{info.CRC:08x}',
                                mediaType='application/pdf', pages=count_pages(body),
                                materialized=False, bodyTextExtracted=False))
        return members


class Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sections, self.figures, self.images, self.links = [], [], [], []
        self.stack = []
        self.canonical = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonical = a.get('href')
        if tag == 'section' and a.get('id'):
            self.sections.append(a['id'])
        if tag == 'figure' and a.get('id'):
            self.figures.append(a['id'])
        if tag == 'img' and (any(t == 'figure' for t, _ in self.stack) or 'fig' in a.get('class', '').lower()):
            figure = next((v.get('id') for t, v in reversed(self.stack) if t == 'figure'), None)
            self.images.append(dict(figureId=figure, src=a.get('src'), srcset=a.get('srcset')))
        if tag == 'a' and a.get('href') and re.search(r'(\.pdf(?:[?#]|$)|\.zip(?:[?#]|$)|\.docx?(?:[?#]|$)|/supplement(?:/|$))', a['href'], re.I):
            self.links.append(dict(href=a['href'], id=a.get('id')))
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:
            self.stack.append((tag, a))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                self.stack = self.stack[:i]; break

    def result(self):
        for row in self.images:
            row['resolvedUrl'] = urljoin(self.canonical, row['src']) if self.canonical and row['src'] else None
        for row in self.links:
            row['resolvedUrl'] = urljoin(self.canonical, row['href']) if self.canonical else None
        return dict(canonicalUrl=self.canonical, sectionIds=list(dict.fromkeys(self.sections)),
                    figureIds=list(dict.fromkeys(self.figures)), figureImageReferences=self.images,
                    documentLinkReferences=list({r['href']: r for r in self.links}.values()),
                    remoteAvailabilityChecked=False, scientificBodyExtracted=False)


def write(name, value):
    (OUT / name).parent.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def main(root):
    old_path = root / 'research/batches/RRX-INGEST-001/calibration/assignments.json'
    old = json.loads(old_path.read_text())
    packets = [p for p in old['packets'] if p['tranche'] == 1 and p['packetId'] != 'CAL-07']
    inventory = []
    for packet in packets:
        row = {k: packet[k] for k in ('packetId','canonicalReportId','primarySourceId','heldDiagnosticPacket','holdReason','selectionDimensions','familyCoordination')}
        row['sourceAssets'] = []
        row['preservedResultIds'] = sorted({rid for rec in packet['sourceRecords'] for key in ('result_ids', 'existing_result_ids')
                                             for rid in (rec.get('priorScientificDisposition') or {}).get(key, [])})
        row['metadataRecords'] = [{k: rec.get(k) for k in ('recordId','sourceId','canonicalReportId','doi','pmid','recordSha256')} for rec in packet['sourceRecords']]
        row['gaps'] = packet['gaps']
        for source in packet['sourceAssignments']:
            path = Path(source['path'])
            data = path.read_bytes()
            if sha(data) != source['sha256'] or len(data) != source['bytes']:
                raise ValueError('Assigned source changed: ' + source['source_id'])
            record = dict(sourceId=source['source_id'], roleFromPriorAssignment=source['role'],
                          logicalSource=source['logicalSource'], path=str(path), sha256=sha(data), bytes=len(data),
                          priorMediaType=source['media_type'], priorHoldReasons=source['holdReasons'],
                          mediaType=source['media_type'], hashVerified=True, scientificBodyExtracted=False)
            if data.startswith(b'%PDF-'):
                record.update(mediaType='application/pdf', pages=pdf_pages(data))
            elif data.startswith(b'PK\x03\x04'):
                record.update(mediaType='application/zip', archiveMembers=archive_inventory(data))
            elif data.startswith(b'RIFF') and data[8:12] == b'WEBP':
                record.update(mediaType='image/webp', framesInspected=False, visualReadPerformed=False)
            elif source['media_type'] == 'text/html':
                parsed = Structure(); parsed.feed(data.decode('utf-8'))
                record['htmlStructure'] = parsed.result()
            else:
                raise ValueError('Unsupported actual media signature: ' + source['source_id'])
            row['sourceAssets'].append(record)
        inventory.append(row)
    result = dict(schemaVersion='remaprx-next-tranche-metadata-v1', status='METADATA_PREFLIGHT_ONLY',
                  previousAssignmentsSha256=sha(old_path.read_bytes()), packets=inventory,
                  scientificBodyExtracted=False, sourceInspectedForScience=False, gpPassed=False,
                  performedAcquisition=False, archiveMembersMaterialized=False, performedImport=False)
    write('metadata-inventory.json', result)
    print(json.dumps({'status': result['status'], 'packets': len(inventory), 'files': sum(len(p['sourceAssets']) for p in inventory),
                      'sha256': sha((OUT/'metadata-inventory.json').read_bytes())}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--root', type=Path, required=True)
    main(parser.parse_args().root.resolve())
