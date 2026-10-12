"""Rebuild the bounded authored summary projection; does not acquire or regrade evidence."""
import json,hashlib,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
def read(path):return json.loads((ROOT/path).read_text())
def sha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def save(path,value):(ROOT/path).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
rows=read('data/reader-evidence.json')['synthesisRows']; public_rows=read('data/public-reader-evidence.json')['synthesisRows']; old=read('editorial/evidence-assessments.json')['records']; sources=read('data/public-content.json')['sources']
byid={r['id']:r for r in rows}; public_byid={r['id']:r for r in public_rows}; old_byid={r['rowId']:r for r in old}; source_byid={r['id']:r for r in sources}
authored=read('editorial/outcome-summary/authored.json'); trials=read('editorial/outcome-summary/trial-identities.json')['trials']; trials_byid={t['id']:t for t in trials}
labels={'A':'Benefit well supported','B':'Benefit likely','C':'Possible benefit','D':'Benefit uncertain','E':'Benefit not demonstrated','F':'Benefit unlikely or harm observed'}
records=[]; provenance=[]
for item in authored:
 member=[byid[x] for x in item['synthesisIds']]; source_ids=list(dict.fromkeys(s for r in member for s in r['sourceIds'])); ts=[trials_byid[t] for t in item['trialIds']]
 public_trials=[{**{key:t[key] for key in ['id','participants','participantBasis']},'sourceIds':[s for s in t['sourceIds'] if s in source_ids]} for t in ts]
 complete=bool(ts) and all(t['participants'] is not None for t in ts)
 evidence={'rctCount':len(ts),'participants':sum(t['participants'] for t in ts) if complete else None,'participantBasis':'; '.join(t['participantBasis'] for t in ts) if ts else 'No randomized clinical trial is represented in this selected evidence.','trialFamilyIds':item['trialIds'],'sourceIds':list(dict.fromkeys(s for t in public_trials for s in t['sourceIds'])),'trials':public_trials}
 record={'id':item['id'],'synthesisIds':item['synthesisIds'],'drugId':member[0]['drugId'],'conditionId':member[0]['conditionId'],'label':item['label'],'purpose':item['purpose'],'grade':{'value':item['grade'],'label':labels[item['grade']] if item['grade'] else item['ungradedLabel'],'rationale':item['rationale'],'sourceIds':source_ids},'effect':{'label':item['effectLabel'],'detail':item['effectDetail'],'direction':item['direction'],'rationale':item['effectRationale']},'evidence':evidence,'sourceIds':source_ids,'aggregationNote':item['aggregationNote']}
 current_input=sha({'rows':member,'publicRows':[public_byid[x] for x in item['synthesisIds']],'priorAssessments':[old_byid[x] for x in item['synthesisIds']],'sources':[source_byid[x] for x in source_ids]})
 if item.get('assessedInputSha256') != current_input: raise ValueError(f"{item['id']}: evidence changed; actual reassessment is required before rebuilding")
 records.append(record)
 provenance.append({'id':item['id'],'synthesisIds':item['synthesisIds'],'assessedOn':'2026-10-12','method':'selected-source-benefit-v1','authoring':'AI-assisted editorial synthesis of existing accepted records; not fresh source inspection','reviewState':'pending_independent_integration_audit','humanApproval':'not recorded','inputsSha256':sha({'rows':member,'publicRows':[public_byid[x] for x in item['synthesisIds']],'priorAssessments':[old_byid[x] for x in item['synthesisIds']],'sources':[source_byid[x] for x in source_ids]}),'publicRecordSha256':sha(record),'priorAssessmentIds':item['synthesisIds'],'sourceLocators':[basis for x in item['synthesisIds'] for basis in old_byid[x]['basis']],'scope':[{'synthesisId':r['id'],'use':r['use'],'population':r['population'],'comparison':r['comparison'],'endpoint':r['endpoint'],'timepoint':r['timepoint']} for r in member]})
save('data/outcome-summaries.json',{'version':'1.0.0','method':'selected-source-benefit-v1','assessedOn':'2026-10-12','records':records})
save('editorial/outcome-summary/assessments.json',{'version':'1.0.0','method':'selected-source-benefit-v1','inputCount':len(rows),'summaryCount':len(records),'records':provenance})
print(f'Compiled {len(records)} explicitly authored summaries for {len(rows)} preserved synthesis rows.')
