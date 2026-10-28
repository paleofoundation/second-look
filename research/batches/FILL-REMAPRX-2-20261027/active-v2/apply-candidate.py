#!/usr/bin/env python3
from pathlib import Path
from copy import deepcopy
import json,subprocess
P=Path(__file__).resolve().parent;R=P.parents[3]
candidate=json.loads((P/'CANDIDATE.json').read_text());BASE=candidate['base'];guides={g['id']:g for g in candidate['guides']}
def load(n):return json.loads(subprocess.check_output(['git','-C',str(R),'show',BASE+':'+n]))
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
for f in ['data/content.json','data/public-content.json']:
 d=load(f)
 for i,g in enumerate(d['guides']):
  if g['id'] in guides:d['guides'][i]=deepcopy(guides[g['id']])
 save(f,d)
s=load('editorial/parent-guide-scopes.json')
for p in s['parents']:
 if p['guideId'] in guides:p['guide']=deepcopy(guides[p['guideId']])
save('editorial/parent-guide-scopes.json',s)
e=load('data/article-updates.json')
for g in candidate['guides']:
 e['entries'].insert(0,{'id':'2026-10-27-source-depth-'+g['entityId'].lower(),'date':'2026-10-27','title':'Evidence interpretation expanded','changeType':'evidence','summary':{'G-CONDITION-C23':'Explained the ACTIM add-on population, molecular response, safety observations and limits of causal attribution.','G-CONDITION-C05':'Distinguished the exploratory pain-modulation analysis from the same trial\'s clinical pain result and explained its limitations.','G-DRUG-D02':'Clarified the higher-dose acute-COVID recovery result, secondary outcomes and limits of mechanism and Long COVID inference.','G-DRUG-D26':'Separated the healthy-volunteer hypoxia experiment from cancer and neurological treatment claims.'}[g['id']],'pagePaths':[g['slug']],'affectedSections':[{'id':x['id'],'label':x['label']} for x in g['sections'] if x['label'] in ['Options','Benefits','Safety','Dosing','Evidence']]})
save('data/article-updates.json',e)
rule='''\n\n## October 27, 09:43: FILL-REMAPRX-2 scoped ownership ruling\n\nSource: Elon's 09:43 Asia/Nicosia bridge GATE. This supersedes the 09:27 whole-file collision prohibition only for G-CONDITION-C31, G-CONDITION-C23, G-CONDITION-C08, G-CONDITION-C22, G-CONDITION-C05, G-DRUG-D02 and G-DRUG-D26 guide objects in data/content.json, data/public-content.json and editorial/parent-guide-scopes.json. Selected-ID mechanism and article-update entries may change only where needed. One entry each in this contract and RULE-CHANGELOG.md records this ruling. All other guide, source, outcome and book objects remain identical to d118d305b59cac5e54ca7f9e5aa55cea682d2cee, with per-ID hashes proving preservation; the 13 previously filled guides and research/batches/RRX-INGEST-* paths are excluded. Use wider local lookup for unmatched originals; missing originals hold dependent new copy. Keep the initial collision checkpoint immutable and version the active plan separately. Cite only; no hosted papers or em/en dashes in new rendered prose. Vitiligo, protected CP027/CP028 pages and azole mechanism work remain held. Draft PR only; scientific/human approval, merge, deployment and publication remain separately gated. The bounded active packet is research/batches/FILL-REMAPRX-2-20261027/active-v2/.\n'''
for f in ['docs/PROJECT-RULES.md','docs/RULE-CHANGELOG.md']:
 old=subprocess.check_output(['git','-C',str(R),'show',BASE+':'+f],text=True);(R/f).write_text(old.rstrip()+rule)
print(json.dumps({'appliedGuideIds':sorted(guides),'sourceOrOutcomeChanges':0,'mechanismFileChanged':False,'newUpdateEvents':len(guides)}))
