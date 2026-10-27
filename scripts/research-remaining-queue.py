#!/usr/bin/env python3
"""Recompute stage-specific remaining work; never count records as studies."""
import json
import hashlib
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BATCH=ROOT/'research/batches/RRX-INGEST-001'
CORPUS=ROOT/'research/corpus/RRX-INGEST-001'
def read(p):return json.loads(p.read_text())
def rows(p):return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    sources=rows(BATCH/'inventory/source-records.jsonl')
    ledger=read(BATCH/'cited-paper-ledger.json')
    dispositions=read(CORPUS/'draft-science/source-dispositions.json')
    results=rows(CORPUS/'draft-science/results.jsonl')
    reviews=rows(CORPUS/'draft-science/reviews.jsonl')
    result_dispositions=read(CORPUS/'draft-science/result-dispositions.json')
    by_source={d['source_id']:d for d in dispositions}
    # Source-level queue is deliberate: candidate clusters still need human identity
    # adjudication before report/companion ownership can collapse duplicate work.
    queue=[]
    cited={x['paperId'] for x in ledger['records']}
    for s in sources:
        old=by_source.get(s['sourceId'],{}) if s['origin']=='acquisition' else s.get('priorScientificDisposition',{})
        state=old.get('state')
        if state in ('held','quarantined') or old.get('processing_state')=='processing_error':wave=1;action='resolve_hold_before_any_support'
        elif s['origin']=='app' or s['origin']=='mechanism' or s.get('canonicalId') in cited:wave=2;action='finish_current_source_and_review_inputs'
        elif s['origin']=='moa':wave=3;action='identity_and_current_target_screen_only'
        else:wave=3;action='screen_then_resume_historical_group'
        queue.append({'recordId':s['id'],'sourceId':s['sourceId'],'recordedReportId':s.get('canonicalId'),
                      'origin':s['origin'],'wave':wave,'nextAction':action,'preservedDisposition':state,
                      'existingResultIds':old.get('result_ids',[]),'fullReviewComplete':old.get('full_review_complete',False),
                      'reextractExistingResultsAutomatically':False,'independentStudyCount':None})
    counts={'historicalAcquisitionRecords':len(dispositions),'historicalDraftResults':len(results),
            'historicalDraftReviewRecords':len(reviews),'historicalFullScientificReviewsComplete':sum(r.get('full_review_complete') is True for r in reviews),
            'sourceDispositionCounts':dict(sorted(Counter(d['state'] for d in dispositions).items())),
            'sourceProcessingCounts':dict(sorted(Counter(d['processing_state'] for d in dispositions).items())),
            'resultDispositionCounts':dict(sorted(Counter(d['state'] for d in result_dispositions).items())),
            'sourcesWithReusableResultIds':sum(bool(d.get('result_ids')) for d in dispositions),
            'citedScholarlyPaperObligations':ledger['counts']['scholarlyPapers'],
            'citedScholarlyPapersStructurallyComplete':ledger['counts']['structurallyCompleteScholarlyReviews'],
            'unresolvedCitedReferenceClassifications':ledger['counts']['unclassifiedReferences'],
            'originSpecificQueueRecords':len(queue),'waveRecordCounts':dict(sorted(Counter(str(q['wave']) for q in queue).items()))}
    inputs=[BATCH/'inventory/source-records.jsonl',BATCH/'cited-paper-ledger.json',CORPUS/'draft-science/source-dispositions.json',CORPUS/'draft-science/results.jsonl',CORPUS/'draft-science/reviews.jsonl',CORPUS/'draft-science/result-dispositions.json']
    out={'schemaVersion':'remaprx-remaining-queue-v1','scope':'Recovered historical baseline; new calibration returns are counted separately in the handoff.',
         'counts':counts,'inputPins':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in inputs],
         'identityPolicy':'Origin records are preserved and not independent papers/studies. Reconcile exact candidate identity clusters before dispatch. Work with partial extraction resumes from verified fields; no whole-source completion is inferred.',
         'additionalMoaDrugNamesRemainLeads':read(BATCH/'inventory/summary.json')['moaAdditionalNames'],
         'queue':queue}
    target=BATCH/'remaining-queue.json';data=json.dumps(out,indent=2,ensure_ascii=False)+'\n'
    if not target.exists() or target.read_text()!=data:target.write_text(data)
    print(json.dumps(counts))
if __name__=='__main__':main()
