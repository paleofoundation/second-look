"""Validate/stage/diff/apply an isolated private intake; no application writer."""
import argparse,collections,hashlib,json,os,subprocess,tempfile,datetime
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[2]
OUTPUTS={'rows':'imported/rows.jsonl','reports':'imported/reports.jsonl','assets':'imported/assets.jsonl','assertions':'imported/assertions.jsonl','reviewObligations':'imported/review-obligations.jsonl'}
def digest(x):return hashlib.sha256(x).hexdigest()
def read(p):return json.loads(p.read_text())
def encoded(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def write(p,x):p.write_bytes(encoded(x))
def schema_check(value,schema):
 # Complete implementation of the small declared schema vocabulary, with no dependency.
 if 'const' in schema:assert value==schema['const'],'const'
 if 'enum' in schema:assert value in schema['enum'],'enum'
 if 'type' in schema:
  t=schema['type'];assert {'object':isinstance(value,dict),'array':isinstance(value,list),'string':isinstance(value,str),'boolean':isinstance(value,bool),'integer':isinstance(value,int) and not isinstance(value,bool)}[t],'type'
 if isinstance(value,dict):
  assert set(schema.get('required',[]))<=value.keys(),'required'
  for k,s in schema.get('properties',{}).items():
   if k in value:schema_check(value[k],s)
 if isinstance(value,list):
  assert len(value)>=schema.get('minItems',0) and len(value)<=schema.get('maxItems',float('inf')),'array length'
  for x in value:schema_check(x,schema.get('items',{}))
def validate(c):
 schema_check(c,read(B/'INGEST-SCHEMA.json'));assert c['base']=='d118d305b59cac5e54ca7f9e5aa55cea682d2cee'
 rows=c['rows'];assert len({r['inputRowId'] for r in rows})==408
 assert {r['inputRowId'] for r in rows}=={r['inputRowId'] for r in read(B/'INPUT-ROWS.json')['rows']}
 reportIds={r['id'] for r in c['reports']};assert len(reportIds)==len(c['reports']);assetIds={r['id'] for r in c['assets']};assert len(assetIds)==len(c['assets']);assertionIds={r['id'] for r in c['assertions']};assert len(assertionIds)==len(c['assertions'])
 for r in rows:
  assert r['reportId'] is None or r['reportId'] in reportIds;assert set(r['assetIds'])<=assetIds and set(r['assertionIds'])<=assertionIds;assert r['reason'] and r['nextAction'];assert r['acceptedSupport']==False and r['scientificExtraction']=='not_extracted_in_this_intake'
  if 'vitiligo' in r['folder']:assert r['disposition']=='held' and not r['assetIds'] and not r['assertionIds']
  if r['disposition'] in ['rejected','held']:assert not r['assertionIds']
  if r['reason']=='exact_source_asset_already_recorded':assert r['priorAssetReference']
  assert not any(k in r for k in ['grade','benefitGrade','released','humanApproved'])
 for r in c['reports']:
  assert r['acceptedSupport']==False and r['humanReview']=='pending' and r['studyFamilyId'] is None;assert r['idNamespace']=='batch_intake_report_identity_not_a_new_canonical_paper';assert set(r['assetIds'])<=assetIds
 for r in c['assets']:
  assert r['id']=='ASSET-'+r['sha256'][:24] and len(r['sha256'])==64;assert r['completeScientificExtraction']==False and r['numericExtractionVerified']==False;assert r['ref'].startswith('$REMAPRX_REED_ROOT/')
 for r in c['assertions']:
  assert r['reportId'] in reportIds and r['inputRowId'] in {x['inputRowId'] for x in rows};assert r['basis']=='supplier_reported_assertion' and r['verificationState']=='pending_source_level_verification' and not r['acceptedSupport'];assert r['locator']['sourcePaperLocator']=='not_extracted_in_this_intake'
 reviews=c['reviewObligations'];assert len({r['reportId'] for r in reviews})==len(reviews)
 for r in reviews:
  assert r['reportId'] in reportIds and r['complete']==False and r['humanApproval']=='pending' and r['publicationState']=='private_draft';assert [q['id'] for q in r['questionInputs']]==['Q'+str(i).zfill(2) for i in range(1,16)];assert all(q['status']=='not_extracted' and q['answer'] is None for q in r['questionInputs'])
 assert c['counts']['dispositions']==dict(collections.Counter(r['disposition'] for r in rows))
 for name,counts in c['counts']['byInput'].items():assert counts==dict(collections.Counter(r['disposition'] for r in rows if r['sourceInput']==name))
 assert c['counts']['newScientificResultsAccepted']==c['counts']['newGradesAssigned']==c['counts']['humanReviewed']==c['counts']['released']==0
 return {'status':'PASS','counts':c['counts'],'scope':'technical private receipt/assertion intake only; scientific/human/release pending'}
def payloads(c):return {f:b''.join(encoded(x) for x in c[k]) for k,f in OUTPUTS.items()}
def verify_input_file(ref,expected,bindings):
 name,_,relative=ref[1:].partition('/');assert ref.startswith('$') and name in bindings,'Missing logical source binding: '+ref
 root=Path(bindings[name]).resolve();p=(root/relative).resolve();assert p.is_relative_to(root),'Source path escapes declared root'
 assert p.is_file(),'Missing private dependency: '+ref;assert digest(p.read_bytes())==expected,'Source changed: '+ref
 return True
def verify_sources(c):
 bindings={name:os.environ[name] for name in ['REMAPRX_REED_ROOT','REMAPRX_BRIDGE_INPUTS'] if os.environ.get(name)};assert len(bindings)==2,'Bind both private source roots for strict source verification'
 inputs=read(B/'INPUTS.json')['inputs']
 for r in inputs:verify_input_file(r['ref'],r['sha256'],bindings)
 for r in c['assets']:verify_input_file(r['ref'],r['sha256'],bindings)
 return {'inputFilesVerified':len(inputs),'assetFilesVerified':len(c['assets']),'sourceIntegrity':'PASS','scientificExtraction':False}
def source_guard():
 readiness=read(B/'READINESS.json')
 for f,h in readiness['hashes'].items():assert digest((B/f).read_bytes())==h,'GP dependency changed: '+f
 subprocess.run(['git','merge-base','--is-ancestor',read(B/'PLAN.json')['base'],'HEAD'],cwd=ROOT,check=True)
 changed=subprocess.check_output(['git','diff','--name-only',read(B/'PLAN.json')['base']],cwd=ROOT,text=True).splitlines();assert all(f.startswith(str(B.relative_to(ROOT))+'/') for f in changed),'Nonpacket base changes require reconciliation'
 verify_sources(read(B/'CANDIDATE.json'))
def stage(c,folder=B):
 validate(c);data=payloads(c);expected={f:digest((folder/f).read_bytes()) if (folder/f).exists() else None for f in data};return {'candidateSha256':digest(encoded(c)),'base':c['base'],'expectedOutputHashes':expected,'newOutputHashes':{f:digest(raw) for f,raw in data.items()},'planSha256':digest((B/'PLAN.json').read_bytes())}
def apply(c,staged,folder=B):
 validate(c);assert staged['candidateSha256']==digest(encoded(c)),'candidate changed';assert staged['planSha256']==digest((B/'PLAN.json').read_bytes()),'plan changed'
 lock=folder/'.ingest-lock';fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd)
 try:
  journal=folder/'apply-journal.json'
  if journal.exists():assert read(journal)['state']=='complete','Interrupted operation requires recovery'
  data=payloads(c)
  for f,expected in staged['expectedOutputHashes'].items():assert (digest((folder/f).read_bytes()) if (folder/f).exists() else None)==expected,'concurrent target change: '+f
  changed=[f for f,raw in data.items() if not (folder/f).exists() or (folder/f).read_bytes()!=raw]
  write(journal,{'state':'intent','candidateSha256':staged['candidateSha256'],'targets':list(data),'changed':changed})
  for f in changed:
   p=folder/f;p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_suffix('.pending');temp.write_bytes(data[f]);os.replace(temp,p)
  write(journal,{'state':'complete','candidateSha256':staged['candidateSha256'],'targets':list(data),'changed':changed,'rollback':'Fresh batch outputs only. Preserve prior receipts; remove newly created imported files only if recovering a failed first apply after inspecting exact hashes. Never modify prior corpus.'})
  return {'status':'PASS','changedFiles':changed,'changedFileCount':len(changed),'outputHashes':staged['newOutputHashes'],'scientificApproval':False}
 finally:lock.unlink()
def verify(c):
 result=validate(c)
 for f,raw in payloads(c).items():assert (B/f).read_bytes()==raw,'Applied payload differs: '+f
 changed=subprocess.check_output(['git','diff','--name-only',c['base']],cwd=ROOT,text=True).splitlines();assert all(f.startswith(str(B.relative_to(ROOT))+'/') for f in changed),'Nonpacket tracked changes'
 for f in ['data/content.json','data/public-content.json','data/reader-evidence.json','data/public-evidence-assessments.json','editorial/evidence-assessments.json','editorial/outcome-summary/authored.json','data/drug-status-table.json','data/public-review-metadata.json']:
  assert (ROOT/f).read_bytes()==subprocess.check_output(['git','show',c['base']+':'+f],cwd=ROOT),f
 assert not list(B.rglob('*.pdf')) and not list(B.rglob('*.html'))
 return result
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('command',choices=['validate','stage','diff','apply','verify']);args=parser.parse_args();c=read(B/'CANDIDATE.json')
 if args.command=='validate':result=validate(c);write(B/'VALIDATE.json',result)
 elif args.command=='stage':source_guard();result=stage(c);write(B/'STAGE.json',result)
 elif args.command=='diff':result={'base':c['base'],'targetFiles':list(OUTPUTS.values()),'newCounts':c['counts'],'applicationChanges':0,'previousCorpusChanges':0};write(B/'DIFF.json',result)
 elif args.command=='apply':source_guard();result=apply(c,read(B/'STAGE.json'));write(B/'APPLY.json',result)
 else:result=verify(c)
 print(json.dumps(result,indent=2))
