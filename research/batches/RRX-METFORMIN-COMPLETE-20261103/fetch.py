"""Bounded, logged lawful source retrieval. Raw responses stay outside Git."""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parents[2]
RAW = ROOT.parent / 'private-research/RRX-METFORMIN-COMPLETE-20261103'
RAW.mkdir(parents=True, exist_ok=True)

def fetch(item):
    key, url = item['id'], item['url']
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    dest = RAW / (key + '-' + stamp)
    record = {'id': key, 'url': url, 'retrievedAt': stamp}
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'RemapRx source verification/1.0'})
        with urllib.request.urlopen(request, timeout=40) as response:
            data = response.read()
            record.update(status=response.status, resolvedUrl=response.url,
                          contentType=response.headers.get('Content-Type'),
                          sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
        dest.write_bytes(data)
        record['path'] = str(dest)
    except Exception as error:
        record.update(status='failed', error=str(error))
    dest.with_suffix('.receipt.json').write_text(json.dumps(record, indent=2)+'\n')
    return record

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('requests')
    parser.add_argument('output')
    args = parser.parse_args()
    requests = json.loads(Path(args.requests).read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(fetch, requests))
    Path(args.output).write_text(json.dumps(records, indent=2)+'\n')
    for record in records:
        print(record['id'], record['status'], record.get('bytes', 0), record.get('error',''))
