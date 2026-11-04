"""Adapt the unchanged reusable renderer for selected private variants."""
import argparse, importlib.util, json
from pathlib import Path
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('consumer_guide_renderer', ROOT / 'vendor/src/render.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)

class GuideParagraph(Paragraph):
    """Keep short references and worksheet prompts together across page breaks."""
    def split(self, available_width, available_height):
        if self.style.name == 'source':
            return []
        return super().split(available_width, available_height)

renderer.Paragraph = GuideParagraph

def render(work, output):
    work, output = Path(work), Path(output)
    config = renderer.load(ROOT / 'config/remaprx.json')
    result = {}
    for variant in ['full', 'preview', 'summary']:
        source = work / (variant + '.native.json')
        data = renderer.load(source)
        renderer.validate(data, config)
        result[variant] = renderer.render_variant(data, config, variant, output)
    renderer.dump(output / 'pdf-manifest.json', {
        'rendererVersion': renderer.VERSION,
        'rendererSha256': renderer.hashfile(ROOT / 'vendor/src/render.py'),
        'adapterSha256': renderer.hashfile(Path(__file__)),
        'configSha256': renderer.hashfile(ROOT / 'config/remaprx.json'),
        'fontHashes': {p.name: renderer.hashfile(p) for p in sorted((ROOT / 'vendor/assets/fonts').glob('*.ttf'))},
        'assets': result,
        'accessibility': 'HOLD: selectable text and working bookmarks; untagged PDF, reading order and PDF/UA are not certified.',
        'releaseState': 'private_draft',
    })
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    print(json.dumps(render(args.work, args.out)))
