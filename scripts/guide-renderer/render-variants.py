"""Adapt the unchanged reusable renderer for selected private variants."""
import argparse, importlib.util, json
from pathlib import Path
from tagged_pdf import install, tag_pdf

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('consumer_guide_renderer', ROOT / 'vendor/src/render.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)

install(renderer)

def render(work, output):
    work, output = Path(work), Path(output)
    config = renderer.load(ROOT / 'config/remaprx.json')
    result = {}
    for variant in ['full', 'preview', 'summary']:
        source = work / (variant + '.native.json')
        data = renderer.load(source)
        renderer.validate(data, config)
        result[variant] = renderer.render_variant(data, config, variant, output)
        asset = result[variant]
        asset.update(tag_pdf(output / asset['file']))
        asset['sha256'] = renderer.hashfile(output / asset['file'])
        asset['bytes'] = (output / asset['file']).stat().st_size
    renderer.dump(output / 'pdf-manifest.json', {
        'rendererVersion': renderer.VERSION,
        'rendererSha256': renderer.hashfile(ROOT / 'vendor/src/render.py'),
        'adapterSha256': renderer.hashfile(Path(__file__)),
        'taggingSha256': renderer.hashfile(ROOT / 'tagged_pdf.py'),
        'configSha256': renderer.hashfile(ROOT / 'config/remaprx.json'),
        'fontHashes': {p.name: renderer.hashfile(p) for p in sorted((ROOT / 'vendor/assets/fonts').glob('*.ttf'))},
        'assets': result,
        'accessibility': 'Structure-tagged text, headings, tables and links; decorative page chrome marked as artifacts. All fonts embedded. Independent screen-reader and PDF/UA certification remain pending.',
        'releaseState': 'private_draft',
    })
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    print(json.dumps(render(args.work, args.out)))
