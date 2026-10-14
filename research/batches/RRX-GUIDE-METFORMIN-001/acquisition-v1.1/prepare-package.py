"""Build metadata request only after integrator GP; never dispatch or acquire."""
import argparse
import datetime
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PACKAGE_ROOT = 'RRX-GUIDE-METFORMIN-001-1.1'
EXCLUDED = {'INPUT-MANIFEST.json','readiness.json','package-receipt.json','validation.json'}

def sha(b):return hashlib.sha256(b).hexdigest()

def entries():
    return [p for p in sorted(ROOT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in EXCLUDED]

def manifest():
    files=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in entries()]
    (ROOT/'INPUT-MANIFEST.json').write_text(json.dumps({'operationId':'RRX-GUIDE-METFORMIN-001-ACQUIRE','planVersion':'1.1','packetRoot':PACKAGE_ROOT,'rawPapers':0,'noReaderData':True,'files':files},indent=2)+'\n')
    print(json.dumps({'manifestFiles':len(files),'status':'prepared_for_integrator_GP'}))

def package(output):
    r=json.loads((ROOT/'readiness.json').read_text())
    assert r['decision']=='PASS' and r['acceptedBy']=='codex/root', 'Root GP acceptance required'
    assert r['inputManifestSha256']==sha((ROOT/'INPUT-MANIFEST.json').read_bytes()), 'Readiness manifest changed'
    for f in json.loads((ROOT/'INPUT-MANIFEST.json').read_text())['files']:
        assert sha((ROOT/f['path']).read_bytes())==f['sha256'], 'Changed input: '+f['path']
    output=Path(output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
    members=entries()+[ROOT/'INPUT-MANIFEST.json',ROOT/'readiness.json',ROOT/'validation.json']
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for f in members:
            name=PACKAGE_ROOT+'/'+str(f.relative_to(ROOT))
            info=zipfile.ZipInfo(name, date_time=(2026,10,12,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,f.read_bytes())
    with zipfile.ZipFile(output) as z:
        assert len(z.namelist())==len(members)
        assert all(z.read(PACKAGE_ROOT+'/'+str(f.relative_to(ROOT)))==f.read_bytes() for f in members)
        assert not any(Path(n).suffix.lower() in {'.pdf','.doc','.docx','.epub'} for n in z.namelist())
        nested=ROOT/'coordination/RRX-GAP-001-1.1-request.zip'
        with zipfile.ZipFile(nested) as nz:
            assert not any(Path(n).suffix.lower() in {'.pdf','.doc','.docx','.epub'} for n in nz.namelist())
    result={'operationId':'RRX-GUIDE-METFORMIN-001-ACQUIRE','version':'1.1','status':'PREPARED_NOT_DISPATCHED','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'path':str(output),'sha256':sha(output.read_bytes()),'bytes':output.stat().st_size,'members':len(members),'rawPapers':0,'readBackHashesVerified':True,'receiverAccessVerified':False,'sourcesAcquired':0,'sourceExtractionPerformed':False}
    (ROOT/'package-receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--manifest',action='store_true');parser.add_argument('--output');args=parser.parse_args()
    if args.manifest:manifest()
    if args.output:package(args.output)
