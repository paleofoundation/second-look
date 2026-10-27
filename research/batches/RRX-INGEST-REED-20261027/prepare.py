"""Closed supplied-pack intake; source assertions remain unaccepted and private."""
import argparse,collections,csv,hashlib,json,os,re,subprocess,unicodedata
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[2]
PACK=Path(os.environ.get('REMAPRX_REED_ROOT','/nonexistent'))
PRIVATE=Path(os.environ.get('REMAPRX_INTAKE_PRIVATE',str(ROOT.parent/'reed-ingest-private')))
def digest(x):return hashlib.sha256(x).hexdigest()
def objhash(x):return digest(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
def load(p):return json.loads(p.read_text())
def write(name,x):(B/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def doi(x):return re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi\s*:)','',str(x or '').strip(),flags=re.I).lower().rstrip(' .')
def pmid(x):return str(x or '').strip() if re.fullmatch(r'\d+',str(x or '').strip()) else ''
def norm(x):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',str(x).lower()))
def nct(x):
 raw=x.get('nct','').strip().upper();match=re.search(r'\bNCT\d{8}\b',x.get('title','').upper());return raw or (match.group() if match else '')
def ident(x):
 d=doi(x.get('doi'));p=pmid(x.get('pmid'));n=nct(x)
 return ('doi:'+d if d else 'pmid:'+p if p else 'registry:'+n if n else None)
def matches(a,b):
 # PMID/DOI contradictions stop even when the other identifier matches.
 common=bool((pmid(a.get('pmid')) and pmid(a.get('pmid'))==pmid(b.get('pmid'))) or (doi(a.get('doi')) and doi(a.get('doi'))==doi(b.get('doi'))) or (not a.get('pmid') and not a.get('doi') and nct(a) and nct(a)==nct(b)))
 conflict=bool((pmid(a.get('pmid')) and pmid(b.get('pmid')) and pmid(a.get('pmid'))!=pmid(b.get('pmid'))) or (doi(a.get('doi')) and doi(b.get('doi')) and doi(a.get('doi'))!=doi(b.get('doi'))))
 return common and not conflict

def existing():
 records=[];assets={};bindings=collections.defaultdict(list)
 app=load(ROOT/'data/content.json')
 for r in app['sources']:records.append({'origin':'data/content.json','id':r['id'],'pmid':pmid(r.get('pmid')),'doi':doi(r.get('doi')),'title':r.get('title','')})
 corpus=ROOT/'research/corpus/RRX-INGEST-001'
 for r in map(json.loads,(corpus/'acquisition/reports.jsonl').read_text().splitlines()):records.append({'origin':'acquisition/reports.jsonl','id':r['id'],'pmid':pmid(r.get('pmid')),'doi':doi(r.get('doi'))})
 for r in load(corpus/'draft-science/corpus.json')['papers']:records.append({'origin':'draft-science/corpus.json:papers','id':r['id'],'pmid':pmid(r.get('pmid')),'doi':doi(r.get('doi')),'title':r.get('title','')})
 for r in map(json.loads,(corpus/'acquisition/assets.jsonl').read_text().splitlines()):assets[r['sha256']]={'sourceIds':r['source_ids'],'origin':'acquisition/assets.jsonl'}
 for r in map(json.loads,(corpus/'acquisition/sources.jsonl').read_text().splitlines()):
  s=r['source_record'];records.append({'origin':'acquisition/sources.jsonl','id':r['source_id'],'reportId':r['canonical_report_id'],'pmid':pmid(s.get('pmid')),'doi':doi(s.get('doi')),'title':s.get('title',''),'assetSha256':r.get('asset_sha256'),'quarantined':r.get('quarantined',False)})
 for f in (ROOT/'research/batches').glob('FILL-REMAPRX*/INPUTS.json'):
  d=load(f)
  for r in d.get('papers',[]):
   if r.get('sha256'):assets[r['sha256']]={'origin':str(f.relative_to(ROOT)),'pmid':pmid(r.get('pmid')),'sourceIds':r.get('sourceIds',[])}
 index=collections.defaultdict(list)
 for r in records:
  if r['doi']:index['doi:'+r['doi']].append(r)
  if r['pmid']:index['pmid:'+r['pmid']].append(r)
 return index,assets

def inspect_asset(path,expected,row):
 if not path.is_file():return {'state':'not_accessible','ref':None}
 raw=path.read_bytes();actual=digest(raw);r={'id':'ASSET-'+actual[:24],'sha256':actual,'expectedSha256':expected or None,'expectedHashMatched':actual==expected if expected else None,'bytes':len(raw),'ref':'$REMAPRX_REED_ROOT/'+path.relative_to(PACK).as_posix(),'state':'verified_bytes','mediaType':'application/pdf' if raw.startswith(b'%PDF-') else 'application/json' if path.suffix=='.json' else 'text/html' if path.suffix in ['.html','.htm'] else 'unknown','identity':'not_checked','numericExtractionVerified':False,'actualReading':'technical_identity_check_only','completeScientificExtraction':False}
 if expected and actual!=expected:r['state']='hash_mismatch';return r
 if r['mediaType']=='application/pdf':
  PRIVATE.mkdir(parents=True,exist_ok=True);textPath=PRIVATE/(actual+'.first-page.txt');q=subprocess.run(['pdftotext','-f','1','-l','1','-layout',str(path),str(textPath)],capture_output=True)
  if q.returncode:r.update(state='unreadable_pdf');return r
  text=textPath.read_text(errors='replace');r['firstPageTextSha256']=digest(text.encode());r['firstPageWords']=len(text.split());canonicalDoi=doi(row.get('doi'));canonicalPmid=pmid(row.get('pmid'));tokens=[w for w in re.findall(r'[a-z0-9]+',row.get('title','').lower()) if len(w)>3];first=norm(text);ratio=sum(norm(w) in first for w in tokens)/len(tokens) if tokens else 0
  r['titleTokenOverlap']=round(ratio,4);r['doiOnFirstPage']=bool(canonicalDoi and norm(canonicalDoi) in first);r['pmidOnFirstPage']=bool(canonicalPmid and canonicalPmid in text);r['preprintMarker']=bool(re.search(r'(?i)(bioRxiv|medRxiv|not certified by peer review|preprint)',text));r['identity']='consistent_first_page' if r['doiOnFirstPage'] or r['pmidOnFirstPage'] or ratio>=.60 else 'needs_manual_identity_review'
  if r['preprintMarker']:r['versionState']='preprint_candidate_do_not_equate_to_journal_version'
 elif r['mediaType']=='application/json':
  try:
   j=json.loads(raw);nct=j.get('protocolSection',{}).get('identificationModule',{}).get('nctId');r['registryIdInFile']=nct;r['identity']='consistent_registry_id' if nct and nct==row.get('nct') else 'needs_manual_identity_review'
  except ValueError:r['state']='unreadable_json'
 return r

def prepare():
 inp=load(B/'INPUTS.json');plan=load(B/'PLAN.json');readiness=load(B/'READINESS.json')
 for f,h in readiness['hashes'].items():assert digest((B/f).read_bytes())==h,'Readiness dependency changed: '+f
 for source in inp['inputs']:
  ref=source['ref']
  if ref.startswith('$REMAPRX_REED_ROOT/'):
   p=PACK/ref.split('/',1)[1];assert digest(p.read_bytes())==source['sha256'],'Source changed after GP: '+ref
 assert PACK.is_dir(),'Bind REMAPRX_REED_ROOT to lawful supplied pack'
 old,priorAssets=existing();raw=load(B/'INPUT-ROWS.json')['rows'];indexes={folder:list(csv.DictReader((PACK/folder/'index.csv').open())) for folder in sorted({x['supplierRecord']['folder_or_pair'] for x in raw})};rows=[];reports={};assets={};assertions=[];seen={};issues=[];reuse=[]
 for item in raw:
  supplied=item['supplierRecord'];folder=supplied['folder_or_pair'];key=ident(supplied);id=item['inputRowId'];candidates=[(i,r) for i,r in enumerate(indexes[folder],2) if matches(supplied,r)];identityResolution='exact_doi_or_pmid';
  if not key:
   candidates=[(i,r) for i,r in enumerate(indexes[folder],2) if norm(r.get('title',''))==norm(supplied.get('title','')) and r.get('nct')]
   if len(candidates)==1:key='registry:'+candidates[0][1]['nct'].strip().upper();identityResolution='exact_full_title_to_explicit_index_registry_id'
  current=candidates[0][1] if len(candidates)==1 else None;currentline=candidates[0][0] if len(candidates)==1 else None
  reportId=('REED-'+digest(key.encode())[:20]) if key else None;hits=[]
  for k in ['doi:'+doi(supplied.get('doi')),'pmid:'+pmid(supplied.get('pmid'))]:hits+=old.get(k,[])
  hits=list({(h['origin'],h['id']):h for h in hits}.values());conflicting=[h for h in hits if (h['doi'] and doi(supplied.get('doi')) and h['doi']!=doi(supplied['doi'])) or (h['pmid'] and pmid(supplied.get('pmid')) and h['pmid']!=pmid(supplied['pmid']))]
  rec={'inputRowId':id,'sourceInput':item['sourceInput'],'folder':folder,'reportId':reportId,'supplierStatus':supplied['status'],'supplierReadStatus':supplied.get('read_status') or 'unknown','identityResolution':identityResolution,'currentIndexLine':currentline,'currentIndexSha256':digest((PACK/folder/'index.csv').read_bytes()),'existingIdentityReferences':hits,'assetIds':[],'assertionIds':[],'acceptedSupport':False,'scientificExtraction':'not_extracted_in_this_intake','disposition':None,'reason':None,'nextAction':None}
  def disp(state,reason,action):rec.update(disposition=state,reason=reason,nextAction=action)
  if 'vitiligo' in folder:disp('held','explicit_vitiligo_hold','Owner hold must be resolved before dependent science or guide changes.')
  elif supplied['status']=='EXCLUDED-RETRACTED' or (current and current.get('status')=='EXCLUDED-RETRACTED'):disp('rejected','retracted_source','Retain exclusion; do not activate supplied claims or replace with an older version.')
  elif not key:disp('held','identity_not_identifiable','Adjudicate exact report or registry identity; title similarity is insufficient.')
  elif conflicting:disp('held','identifier_conflict_with_existing_record','Resolve conflicting DOI/PMID mappings before merge.');issues.append({'inputRowId':id,'kind':'identifier_conflict','existing':conflicting})
  elif len(candidates)!=1:disp('held','current_index_identity_missing_or_ambiguous','Reconcile supplied ledger identity against exact current index; no fuzzy merge.')
  else:
   src=current;path=src.get('path') or src.get('file') or '';path=path.replace('/workspace/ops/remaprx-fill/','').replace('/Users/kmfp/papers-for-claude/remaprx-fill/','');p=(PACK/path) if path.startswith(folder+'/') else PACK/folder/path if path else None
   expected=src.get('sha256') or supplied.get('sha256') or '';asset=None
   if p:
    p=p.resolve()
    if not p.is_relative_to(PACK.resolve()):p=None
   if p and p.is_file():
    asset=inspect_asset(p,expected,src);assets.setdefault(asset['id'],asset);rec['assetIds'].append(asset['id'])
    if supplied.get('sha256') and supplied['sha256']!=asset['sha256']:issues.append({'inputRowId':id,'kind':'snapshot_to_current_asset_drift','snapshotSha256':supplied['sha256'],'currentSha256':asset['sha256']});disp('held','snapshot_asset_changed','Adjudicate old/new source versions; current bytes cannot silently replace the frozen snapshot.')
    elif asset['state']!='verified_bytes' or asset['identity'].startswith('needs_manual') or asset.get('preprintMarker'):disp('held','asset_identity_integrity_or_version_hold','Inspect exact version/first page; do not equate preprint with journal report or accept unreadable bytes.')
    else:
     if asset['sha256'] in priorAssets:disp('duplicate','exact_source_asset_already_recorded','Reuse recorded asset/report identity; any new assertion still needs exact-scope verification.');rec['priorAssetReference']=priorAssets[asset['sha256']]
     else:disp('ingested','new_verified_source_asset_receipt','Complete source-level extraction/Q01-Q15 and independent review before scientific use.')
   elif supplied.get('status')=='IN-CORPUS' and hits:disp('duplicate','existing_report_identity_no_new_asset','Reuse existing report; this is identity reuse, not evidence that a new assertion is already extracted.')
   elif src.get('nct') and (not src.get('pmid')) and ('registry' in (src.get('design','')+src.get('status','')).lower()):disp('ingested','registry_metadata_only_no_efficacy_result','Verify registry version, report linkage and results before any efficacy extraction.')
   elif hits:disp('duplicate','existing_report_identity_source_access_still_pending','Reuse report identity and retain missing original/source-level review as a gap.')
   else:disp('held','original_not_accessible','Obtain lawful exact original/source version; supplied abstract/index notes are not full-text extraction.')
   if rec['disposition'] in ['ingested','duplicate']:
    assertion=src.get('outcome_as_reported') or src.get('key_finding')
    if assertion:
     # Adjacent-drug and proposed azole-mechanism material stays inactive/internal.
     hold=bool(src.get('kind')=='ADJ' or ('azole' in folder and re.search(r'hedgehog|npc1|cholesterol|mechanism|gli1',assertion,re.I)))
     aid='REED-ASSERT-'+digest((id+'|'+assertion).encode())[:20];assertions.append({'id':aid,'reportId':reportId,'inputRowId':id,'text':assertion,'basis':'supplier_reported_assertion','locator':{'kind':'supplier_index_csv_record','ref':'$REMAPRX_REED_ROOT/'+folder+'/index.csv','sha256':rec['currentIndexSha256'],'csvRecordLine':currentline,'sourcePaperLocator':'not_extracted_in_this_intake'},'verificationState':'pending_source_level_verification','humanReview':'pending','acceptedSupport':False,'heldScientificScope':hold,'scopeLimit':'Adjacent drug findings cannot transfer to fenbendazole; azole mechanisms await separate findings/order.' if hold else 'Acquisition purpose is not scientific applicability; no pooling or new grade.'});rec['assertionIds'].append(aid)
   if key in seen and rec['disposition']=='ingested':disp('duplicate','repeated_report_identity_in_input','Reuse first input report/asset; do not add trial or participant counts.');rec['duplicateOfInputRowId']=seen[key]
   seen.setdefault(key,id)
  if reportId:
   report=reports.setdefault(reportId,{'id':reportId,'idNamespace':'batch_intake_report_identity_not_a_new_canonical_paper','identityKey':key,'doi':doi(supplied.get('doi')) or None,'pmid':pmid(supplied.get('pmid')) or None,'nct':current.get('nct') if current else None,'title':supplied['title'],'inputRowIds':[],'existingIdentityReferences':[],'assetIds':[],'scientificState':'pending','humanReview':'pending','acceptedSupport':False,'studyFamilyId':None,'studyFamilyMissingReason':'not_adjudicated; registry/report appearances and overlapping cohorts are not independent trials'})
   report['inputRowIds'].append(id);report['assetIds']=sorted(set(report['assetIds']+rec['assetIds']));report['existingIdentityReferences']=list({(h['origin'],h['id']):h for h in report['existingIdentityReferences']+hits}.values())
  rows.append(rec)
  if len(rows)%50==0:print('dispositioned',len(rows),flush=True)
 obligations=[];existingReviews={x['sourceId']:x.get('reviewId') for x in load(ROOT/'data/public-review-metadata.json')['records']}
 for report in reports.values():
  if report['identityKey'].startswith('registry:'):continue
  ref=next((r['id'] for r in report['existingIdentityReferences'] if r['origin']=='data/content.json'),None)
  obligations.append({'reportId':report['id'],'reviewId':existingReviews.get(ref) or ('REVIEW-'+ref if ref else 'REVIEW-'+report['id']),'existingSourceId':ref,'questionInputs':[{'id':'Q'+str(i).zfill(2),'status':'not_extracted','reason':'Source-level answer not completed by acquisition/assertion intake.','answer':None} for i in range(1,16)],'complete':False,'humanApproval':'pending','publicationState':'private_draft'})
 candidate={'schemaVersion':'remaprx-reed-ingest-v1','base':inp['base'],'rows':rows,'reports':list(reports.values()),'assets':list(assets.values()),'assertions':assertions,'reviewObligations':obligations,'integrityIssues':issues,'counts':{'inputAppearances':len(rows),'byInput':{name:dict(collections.Counter(r['disposition'] for r in rows if r['sourceInput']==name)) for name in sorted({r['sourceInput'] for r in rows})},'dispositions':dict(collections.Counter(r['disposition'] for r in rows)),'uniqueReportIdentities':len(reports),'assetVersions':len(assets),'supplierAssertionsRetained':len(assertions),'newScientificResultsAccepted':0,'newGradesAssigned':0,'humanReviewed':0,'released':0}}
 write('CANDIDATE.json',candidate);write('COUNTS.json',candidate['counts']);print(json.dumps(candidate['counts'],indent=2))
if __name__=='__main__':prepare()
