"""Seal and verify the actual transferable ZIP in a fresh directory."""
import hashlib, json, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

B=Path(__file__).resolve().parent
PRIVATE=B.parents[3]/'private-guides/metformin-candidate3-20261104'
packet=PRIVATE/'handoff/Metformin-candidate-3-review-packet'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v): Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')

review=read(B/'review.json')
for issue in review['issueDispositions']:
    if issue['id']=='PORTABLE-VERIFICATION':
        issue['status']='corrected'
        issue['disposition']='Verifier and required manuscript/artifact inputs are bundled. It uses packet-relative files and never opens original Mac source paths. Exact extracted-ZIP results are recorded separately in portability-check.json.'
write(B/'review.json',review)
artifact=read(B/'guide-artifacts.json');artifact['modelReview']['sha256']=sha(B/'review.json');write(B/'guide-artifacts.json',artifact)
shutil.copy2(B/'review.json',packet/'review.json')
shutil.copy2(B.parents[2]/'scripts/guide-renderer/verify-packet.py',packet/'verify-packet.py')
write(packet/'packet-manifest.json',{'schemaVersion':1,'editionId':review['editionId'],'files':{str(p.relative_to(packet)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(packet.rglob('*')) if p.is_file() and p.name!='packet-manifest.json'}})
archive=PRIVATE/'Metformin-candidate-3-review-packet.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for p in sorted(packet.rglob('*')):
        if p.is_file():z.write(p,str(Path(packet.name)/p.relative_to(packet)))
root=Path(tempfile.mkdtemp(prefix='remaprx-portable-candidate3-'))
with zipfile.ZipFile(archive) as z:z.extractall(root)
extracted=root/packet.name
# Import dependencies before the audit hook, then forbid reads of either the
# original workspace or another local user's source tree during verification.
runner=root/'run_isolated_check.py'
runner.write_text('''import importlib.util, pathlib, sys
base=pathlib.Path(sys.argv[1]).resolve()
spec=importlib.util.spec_from_file_location('packet_verifier',base/'verify-packet.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def audit(event,args):
    if event=='open' and isinstance(args[0],(str,bytes)):
        value=str(args[0])
        if value.startswith(('/Users/','/workspace/')) and not value.startswith(sys.prefix+'/'):
            raise RuntimeError('Unexpected host-dependent read: '+value)
sys.addaudithook(audit)
import json
print(json.dumps(module.verify(base)))
''')
result=subprocess.run([sys.executable,str(runner),str(extracted)],cwd=root,text=True,capture_output=True)
if result.returncode:raise RuntimeError(result.stderr)
verified=json.loads(result.stdout)
assert verified['status']=='PASS'
asset=next(extracted.glob('*-full.pdf'));asset.write_bytes(asset.read_bytes()+b'\nTAMPER-NEGATIVE-CONTROL\n')
negative=subprocess.run([sys.executable,str(runner),str(extracted)],cwd=root,text=True,capture_output=True)
assert negative.returncode!=0 and 'AssertionError' in negative.stderr,'Tampered file was not rejected'
receipt={'status':'PASS','editionId':review['editionId'],'zipSha256':sha(archive),'packetManifestSha256':sha(packet/'packet-manifest.json'),'extractedDirectory':str(root),'originalHostFileReads':'Denied /Users/ and /workspace/ reads except installed Python runtime under sys.prefix; verification passed without original workspace files','tamperedPdf':'Rejected','result':verified}
write(B/'portability-check.json',receipt)
write(B/'handoff-package.json',{'editionId':review['editionId'],'archive':{'path':str(archive),'sha256':sha(archive),'bytes':archive.stat().st_size},'packetManifestSha256':sha(packet/'packet-manifest.json'),'files':read(packet/'packet-manifest.json')['files'],'verificationReceiptSha256':sha(B/'portability-check.json'),'releaseState':'private_review_candidate','humanApprovals':'pending'})
print(json.dumps({'status':'PASS','archive':str(archive),'sha256':sha(archive),'bytes':archive.stat().st_size,'originalHostReads':'denied','tamperedPdf':'rejected'}))
