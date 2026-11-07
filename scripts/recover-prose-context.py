"""Recover only the approved official context allowlist into private staging."""
import datetime
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'research/batches/RRX-PROSE-MINIMUM-20261104'
RAW = Path('/private/tmp/remaprx-prose-context-20261107/raw')
RETURNS = BATCH / 'returns'


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style']:
            self.skip += 1
        if tag in ['p', 'div', 'section', 'li', 'tr', 'h1', 'h2', 'h3', 'h4', 'h5', 'br']:
            self.out.append('\n')

    def handle_endtag(self, tag):
        if tag in ['script', 'style'] and self.skip:
            self.skip -= 1
        if tag in ['p', 'div', 'section', 'li', 'tr', 'h1', 'h2', 'h3', 'h4', 'h5']:
            self.out.append('\n')

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


arguments = sys.argv[1:]
version = '3'
if arguments[:1] == ['--version']:
    version = arguments[1]
    arguments = arguments[2:]
inventory = json.loads((BATCH / f'source-inventory-v{version}.json').read_text())
ready = json.loads((BATCH / f'readiness-v{version}.json').read_text())
assert ready['decision'] == 'PASS'
for item in ready['files']:
    assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256'], item['path']
RAW.mkdir(parents=True, exist_ok=True)
RETURNS.mkdir(exist_ok=True)
for identity in arguments:
    source = next(item for item in inventory if item['sourceId'] == identity)
    safe = re.sub(r'[^a-zA-Z0-9_-]', '_', identity)
    receipt_path = RETURNS / f'{safe}-receipt.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        if receipt.get('file') and Path(receipt['file']).exists():
            assert hashlib.sha256(Path(receipt['file']).read_bytes()).hexdigest() == receipt['sha256']
            print(identity, 'reused immutable snapshot', flush=True)
            continue
    temporary = RAW / (safe + '.download')
    command = ['curl', '--fail', '--location', '--silent', '--show-error', '--max-time', '45',
               '--output', str(temporary), '--write-out', '%{json}', source['url']]
    response = subprocess.run(command, capture_output=True, text=True)
    metadata = json.loads(response.stdout) if response.stdout.strip() else {}
    receipt = {'planVersion': version, 'sourceId': identity, 'url': source['url'], 'resolvedUrl': metadata.get('url_effective'),
               'retrievedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'accessStatus': 'not_accessible', 'mediaType': metadata.get('content_type'),
               'file': None, 'sha256': None,
               'identity': {'kind': 'product', 'name': source['title'], 'formulation': None, 'verified': False},
               'observations': [], 'gaps': []}
    if response.returncode == 0 and temporary.exists():
        body = temporary.read_bytes()
        digest = hashlib.sha256(body).hexdigest()
        suffix = '.pdf' if body.startswith(b'%PDF') else '.html'
        actual = RAW / f'{safe}-{digest[:16]}{suffix}'
        temporary.rename(actual)
        receipt.update(accessStatus='partial_text', file=str(actual), sha256=digest)
        text_path = actual.with_suffix('.txt')
        if suffix == '.pdf':
            subprocess.run(['pdftotext', '-layout', str(actual), str(text_path)], check=True)
        else:
            parser = Text(); parser.feed(body.decode('utf-8', errors='replace'))
            text_path.write_text('\n'.join(' '.join(line.split()) for line in ''.join(parser.out).splitlines() if line.strip()) + '\n')
        receipt['gaps'].append({'reason': 'Snapshot acquired; product identity and relevant label observations not yet inspected.', 'status': 'not_checked', 'nextAction': 'Root verifies product/formulation, stable source locators and actual claim support before use.'})
        print(identity, 'acquired', len(body), 'bytes', text_path, flush=True)
    else:
        receipt['gaps'].append({'reason': response.stderr.strip() or f'HTTP {metadata.get("http_code")}', 'status': 'not_accessible', 'nextAction': 'Resolve official-source access without substituting an unverified product.'})
        print(identity, 'not_accessible', receipt['gaps'][0]['reason'], flush=True)
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
