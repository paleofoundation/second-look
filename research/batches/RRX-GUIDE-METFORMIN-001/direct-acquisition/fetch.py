"""Bounded acquisition transport. Source bytes go only to declared private staging.

Run with a JSON list of {assignmentId, purpose, url}. No source appraisal occurs.
Each request preserves response bytes, headers, status and transport failure.
"""
import concurrent.futures
import datetime
import hashlib
import json
import pathlib
import subprocess
import sys
import uuid
from urllib.parse import urlparse

STAGE = pathlib.Path('/Users/kmfp/Documents/ChatGPT/Drug Repurposing/private-research/RRX-GUIDE-METFORMIN-001/ACQUIRE-1.1')
ALLOWED = {'www.ebi.ac.uk', 'europepmc.org', 'pmc.ncbi.nlm.nih.gov', 'pubmed.ncbi.nlm.nih.gov', 'www.ncbi.nlm.nih.gov', 'www.nature.com', 'static-content.springer-cdn.com', 'jamanetwork.com', 'cdn.jamanetwork.com', 'doi.org', 'www.thelancet.com', 'www.sciencedirect.com', 'api.elsevier.com', 'eprints.ncl.ac.uk', 'dailymed.nlm.nih.gov', 'www.fda.gov', 'clinicaltrials.gov', 'api.crossref.org', 'www.acpjournals.org', 'aacrjournals.org'}

def fetch(r):
    assert r['assignmentId'] in {f'MF-GAP-{i:02}' for i in range(1,15)}
    assert urlparse(r['url']).scheme == 'https' and urlparse(r['url']).hostname in ALLOWED
    token = r['assignmentId'] + '-' + uuid.uuid4().hex[:12]
    folder = STAGE / 'attempts' / token
    folder.mkdir(parents=True)
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cmd = ['curl', '--silent', '--show-error', '--location', '--max-redirs', '5', '--max-time', '60', '--proto', '=https', '--proto-redir', '=https', '--user-agent', 'RemapRx-Research-Receipt/1.1 (exact-source archival acquisition)', '--dump-header', str(folder/'headers.txt'), '--output', str(folder/'body'), '--write-out', '%{json}', r['url']]
    p = subprocess.run(cmd, capture_output=True, text=True)
    try: http = json.loads(p.stdout)
    except ValueError: http = {'output': p.stdout}
    data = (folder/'body').read_bytes() if (folder/'body').exists() else b''
    rec = {**r, 'retrievedAt': start, 'curlExit': p.returncode, 'error': p.stderr.strip() or None, 'httpStatus': http.get('http_code'), 'resolvedUrl': http.get('url_effective'), 'mediaType': http.get('content_type'), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'body': str((folder/'body').relative_to(STAGE)), 'headers': str((folder/'headers.txt').relative_to(STAGE))}
    (folder/'receipt.json').write_text(json.dumps(rec, indent=2)+'\n')
    return rec

if __name__ == '__main__':
    requests = json.loads(pathlib.Path(sys.argv[1]).read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(fetch, requests))
    for r in results:
        print(json.dumps(r))
