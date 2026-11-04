"""Record hashes and block-to-assessment links without putting the manuscript in Git."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent
G=B.parents[3]/'private-guides/metformin-20261104'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
source=read(G/'manuscript-source.json');m=source['manuscript'];coverage=read(B/'coverage.json');rows={r['sourceId']:r for r in coverage['coverage']}
blocks=[]
for c in m['chapters']:
 for i,b in enumerate(c['blocks']):
  links=[]
  for sid in b['sourceIds']:
   r=rows[sid]
   links.append({'sourceId':sid,'assessment':r.get('assessment',r.get('record')),'sha256':r.get('sha256',sha(B/r.get('record','context-and-exclusions.json')))})
  blocks.append({'id':m['editionId']+':'+c['id']+':'+str(i),'chapterId':c['id'],'blockIndex':i,'type':b['type'],'blockSha256':hashlib.sha256(json.dumps(b,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'sources':links,'uncitedPurpose':'Editorial navigation, source-scope disclosure or personal worksheet' if not links else None})
manifest={'productId':m['productId'],'editionId':m['editionId'],'version':m['version'],'state':'private_candidate','source':{'path':str(G/'manuscript-source.json'),'sha256':sha(G/'manuscript-source.json')},'buildManifest':{'path':str(G/'output/build-manifest.json'),'sha256':sha(G/'output/build-manifest.json')},'assets':[{'file':str(G/'output'/f),'sha256':a['sha256'],'bytes':a['bytes']} for f,a in read(G/'output/build-manifest.json')['assets'].items()],'assessmentCoverageSha256':sha(B/'coverage.json'),'independentClinicalReview':'pending','humanEditorialApproval':'pending','commercialLegalApproval':'pending','release':'not_deployed_or_for_sale','pdfAccessibility':'Selectable text, working links and bookmarks; untagged, not PDF/UA certified.'}
(B/'guide-artifacts.json').write_text(json.dumps(manifest,indent=2)+'\n')
(B/'guide-block-map.json').write_text(json.dumps({'editionId':m['editionId'],'sourceSha256':sha(G/'manuscript-source.json'),'blocks':blocks},indent=2)+'\n')
print('Recorded',len(blocks),'blocks and',len(manifest['assets']),'private assets')
