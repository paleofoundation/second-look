"""Semantic/geometry assertions supplement (never replace) every-page visual review."""
import argparse, hashlib, json
from pathlib import Path
from pypdf import PdfReader
import pdfplumber

def verify(output):
    output = Path(output)
    manifest = json.loads((output / 'build-manifest.json').read_text())
    web = json.loads((output / 'web-manuscript.json').read_text())
    summary = json.loads((output / 'summary-candidate.json').read_text())
    preview = json.loads((output / 'sample-candidate.json').read_text())
    checks = []
    for variant, asset in manifest['pdf']['assets'].items():
        file = output / asset['file']
        assert hashlib.sha256(file.read_bytes()).hexdigest() == asset['sha256']
        reader = PdfReader(file)
        text = '\n'.join(page.extract_text() or '' for page in reader.pages)
        compact = ' '.join(text.split())
        assert web['version'] in text and web['evidenceCutoff'] in text
        assert ' '.join(web['medicalNotice'].split()) in compact
        assert len(reader.outline) == len(asset['bookmarks'])
        for bookmark in reader.outline:
            assert 0 <= reader.get_destination_page_number(bookmark) < len(reader.pages)
        for link in asset['linkAnnotations']:
            assert link['uri'].startswith('https://') or 1 <= link['destinationPage'] <= len(reader.pages)
        if variant != 'full':
            assert 'PRIVATE-ONLY-SENTINEL' not in text and 'PRIVATE-REFERENCE-SENTINEL' not in text
            assert not any(link['uri'].endswith('/private-fixture') for link in asset['linkAnnotations'])
        else:
            assert 'PRIVATE-ONLY-SENTINEL' in text and 'PRIVATE-REFERENCE-SENTINEL' in text
        if variant == 'full':
            assert 'Two fictional record fields' in text and 'Which edition am I reading?' in text
        scoped = web if variant == 'full' else preview if variant == 'preview' else summary
        for chapter in scoped['chapters']:
            for block in chapter['blocks']:
                phrases = [block['text']] if block['type'] in ['paragraph', 'callout'] else block['items'] if block['type'] in ['list', 'questions'] else [block['caption'], *block['columns'], *(cell for row in block['rows'] for cell in row)]
                for phrase in phrases:
                    assert ' '.join(phrase.split()) in compact, (variant, phrase)
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                assert page.chars, 'No empty pages'
                assert all(char['x0'] >= 0 and char['x1'] <= page.width + .5 and char['top'] >= 0 and char['bottom'] <= page.height + .5 for char in page.chars), 'Text escapes page bounds'
                assert not any(char['text'] == '\ufffd' for char in page.chars), 'Missing text glyph'
        checks.append({'variant': variant, 'pages': len(reader.pages), 'bookmarks': len(reader.outline), 'links': len(asset['linkAnnotations']), 'sha256': asset['sha256']})
    return checks

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--out', required=True)
    args = parser.parse_args(); print(json.dumps(verify(args.out)))
