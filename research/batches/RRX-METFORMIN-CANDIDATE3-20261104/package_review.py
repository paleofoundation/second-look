"""Bind candidate 3 and assemble its private, portable reviewer packet."""
import collections, hashlib, html, json, shutil, zipfile
from datetime import datetime, timezone
from pathlib import Path

B=Path(__file__).resolve().parent
REPO=B.parents[2]
PRIVATE=B.parents[3]/'private-guides/metformin-candidate3-20261104'
RAW=B.parents[3]/'private-research/RRX-METFORMIN-CANDIDATE3-20261104'
OLD=B.parent/'RRX-METFORMIN-REVIEW-20261104'
EVIDENCE=B.parent/'RRX-METFORMIN-COMPLETE-20261103'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v): Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def file_record(p): return {'sha256':sha(p),'bytes':Path(p).stat().st_size}

def main():
    m=read(PRIVATE/'manuscript-source.json')['manuscript']
    build=read(PRIVATE/'output/build-manifest.json')
    verification=read(B/'verification.json')
    assert verification['status']=='PASS' and verification['editionId']==m['editionId']
    for a in verification['pdfs']:
        assert a['sha256']==build['pdf']['assets'][a['variant']]['sha256']
    old_art=read(OLD/'guide-artifacts.json')
    for a in old_art['assets']: assert sha(a['file'])==a['sha256'],'Historical candidate changed'
    for a in read(B/'plan.json')['inputs']: assert sha(a['path'])==a['sha256']
    prior=read(old_art['source']['path'])['manuscript']
    prior_chapters={c['id']:c for c in prior['chapters']}
    locators={s['sourceId']:s['locator'] for s in read(OLD/'review.json')['sourceChecks']}
    locators.update({
        'MF-ACTIV6-ACUTE-2025':'JAMA Internal Medicine 2025; Table 2, Primary Outcome, Methods/Outcomes: aHR 0.96 (95% CrI 0.89–1.03), recovery to third consecutive symptom-free day within day 28.',
        'P-ACTIV6-2026':'CID 2026 separate follow-up: Table 3 primary modeled rates 2.9%/3.6%, RD -0.8 (-2.2,0.6), PPE .83; Table 2 day-180 missing 300/1439 and 293/1544, total593/2983.',
        'REVIVE-REPLACEMENT':'Replacement DOI10.7326/ANNALS-26-02144; Figure1 sequential cohorts, Table2 FSS, Table5 harms32/71(45.1%),17/40(42.5%),49/138(35.5%).',
        'MF-LABEL-IR-2025':'Current DailyMed SPL20261026; sections2.4 and5.1: eGFR30–60/other contrast-risk criteria,48h renal reassessment/stable restart; age65+, hypoxic states including acuteHF andsepsis.',
        'MF-LABEL-ER-2025':'Current DailyMed SPL20260625; sections2.3 and5.1, corresponding contrast and lactic-acidosis warnings.'})
    blocks=[];changed=[]
    for c in m['chapters']:
        for i,block in enumerate(c['blocks']):
            old_index=i-(1 if c['id']=='infection' and i>4 else 0)
            added=c['id']=='infection' and i==4
            before=None if added else prior_chapters[c['id']]['blocks'][old_index]
            decision='new_source_verified' if added else 'revised_and_checked' if before!=block else 'unchanged_from_candidate_2'
            if before!=block:changed.append({'chapterId':c['id'],'block':i+1,'decision':decision})
            blocks.append({'chapterId':c['id'],'block':i+1,'sourceIds':block['sourceIds'],'decision':decision,
                'blockSha256':hashlib.sha256(json.dumps(block,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
                'sourceLocators':[{'sourceId':s,'locator':locators[s]} for s in block['sourceIds']]})
    issues=[
      {'id':'ACTIV6-PRIMARY','severity':'major','status':'corrected','location':'Full PDF page7; infection block5; overview table full/sample page3 and summary page1','disposition':'Added the acute Table2 primary result and identified the CID endpoint as the separate follow-up primary. Overview wording also names the long-term report.'},
      {'id':'ACTIV6-CID-NUMBERS','severity':'major','status':'retained_with_verified_locators','location':'Full PDF page7; references27/29','disposition':'CID Table3 supports 2.9% versus3.6%; CID Table2 supports593/2983 missing, including300 and293 byarm. Replaced vague missingness with exact counts andtable references; these figures are not from the JAMA report.'},
      {'id':'REVIVE-HARMS','severity':'major','status':'corrected','location':'Full PDF page8; infection blocks10–11','disposition':'Replaced pooled49/111 with32/71(45.1%) at750mg twice daily and17/40(42.5%) at500mg twice daily; placebo49/138(35.5%). Explicit sequential enrollment, no randomized dose comparison. Retracted original stays excluded.'},
      {'id':'LABEL-CONTRAST-RISK','severity':'minor','status':'corrected','location':'Full PDF pages20–21; safety blocks3–4','disposition':'Added eGFR30–60 contrast stopping rule, other labeled contrast criteria,48h eGFR reassessment and restart only ifstable. Added age65+, acute hypoxic heart failure andsepsis context.'},
      {'id':'BIBLIOGRAPHY','severity':'minor','status':'corrected','location':'Full PDF pages26–29; all variant reference lists','disposition':'31 references with authors/corporate authors, journal/publisher and year/date status. All27 scholarly entries have verifiedDOIs. Four official label/FDA documents explicitly lack assignedDOIs. No fixed reference quota.'},
      {'id':'PDF-STRUCTURE-FONTS','severity':'minor','status':'technical_defects_corrected_acceptance_pending','location':'All three PDFs','disposition':'Actual structure tree/marked-content and link mapping, language, headings, table headers, decorative artifacts; Inter andLora embedded and unused Helvetica removed. Independent assistive-technology/reader acceptance and PDF/UA certification are not claimed.'},
      {'id':'PORTABLE-VERIFICATION','severity':'release_blocker','status':'implemented_pending_extracted_packet_run','location':'verify-packet.py and bundled inputs','disposition':'Artifact verification uses packet-relative files; original-paper archive audit is separate. No original Mac paths are opened by this verifier.'},
    ]
    assessments=[read(p) for p in sorted((EVIDENCE/'assessments').glob('*.json'))]+[read(B/'assessments/MF-ACTIV6-ACUTE-2025.json')]
    assert len(assessments)==25
    assert all(len(a['inputs'])==67 and len(a['questions'])==15 for a in assessments)
    metadata=read(B/'bibliography-metadata.json')
    assert len(metadata)==31 and sum(bool(v.get('doi')) for v in metadata.values())==27
    assert {r['id'] for r in m['references']}=={s for c in m['chapters'] for b in c['blocks'] for s in b['sourceIds']}
    review={'schemaVersion':1,'editionId':m['editionId'],'version':m['version'],'reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'Codex (OpenAI), model revision review; not independent human approval',
      'reviewInput':'User-relayed Elon candidate-2 findings. The named /workspace review file was unavailable on this host and is not claimed inspected.',
      'inputCommit':read(B/'plan.json')['baseCommit'],'issueDispositions':issues,
      'sourceChecks':[{'sourceId':r['id'],'locator':locators[r['id']],'bibliographicMetadata':'bibliography-metadata.json','disposition':'verified_changed_scope' if r['id'] in ['MF-ACTIV6-ACUTE-2025','P-ACTIV6-2026','REVIVE-REPLACEMENT','MF-LABEL-IR-2025','MF-LABEL-ER-2025'] else 'prior_assessment_preserved_metadata_verified'} for r in m['references']],
      'blockAudit':blocks,'changedBlocks':changed,'artifactChecks':verification,
      'assessmentCoverage':{'distinctSourceIds':34,'citedReferences':31,'structuredStudyReports':25,'states':dict(collections.Counter(a['completion'] for a in assessments)),'newStudyInputs':67,'newStudyQuestions':15,'limits':'Access gaps remain explicit; assessments are not fabricated as fully accessed or independently approved.'},
      'remainingApprovals':['Qualified independent pharmacist/physician, exact candidate-3 hashes','Human editor, exact candidate-3 hashes','Legal counsel, exact candidate-3 hashes','Existing accessibility/reader acceptance and production merchant/tax/refund/support and test checkout requirements'],
      'decision':'corrected_candidate_ready_for_independent_review','releaseDecision':'not_ready_to_activate','humanClinicalApproval':'pending','humanEditorialApproval':'pending','commercialLegalApproval':'pending'}
    write(B/'review.json',review);write(B/'guide-block-map.json',blocks)
    write(B/'source-acquisition.json',{'files':[{'file':p.name,**file_record(p)} for p in sorted(RAW.iterdir()) if p.is_file()],'retrievalReceipt':read(RAW/'acquisition.json'),'supplementWarning':'Files s001–s005 have .pdf suffixes but contain HTML, not retrieved PDFs; no supplement inspection is claimed.'})
    artifacts={'productId':m['productId'],'editionId':m['editionId'],'version':m['version'],'state':'private_reviewed_candidate','supersedes':prior['editionId'],
      'source':{'path':str(PRIVATE/'manuscript-source.json'),**file_record(PRIVATE/'manuscript-source.json')},
      'buildManifest':{'path':str(PRIVATE/'output/build-manifest.json'),**file_record(PRIVATE/'output/build-manifest.json')},
      'assets':[{'file':str(PRIVATE/'output'/f),**a} for f,a in build['assets'].items()],
      'modelReview':{'path':str(B/'review.json'),'sha256':sha(B/'review.json'),'decision':review['decision']},
      'independentClinicalReview':'pending','humanEditorialApproval':'pending','commercialLegalApproval':'pending','release':'not_deployed_or_for_sale','pdfAccessibility':'Structure tags and font embedding checked; independent screen-reader/reader acceptance and PDF/UA certification pending.'}
    write(B/'guide-artifacts.json',artifacts)
    approvals=read(OLD/'pending-approvals.json')
    approvals['bindings'].update(editionId=m['editionId'],version=m['version'],assets=artifacts['assets'])
    approvals['requiredFurtherAcceptance'][0]='Independent accessibility/assistive-technology and real-reader acceptance; structural repairs are not certification'
    write(B/'pending-approvals.json',approvals)
    packet=PRIVATE/'handoff/Metformin-candidate-3-review-packet';packet.mkdir(parents=True,exist_ok=True)
    for f in [*build['assets'],'build-manifest.json','pdf-manifest.json']:shutil.copy2(PRIVATE/'output'/f,packet/f)
    shutil.copy2(PRIVATE/'manuscript-source.json',packet/'manuscript-source.json')
    shutil.copy2(REPO/'scripts/guide-renderer/verify-packet.py',packet/'verify-packet.py')
    for f in ['review.json','verification.json','pending-approvals.json','bibliography-metadata.json','guide-block-map.json']:
        shutil.copy2(B/f,packet/f)
    (packet/'assessments').mkdir(exist_ok=True)
    parts=['<!doctype html><html lang="en"><meta charset="utf-8"><title>Metformin candidate 3 source assessments</title><style>body{font:17px/1.6 system-ui;max-width:950px;margin:40px auto;padding:0 24px}h1,h2{color:#1937df}section{border-top:2px solid #ddd;margin-top:40px}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><body><h1>Metformin candidate 3: 25 study-report assessments</h1><p>Model-authored assessments retain their access limits. No clinical, editorial or legal approval is implied. Original papers are linked in the guide and are not redistributed.</p>']
    for a in assessments:
        write(packet/'assessments'/(a['sourceId']+'.json'),a)
        parts.append('<section><h2>'+html.escape(a['title'])+'</h2><p>'+html.escape(a['sourceId']+'; '+a['completion'])+'</p>')
        for qid,q in a['questions'].items():parts.append('<h3>'+html.escape(qid)+'</h3><p>'+html.escape(q['answer'])+'</p>')
        parts.append('<h3>Appraisal</h3><p>'+html.escape(a['appraisal'])+'</p><p>Unresolved inputs: '+html.escape(', '.join(a.get('unresolvedInputs',[])) or 'None recorded for the available packet; not independent approval.')+'</p></section>')
    (packet/'Study-assessments.html').write_text('\n'.join(parts)+'</body></html>')
    (packet/'requirements.txt').write_text('pypdf==6.10.0\npdfplumber==0.11.9\n')
    (packet/'READ-ME-FIRST.txt').write_text('''METFORMIN — CANDIDATE 3 REVIEW HANDOFF
Edition: 2026.11.04-candidate.3
Status: Corrected private review candidate. Purchase/release NOT ready to activate.

Start with the 29-page full PDF. Preview: 8 pages. Printable summary: 3 pages.
The PDF and web JSON share the same authoritative manuscript. The 31-reference
bibliography has no arbitrary source-count limit. Original journal papers are
linked, not redistributed. Study-assessments.html contains all 25 structured
study-report assessments; individual JSON records preserve all 67 inputs each.
Source-path strings in those records are provenance, not verifier dependencies.

Changes to recheck:
1. Full p7: acute ACTIV-6 primary recovery aHR0.96, 95%CrI0.89–1.03; separate CID
   long-term primary clearly named. CID Table3 supports2.9% versus3.6%, and
   Table2 supports593/2983 missing day180 responses. Overview wording agrees.
2. Full p8: REVIVE harms split by sequential dose cohort (32/71;17/40;49/138
   placebo); doses were not randomized against each other. Original excluded.
3. Full pp20–21: labeled contrast interruption/reassessment/restart criteria,
   age65+, acute hypoxic heart failure andsepsis context.
4. Full pp26–29: authors/journal/year and verified scholarly DOIs. Four official
   documents have no assigned DOI and are identified accordingly.
5. All PDFs: actual structure tags and embedded fonts. Independent screen-reader
   and real-reader acceptance remain pending; PDF/UA certification not claimed.

PORTABLE VERIFICATION (Python3.10+; no original Mac files needed)
From this extracted directory, use a virtual environment if preferred:
  python -m pip install -r requirements.txt
  python verify-packet.py --packet . --report verification-local.json

This checks packet hashes, web/PDF text and reference parity, tags, fonts, links,
bookmarks and page geometry. It does not re-audit the full original-paper archive
or supply clinical, editorial, legal or commercial approval. packet-manifest.json
lists the transferred files; compare its hash and the ZIP hash with the separately
provided handoff receipt to establish the intended package identity.

SIGN-OFF
An independent pharmacist/physician, a human editor, and legal counsel must review
this exact candidate, identifying themselves, qualifications, scope, conflicts,
decision and date against its hashes. pending-approvals.json is an unfilled
template; blank fields and technical PASS results are not approvals.

Commerce remains pending: merchant/tax/refund/support details and real test-mode
checkout/fulfillment. Seller selected by owner: Microbiome Signatures LLC.
Membership launch also waits for Long COVID and itraconazole guides.
No deployment, sale or human approval is created by this handoff.
''')
    print('Review records and portable inputs prepared:',packet)

if __name__=='__main__':main()
