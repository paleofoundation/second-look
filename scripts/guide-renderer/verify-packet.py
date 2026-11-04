"""Portable artifact checks. Reads only the selected packet, not a source archive.

Run: python verify-packet.py --packet /path/to/unzipped-packet
Requires pypdf and pdfplumber. This verifies byte integrity and artifact parity;
it neither re-audits unavailable original papers nor confers human approval.
"""
import argparse, hashlib, json, unicodedata
from pathlib import Path
from pypdf import PdfReader
from pypdf.generic import ContentStream, IndirectObject
import pdfplumber


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(value):
    return ' '.join(unicodedata.normalize('NFKC', value).split())


def structure_check(reader):
    root = reader.trailer['/Root']
    assert root.get('/MarkInfo', {}).get('/Marked'), 'PDF is not marked'
    assert root.get('/Lang') == 'en-US', 'Document language missing'
    tree = root['/StructTreeRoot']
    nums = tree['/ParentTree']['/Nums']
    parent_tree = dict(zip(nums[::2], nums[1::2]))
    seen = set(); counts = {}; mcr = {}; objects = set()
    page_refs = {p.indirect_reference.idnum: i for i,p in enumerate(reader.pages)}

    def walk(ref, parent):
        obj = ref.get_object()
        assert obj['/Type'] == '/StructElem'
        assert obj.raw_get('/P') == parent, 'Broken structure parent'
        assert ref.idnum not in seen, 'Repeated structure object'
        seen.add(ref.idnum)
        role = obj['/S']; counts[role] = counts.get(role, 0) + 1
        if role == '/TH': assert obj.get('/A', {}).get('/Scope') == '/Column'
        for kid in obj['/K']:
            if isinstance(kid, int):
                page = page_refs[obj.raw_get('/Pg').idnum]
                key = (page, int(kid)); assert key not in mcr, 'Duplicate MCID'
                mcr[key] = ref
            elif isinstance(kid, IndirectObject): walk(kid, ref)
            else:
                assert kid['/Type'] == '/OBJR' and role == '/Link'
                annotation_ref = kid.raw_get('/Obj'); annotation = annotation_ref.get_object()
                assert annotation['/Subtype'] == '/Link'
                assert parent_tree[annotation['/StructParent']] == ref
                assert obj.get('/Alt') and annotation.get('/Contents')
                objects.add(annotation_ref.idnum)

    for ref in tree['/K']: walk(ref, root.raw_get('/StructTreeRoot'))
    assert counts.get('/H1') == 1 and counts.get('/Document') == 1
    content_seen=set(); font_names=set(); links=0
    for index,page in enumerate(reader.pages):
        assert page['/Tabs'] == '/S'
        parents=parent_tree[page['/StructParents']]
        stack=[]
        for operands,op in ContentStream(page.get_contents(), reader).operations:
            if op in (b'BMC', b'BDC'):
                tag=str(operands[0]); mcid=operands[1].get('/MCID') if op==b'BDC' else None
                if mcid is not None:
                    key=(index,int(mcid)); assert key not in content_seen
                    content_seen.add(key); assert mcr[key] == parents[int(mcid)]
                stack.append((tag,mcid))
            elif op==b'EMC':
                assert stack, 'Unbalanced marked content';stack.pop()
            elif op in (b'Tj', b'TJ', b"'", b'"'):
                assert any(tag=='/Artifact' or mcid is not None for tag,mcid in stack), 'Untagged text'
        assert not stack
        for f in page['/Resources'].get('/Font', {}).values():
            font=f.get_object();font_names.add(str(font.get('/BaseFont')))
            descendants=font.get('/DescendantFonts',[font])
            for item in descendants:
                descriptor=item.get_object().get('/FontDescriptor')
                if descriptor: descriptor=descriptor.get_object()
                assert descriptor and any(key in descriptor for key in ('/FontFile','/FontFile2','/FontFile3')), 'Unembedded font'
        for ref in page.get('/Annots',[]):
            a=ref.get_object();assert ref.idnum in objects, 'Annotation not in structure tree'
            if a['/Subtype']=='/Link':
                links+=1
                if a.get('/A'): assert str(a['/A'].get('/URI','')).startswith('https://')
                else: assert a.get('/Dest') and a['/Dest'][0].idnum in page_refs
    assert content_seen == set(mcr), 'Unreachable or missing tagged content'
    return {'taggedContent':len(mcr),'structureRoles':counts,'taggedLinks':links,'embeddedFonts':sorted(font_names),'pdfUaCertified':False}


def verify(packet):
    packet=Path(packet).resolve()
    def file(relative):
        candidate=(packet/relative).resolve()
        assert candidate.is_relative_to(packet), 'Packet path escapes its directory'
        assert candidate.is_file(), 'Missing packet file: '+relative
        return candidate
    def read(relative): return json.loads(file(relative).read_text())
    manifest=read('build-manifest.json')
    for relative,asset in manifest['assets'].items():
        p=file(relative); assert sha(p)==asset['sha256'] and p.stat().st_size==asset['bytes'], relative
    if (packet/'packet-manifest.json').is_file():
        for relative,asset in read('packet-manifest.json')['files'].items():
            p=file(relative); assert sha(p)==asset['sha256'] and p.stat().st_size==asset['bytes'], relative
    web=read('web-manuscript.json')
    assert manifest['releaseState']=='private_draft' and manifest['sampleApproval']=='pending'
    assert web['editionId']==manifest['editionId'] and web['version']==manifest['version']
    if (packet/'manuscript-source.json').is_file():
        source=read('manuscript-source.json')
        assert sha(file('manuscript-source.json'))==manifest['sourceSha256']
        assert source['manuscript']==web
    refs={r['id'] for r in web['references']}
    assert len(refs)==len(web['references'])
    assert {sid for c in web['chapters'] for b in c['blocks'] for sid in b['sourceIds']} <= refs
    results=[]
    for variant,asset in manifest['pdf']['assets'].items():
        path=file(asset['file']); assert sha(path)==asset['sha256']
        reader=PdfReader(path)
        page_text=[p.extract_text() or '' for p in reader.pages]
        # Header/footer text is a separate artifact; omit its four extracted lines
        # so page boundaries do not interrupt manuscript paragraphs.
        label='PRIVATE SYNTHETIC FIXTURE' if manifest['synthetic'] else 'PRIVATE EDITORIAL DRAFT'
        assert all(t.startswith('REMAPRX\n'+label+'\n') for t in page_text)
        compact=normalize('\n'.join('\n'.join(t.splitlines()[4:]) for t in page_text))
        scoped=web if variant=='full' else read('sample-candidate.json' if variant=='preview' else 'summary-candidate.json')
        assert normalize(web['medicalNotice']) in compact
        checked=0
        for c in scoped['chapters']:
            for b in c['blocks']:
                phrases=[b['text']] if b['type'] in ('paragraph','callout') else b['items'] if b['type'] in ('list','questions') else [b['caption'],*b['columns'],*(cell for row in b['rows'] for cell in row)]
                for phrase in phrases:
                    assert normalize(phrase) in compact,(variant,c['id'],phrase[:80])
                checked+=1
        for r in scoped['references']:
            assert normalize(r['title']) in compact, (variant,r['id'],'title')
            assert normalize(r.get('note','')) in compact,(variant,r['id'],'bibliography')
        assert len(reader.outline)==len(asset['bookmarks'])
        for bookmark in reader.outline: assert 0<=reader.get_destination_page_number(bookmark)<len(reader.pages)
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                assert page.chars
                assert all(0<=c['x0'] and c['x1']<=page.width+.5 and 0<=c['top'] and c['bottom']<=page.height+.5 for c in page.chars),'Text outside page'
                assert all(c['text']!='\ufffd' for c in page.chars),'Replacement glyph'
        results.append({'variant':variant,'pages':len(reader.pages),'blocksMatched':checked,'referencesMatched':len(scoped['references']),'sha256':sha(path),**structure_check(reader)})
    return {'status':'PASS','editionId':web['editionId'],'version':web['version'],'pdfs':results,
            'scope':'Packet-contained hashes, manuscript/PDF text and reference parity, bookmark destinations, PDF structure, link annotations, embedded fonts and page geometry.',
            'limits':'Not a fresh original-paper audit, clinical/editorial/legal sign-off, screen-reader user test or PDF/UA certification.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--packet',default='.');parser.add_argument('--report')
    args=parser.parse_args();result=verify(args.packet)
    if args.report: Path(args.report).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
