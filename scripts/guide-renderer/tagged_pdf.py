"""Host-owned structure tagging; the vendored renderer remains unchanged.

Tags are recorded while flowables draw, then linked to the actual PDF page and
annotation objects. This supplies semantic reading order, headings and tables;
it does not claim independent PDF/UA or assistive-technology certification.
"""
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, LongTable, TableStyle
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject, BooleanObject, DictionaryObject, NameObject, NumberObject,
    TextStringObject,
)


class TaggedCanvas(Canvas):
    latest = None

    def __init__(self, *args, **kwargs):
        kwargs['initialFontName'] = 'GuideBody'
        kwargs['lang'] = 'en-US'
        super().__init__(*args, **kwargs)
        self.structure = {'role': 'Document', 'children': []}
        self.parents = [self.structure]
        self.mcids = {}
        self.chapter_count = 0
        self.annotation_nodes = []
        TaggedCanvas.latest = self

    def enter(self, role, **attributes):
        node = {'role': role, 'children': [], **attributes}
        self.parents[-1]['children'].append(node)
        self.parents.append(node)
        return node

    def leave(self):
        self.parents.pop()

    def begin_content(self, role):
        node = self.enter(role)
        page = self.getPageNumber() - 1
        mcid = self.mcids.get(page, 0)
        self.mcids[page] = mcid + 1
        node.update(page=page, mcid=mcid)
        self._code.append(f'/{role} <</MCID {mcid}>> BDC')
        return len(self._annotationrefs)

    def end_content(self, annotation_start):
        node = self.parents[-1]
        for index in range(annotation_start, len(self._annotationrefs)):
            self.annotation_nodes.append((self.getPageNumber() - 1, index, node))
        self._code.append('EMC')
        self.leave()

    def begin_artifact(self):
        self._code.append('/Artifact BMC')

    def end_artifact(self):
        self._code.append('EMC')


class GuideParagraph(Paragraph):
    def split(self, available_width, available_height):
        if self.style.name == 'source':
            return []
        return super().split(available_width, available_height)

    def draw(self):
        canvas = self.canv
        role = 'P'
        if self.style.name == 'title':
            role = 'H1' if canvas.chapter_count == 0 else 'H2'
            canvas.chapter_count += 1
        elif self.style.name == 'heading':
            role = 'H2' if canvas.chapter_count <= 1 else 'H3'
        start = canvas.begin_content(role)
        try:
            super().draw()
        finally:
            canvas.end_content(start)


def table_callback(table, event, *args):
    canvas = table.canv
    if event == 'startTable':
        canvas.enter('Table')
    elif event == 'startRow':
        canvas.enter('TR')
    elif event == 'startCell':
        canvas.enter('TH' if args[0] == 0 else 'TD', scope='Column' if args[0] == 0 else None)
    elif event in ('endTable', 'endRow', 'endCell'):
        canvas.leave()
    elif event in ('startBG', 'startLines'):
        canvas.begin_artifact()
    elif event in ('endBG', 'endLines'):
        canvas.end_artifact()


class GuideTable(LongTable):
    def __init__(self, *args, **kwargs):
        kwargs['renderCB'] = table_callback
        super().__init__(*args, **kwargs)
        self.setStyle(TableStyle([('FONTNAME', (0, 0), (-1, -1), 'GuideBody')]))


def install(renderer):
    """Install a host adapter without changing shared ReportLab module globals."""
    from types import SimpleNamespace
    renderer.canvas = SimpleNamespace(Canvas=TaggedCanvas)
    renderer.Paragraph = GuideParagraph
    renderer.LongTable = GuideTable
    original_doc = renderer.GuideDoc
    original_art = renderer.TraceArt
    original_credit = renderer.OrcidCredit

    class GuideDoc(original_doc):
        def addPageTemplates(self, templates):
            for template in templates if isinstance(templates, (list, tuple)) else [templates]:
                callback = template.onPage
                def artifact_page(canvas, doc, callback=callback):
                    canvas.begin_artifact()
                    try:
                        callback(canvas, doc)
                    finally:
                        canvas.end_artifact()
                template.onPage = artifact_page
            return super().addPageTemplates(templates)

    class TraceArt(original_art):
        def draw(self):
            self.canv.begin_artifact()
            try:
                super().draw()
            finally:
                self.canv.end_artifact()

    class OrcidCredit(original_credit):
        def draw(self):
            start = self.canv.begin_content('P')
            try:
                super().draw()
            finally:
                self.canv.end_content(start)

    renderer.GuideDoc, renderer.TraceArt, renderer.OrcidCredit = GuideDoc, TraceArt, OrcidCredit


def tag_pdf(path):
    """Build a real structure tree and ParentTree from the drawing-time log."""
    path = Path(path)
    canvas = TaggedCanvas.latest
    if canvas is None or len(canvas.parents) != 1:
        raise ValueError('Unbalanced or absent PDF structure recording')
    writer = PdfWriter(clone_from=PdfReader(path))
    name = NameObject
    number = NumberObject
    root = DictionaryObject({name('/Type'): name('/StructTreeRoot')})
    root_ref = writer._add_object(root)
    page_parents = {i: [None] * count for i, count in canvas.mcids.items()}
    node_refs = {}
    role_counts = {}

    def build(node, parent):
        role_counts[node['role']] = role_counts.get(node['role'], 0) + 1
        obj = DictionaryObject({name('/Type'): name('/StructElem'), name('/S'): name('/' + node['role']), name('/P'): parent})
        ref = writer._add_object(obj)
        node_refs[id(node)] = ref
        kids = []
        if 'mcid' in node:
            obj[name('/Pg')] = writer.pages[node['page']].indirect_reference
            kids.append(number(node['mcid']))
            page_parents[node['page']][node['mcid']] = ref
        if node.get('scope'):
            obj[name('/A')] = DictionaryObject({name('/O'): name('/Table'), name('/Scope'): name('/' + node['scope'])})
        for child in node['children']:
            kids.append(build(child, ref))
        obj[name('/K')] = ArrayObject(kids)
        return ref

    root[name('/K')] = ArrayObject([build(canvas.structure, root_ref)])
    parent_entries = {}
    for page_index, page in enumerate(writer.pages):
        page[name('/StructParents')] = number(page_index)
        page[name('/Tabs')] = name('/S')
        parents = page_parents.get(page_index, [])
        if any(value is None for value in parents):
            raise ValueError('Unowned marked content')
        parent_entries[page_index] = ArrayObject(parents)
    next_key = len(writer.pages)
    for page_index, annotation_index, node in canvas.annotation_nodes:
        page = writer.pages[page_index]
        annotation_ref = page['/Annots'][annotation_index]
        annotation = annotation_ref.get_object()
        if annotation.get('/Subtype') != '/Link':
            raise ValueError('Unexpected annotation type')
        parent_ref = node_refs[id(node)]
        target = annotation.get('/A', {}).get('/URI')
        description = str(target) if target else 'Go to the linked guide chapter'
        annotation[name('/Contents')] = TextStringObject(description)
        annotation[name('/StructParent')] = number(next_key)
        link = DictionaryObject({
            name('/Type'): name('/StructElem'), name('/S'): name('/Link'),
            name('/P'): parent_ref, name('/Pg'): page.indirect_reference,
            name('/Alt'): TextStringObject(description),
            name('/K'): ArrayObject([DictionaryObject({name('/Type'): name('/OBJR'), name('/Obj'): annotation_ref, name('/Pg'): page.indirect_reference})]),
        })
        link_ref = writer._add_object(link)
        parent_ref.get_object()['/K'].append(link_ref)
        parent_entries[next_key] = link_ref
        next_key += 1
    nums = ArrayObject()
    for key, value in sorted(parent_entries.items()):
        nums.extend([number(key), value])
    root[name('/ParentTree')] = writer._add_object(DictionaryObject({name('/Nums'): nums}))
    root[name('/ParentTreeNextKey')] = number(next_key)
    writer.root_object[name('/StructTreeRoot')] = root_ref
    writer.root_object[name('/MarkInfo')] = DictionaryObject({name('/Marked'): BooleanObject(True)})
    writer.root_object[name('/Lang')] = TextStringObject('en-US')
    writer.root_object[name('/ViewerPreferences')] = DictionaryObject({name('/DisplayDocTitle'): BooleanObject(True)})
    temporary = path.with_suffix('.tagged.tmp')
    writer.write(temporary)
    temporary.replace(path)
    return {'tagged': True, 'markedContentCount': sum(canvas.mcids.values()), 'structureRoles': role_counts,
            'taggedLinks': len(canvas.annotation_nodes), 'pdfUaCertified': False}
