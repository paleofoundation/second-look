#!/usr/bin/env python3
import hashlib,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
R=P.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a):return subprocess.check_output(['git','-C',str(R),*a],text=True)
baseline=json.loads((P/'BASELINE-PRESERVATION.json').read_text())
assert git('merge-base',baseline['base'],'HEAD').strip()==baseline['base'], 'Pinned base is no longer an ancestor'
for f in baseline['forbiddenFiles']:
 assert sha(R/f['path'])==f['sha256'], f['path']
selection=json.loads((P/'SELECTION.json').read_text());selected=set(selection['proposedRoutes']); dispositions={x['route']:x for x in selection['allDrugConditionRows']}
assert len(selected)==7
assert all(dispositions[r]['disposition']=='selected' for r in selected)
assert not selected.intersection(selection['filledGuideRoutes'])
assert all(not dispositions[r]['protectedBookSourceIds'] for r in selected)
content=json.loads((R/'data/content.json').read_text());sources={s['id'] for s in content['sources']}
plan=json.loads((P/'CLAIM-PLAN.json').read_text())
assert all(set(p['canonicalSourceIds'])<=sources for p in plan['pages'])
changed=git('diff','--name-only',baseline['base']).splitlines()
untracked=git('ls-files','--others','--exclude-standard').splitlines()
allowed=str(P.relative_to(R))+'/'
assert all(p.startswith(allowed) for p in changed+untracked),(changed,untracked)
assert not any(p.startswith('research/batches/RRX-INGEST-') for p in changed+untracked)
manifest=P/'OUTPUT-HASHES.json'
if manifest.exists():
 for x in json.loads(manifest.read_text())['files']:assert sha(P/x['path'])==x['sha256'],x['path']
print(json.dumps({'status':'PASS_inventory_and_preservation_only','base':baseline['base'],'forbiddenFilesUnchanged':len(baseline['forbiddenFiles']),'proposedPages':len(selected),'newScientificClaims':0,'pageEdits':0,'scientificAcceptance':False,'appBuild':'not_run','browserChecks':'not_run'}))
