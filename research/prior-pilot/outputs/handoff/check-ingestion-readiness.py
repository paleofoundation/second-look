"""Read-only operational preflight. Run from this project's root. Does not dispatch or import."""
import argparse,json,pathlib,hashlib,sys
p=argparse.ArgumentParser();p.add_argument('--operation',required=True,choices=['grokbot-handoff','grokbot-request','source-extraction','corpus-import']);p.add_argument('--batch',required=True);p.add_argument('--receipt');p.add_argument('--candidate-acceptance');p.add_argument('--plan-id');p.add_argument('--candidate-manifest');a=p.parse_args()
R=pathlib.Path.cwd();O=R/'outputs';fail=[];mechanism_requirement={'status':'not_loaded','performed_operation':False}
def load(p):return json.loads(p.read_text())
def check(test,reason):
 if not test:fail.append(reason)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mechanism_report(mc,plan):
 cfg=mc.get('mechanismIngestionRequirement',{})
 report={'status':cfg.get('status','not_registered'),'plan_id':cfg.get('plan_id'),'required_for':['source-extraction','corpus-import'],'scope':'Prospective compatible scientific operations; historical receipts and acquisition-only readiness unchanged','readiness_granted':False,'performed_operation':False,'adoption_record':cfg.get('adoption_record'),'contracts':cfg.get('contracts',[])}
 if a.operation in report['required_for']:
  check(cfg.get('status')=='ADOPTED_PROSPECTIVELY','Mechanism ingestion requirement is not registered as adopted')
  expected={}
  for item in cfg.get('contracts',[]):
   path=O/item.get('path','MISSING')
   check(path.exists() and sha(path)==item.get('sha256'),'Mechanism contract hash mismatch: '+item.get('role','unknown'))
   expected[item.get('role')]=item.get('sha256')
  incorporated=plan.get('mechanism_contract',{})
  check(incorporated.get('plan_id')==cfg.get('plan_id'),'Scientific operation plan must incorporate the adopted mechanism contract')
  for role in ['plan','schema','coverage']:
   check(bool(expected.get(role)) and incorporated.get(role+'_sha256')==expected.get(role),'Scientific operation mechanism '+role+' hash missing/mismatched')
 return report
# Prospective scientific plans are explicitly selected; the legacy acquisition route stays unchanged.
if a.plan_id and a.operation in ['source-extraction','corpus-import']:
 try:
  mc=load(O/'mission-control.json');registration=mc.get('scientificOperationPlans',{}).get(a.plan_id,{})
  checker=R/registration.get('readiness_checker','MISSING')
  if not checker.is_file() or sha(checker)!=registration.get('readiness_checker_sha256'):raise ValueError('Scientific checker is missing or differs from registered hash')
  import importlib.util
  spec=importlib.util.spec_from_file_location('scientific_gate',checker);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  report=module.run(R,checker.parent,a.operation,a.batch,a.plan_id,a.candidate_manifest,a.candidate_acceptance)
 except (OSError,ValueError,KeyError,TypeError) as e:report={'status':'HOLD','errors':[str(e)],'performed_operation':False}
 print(json.dumps(report,indent=2));sys.exit(bool(report.get('errors')))
try:
 mc=load(O/'mission-control.json');gate=mc.get('ingestionPlanReadiness',{});planpath=O/gate.get('path','MISSING');plan=load(planpath)
 mechanism_requirement=mechanism_report(mc,plan)
 check(gate.get('status')=='READY','Mission Control plan is not READY')
 check(gate.get('sha256')==sha(planpath),'Plan hash mismatch')
 check(gate.get('plan_id')==plan['plan_id'],'Plan identity mismatch')
 if plan['plan_id'] in {'SL-INGEST-3.0-FETCH30','SL-INGEST-3.1-FETCH30'}:
  import importlib.util
  spec=importlib.util.spec_from_file_location('fetch30_checker',planpath.parent/'check_packet.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  report=module.check_packet(planpath.parent);fail.extend(report['failures'])
  check(a.batch in {b['id'] for b in plan['batch_order']},'Unknown acquisition batch')
  check(a.operation in ['grokbot-handoff','grokbot-request'],'Fetch-only contract: scientific extraction/import requires actual source receipt and a checked applicable extraction/mapping schema before readiness can pass')
  print(json.dumps({'operation':a.operation,'batch':a.batch,'status':'HOLD' if fail else 'READY','plan_id':plan['plan_id'],'plan_sha256':sha(planpath),'reasons':fail,'performed_operation':False,'mechanism_requirement':mechanism_requirement,'next':'READY permits a prepared acquisition handoff; no external request, ingestion or publication is performed by this checker.'},indent=2))
  sys.exit(1 if fail else 0)
 check(a.batch in {b['batch_id'] for b in plan['batch_order']},'Unknown batch')
 check(a.batch!='B00','B00 is a retrospective audit, not an acquisition or import batch')
 for item in plan['inputs']:check((R/item['path']).exists() and sha(R/item['path'])==item['sha256'],'Input mismatch: '+item['role'])
 if a.operation in ['source-extraction','corpus-import']:
  check(bool(a.receipt),'Received source receipt required before extraction/import')
  if a.receipt:
   receipt=load(pathlib.Path(a.receipt))
   for k,v in [('plan_id',plan['plan_id']),('plan_sha256',gate['sha256']),('batch_id',a.batch),('schema_sha256',plan['delivery']['schema_sha256']),('triage_status','PASS')]:check(receipt.get(k)==v,'Receipt mismatch: '+k)
   check(bool(receipt.get('assigned_worker')),'Receipt must identify assigned worker')
   check(isinstance(receipt.get('eligible_files'),list) and bool(receipt['eligible_files']),'Eligible file list required')
   for f in receipt.get('eligible_files',[]):check((R/f['path']).exists() and sha(R/f['path'])==f['sha256'],'Receipt source hash mismatch')
 if a.operation=='corpus-import':
  check(bool(a.candidate_acceptance),'Candidate acceptance required before import')
  if a.candidate_acceptance:
   c=load(pathlib.Path(a.candidate_acceptance));check(c.get('plan_sha256')==gate['sha256'] and c.get('batch_id')==a.batch,'Candidate plan/batch mismatch')
   for name in ['schema','semantic','source_hashes','identity','count_reconciliation','record_page_diff','independent_audit','repeat_import','mechanisms']:
    item=c.get('checks',{}).get(name,{});check(item.get('status')=='PASS' and bool(item.get('evidence_path')),'Candidate check incomplete: '+name)
    if item.get('evidence_path'):check((R/item['evidence_path']).exists(),'Candidate evidence missing: '+name)
   check(c.get('accepted_base_sha256')==sha(R/'outputs/research/evidence/corpus.json'),'Accepted base changed; reconcile concurrent records first')
except (OSError,ValueError,KeyError,TypeError) as e:fail.append('Missing or malformed planning input: '+str(e))
print(json.dumps({'operation':a.operation,'batch':a.batch,'status':'HOLD' if fail else 'READY','reasons':fail,'performed_operation':False,'mechanism_requirement':mechanism_requirement,'next':'Record actual operation with plan hash in operation log before dispatch/extraction/import; READY is not execution evidence.'},indent=2))
sys.exit(1 if fail else 0)
