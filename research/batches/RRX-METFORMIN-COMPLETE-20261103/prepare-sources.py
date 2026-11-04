"""Inventory immutable source bytes and make private, readable derivatives.

No scientific assessment or completion state is inferred by this script.
"""
import hashlib
import json
import subprocess
from pathlib import Path
from lxml import etree, html

BATCH = Path(__file__).resolve().parent
RAW = BATCH.parents[2].parent / 'private-research/RRX-METFORMIN-COMPLETE-20261103'
INDEX = BATCH / 'source-access.json'
data = json.loads(INDEX.read_text())
sources = {s['sourceId']: s for s in data['sources']}
for sid in ['REVIVE-REPLACEMENT', 'REVIVE-NOTICE', 'COVIDOUT-CORRECTION']:
    sources.setdefault(sid, {'sourceId': sid, 'kind': 'version_companion', 'assets': []})

def add(sid, path, role, url=None):
    if not path.exists():
        return
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    entry = next((a for a in sources[sid]['assets'] if a['sha256'] == digest), None)
    if entry is None:
        entry = {'path': str(path.resolve()), 'sha256': digest, 'role': role}
        sources[sid]['assets'].append(entry)
    if url:
        entry['url'] = url

for receipt in ['fulltext-receipt.json','recovery-receipt.json','companions-receipt.json']:
    for r in json.loads((BATCH / receipt).read_text()):
        if r.get('status') != 200 or 'metadata' in r['id']:
            continue
        matches = [sid for sid in sources if r['id'].startswith(sid + '-')]
        if matches:
            add(max(matches,key=len), Path(r['path']), 'retrieved_source', r['url'])

for sid, file, url, role in [
    ('REVIVE-REPLACEMENT','REVIVE-REPLACEMENT-browser.html','https://www.acpjournals.org/doi/full/10.7326/ANNALS-26-02144','rendered_browser_dom'),
    ('REVIVE-NOTICE','REVIVE-NOTICE-browser.html','https://www.acpjournals.org/doi/full/10.7326/ANNALS-26-03050','rendered_browser_dom'),
    ('P-KOREA-2026','KOREA-browser.html','https://www.acpjournals.org/doi/full/10.7326/ANNALS-25-04883','rendered_browser_dom'),
    ('P-COVIDOUT-2023','COVIDOUT-current-browser.html','https://www.thelancet.com/journals/laninf/article/PIIS1473-3099(23)00299-2/fulltext','rendered_browser_dom'),
    ('P-COVIDOUT-2023','COVIDOUT-corrected-appendix.pdf','https://www.thelancet.com/cms/10.1016/S1473-3099(23)00299-2/attachment/b1b2da41-fb78-40d1-bcc7-70b0420195ad/mmc1.pdf','corrected_supplement'),
    ('COVIDOUT-CORRECTION','COVIDOUT-CORRECTION-publisher.pdf','https://www.thelancet.com/action/showPdf?pii=S1473-3099%2823%2900562-5','correction_notice'),
]: add(sid, RAW/file, role, url)

(RAW/'text').mkdir(exist_ok=True)
for sid,s in sources.items():
    for a in s['assets']:
        path=Path(a['path']); b=path.read_bytes()
        out=RAW/'text'/f'{sid}-{a["sha256"][:8]}.txt'
        if b[:4] == b'%PDF':
            subprocess.run(['pdftotext','-layout',str(path),str(out)],check=True)
        elif b'<html' in b[:2000].lower() or b'<body' in b[:2000].lower():
            root=html.fromstring(b)
            for junk in root.xpath('//script|//style|//nav|//header|//footer|//iframe'):
                if junk.getparent() is not None: junk.getparent().remove(junk)
            nodes=root.xpath('//article') or [root]
            lines=[]
            for node in nodes:
                for e in node.iter():
                    if e.tag in ['h1','h2','h3','h4','p','table','figcaption']:
                        if any(x.tag in ['table','p','figcaption'] for x in e.iterancestors()): continue
                        txt=' '.join(e.text_content().split())
                        if txt: lines.append(f'[{e.tag} {e.get("id", "")}] {txt}')
            out.write_text('\n\n'.join(lines))
        elif b'<article' in b[:1500]:
            root=etree.fromstring(b); lines=[]
            for e in root.iter():
                if e.tag in ['article-title','title','p','table-wrap','fig','ack','fn']:
                    if any(x.tag in ['table-wrap','fig','ack','fn','p','ref-list'] for x in e.iterancestors()): continue
                    lines.append(f'[{e.tag} {e.get("id", "")}] '+ ' '.join(''.join(e.itertext()).split()))
            out.write_text('\n\n'.join(lines))
        else: continue
        a['textPath']=str(out.resolve())
        a['textSha256']=hashlib.sha256(out.read_bytes()).hexdigest()
data['sources']=list(sources.values())
INDEX.write_text(json.dumps(data,indent=2)+'\n')
print(f'Indexed {len(sources)} source/report identities; no assessment states promoted.')
