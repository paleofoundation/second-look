from pathlib import Path
from copy import deepcopy
import json,subprocess
P=Path(__file__).resolve().parent;R=P.parents[2];B='d118d305b59cac5e54ca7f9e5aa55cea682d2cee';c=json.loads((P/'CANDIDATE.json').read_text())
def read(path):return json.loads(subprocess.check_output(['git','-C',str(R),'show',B+':'+path],text=True))
def write(path,data):(R/path).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
for f in ['data/content.json','data/public-content.json']:
 j=read(f);oldids={s['id'] for s in j['sources']};assert not oldids.intersection(s['id'] for s in c['newSources']);j['sources']+=deepcopy(c['newSources']);j['guides']=[deepcopy(c['guide']) if g['id']=='G-DRUG-D07' else g for g in j['guides']];terms={t['slug']:t for t in c['glossary']};j['glossary']=[deepcopy(terms.get(t['slug'],t)) for t in j['glossary']];write(f,j)
f='editorial/parent-guide-scopes.json';j=read(f)
for parent in j['parents']:
 if parent['guideId']=='G-DRUG-D07':parent['guide']=deepcopy(c['guide'])
write(f,j)
f='data/public-mechanisms.json';j=read(f);j['drugs']=[deepcopy(c['mechanisms'][0]) if d.get('drugId')=='D07' else d for d in j['drugs']]+deepcopy(c['mechanisms'][1:]);write(f,j)
f='data/article-updates.json';j=read(f);entries=[]
for route,name in [('/drugs/itraconazole','Itraconazole mechanism evidence'),('/glossary/hedgehog-pathway','Hedgehog pathway distinctions'),('/glossary/hyphae','Candida morphology distinctions')]:
 entries.append({'id':'azole-mechanism-20261027-'+route.split('/')[-1],'date':'2026-10-27','pagePaths':[route],'changeType':'evidence','title':name,'summary':'Added source-specific mechanism comparisons with model limits and scoped clinical-inference judgments.','affectedSections':[{'id':'mechanisms','label':'Mechanism of Action'}],'sourceIds':[s['id'] for s in c['newSources']] if route!='/glossary/hyphae' else ['MECH-AZOLE-HYPHAE-2011','MECH-KETOCONAZOLE-FILAMENTS-2008']})
j['entries']=entries+j['entries'];write(f,j)
for f in ['docs/PROJECT-RULES.md','docs/RULE-CHANGELOG.md']:
 s=subprocess.check_output(['git','-C',str(R),'show',B+':'+f],text=True).rstrip();s+='\n\n## October 27 azole mechanism scope and 10:43 gates\n\nElon\'s 10:24 order and 10:43 A/B/C rulings authorize only D07 itraconazole and the existing hedgehog-pathway/hyphae glossary entries, six append-only primary source objects in the named proposal, the exact three-file optional comparison-table patch as a separate commit, and this one scope entry. Preserve all prior source objects, the 13 filled guides including D34, the seven PR9 IDs, fenbendazole, outcomes, book objects and protected batches. Missing azole guides remain candidates. Tables require build, outside-scope rejection, SSR citation closure, 390 by 844 and exact outside-route HTML preservation; revert the table commit if a required gate fails. The exact table commit was subsequently reverted after the required outside-route HTML check failed; tables and the optional FAQ are held only in the packet, not completed public deliverables. Source identities were checked against PubMed before commit. Keep mixed human itraconazole data, preclinical posaconazole, strain-dependent in vitro morphology and unresolved Kim2014 estimates distinct. Primary papers govern internal book conflicts. Draft, independent/human review and release states remain pending; no merge, deployment, publication or raw PDF hosting is authorized.\n';(R/f).write_text(s)
print('Applied exact bounded azole candidate; all unselected objects read from fixed base')
