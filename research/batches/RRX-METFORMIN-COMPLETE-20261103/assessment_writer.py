"""Serialize manually authored evidence fields; never fill absent fields."""
import hashlib
import json
from pathlib import Path

B = Path(__file__).resolve().parent
QUESTIONS = json.loads((B/'review-questions-and-inputs.json').read_text())['questions']
SOURCES = {s['sourceId']:s for s in json.loads((B/'source-access.json').read_text())['sources']}

def write_review(sid, title, groups, appraisal, assets=None, completion=None):
    assert len(groups) == 15, (sid, len(groups))
    inputs=[]; answers={}
    for q,(locator,cells,interpretation) in zip(QUESTIONS,groups):
        assert len(cells)==len(q['inputFields']), (sid,q['id'],len(cells))
        values=[]
        for field,cell in zip(q['inputFields'],cells):
            status='assessed'
            for prefix,state in [('NR:','not_reported'),('NA:','not_applicable'),('GAP:','not_accessible'),('UNCHECKED:','not_checked')]:
                if cell.startswith(prefix):status=state;cell=cell[len(prefix):].strip();break
            assert cell.strip(), (sid,field)
            inputs.append({'questionId':q['id'],'field':field,'value':cell,'status':status,'locators':[locator]})
            values.append(cell)
        assert interpretation.strip(), (sid,q['id'])
        answers[q['id']]={'answer':' '.join(values)+' '+interpretation,'status':('partial' if any(i['status'] in ['not_accessible','not_checked'] for i in inputs if i['questionId']==q['id']) else 'assessed'),'locators':[locator]}
    assert len(inputs)==67
    source_assets=assets or SOURCES[sid]['assets']
    unresolved=[i['field'] for i in inputs if i['status'] in ['not_accessible','not_checked']]
    record={'sourceId':sid,'title':title,'version':'metformin-assessment-20261104.1',
            'sourceAssets':[{'path':a['path'],'sha256':a['sha256']} for a in source_assets],
            'questions':answers,'inputs':inputs,'appraisal':appraisal,
            'completion':completion or ('partial' if unresolved else 'assessed_available_packet'),
            'unresolvedInputs':unresolved,'independentVerification':'pending','humanApproval':'pending',
            'release':'private_candidate','plan':'plan.v3.json'}
    dest=B/'assessments';dest.mkdir(exist_ok=True)
    (dest/(sid+'.json')).write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n')
    sections=[f'# {title}','Private source assessment. Independent verification and human approval are pending.']
    for q in QUESTIONS:sections += ['\n## '+q['question'],answers[q['id']]['answer']]
    sections += ['\n## Overall appraisal',appraisal,'\n## Source trail']
    sections += [f'- `{a["sha256"]}`: `{a["path"]}`' for a in source_assets]
    if unresolved:sections += ['\nUnresolved source inputs: '+', '.join(unresolved)+'.']
    (dest/(sid+'.md')).write_text('\n\n'.join(sections)+'\n')
    print(sid,record['completion'],len(inputs),'inputs;',len(unresolved),'unresolved')
