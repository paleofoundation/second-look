import json,hashlib,subprocess,re,os
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[2];os.chdir(ROOT)
s=json.loads((B/'SITES-PROVENANCE.json').read_text());p=json.loads((B/'SOURCE-COMPARISON.json').read_text());live=p['deployedCommit'];assert s['version']['source']['commit_sha']==live and s['version']['version_number']==46 and s['deployment']['status']=='succeeded';assert s['deployment']['version_id']==s['version']['id'];assert s['site']['current_live_url']=='https://remaprx.com'
for f,h in p['applicationFilesUnchanged'].items():
 raw=Path(f).read_bytes();assert hashlib.sha256(raw).hexdigest()==h;assert raw==subprocess.check_output(['git','show',live+':'+f])
assert p['externalPublishingPlan']['gitStatus']=='untracked' and not p['externalPublishingPlan']['importedOrModified'] and not Path('docs/RESEARCH-PUBLISHING-PLAN.md').exists()
for page in json.loads((B/'LIVE-BROWSER.json').read_text()):
 headings=page['headings'];assert all(h in headings for h in ['Options','Mechanism of Action','Comparisons','Evidence','Research Feed','FAQs','Update History','References']);assert all(h in page['columns'] for h in ['Intervention','Outcome','Grade','Effect','Evidence']);assert page['robots']==['noindex, nofollow']
for f in ['docs/CONDITION-STRUCTURE-COMPARISON.md','docs/CONDITION-PAGES.md']:
 for target in re.findall(r'\]\(([^)]+)\)',Path(f).read_text()):
  if '://' in target or target.startswith('#'):continue
  assert (Path(f).parent/target.split('#')[0]).exists(),(f,target)
changed=subprocess.check_output(['git','diff','--name-only',p['reportBase']],text=True).splitlines();assert all(f.startswith('docs/') or f.startswith(str(B.relative_to(ROOT))) for f in changed)
print('PASS: Sites version/source/deployment, live structure, eight application hashes, external-plan distinction, local links and documentation-only scope.')
