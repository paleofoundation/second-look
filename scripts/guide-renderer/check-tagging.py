"""Regression checks against rendered fixtures, including broken-PDF controls."""
import argparse, importlib.util, json
from pathlib import Path
from pypdf import PdfReader
from pypdf.generic import NameObject, NumberObject

spec=importlib.util.spec_from_file_location('packet_verification',Path(__file__).with_name('verify-packet.py'))
verification=importlib.util.module_from_spec(spec);spec.loader.exec_module(verification)


def check(packet):
    packet=Path(packet)
    result=verification.verify(packet)
    manifest=json.loads((packet/'build-manifest.json').read_text())
    path=packet/manifest['pdf']['assets']['full']['file']
    mutations={
        'missing structure tree':lambda r:r.trailer['/Root'].pop('/StructTreeRoot'),
        'missing marked status':lambda r:r.trailer['/Root'].pop('/MarkInfo'),
        'missing document language':lambda r:r.trailer['/Root'].pop('/Lang'),
        'wrong parent-tree index':lambda r:r.pages[0].__setitem__(NameObject('/StructParents'),NumberObject(999999)),
    }
    def remove_font_program(reader):
        for font in reader.pages[0]['/Resources']['/Font'].values():
            descriptor=font.get_object().get('/FontDescriptor')
            if descriptor:
                descriptor=descriptor.get_object()
                for key in ('/FontFile','/FontFile2','/FontFile3'):
                    if key in descriptor:
                        del descriptor[key];return
        raise RuntimeError('Fixture has no embedded font to mutate')
    mutations['unembedded font']=remove_font_program
    rejected=[]
    for label,mutate in mutations.items():
        reader=PdfReader(path);mutate(reader)
        try: verification.structure_check(reader)
        except (AssertionError,KeyError,IndexError): rejected.append(label)
        else: raise AssertionError('Broken control was accepted: '+label)
    return {'status':'PASS','variants':len(result['pdfs']),'rejectedBrokenControls':rejected}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--packet',required=True)
    print(json.dumps(check(parser.parse_args().packet)))
