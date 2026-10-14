#!/usr/bin/env python3
"""Prepare prospective metadata assignments; no source reading or GP approval."""
import hashlib
import json
from pathlib import Path
import sys

OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'AGENTS.md').is_file() and (p/'data').is_dir())
sys.path.insert(0,str(ROOT))
from scripts.research_full_review import ASSIGNMENT_SCHEMA
from scripts.research_ingest.source_validation import schema_errors


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name,value):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def pin(path):return dict(path=path.relative_to(ROOT).as_posix(),sha256=digest(path))


def asset(row,role):
    if row['mediaType']=='application/pdf':units=[dict(id=f'page-{n}',kind='pdf_page',locator=str(n)) for n in range(1,row['pages']+1)]
    elif row['mediaType']=='image/webp':units=[dict(id='image',kind='image',locator=Path(row['path']).name)]
    else:raise ValueError('Assignment requires an adopted media contract')
    return dict(sourceId=row['sourceId'],role=role,required=True,mediaType=row['mediaType'],availability='available',
                sha256=row['sha256'],bytes=row['bytes'],path=row['path'],expectedUnits=units,
                reason='Preserved assigned report or companion bytes; source identity and scientific content require prospective inspection.')


def main():
    inventory=json.loads((OUT/'metadata-inventory.json').read_text())
    prior_assignments=json.loads((ROOT/'research/batches/RRX-INGEST-001/calibration/assignments.json').read_text())
    prior_locations=json.loads((ROOT/'research/batches/RRX-INGEST-001/inventory/source-locations.json').read_text())
    mapping=dict(schemaVersion='remaprx-research-inventory-v1',roots={},files=[],archiveMembers=[])
    summaries=[];assignments=[];archive_manifest=[]
    for packet in inventory['packets']:
        pid=packet['packetId'];existing=packet['sourceAssets'];held=packet['heldDiagnosticPacket']
        summary=dict(packetId=pid,canonicalReportId=packet['canonicalReportId'],existingSourceAssets=len(existing),
                     preservedResultIds=packet['preservedResultIds'],familyCoordination=packet['familyCoordination'],
                     inheritedHold=packet['holdReason'],sourceIntegrityReview='pending_new_dated_scoped_review',
                     scientificInspectionPerformed=False,fullReviewComplete=False,gpStatus='NOT_RECORDED',
                     sourceCoverageCompleteness='not_established_by_metadata_preflight',gaps=[])
        for row in existing:
            logical=row['logicalSource'];root_id=logical['rootId']
            mapping['roots'][root_id]=prior_locations['roots'][root_id]
            mapping['files'].append(dict(id=row['sourceId'],rootId=root_id,path=logical['path'],sha256=row['sha256'],bytes=row['bytes'],mediaType=row['mediaType'],verificationState='verified'))
        if pid in ('CAL-01','CAL-02','CAL-03'):
            aid=f'{pid}-FULL-PROSPECTIVE-1'
            assignment=dict(schemaVersion='remaprx-full-review-assignment-v1',assignmentId=aid,
                            planId=f'RRX-CAL-T1-{pid.replace("-","")}-REVIEW-PROSPECTIVE-1.0',canonicalReportId=packet['canonicalReportId'],
                            reviewId=packet['canonicalReportId'],assets=[])
            for row in existing:
                role='primary' if row['sourceId']==packet['primarySourceId'] else 'companion'
                if row['mediaType']!='application/zip':assignment['assets'].append(asset(row,role));continue
                for member in row['archiveMembers']:
                    sid=row['sourceId']+'::'+member['sha256'][:12]
                    mapping['archiveMembers'].append(dict(id=sid,archiveFileId=row['sourceId'],path=member['path'],sha256=member['sha256'],bytes=member['bytes'],mediaType='application/pdf',verificationState='verified'))
                    archive_manifest.append(dict(sourceId=sid,canonicalReportId=packet['canonicalReportId'],archiveSourceId=row['sourceId'],archiveSha256=row['sha256'],member=member,
                                                 expectedUnits=[dict(id=f'page-{n}',kind='pdf_page',locator=str(n)) for n in range(1,member['pages']+1)],
                                                 proposedMaterializationRelativePath=f'{pid}/archive-members/{member["sha256"]}.pdf',
                                                 currentState='verified_in_archive_not_materialized',scientificInspectionPerformed=False))
                    assignment['assets'].append(dict(sourceId=sid,role='companion',required=True,mediaType='application/pdf',availability='pending',sha256=None,bytes=None,path=None,expectedUnits=[],
                        reason='Exact PDF member bytes/hash/pages are inventoried separately; safe materialization and receipt require prospective GP before the readable source assignment is finalized.'))
                summary['gaps'].append('Three PDF companions are verified inside the ZIP but not materialized for the path-based full-review validator. Preserve hashes/member identity and complete prospective safe materialization before final source GP.')
            if pid=='CAL-03':summary['gaps'].append('Two prior octet-stream/unsupported-format holds correspond to verified WebP signatures. Adopt the existing image locator/visual inspection contract prospectively and verify source association before superseding these format holds.')
            errors=schema_errors(ASSIGNMENT_SCHEMA,assignment)
            if errors:raise ValueError(errors)
            relative=pid+'/assignment.candidate.json';save(relative,assignment);assignments.append(relative)
            summary.update(status='PROSPECTIVE_METADATA_ELIGIBLE',assignment=relative,requiredAssets=len(assignment['assets']),
                           availableInspectionUnits=sum(len(a['expectedUnits']) for a in assignment['assets']),
                           activation='After CAL07 acceptance, fresh design-specific GP and any source preparation prerequisites; no extraction authorized by this draft.')
        elif pid=='CAL-08':
            structure=existing[0]['htmlStructure']
            summary.update(status='HOLD_MISSING_REQUIRED_FIGURES_AND_UNSUPPORTED_DOCX',requiredMissingFigureCount=len(structure['figureImageReferences']),
                           missingFigures=structure['figureImageReferences'],documentLinks=structure['documentLinkReferences'],
                           nativeSectionCount=len(structure['sectionIds']),nativeFigureCount=len(structure['figureIds']),assignment=None)
            summary['gaps'] += ['Four referenced JPEG figure assets are absent from this assigned packet; figure URLs are not receipt or visual inspection.',
                                 'Required linked ALZ-18-2393-s001.docx is not present. The frozen full-review schema has no DOCX locator contract; preserve original bytes and adopt a separately versioned native/derived-representation contract before authoring.',
                                 'Optional article PDF does not replace missing supporting information. Remote URLs have not been requested or checked.']
        else:
            summary.update(status='HOLD_PRESERVED',assignment=None)
            summary['gaps'] += [packet['holdReason'],* [g['reason'] for g in packet['gaps']]]
            if pid in ('CAL-04','CAL-05'):summary['gaps'].append('Same34-page preprint bytes are assigned to distinct report/version identities. Preserve both IDs and existing held results; require additive identity/version adjudication and fresh acceptance before any supporting extraction.')
        save(pid+'/eligibility.json',summary);summaries.append(summary)
    save('source-locations.prospective.json',mapping)
    save('archive-members.prospective.json',dict(schemaVersion='remaprx-prospective-archive-members-v1',status='NOT_MATERIALIZED_NOT_APPROVED',members=archive_manifest))
    save('eligibility-summary.json',dict(schemaVersion='remaprx-tranche-eligibility-v1',status='PROSPECTIVE_METADATA_ONLY',packets=summaries,
         conditionallyEligible=['CAL-01','CAL-02','CAL-03'],held=['CAL-04','CAL-05','CAL-06','CAL-08'],sourceReviewComplete=0,gpPassed=False,performedAcquisition=False,performedImport=False))
    identities=[]
    for packet in prior_assignments['packets']:
        if packet['packetId'] not in ('CAL-01','CAL-02','CAL-03'):continue
        main=next(a for a in packet['sourceAssignments'] if a['source_id']==packet['primarySourceId'])
        identities.append(dict(packetId=packet['packetId'],canonicalReportId=packet['canonicalReportId'],sourceId=packet['primarySourceId'],sourceSha256=main['sha256'],
            expectedTitleFromPreservedMetadata=packet['titleFromMetadata'],expectedDois=sorted({r['doi'] for r in packet['sourceRecords'] if r.get('doi')}),expectedPmids=sorted({r['pmid'] for r in packet['sourceRecords'] if r.get('pmid')}),
            frontMatterInspection='NOT_PERFORMED',version='NOT_YET_CONFIRMED_FROM_ASSIGNED_PRIMARY',historicalIdsPreserved=True,
            requiredReceipt=['Exact primary-file hash and physical front-matter locator','Literal title/DOI/version printed in the source; PMID only if actually present','Separate external PMID/DOI/title/version cross-check with exact receipt hash and dated scope','Alias/version discrepancies preserved as HOLD; no silent renaming or report merging'],
            activation='Central integrator identity acceptance before scientific extraction fan-out; metadata check under prospective GP.'))
    save('bibliographic-identity.proposed.json',dict(schemaVersion='remaprx-bibliographic-identity-preflight-v1',status='PROPOSED_NOT_PERFORMED',packets=identities,
         currentIntegrityAcquisition=dict(status='PENDING_SEPARATE_GP_AFTER_CAL07',sources=['Europe PMC exact identifier metadata','Crossref exact identifier metadata'],
             scope='Exact assigned DOI/PMID title, version and notice/link metadata only; acquisition cutoff and execution timestamps are actual, not backdated.',
             sourceAssetsReceived=False,currentCorrectionRetractionCheckPerformed=False,fullWorldwideNoticeSearchClaimed=False),
         rule='Local preserved metadata and closed-packet inspection are not a current external integrity check. Add exact received metadata source assets to finalized review assignments before source GP.'))
    pins=[ROOT/'research/batches/RRX-INGEST-001/calibration/assignments.json',ROOT/'research/batches/RRX-INGEST-001/calibration/audits/held-packets.json',
          ROOT/'rules/one-match-rule/references/research-reviews/review-questions-and-inputs.json']
    pins += [OUT/name for name in ['metadata-inventory.json','source-locations.prospective.json','archive-members.prospective.json','eligibility-summary.json','bibliographic-identity.proposed.json',*assignments]]
    pins += [OUT/name for name in ['CLINICAL-APPRAISAL-DRAFT.md','ZIP-MEMBER-CONTRACT-DRAFT.md','inventory.py','test_inventory.py','prepare-drafts.py']]
    save('plan.proposed.json',dict(schemaVersion='remaprx-tranche-preflight-plan-proposal-v1',planId='RRX-CAL-T1-REMAINING-PROSPECTIVE-1.0',
         status='DRAFT_REQUIRES_FRESH_GP',scope='Design-appropriate full private reviews for eligible remaining first-tranche reports after CAL07; preserved identity/integrity and missing-source holds.',
         immediatePermittedOperations=['metadata_inventory','prospective_assignment_planning'],futureOperationsRequiringNewGP=['safe_zip_materialization','front_matter_identity_verification','exact_identifier_integrity_acquisition','clinical_source_authoring','independent_full_report_review','guarded_private_integration'],
         eligiblePacketIds=['CAL-01','CAL-02','CAL-03'],heldPacketIds=['CAL-04','CAL-05','CAL-06','CAL-08'],
         prospectiveAssignmentFiles=assignments,inputs=[pin(p) for p in pins],
         requiredBeforeActivation=['CAL07 exact independent acceptance and continuation decision','Adopt prospective trial/observational appraisal method','Resolve archive materialization and format prerequisites','Centrally confirm title/DOI/PMID/version against primary front matter and preserved identities before source fan-out','Perform separately approved exact-identifier Europe PMC/Crossref current metadata checks with dated actual receipt scope','Finalize assignments with private readable sources and received integrity metadata assets','Pin current rules/code/schemas and record independent GP before source authoring'],
         ownership={'integrator':'codex/root','maxWorkerSlots':3,'authorsCannotAcceptOwnWork':True,'sourceOwnership':'One report and all companions together; same owner for overlapping family/version packets.'},
         scopeLimits={'sourceBodyExtractionPerformed':False,'newAcquisitionPerformed':False,'independentScienceAccepted':False,'humanApproval':False,'released':False,'canonicalWrites':False}))
    print(json.dumps(dict(status='DRAFTS_READY_NOT_APPROVED',schemaValidAssignmentCandidates=len(assignments),archiveMembers=len(archive_manifest),heldPackets=4)))


if __name__=='__main__':main()
