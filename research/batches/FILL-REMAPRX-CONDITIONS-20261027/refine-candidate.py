raise SystemExit('Checkpoint recipe retired; use current guarded candidate/projector. Original recipe at 9d3e696.')
"""Keep the final prose concise, preserve inherited question meanings, and scope mechanism judgments."""
import json,copy
from pathlib import Path
B=Path(__file__).parent;c=json.loads((B/'CANDIDATE.json').read_text());d=json.loads((B/'CLAIMS.json').read_text());inputs=json.loads((B/'INPUTS.json').read_text())
def section(g,label,text,ss):
 s=next(s for s in g['sections'] if s['label']==label);s.update(paragraph=text,sources=ss,sentences=[{'text':text,'sources':ss}])
def add_from(id,template,text,scope,grade,reason,notes):
 r=copy.deepcopy(next(x for x in d['claims'] if x['claimId']==template));r.update(claimId=id,statement=text,scope=scope,grade=grade,rationale=reason)
 for key in ['reusesAssessmentRowId','reusesAssessmentSha256']:r.pop(key,None)
 for dom,note in zip(r['domains'],notes):dom['judgment']=note
 d['claims']=[x for x in d['claims'] if x['claimId']!=id]+[r]
 return {'text':text,'sources':r['sourceIds']}
for g in c['guides']:
 entity=g['entityId'];m=next(m for m in c['mechanisms'] if m['conditionId']==entity)
 if entity=='C21':
  s=next(s for s in g['sections'] if s['label']=='Options');old=next(s for q in inputs['guides'] if q['entityId']==entity for s in q['sections'] if s['label']=='Options')['questions'];new=[q for q in s['questions'] if q['id'] in ['c21-metformin-models','c21-itraconazole-combination','c21-simvastatin-cells']];s['questions']=copy.deepcopy(old)+new
 elif entity=='C06':
  ss=['COND-C06-TRPM3-2021','COND-C06-LDN-CASES-2020'];section(g,'Comparisons','Cellular channel measurements and patient symptom histories answer different questions. Neither selected report supplies a controlled comparison of clinical benefit.',ss)
  text='Clinical benefit: Not established by these selected studies. The case histories and cell findings support further investigation, while comparative response rates, durability and an optimal ME/CFS regimen remain unresolved.'
  item=add_from('C06-COVERAGE','C06-HUMAN-CASES',text,'Selected cellular and uncontrolled human evidence coverage','not_established','No controlled symptom-efficacy comparison is supplied by the selected case histories or NK-cell experiment.',['Uncontrolled case histories and an observational cell comparison.','Neither isolates a causal patient treatment effect.','No comparative response rate or reliable optimal-dose estimate.','Different source types cannot be pooled into clinical replication.','Original source identities inspected at recorded reading depths; no exhaustive search claim.'])
  # Keep both source identities explicit on the coverage claim.
  row=next(x for x in d['claims'] if x['claimId']=='C06-COVERAGE');other=next(x for x in d['claims'] if x['claimId']=='C06-CHANNEL');row['sourceIds']=ss;row['sourceBindings']=other['sourceBindings']+row['sourceBindings'];row['locators']=other['locators']+row['locators']
  for dom in row['domains']:dom['sourceIds']=ss
  section(g,'Evidence',text,ss)
  text='Clinical translation: Low confidence. Opioid-receptor blockade is proposed to release inhibition of TRPM3-mediated calcium entry in natural-killer cells. A cellular finding does not identify the cause of the whole illness or establish symptom benefit.'
  item=add_from('C06-MECHANISM','C06-CHANNEL',text,'TRPM3/opioid hypothesis and clinical translation','Low','The selected observational cell experiment does not demonstrate a causal mechanism for clinical recovery.',['Selected treated-patient NK-cell recordings versus healthy controls.','Mechanistic cellular rationale is indirect for whole-illness symptom benefit.','Nine patients and nine controls, without a comparative symptom-efficacy estimate.','Cell recordings are not independent clinical response replication.','Exact primary abstract and selected sections inspected; source review pending.']);m['summary']={'text':text,'sourceIds':item['sources'],'sentences':[item]}
  for faq in g['faqs']:
   if faq['id']=='c06-safety-gap':faq.update(answer='Safety evidence: Low for estimating frequency. These reports cannot establish uncommon-event risks or a safe dosing schedule.',sentences=[{'text':'Safety evidence: Low for estimating frequency. These reports cannot establish uncommon-event risks or a safe dosing schedule.','sources':faq['sources']}])
 elif entity=='C28':
  old=next(x for x in json.load(open('data/public-mechanisms.json'))['drugs'] if x.get('conditionId')==entity);m['questions']=copy.deepcopy(old['questions'])
  text='Mechanistic clinical inference: Low confidence. Laboratory anti-inflammatory and anti-apoptotic findings supplied the rationale for minocycline. They did not predict the harmful functional result in the ALS trial.'
  item=add_from('C28-MECHANISM','C28-FUNCTION',text,'Historical laboratory rationale versus observed clinical result','Low','The original clinical report describes the preclinical rationale, but directly tests function rather than establishing a protective molecular mechanism in patients.',['Historical rationale described in the clinical report; no new primary animal-study appraisal.','Preclinical rationale is indirect for patient benefit and conflicts with the human functional result.','No protective molecular-mediated clinical effect estimate is established.','One human trial does not validate the proposed neuroprotective pathway.','Primary trial abstract background and clinical results inspected; no animal-paper transfer.']);m['summary']={'text':text,'sourceIds':item['sources'],'sentences':[item]};section(g,'Evidence','The selected trial directly measured function, survival and safety. Its functional-harm assessment applies to the tested regimen; mortality and individual adverse-event risks retain separate uncertainty.',['COND-C28-MINO-2007'])
 elif entity=='C19':
  old=next(x for x in json.load(open('data/public-mechanisms.json'))['drugs'] if x.get('conditionId')==entity);m['questions']=copy.deepcopy(old['questions']);section(g,'Evidence','Clinical evidence: Low. The short-duration study supports further controlled evaluation, while recurrence, definitive cure and comparison with established local treatment remain unresolved.',['P-D07-BCC-2014'])
(B/'CANDIDATE.json').write_text(json.dumps(c,indent=2,ensure_ascii=False)+'\n');(B/'CLAIMS.json').write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n');print('Final refinement:',len(d['claims']),'claim/context records; inherited question meanings retained.')
