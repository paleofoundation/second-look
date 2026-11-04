"""Import the assessed private reviews without granting release or human approval."""
import copy,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent
ROOT=B.parents[2]
def read(p):return json.loads((ROOT/p).read_text())
def save(p,x):(ROOT/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
reviews=read('data/private-reviews.json');envelopes=read('data/review-envelopes.json');metadata=read('data/public-review-metadata.json');content=read('data/content.json');public=read('data/public-content.json')
sources={x['sourceId']:x for x in json.loads((B/'source-access.json').read_text())['sources']}
questions=json.loads((B/'review-questions-and-inputs.json').read_text())['questions']
sections={'summary':['Q01','Q15'],'methods':['Q02','Q03','Q04','Q07'],'results':['Q05','Q06','Q14'],'limits':['Q08','Q09','Q10'],'sources':['Q11','Q12','Q13']}
section_for={q:s for s,qs in sections.items() for q in qs}
openings=copy.deepcopy(reviews['P-COVIDOUT-2023']['openingBlocks'])
canonical={s['id']:s for s in content['sources']}
for sid in ['REVIVE-REPLACEMENT','REVIVE-NOTICE','COVIDOUT-CORRECTION']:
 if sid in canonical:continue
 s=sources[sid]
 c={'id':sid,'title':s['title'],'url':s['url'],'doi':s['doi'],'year':2023 if sid=='COVIDOUT-CORRECTION' else 2026,'authors':[],
 'design':'Retraction and republication notice' if sid=='REVIVE-NOTICE' else 'Published correction' if sid=='COVIDOUT-CORRECTION' else 'Adaptive randomized placebo-controlled trial; replacement report',
 'population':'Adults with fatigue after COVID-19' if sid=='REVIVE-REPLACEMENT' else 'Publication integrity record','n':399 if sid=='REVIVE-REPLACEMENT' else None,
 'sourceType':'primary' if sid=='REVIVE-REPLACEMENT' else 'other',
 'preview':'Replacement report acquired and assessed separately. The retracted original is excluded.' if sid=='REVIVE-REPLACEMENT' else 'Notice acquired and linked to the source-version assessment.',
 'familyId':'S-REVIVE-2026' if sid.startswith('REVIVE') else 'S-COVIDOUT-2023','reviewState':'pending','publicationState':'private_ai_draft','humanApproval':'pending','access':'full_text','status':'Assessment pending independent review'}
 content['sources'].append(c);canonical[sid]=c
 allowed=['id','title','url','doi','year','authors','design','population','n','sourceType','preview','familyId']
 public['sources'].append({k:c[k] for k in allowed})
# Scientific assessments retain source gaps and separate independent approval.
for f in sorted((B/'assessments').glob('*.json')):
 r=json.loads(f.read_text());sid=r['sourceId'];s=sources[sid];version=r['version'];qas=[]
 for q in questions:
  qid=q['id'];answer=r['questions'][qid];missing=[i for i in r['inputs'] if i['questionId']==qid and i['status'] in ['not_accessible','not_checked']]
  item={'id':qid,'question':q['question'],'answer':answer['answer'],'status':'partial' if missing else 'complete','sources':[sid],
   'locators':[{'paper_id':sid,'source_url':s.get('url') or canonical[sid]['url'],'file':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'nativeLocator':'#/questions/'+qid+'; '+ '; '.join(answer['locators']),'basis':'assessed_full_text_source_packet','missingness':'not_applicable'}],
   'render':{'section':section_for[qid],'fragment':qid.lower(),'existingSection':section_for[qid],'requiresAnswerDetailRender':True},
   'acceptedRecordPointer':str(f.relative_to(ROOT))+'#/questions/'+qid,'requiredInputFields':q['inputFields'],'extractionBasis':'Source packet and locators retained in the versioned assessment.',
   'nextAction':'Recover the specifically listed source inputs and reassess; independent review remains pending.' if missing else 'Obtain independent verification and exact-version human approval.',
   'verificationState':'source_assessed_independent_verification_pending','contentClass':'reported_data_and_bounded_editorial_interpretation'}
  if missing:item['unresolvedInputReason']='; '.join(i['field']+': '+i['value'] for i in missing)
  qas.append(item)
 body={'id':sid,'version':version,'sourceIds':[sid],
  'sections':[{'id':sec,'title':sec.title(),'paragraph':' '.join(r['questions'][qid]['answer'] for qid in qs),'sources':[sid]} for sec,qs in sections.items()],
  'questionAnswers':qas,'openingBlocks':openings}
 body['contentSha256']=digest(body);reviews[sid]=body
 envelopes[sid]={'preview':{'id':sid,'title':canonical[sid]['title'],'route':'/research/'+sid,'sourceUrl':canonical[sid]['url'],
  'preview':'Source assessment prepared; independent review is pending.','decisiveLimit':r['appraisal'],'reviewState':'pending','version':version,'sourceIds':[sid]},
  'release':{'state':'pending','version':version,'contentSha256':body['contentSha256'],'approvedSha256':None,'humanEditorialApproved':False,'clinicalSafetyReviewRequired':True,'qualifiedClinicalApproval':False}}
 m={'sourceId':sid,'paperId':sid,'reviewId':'REVIEW-'+sid,'route':'/research/'+sid,'version':version,'reviewState':'pending','draftBodyAvailable':True,'humanApproval':'pending','publicationState':'private_ai_draft','complete':False,
  'questions':[{'id':q['id'],'question':q['question'],'status':q['status'],'section':q['render']['section'],'nextAction':q['nextAction']} for q in qas]}
 prior=next((i for i,x in enumerate(metadata['records']) if x['sourceId']==sid),None)
 if prior is None:metadata['records'].append(m)
 else:metadata['records'][prior]=m
# Retraction is a permanent disposition for the original, not an unfinished efficacy review.
sid='P-REVIVE-2026';version='metformin-integrity-20261104.1'
notice='The original report was retracted and replaced. The actual notice and replacement were acquired. The original omitted a dose modification and a futility stop. Use REVIVE-REPLACEMENT (DOI 10.7326/ANNALS-26-02144) for the separately assessed report; the original is excluded from efficacy claims.'
body={'id':sid,'version':version,'sourceIds':[sid,'REVIVE-NOTICE','REVIVE-REPLACEMENT'],'sections':[{'id':'summary','title':'Retraction and replacement','paragraph':notice,'sources':['REVIVE-NOTICE','REVIVE-REPLACEMENT']}]};body['contentSha256']=digest(body);reviews[sid]=body
original=envelopes[sid];original['preview'].update({'preview':'Retracted original excluded. Notice and replacement acquired and assessed.','decisiveLimit':notice,'reviewState':'withdrawn','version':version,'sourceIds':body['sourceIds']});original['release'].update({'state':'withdrawn','version':version,'contentSha256':body['contentSha256'],'approvedSha256':None,'humanEditorialApproved':False,'qualifiedClinicalApproval':False})
for m in metadata['records']:
 if m['sourceId']==sid:m.update({'version':version,'reviewState':'withdrawn','complete':False,'questions':[]})
for collection in [content['sources'],public['sources']]:
 s=next(s for s in collection if s['id']==sid);s.update({'preview':'Retracted original excluded. The notice and replacement report have been acquired and assessed.','correction':notice,'decisiveLimit':'Retracted original: no efficacy claim may cite it. Replacement DOI 10.7326/ANNALS-26-02144.'})
 if collection is content['sources']:s.update({'reviewState':'withdrawn','status':'Quarantined','review':None,'reviewVersion':version,'reviewHash':body['contentSha256']})
envelopes['P-COVIDOUT-2023']['preview']['preview']='Correction notice and current appendix checked; source assessment prepared. Independent review is pending.'
envelopes['REVIVE-REPLACEMENT']['preview']['preview']='Replacement report assessed with dose-change and futility information retained. Independent review is pending.'
for p,x in [('data/private-reviews.json',reviews),('data/review-envelopes.json',envelopes),('data/public-review-metadata.json',metadata),('data/content.json',content),('data/public-content.json',public)]:save(p,x)
catalogue=read('data/guide-catalogue.json');product=next(p for p in catalogue['products'] if p['id']=='SL-GUIDE-METFORMIN')
product.update({'description':'Understand what metformin research can and cannot tell you, with comparisons across infections, neurological conditions, individual cancers and physical function.','statusLabel':'In review','readiness':'The complete manuscript and reading files are prepared and undergoing editorial and clinical review. The guide is not yet available to buy. The free article remains available.'})
save('data/guide-catalogue.json',catalogue)
print('Imported 24 private source assessments; original REVIVE withdrawn; release approvals unchanged.')
