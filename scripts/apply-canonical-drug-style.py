"""Bounded, idempotent editorial reuse. Never acquires studies or changes outcomes/grades.

Invoke with an explicit batch number and eight-or-fewer drug slugs. Existing sentence
maps are the evidence inputs; missing facts stay missing. Metformin is forbidden.
"""
from pathlib import Path
import json,re,sys,copy,hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text())
def save(p,v):(ROOT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def clean(t):
 t=t.replace('\u2014','; ').replace('\u2013','-')
 t=re.sub(r'\bpartnerships?\b','collaboration',t,flags=re.I)
 t=re.sub(r'\bpartners?\b','combination component',t,flags=re.I)
 for old,new in [('diarrhoea','diarrhea'),('hypoglycaemia','hypoglycemia'),('randomised','randomized'),('randomisation','randomization'),('tumour','tumor'),('behaviour','behavior'),('haematological','hematological'),('signalling','signaling')]:t=t.replace(old,new)
 return t

def sentences(s):
 if s.get('sentences'):return copy.deepcopy(s['sentences'])
 return [{'text':s.get('paragraph',s.get('text','')),'sources':s.get('sources',s.get('sourceIds',[]))}] if s.get('paragraph',s.get('text','')) else []
def join(items):
 out=[];seen=set()
 for s in items:
  t=clean(s['text']).strip()
  if t and t not in seen:out.append(dict(text=t,sources=s['sources']));seen.add(t)
 return {'paragraph':' '.join(s['text'] for s in out),'sentences':out,'sources':list(dict.fromkeys(i for s in out for i in s['sources']))}
def normalize(v):
 if isinstance(v,list):return [normalize(x) for x in v]
 if isinstance(v,dict):return {k:normalize(x) if k not in ['id','sourceIds','sources','slug','url','conditionHref','title'] else x for k,x in v.items()}
 return clean(v) if isinstance(v,str) else v

def apply(batch,slugs):
 assert 0<len(slugs)<=8 and 'metformin' not in slugs
 c=read('data/content.json');pub=read('data/public-content.json');disc=read('data/discovery-pages.json');ms=read('data/public-mechanisms.json');scopes=read('editorial/parent-guide-scopes.json');config=read('data/canonical-drug-pages.json');summaries=read('data/drug-study-summaries.json');updates=read('data/article-updates.json');suit=read('data/treatment-suitability.json');rows=read('data/public-reader-evidence.json')['synthesisRows'];sources={s['id']:s for s in pub['sources']};allguides=c['guides']+disc;reports=[]
 missing_pop={
 'COND-C02-COVIDOUT-2022':'People with acute COVID-19.',
 'COND-C03-ITRA-2014':'Patients with recurrent or persistent ovarian clear cell carcinoma.',
 'COND-C04-MEB-2021':'Patients with newly diagnosed high-grade gliomas.',
 'COND-C10-DOXY-2004':'Patients receiving scaling and root planing for periodontal disease.',
 'COND-C14-ITRA-2013':'Patients receiving second-line treatment for metastatic nonsquamous non-small-cell lung cancer.',
 'COND-C16-ALASCCA-2025':'Patients with PI3K-altered localized colorectal cancer.',
 'COND-C18-PROP-2021':'Patients with advanced melanoma.',
 'COND-C20-ASP-2020':'Participants in an observational investigation of hepatocellular carcinoma and liver-related mortality; detailed eligibility is not on hand.',
 'COND-C22-VPA-2019':'Older patients with acute myeloid leukemia.',
 'COND-C23-ACTIM-2017':'Patients with chronic myeloid leukemia.',
 'COND-C25-BENEMIN-2018':'Patients with recent-onset psychosis.',
 'COND-C27-MINOCIS-2017':'People with a clinically isolated syndrome of multiple sclerosis.',
 'COND-C28-MINO-2007':'Patients with amyotrophic lateral sclerosis.',
 'COND-C29-ATOR-2018':'Patients with active vitiligo receiving narrowband UV-B.'}
 for slug in slugs:
  path='/drugs/'+slug;g=next(g for g in allguides if g['type']=='Drug' and g['slug']==path);allowed=set(g['sourceIds']);before=copy.deepcopy(g);sec={s['label']:s for s in g['sections']};mechanism=next((m for m in ms['drugs'] if m.get('drugId')==g.get('entityId')),None);gaps=[]
  # Relocate existing benefit prose into Overview. Preserve all follow-up questions.
  overview=sentences(sec.get('Overview',{}));benefits=sec.get('Benefits');overview+=sentences(benefits or {})
  if overview:sec['Overview'].update(join(overview))
  if benefits:benefits.update(paragraph='',sentences=[],sources=[])
  evidence=sec.get('Evidence');results=sec.get('Results')
  if evidence:evidence.update(join(sentences(evidence)+sentences(results or {})))
  # Required modules are never silently empty. Absence is not a contraindication or a dose.
  for label,note in [('Contraindications','A product-specific contraindication summary is not on hand in the permitted sources. Trial eligibility criteria cannot substitute for the official label.'),('Interactions','A product-specific interaction assessment is not on hand in the permitted sources. The absence of that assessment does not establish that combinations are safe.'),('Dosing','A supported dosing description is not on hand in the permitted sources. No dose is inferred from a related drug or experimental model.')]:
   if label not in sec:
    s={'id':'authored-'+label.lower(),'label':label,'title':'','paragraph':note,'sentences':[{'text':note,'sources':[]}],'sources':[],'questions':[]};g['sections'].append(s);sec[label]=s;gaps.append(label+': '+note)
  # Follow-up dosing question reuses the page's actual research-dose explanation.
  dosing=sec.get('Dosing')
  if dosing and dosing.get('paragraph') and not dosing.get('questions') and dosing.get('sources'):
   dosing['questions']=[{'id':slug+'-dosing-scope','question':'Does this schedule establish a dose for every investigated use?','answer':'No single dosing schedule can be inferred across these uses. '+dosing['paragraph'],'sentences':[{'text':'No single dosing schedule can be inferred across these uses.','sources':[]}]+sentences(dosing),'sources':dosing['sources']}]
  if mechanism:
   # The shared renderer makes these source-bound explanations visible; no hidden main mechanism.
   for field in ['originalAction','summary']:
    if mechanism.get(field):
     x=join(sentences(mechanism[field]));mechanism[field].update(text=x['paragraph'],sourceIds=x['sources'],sentences=x['sentences'])
   for q in mechanism.get('questions',[]):
    q['title']=clean(q['title']);q['text']=clean(q['text']);q['sentences']=[dict(text=clean(s['text']),sources=s['sources']) for s in sentences(q)]
  else:gaps.append('Mechanism: no canonical drug mechanism record is on hand; no mechanism is inferred.')
  # Suitability rows reuse only label-supported statements, preserving mixed restriction wording.
  contraindications=sec['Contraindications'];label_sources=[i for i in contraindications['sources'] if i in sources and sources[i].get('sourceType')=='context' and re.search('label|prescribing',sources[i].get('design','')+' '+sources[i]['title'],re.I)]
  if path not in suit['pages'] and label_sources:
   suit['pages'][path]=[g['title']]
   suit['rows'].append({'id':slug+'-label-restrictions','drug':g['title'],'category':'precaution','label':'Label restrictions and eligibility review','text':clean(contraindications['paragraph']),'sourceIds':contraindications['sources']})
   # Text determines formal contraindications; category deliberately does not recast mixed precautions.
  for sid in g['sourceIds']:
   s=sources.get(sid)
   if not s or s.get('sourceType') in ['context','review','textbook','other'] or sid in summaries:continue
   related=[r for r in rows if sid in r['sourceIds'] and r.get('status') not in ['held','provisional_correction_hold']]
   ownfinding=[r['finding']['text'] for r in related if sid in r['finding'].get('sources',[])]
   limits=[l['text'] for r in related for l in r.get('limitations',[]) if sid in l.get('sources',[])]
   preview=s.get('preview','');finding=' '.join(dict.fromkeys(ownfinding)) or preview
   if preview==s['title'] and not ownfinding:
    details=[q['text'] for m in ms['drugs'] for q in m.get('questions',[]) if q.get('sourceIds')==[sid]]
    finding=' '.join(dict.fromkeys(details)) or 'A numerical findings account is not on hand beyond the cited bibliographic description.'
    if not details:gaps.append(sid+': full findings and numerical results not on hand.')
   population=s.get('population') or missing_pop.get(sid) or next((r['population'] for r in related if r.get('population')),None)
   if not population:population='A detailed population or experimental-model description is not on hand in the cited source record.';gaps.append(sid+': population/model detail missing.')
   endpoint=next((r['endpoint'] for r in related if r.get('endpoint')),None)
   comparison=s.get('comparator') or next((r['comparison'] for r in related if r.get('comparison')),None)
   if endpoint:
    question=f"The {s.get('design','study').lower()} examined {endpoint.rstrip('.')}."
    if comparison:question+=' The recorded comparison was '+comparison.rstrip('.')+'.'
   else:question=clean(s['title']).rstrip('.')+'. '+s.get('design','Study').rstrip('.')+'.'
   implications=s.get('decisiveLimit') or ' '.join(dict.fromkeys(limits))
   if not implications:
    design=s.get('design','').lower();model=population.lower()
    if s.get('status')=='Quarantined':implications='This report is excluded from efficacy conclusions because of its source-integrity status.'
    elif re.search(r'protocol',design):implications='This is a planned study, not a reported treatment result. Its design does not establish an efficacy or safety finding.'
    elif re.search(r'cell|mouse|mice|animal|preclinical|xenograft|computational|bioinformatic|in.silico',design+' '+model):implications='The finding applies to '+population.rstrip('.')+'. It does not establish patient benefit or a human treatment schedule.'
    elif re.search(r'case|series|uncontrolled|open.label|observational|cohort',design):implications='The finding concerns '+population.rstrip('.')+'. The reported design does not independently establish that the drug caused the observed clinical change.'
    else:implications='The reported finding concerns '+population.rstrip('.')+'. Its applicability beyond that population and the reported outcome is not established by this source summary.'
   summaries[sid]=[clean(x) for x in [question,population,finding,implications]]
  g.update(normalize(g))
  # The supported intro and mechanism main text remain intact; record thin source-bound sections.
  for label in ['Safety','Contraindications','Interactions','Dosing','Evidence']:
   s=sec.get(label)
   if s and len(s.get('paragraph','').split())<45:gaps.append(label+': limited source-bound prose retained; no unsupported expansion.')
  # All additions must cite only sources originally on this exact page.
  def refs(v):
   if isinstance(v,list):return [i for x in v for i in refs(x)]
   if isinstance(v,dict):return [i for k,x in v.items() for i in (x if k in ['sourceIds','sources'] and isinstance(x,list) else refs(x))]
   return []
  assert set(refs(g))<=allowed,(path,set(refs(g))-allowed)
  for collection in [pub['guides']]:
   for i,x in enumerate(collection):
    if x['id']==g['id']:collection[i]=copy.deepcopy(g)
  for parent in scopes['parents']:
   if parent['guideId']==g['id']:parent['guide']=copy.deepcopy(g)
  if path not in config['pages']:config['pages'].append(path)
  uid='canonical-'+slug+'-20261105'
  if not any(u['id']==uid for u in updates['entries']):updates['entries'].insert(0,{'id':uid,'date':'2026-11-05','pagePaths':[path],'changeType':'presentation','title':'Expanded study summaries and visible mechanism explanations','summary':'Reorganized the existing cited overview and findings, made the main mechanism explanations visible and added source-bound Research Feed answers. Preserved the existing outcome grades, trial identities and source-integrity limits. Missing source details remain explicit.','affectedSections':[{'id':'section-overview','label':'Overview'},{'id':'mechanisms','label':'Mechanism of Action'},{'id':'research-feed','label':'Research Feed'}],'sourceIds':g['sourceIds']})
  reports.append({'url':'https://remaprx.com'+path,'sourceIds':list(allowed),'remainingThin':gaps,'beforeSha256':hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),'afterSha256':hashlib.sha256(json.dumps(g,sort_keys=True).encode()).hexdigest()})
 for p,v in [('data/content.json',c),('data/public-content.json',pub),('data/discovery-pages.json',disc),('data/public-mechanisms.json',ms),('editorial/parent-guide-scopes.json',scopes),('data/canonical-drug-pages.json',config),('data/drug-study-summaries.json',summaries),('data/article-updates.json',updates),('data/treatment-suitability.json',suit)]:save(p,v)
 save('research/batches/RRX-DRUG-CANONICAL-20261105/batch-'+batch+'-report.json',{'batch':batch,'pages':reports,'status':'Review branch only. No new efficacy assessment, trial count or scientific approval.','sourcePolicy':'Existing exact-page citations only; no outside study acquisition.','validation':'Run the canonical content, render, citation, grading, privacy and TypeScript checks after applying.'})
 print(json.dumps({'batch':batch,'pages':len(reports),'summaries':len(summaries)}))
if __name__=='__main__':apply(sys.argv[1],sys.argv[2:])
