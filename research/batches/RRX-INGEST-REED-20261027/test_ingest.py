import copy,importlib.util,json,tempfile
from pathlib import Path
B=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('reed_ingest',B/'ingest.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
spec2=importlib.util.spec_from_file_location('reed_prepare',B/'prepare.py');p=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(p)
c=json.loads((B/'CANDIDATE.json').read_text());checks=[]
def reject(name,fn):
 try:fn()
 except (AssertionError,FileExistsError):checks.append({'name':name,'status':'PASS'});return
 raise AssertionError('Fixture unexpectedly accepted: '+name)
def mutation(name,mutate):
 x=copy.deepcopy(c);mutate(x);reject(name,lambda:m.validate(x))
m.validate(c);checks.append({'name':'valid408rowcandidate','status':'PASS'})
mutation('rejectduplicateinputidentity',lambda x:x['rows'][1].update(inputRowId=x['rows'][0]['inputRowId']))
mutation('rejectmissingrowcoverage',lambda x:x['rows'].pop())
mutation('rejectacceptedtechnicalrow',lambda x:x['rows'][0].update(acceptedSupport=True))
mutation('rejectorphanreport',lambda x:x['rows'][0].update(reportId='missing'))
mutation('rejectassetidhashmismatch',lambda x:x['assets'][0].update(sha256='0'*64))
mutation('rejectinventedgrade',lambda x:x['rows'][0].update(grade='High'))
mutation('rejectvitiligoholdbypass',lambda x:next(r for r in x['rows'] if 'vitiligo' in r['folder']).update(disposition='ingested'))
mutation('rejectsupplierassertionpromotedtosourcedata',lambda x:x['assertions'][0].update(basis='reported_data'))
mutation('rejectcompletequestionautoapproval',lambda x:x['reviewObligations'][0].update(complete=True))
mutation('rejectfakedispositiontotals',lambda x:x['counts']['dispositions'].update(ingested=999))
mutation('rejectduplicatereviewobligation',lambda x:x['reviewObligations'].append(x['reviewObligations'][0]))
assert p.matches({'pmid':'123','doi':'10.1/a'},{'pmid':'123','doi':'10.1/b'})==False;checks.append({'name':'samePMIDdifferentDOInotautomerged','status':'PASS'})
assert p.ident({'doi':'10.1/a','nct':'NCT00000001'})!=p.ident({'doi':'10.1/b','nct':'NCT00000001'});checks.append({'name':'sameNCTdifferentpapersretainreportidentity','status':'PASS'})
assert p.ident({'title':'[NCT01729260] Actual registered title'})=='registry:NCT01729260';checks.append({'name':'literalNCTnotlostwhenledgercolumnmissing','status':'PASS'})
with tempfile.TemporaryDirectory() as directory:
 folder=Path(directory);st=m.stage(c,folder);r=m.apply(c,st,folder);assert r['changedFileCount']==5;again=m.apply(c,m.stage(c,folder),folder);assert again['changedFileCount']==0;checks.append({'name':'firstapply5repeat0outputchanges','status':'PASS'})
 st=m.stage(c,folder);target=folder/'imported/rows.jsonl';old=target.read_bytes();target.write_bytes(b'concurrent edit\n');reject('concurrenttargetrejectswithoutoverwrite',lambda:m.apply(c,st,folder));assert target.read_bytes()==b'concurrent edit\n';target.write_bytes(old)
 st=m.stage(c,folder);x=copy.deepcopy(c);x['rows'][0]['nextAction']='Different candidate';reject('changedcandidateafterstage',lambda:m.apply(x,st,folder))
 x=copy.deepcopy(st);x['planSha256']='0'*64;reject('changedplanrejects',lambda:m.apply(c,x,folder))
 (folder/'.ingest-lock').write_text('other integrator');reject('exclusiveintegratorlock',lambda:m.apply(c,m.stage(c,folder),folder));(folder/'.ingest-lock').unlink()
 (folder/'apply-journal.json').write_text('{"state":"intent"}');before=target.read_bytes();reject('interruptedintentrequiresrecovery',lambda:m.apply(c,m.stage(c,folder),folder));assert target.read_bytes()==before
for r in c['rows']:
 if r['reason']=='retracted_source':assert not r['assertionIds']
checks.append({'name':'retractedsourcesneveractivated','status':'PASS'})
assert next(r for r in c['rows'] if r['inputRowId']=='baseline-286:050')['disposition']=='held';checks.append({'name':'observedpreprintjournalconflictheld','status':'PASS'})
# Real committed-candidate output idempotence, with first APPLY receipt preserved.
st=m.stage(c);m.write(B/'REPEAT-STAGE.json',st);r=m.apply(c,st);assert r['changedFileCount']==0;m.write(B/'REPEAT-APPLY.json',r);checks.append({'name':'actualpacketreimportzeroscientificpayloadchanges','status':'PASS'})
m.verify(c);checks.append({'name':'appliedoutputsandapplicationpreservation','status':'PASS'})
with tempfile.TemporaryDirectory() as directory:
 folder=Path(directory);source=folder/'source.txt';source.write_text('source version1');bindings={'ROOT':str(folder)};expected=m.digest(source.read_bytes());m.verify_input_file('$ROOT/source.txt',expected,bindings);source.write_text('source version2');reject('concurrentprivatesourcechange',lambda:m.verify_input_file('$ROOT/source.txt',expected,bindings));reject('privatesourcerootescape',lambda:m.verify_input_file('$ROOT/../escape.txt',expected,bindings));reject('missingprivatesourcebinding',lambda:m.verify_input_file('$MISSING/source.txt',expected,bindings))
result={'status':'PASS','checks':checks,'total':len(checks),'independentScientificReview':False};(B/'TESTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
