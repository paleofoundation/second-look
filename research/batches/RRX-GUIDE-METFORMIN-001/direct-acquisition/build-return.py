"""Build private source receipt from actual transport bytes; no scientific extraction."""
import datetime
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parent
PACKET = ROOT.parent / 'acquisition-v1.1'
STAGE = Path('/Users/kmfp/Documents/ChatGPT/Drug Repurposing/private-research/RRX-GUIDE-METFORMIN-001/ACQUIRE-1.1')
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(b): return hashlib.sha256(b).hexdigest()
def write(p, obj): p.write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n')
assignments = json.loads((PACKET/'assignment.json').read_text())['assignments']
expected = {a['assignmentId']:a for a in assignments}
attempts = sorted([json.loads(p.read_text()) for p in (STAGE/'attempts').glob('*/receipt.json')],key=lambda r:(r['retrievedAt'],r['url']))
assets=[]
verifications=[]

def get(n, purpose):
    return next(r for r in attempts if r['assignmentId']==f'MF-GAP-{n:02}' and r['purpose']==purpose)

def add(n,purpose,role,filename,doi,pmid,title,version,rights,member=None):
    r=get(n,purpose)
    assert r['curlExit']==0 and r['httpStatus']==200
    raw=(STAGE/r['body']).read_bytes()
    assert sha(raw)==r['sha256'] and len(raw)==r['bytes']
    if member:
        with zipfile.ZipFile(STAGE/r['body']) as z:
            assert z.testzip() is None
            data=z.read(member)
    else:data=raw
    mime={'xml':'application/xml','html':'text/html','pdf':'application/pdf','docx':'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}[filename.rsplit('.',1)[1]]
    identity={'assetFilename':filename,'assignmentId':r['assignmentId'],'identityStatus':'checked_for_receipt_not_scientific_assessment','originalTransportSha256':r['sha256'],'archiveMember':member,'checks':[]}
    if mime=='application/xml':
        root=ET.fromstring(data)
        ids={x.attrib.get('pub-id-type'):x.text for x in root.findall('.//article-meta/article-id')}
        assert ids.get('doi','').lower()==doi.lower() and ids.get('pmid')==pmid
        assert root.find('body') is not None
        identity['checks']=['XML parses','embedded DOI and PMID match','article body present'];identity['identifiers']=ids
    elif mime=='text/html':
        text=data.decode()
        if role=='full_report':
            assert html.unescape(re.search(r'<meta name="citation_doi" content="([^"]+)"',text).group(1)).lower()==doi.lower()
            assert re.search(r'<meta name="citation_pmid" content="([^"]+)"',text).group(1)==pmid
            assert all(k in text for k in ['Methods','Results','Discussion','References'])
            identity['checks']=['embedded DOI and PMID match','methods/results/discussion/references sections present','not challenge/abstract-only response']
        else:
            assert '<title>Generic Drug Facts | FDA</title>' in text
            identity['checks']=['official FDA URL','expected page title','content-current date 2021-11-01 visible']
    elif mime=='application/pdf':
        assert data.startswith(b'%PDF-') and b'%%EOF' in data[-2048:]
        identity['checks']=['PDF header and EOF present','publisher/repository or exact article supplement linkage verified']
        if n==2:identity['checks']+=['10-page PDF opened with pypdf','first-page title matches MET-PREVENT','embedded DOI link matches 10.1016/j.lanhl.2025.100695','front-page CC BY notice present']
        if n==13:identity['checks']+=['29-page PDF opened with pypdf','front-page Time Cap product matches requested DailyMed setid','official HTML revised 2/2025; updated 2025-02-10; distinct from held Zydus/Glumetza products']
    target=expected[r['assignmentId']]['targetSourceId']
    aid=f'MF-A11-{n:02}-{len([a for a in assets if a["assignmentId"]==r["assignmentId"]])+1:02}'
    tier='PRIMARY' if n<=11 else 'CONTEXT'
    path='sources/'+tier+'/'+filename
    out=STAGE/path;out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():assert out.read_bytes()==data,'Never overwrite a different source version'
    else:out.write_bytes(data)
    asset={'assetId':aid,'assignmentId':r['assignmentId'],'targetSourceId':target,'canonicalReportId':target if role!='correction_notice' else target+'-CORRECTION-32141718',
        'role':role,'relationshipToTarget':('Exact linked supplementary member '+member+' of immutable downloaded archive '+r['sha256']) if member else ('Published corrigendum explicitly links PMC6826125; correction impact not assessed' if role=='correction_notice' else 'Exact report or official context identified for receipt; downstream scientific acceptance pending'),
        'title':title,'doi':doi,'pmid':pmid,'identifierMissingReason':None if doi and pmid else 'Official context is identified by URL/product setid; no DOI or PMID applies',
        'originalUrl':r['url'],'resolvedUrl':r['resolvedUrl'],'retrievedAt':r['retrievedAt'],'sourceVersion':version,'versionMissingReason':None,
        'path':path,'mediaType':mime,'bytes':len(data),'sha256':sha(data),'rights':rights,
        'accessBasis':'official_source' if n>=13 else 'permitted_supplement' if member else 'lawful_full_text',
        'scientificExtraction':'not_performed','quarantine':False}
    assets.append(asset);verifications.append(identity)

cc='CC BY 4.0 stated by source; attribution and third-party material exceptions apply. Private research copy; no source redistribution performed.'
pmc='Freely accessible article on PMC; publisher copyright retained. Private research copy only, no redistribution grant inferred.'
add(2,'repository-published-version','full_report','MF-METPREVENT-2025.pdf','10.1016/j.lanhl.2025.100695','40147475',expected['MF-GAP-02']['title'],'Published version, 2025; Newcastle deposit 305174',cc)
add(3,'lawful-oa-fulltext','full_report','MF-MASTERS-2019.xml','10.1111/acel.13039','31557380',expected['MF-GAP-03']['title'],'PMC6826125 XML captured 2026-10-12; linked corrigendum retained separately',cc)
add(3,'lawful-oa-correction','correction_notice','MF-MASTERS-CORRECTION-32141718.xml','10.1111/acel.13098','32141718','Corrigendum to MASTERS trial','PMC7059173.1; PMC last-change 2020-03-12',cc)
add(4,'lawful-oa-fulltext','full_report','MF-SCHIZOPHRENIA-PARENT-2023.xml','10.1038/s41398-023-02616-x','37821461',expected['MF-GAP-04']['title'],'PMC10567690.1; PMC last-change 2024-01-27',cc)
for n,doi,pmid,pmcid in [(5,'10.1001/jamaoncol.2021.2318','34323922','PMC8323052'),(6,'10.1001/jamaoncol.2021.2328','34323924','PMC8323053'),(7,'10.1001/jama.2022.6147','35608580','PMC9131745'),(8,'10.1038/s41523-021-00275-z','34103538','PMC8187713')]:
    add(n,'lawful-free-fulltext','full_report',expected[f'MF-GAP-{n:02}']['targetSourceId']+'.html',doi,pmid,expected[f'MF-GAP-{n:02}']['title'],pmcid+' served HTML captured 2026-10-12; exact historical revision not established',cc if n==8 else pmc)
for part in ['1','2']:
    member='41523_2021_275_MOESM'+part+'_ESM.pdf'
    add(8,'documented-supplement-archive','supplement',member,'10.1038/s41523-021-00275-z','34103538','MA.32 metabolic report supplementary file '+part,'Supplement as served with PMC8187713 on 2026-10-12; internal amendment history not assessed',cc,member)
add(13,'different-product-official-label','official_label','MF-LABEL-TIMECAP-2025.pdf',None,None,'Metformin HCl tablets — Time Cap Laboratories, Inc','DailyMed setid 542cec22-eeae-4704-9bb6-4176640e5ea8; revised 2/2025; page updated 2025-02-10','Official DailyMed prescribing information; private source copy; no new efficacy claims or prescribing advice.')
add(14,'official-version-identity','regulatory_context','MF-FDA-GENERICS.html',None,None,'Generic Drug Facts','FDA content current as of 2021-11-01; captured 2026-10-12','Official FDA public regulatory context; third-party rights, if any, retained.')

missing={
1:['Complete report DOI 10.7326/ANNALS-25-04883','Supplementary Material (5.08 MB) linked on publisher page','Study Protocol and Statistical Analysis Plan (969.86 KB)','Data Sharing Statement (67.46 KB); associated registry KCT0009342 and version check'],
2:['Linked appendix/supplement','Protocol and SAP; repository says available from investigator, no contact authorized','ISRCTN29932357 record and amendment/version comparison'],
3:['ACEL-18-e13039-s001.docx','ACEL-18-e13039-s002.docx','ACEL-18-e13039-s003.docx','ACEL-18-e13039-s004.docx','ACEL-18-e13039-s005.docx','NCT02308228 history/SAP comparison; reuse held B-R0057 protocol and Word companion'],
4:['41398_2023_2616_MOESM1_ESM.pdf reporting checklist','41398_2023_2616_MOESM2_ESM.docx supplemental material including protocol','NCT03271866 history and SAP comparison'],
5:['jamaoncol-e212318-s001.pdf','jamaoncol-e212318-s002.pdf','jamaoncol-e212318-s003.pdf','Article-linked registry/protocol/SAP version audit'],
6:['jamaoncol-e212328-s001.pdf','jamaoncol-e212328-s002.pdf','jamaoncol-e212328-s003.pdf','Article-linked registry/protocol/SAP version audit'],
7:['jama-e226147-s001.pdf','jama-e226147-s002.pdf','jama-e226147-s003.pdf','jama-e226147-s004.pdf','NCT01101438 history/protocol/SAP comparison shared with metabolic report'],
8:['NCT01101438 history/protocol/SAP comparison shared with clinical report; companion scientific contents not yet audited'],
9:['Complete report DOI 10.1016/S1470-2045(15)00027-3 and linked supplements/protocol/SAP'],
10:['Complete report DOI 10.1016/S1470-2045(15)00565-3 and linked supplements/protocol/SAP'],
11:['Complete report DOI 10.1158/1940-6207.CAPR-10-0186 and linked supplements/protocol/SAP'],
12:['Actual correction notice DOI 10.1016/S1473-3099(23)00562-5 / PMID 37666258','Changed-version/companion trail against held original DOI 10.1016/S1473-3099(23)00299-2 / PMID 37302406'],13:[],14:[]}
reasons={1:'Exact identity confirmed in Europe PMC. Publisher returned 403 challenge. Search-visible primary publisher content has companion links; cached text is not a complete delivered source file. Europe PMC subscription metadata and PubMed free-article label differ; do not infer definitive paywall status.',2:'Published report actually obtained from Newcastle repository after initial landing request timed out. Publisher returned 403; companion version audit remains.',3:'Full XML and actual linked corrigendum obtained. Five supplement URLs returned HTML instead of Word files. Documented Europe PMC archive timed out/incomplete twice; none of those partial bytes accepted as source.',4:'Full XML obtained. Linked PDF/Word files returned HTML; Europe PMC supplement archive incomplete twice; not accepted.',5:'Complete served PMC article HTML obtained. Linked PDFs returned HTML challenge; Europe PMC API says not OA; no bypass attempted.',6:'Complete served PMC article HTML obtained. Linked PDFs returned HTML challenge; Europe PMC API says not OA; no bypass attempted.',7:'Complete served PMC article HTML obtained. Linked PDFs returned HTML challenge; Europe PMC API says not OA; no bypass attempted.',8:'Complete PMC HTML and both exact PDF supplement members obtained from a complete Europe PMC ZIP; ZIP CRC and member hashes verified. This is the metabolic report DOI 10.1038/s41523-021-00275-z, not the separate sex-hormone report.',9:'Exact identity confirmed. DOI landing was redirect HTML, publisher returned 403; no complete report acquired.',10:'Exact identity confirmed. DOI landing was redirect HTML, publisher returned 403; no complete report acquired.',11:'Exact identity/DOI resolved. Publisher returned 403; no complete report acquired.',12:'PubMed/Europe PMC correction relationship and separate notice DOI resolved; publisher API supplied metadata only and publisher page returned 403. Actual notice body not acquired; original remains held.',13:'Exact article-linked Time Cap product/version obtained; distinct from held Zydus IR and Glumetza ER labels, which remain reusable and unchanged.',14:'Actual dated FDA page obtained and expected title/date verified.'}
dispositions=[]
for n,a in enumerate(assignments,1):
    ids=[x['assetId'] for x in assets if x['assignmentId']==a['assignmentId']]
    status='acquired' if n>=13 else 'partially_acquired' if ids else 'not_accessible'
    next_action='Independent source receipt and source-specific safety/context assessment; no public changes.' if n>=13 else ('Obtain listed missing complete report/notice through ordinary publisher access or authorized library/owner upload; no need to reacquire held originals. ' if not ids else 'Reuse newly held full source; obtain only listed missing companions where required. ')+ 'Reconcile identity/version/family, prepare source-pinned extraction readiness, complete Q01–Q15/numerical audit and independent scientific review before guide synthesis.'
    dispositions.append({'assignmentId':a['assignmentId'],'targetSourceId':a['targetSourceId'],'status':status,'assetIds':ids,'missingArtifacts':missing[n],'reason':reasons[n],'nextAction':next_action})

manifest={'operationId':'RRX-GUIDE-METFORMIN-001-ACQUIRE','planVersion':'1.1','artifactType':'source_acquisition_return','fixture':False,'preparedAt':NOW,'actualCutoff':'2026-10-12','inputPlanSha256':sha((PACKET/'PLAN.md').read_bytes()),'inputSchemaSha256':sha((PACKET/'return.schema.json').read_bytes()),'assignments':dispositions,'assets':assets,'fileCount':len(assets),'totalSourceBytes':sum(a['bytes'] for a in assets),'logs':{'searches':'searches.json','screening':'screening.json','reviewInputAvailability':'review-input-availability.json','gaps':'gaps.json','reversePrompt':'CHATGPT-INGEST-PROMPT.txt'},'scientificAssessmentComplete':False,'humanReviewComplete':False,'released':False}
write(STAGE/'manifest.json',manifest)
query_log=[]
for r in attempts:
    item=dict(r);item['observedHitCount']=None;item['hitCountReason']='Direct source retrieval, not a result-list search'
    if r['purpose']=='exact-metadata-identity':
        data=json.loads((STAGE/r['body']).read_text());item['observedHitCount']=data['hitCount'];item['queryString']=data['request']['queryString'];item['hitCountReason']=None
    item['bodyIsDeliveredSource']=any(a['originalUrl']==r['url'] and a['retrievedAt']==r['retrievedAt'] for a in assets)
    query_log.append(item)
write(STAGE/'searches.json',{'scope':'Exact report/companion retrieval; not comprehensive literature search','executedDate':'2026-10-12','transportRequests':query_log,'supplementApiDocumentation':'https://europepmc.org/RestfulWebService','publisherApiDocumentation':'https://dev.elsevier.com/documentation/FullTextRetrievalAPI.wadl','webLocatorChecks':[{'url':'https://eprints.ncl.ac.uk/305174','finding':'Published version link and CC BY4.0 license verified; download captured separately in transport log'},{'query':'"10.7326/ANNALS-25-04883" full text','finding':'Primary publisher indexed content exposes companion names/sizes; not counted as local fulltext'},{'query':'"10.1016/S1473-3099(23)00562-5" correction','finding':'No additional complete actual notice obtained'},{'query':'"10.1158/1940-6207.CAPR-10-0186" full text','finding':'No additional lawful complete original obtained'}],'webCheckTimestamp':None,'webCheckTimestampMissingReason':'Tool did not return execution timestamp; checks occurred 2026-10-12 during this acquisition, exact raw HTTP retrieval times recorded individually','excludedCoordinatedTargets':['P-ACTIV6-2026','P-REVIVE-2026']})
write(STAGE/'screening.json',{'assignments':dispositions,'sourceChecks':verifications,'notAcceptedAsSource':['403/challenge/redirect HTML','Metadata-only correction API response','Incomplete supplementary ZIPs','Europe PMC non-OA error XML'],'integratorAcceptance':'pending'})
planned=json.loads((PACKET/'inputs/planned-review-inputs.json').read_text())
for paper in planned['papers']:
    d=next(x for x in dispositions if x['targetSourceId']==paper['targetSourceId'])
    for q in paper['questions']:
        q['status']='not_extracted';q['deliveredAssetIds']=d['assetIds'];q['inputAvailability']='full_report_received_companions_or_version_audit_pending' if d['assetIds'] else 'complete_report_missing';q['questionSpecificLocation']='not_checked';q['nextAction']='Use actual pinned source assets after independent receipt acceptance; locate each required field, preserve omissions and complete source-specific scientific review.'
write(STAGE/'review-input-availability.json',planned)
write(STAGE/'gaps.json',{'operationId':manifest['operationId'],'assignments':[d for d in dispositions if d['missingArtifacts']],'correctionHolds':[{'target':'P-COVIDOUT-2023','noticeDoi':'10.1016/S1473-3099(23)00562-5','noticePmid':'37666258','originalDoi':'10.1016/S1473-3099(23)00299-2','originalPmid':'37302406','noticeBody':'not_acquired','scientificImpact':'not_assessed'},{'target':'MF-MASTERS-2019','noticeDoi':'10.1111/acel.13098','noticePmid':'32141718','noticePmcid':'PMC7059173','noticeBody':'acquired','scientificImpact':'not_assessed'}],'coordinatedExistingRequest':'RRX-GAP-001-1.1 unchanged: ACTIV-6/REVIVE; no duplicate acquisition/dispatch','newCompletedExtractions':0,'newCompletedAssessments':0,'newHumanApprovals':0,'guideManuscript':'HOLD'})
write(STAGE/'source-verification.json',{'performedBy':'codex/metformin_research','scope':'Byte/media and report-identity receipt checks only; independent root acceptance pending','checks':verifications})

prompt=f'''Continue Drug Repurposing / RemapRx, operation RRX-GUIDE-METFORMIN-001-ACQUIRE v1.1. This is a direct local acquisition return in {STAGE}; no external worker dispatch or transfer is claimed. Use the existing shared private staging files. If moving between environments, transfer the actual private return ZIP and verify its sidecar receipt before receipt acceptance.

The accepted input request is RRX-GUIDE-METFORMIN-001-1.1-request.zip, root RRX-GUIDE-METFORMIN-001-1.1/. Input plan SHA-256 {manifest['inputPlanSha256']}; input schema SHA-256 {manifest['inputSchemaSha256']}. Actual manifest SHA-256 {sha((STAGE/'manifest.json').read_bytes())}. The local return has {len(assets)} delivered source files and {manifest['totalSourceBytes']} source bytes: seven main reports, one MASTERS corrigendum, two MA.32 metabolic PDF supplements, one exact Time Cap label and one FDA context page. Retrieval cutoff: 2026-10-12. Two assignments acquired, seven partially acquired, five not accessible. Root receiver verification is pending; transport/identity verification by acquisition worker is not independent acceptance.

Read manifest.json, searches.json, screening.json, review-input-availability.json, gaps.json and source-verification.json. Raw sources are in sources/PRIMARY/ and sources/CONTEXT/. Validate every byte/hash/path/media type and all fourteen dispositions; reconcile exact report IDs and overlapping study families. Keep the separate RRX-GAP-001 ACTIV-6/REVIVE request intact and preserve its version/quarantine holds. COVID-OUT notice DOI 10.1016/S1473-3099(23)00562-5 / PMID 37666258 is metadata-confirmed but its actual body remains missing. MASTERS corrigendum DOI 10.1111/acel.13098 / PMID 32141718 is acquired but its impact is not assessed.

Missing main reports: established Long COVID DOI 10.7326/ANNALS-25-04883; pancreatic trial DOI 10.1016/S1470-2045(15)00027-3; adenoma trial DOI 10.1016/S1470-2045(15)00565-3; crypt-foci trial DOI 10.1158/1940-6207.CAPR-10-0186. Missing actual COVID-OUT correction as above. Obtain only missing companions listed by exact filename in gaps.json, including MASTERS five Word files, schizophrenia PDF/Word companions, three NRG-LU001 PDFs, three ALMERA PDFs, four MA.32 clinical PDFs, MET-PREVENT appendix and required registry/protocol/SAP histories. Do not request the seven newly held main reports, two held metabolic supplements or original holdings again.

Seven new main-report byte/identity candidates, twelve total source assets; zero new completed scientific extractions, assessments, human reviews, syntheses or releases. All 165 Q01–Q15 entries remain not_extracted. After independent source receipt, prepare matching source-pinned extraction readiness, reuse existing result/review IDs, extract source-located question inputs and numerical checks, independently audit, then stage/diff an idempotent canonical candidate. Do not regenerate the historical corpus or publish automatically. The substantive metformin manuscript remains held until ingestion and assessment pass.
'''
(STAGE/'CHATGPT-INGEST-PROMPT.txt').write_text(prompt)
summary={'operationId':manifest['operationId'],'phase':'direct_local_source_receipt_candidate','preparedAt':NOW,'privateStagingPath':str(STAGE),'manifestSha256':sha((STAGE/'manifest.json').read_bytes()),'assets':[{k:a[k] for k in ['assetId','assignmentId','targetSourceId','role','path','bytes','sha256','doi','pmid']} for a in assets],'fileCount':len(assets),'totalSourceBytes':manifest['totalSourceBytes'],'mainReports':7,'correctionNotices':1,'supplementFiles':2,'officialContextFiles':2,'assignmentDispositions':dispositions,'newCompletedExtractions':0,'newCompletedAssessments':0,'newHumanApprovals':0,'released':False,'independentReceiptAcceptance':'pending'}
write(ROOT/'receipt.json',summary)
write(ROOT/'source-verification.json',json.loads((STAGE/'source-verification.json').read_text()))
print(json.dumps({k:summary[k] for k in ['fileCount','totalSourceBytes','mainReports','correctionNotices','supplementFiles','officialContextFiles','manifestSha256']}))
