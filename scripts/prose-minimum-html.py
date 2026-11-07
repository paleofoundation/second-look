"""Count real rendered prose, excluding citations, tables and disclosures."""
import json
import sys
from html.parser import HTMLParser


class ProseParser(HTMLParser):
    def __init__(self, targets):
        super().__init__(convert_charrefs=True)
        self.targets = set(targets)
        self.stack = []
        self.parts = {key: [] for key in targets}
        self.rendered = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        target = attrs.get('id') if attrs.get('id') in self.targets else None
        if target:
            self.rendered.add(target)
        hidden = tag in {'details', 'table', 'sup', 'script', 'style', 'summary'} or attrs.get('aria-hidden') == 'true' or 'hidden' in attrs
        frame = {'tag': tag, 'target': target, 'hidden': hidden}
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append(frame)
        if tag == 'p':
            self.handle_data(' ')

    def handle_endtag(self, tag):
        if tag == 'p':
            self.handle_data(' ')
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]['tag'] == tag:
                self.stack = self.stack[:index]
                break

    def handle_data(self, value):
        if not any(frame['tag'] == 'p' for frame in self.stack) or any(frame['hidden'] for frame in self.stack):
            return
        for frame in self.stack:
            if frame['target']:
                self.parts[frame['target']].append(value)


pages = json.load(sys.stdin)
sections = []
omitted = []
for page in pages:
    targets = {section['id']: section['label'] for section in page['sections']}
    required = {section['id'] for section in page['sections'] if section.get('required')}
    if page['hasMechanismProse']:
        targets['mechanisms'] = 'Mechanism of Action'
        required.add('mechanisms')
    parser = ProseParser(targets)
    parser.feed(page['html'])
    for identity, label in targets.items():
        text = ' '.join(''.join(parser.parts[identity]).split())
        # Replaced Status prose retains an invisible fragment target, but no paragraph.
        if identity not in parser.rendered or (not text and identity not in required):
            omitted.append({'slug': page['slug'], 'sectionId': identity, 'label': label})
            continue
        words, characters = len(text.split()), len(text)
        sections.append({'guideId': page['guideId'], 'slug': page['slug'], 'sectionId': identity,
                         'label': label, 'words': words, 'characters': characters,
                         'passes': words >= 113 and characters >= 845})
report = {'minimumWords': 113, 'minimumCharactersIncludingSpaces': 845,
          'pageCount': len(pages), 'sectionCount': len(sections), 'sections': sections,
          'omittedStructuredOrHiddenSections': omitted,
          'failures': [section for section in sections if not section['passes']]}
print(json.dumps(report))
