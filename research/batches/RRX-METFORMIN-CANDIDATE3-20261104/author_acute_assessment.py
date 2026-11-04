"""Serialize the individually authored ACTIV-6 acute assessment, without inference of approval."""
import hashlib, json
from pathlib import Path

B = Path(__file__).resolve().parent
OLD = B.parent / 'RRX-METFORMIN-COMPLETE-20261103'
RAW = B.parents[3] / 'private-research/RRX-METFORMIN-CANDIDATE3-20261104'
Q = json.loads((OLD / 'review-questions-and-inputs.json').read_text())['questions']
groups = [
 ('Objectives; Methods/Outcomes and Statistical Analysis; Table 2', [
  'Test whether immediate-release metformin shortens acute COVID-19 symptom duration in outpatients.',
  'The report identifies recovery as the prespecified primary for this substudy, selected from two platform options before unblinding; hospitalization/death was secondary because events were expected to be too sparse. The separately linked SAP could not be retrieved as a readable PDF in this acquisition.',
  'Time from drug receipt to the third of three consecutive symptom-free days, through day 28; this is not the long-term CID primary outcome.'
 ], 'Assess the reported acute primary on its own terms; the companion long-term report cannot replace it.'),
 ('Methods/Trial Design and Participants; Figure 1; Table 1', [
  'Human adults; no animal or cell experiments in this report.',
  '90 US sites, decentralized enrollment September 19, 2023–May 1, 2024; age at least 30, positive antigen/PCR within 10 days, at least two symptoms for no more than seven days at enrollment. Current COVID hospitalization, recent metformin/insulin/sulfonylurea, allergy or contraindication excluded.',
  '3,214 randomized; 223 excluded after randomization, principally nonreceipt within seven days or administrative eligibility confirmation; 2,991 in the modified intention-to-treat analysis (1,443 metformin, 1,548 placebo); 2,815 took at least one dose for safety analysis. Median age 47; 63.4% female; 68.3% had at least two vaccine doses.'
 ], 'The largely low-risk population and postrandomization exclusions restrict generalization.'),
 ('Methods/Interventions; Trial Procedures; Table 1', [
  'Aurobindo immediate-release metformin, 500-mg tablets; not the REVIVE extended-release product.',
  'Oral: 500 mg on day 1, 500 mg twice daily on days 2–5, then 500 mg morning plus 1,000 mg evening through day 14; 36 tablets sent by pharmacy to the home.',
  'Approved antivirals permitted; about 14.5% received nirmatrelvir/ritonavir. Vaccination and prior infection allowed. Concurrent recent glucose-lowering exposure was restricted by eligibility.',
  'Daily symptoms through day 28; adverse events through day 28 and serious events through day 180. Long-term outcomes were collected but are reported separately.'
 ], 'These are descriptive research exposures, not a dosing recommendation.'),
 ('Methods/Randomization and Interventions', [
  'Placebo during the same platform period; generic placebo before matched tablets became available on November 9, 2023 (134 placebo participants).',
  'Simple 1:1 assignment to metformin or placebo using a random-number process.',
  'Randomized, with no overlapping enrollment to other active platform agents in this substudy.',
  'Double blind; participants and investigators blinded. Early nonmatching generic placebo is a potential weakness of masking.',
  'Median five days from symptom onset to drug receipt; only about 21% received it within three days of onset.'
 ], 'Compare assigned active treatment with placebo; delayed delivery limits inference about very early administration.'),
 ('Methods/Outcomes; Statistical Analysis; Table 2', [
  'Primary: sustained recovery. Secondary: health-care contacts/hospitalization/death, time unwell, clinical progression and mortality; subgroup analyses exploratory.',
  'Daily participant-reported COVID-19 symptom surveys; recovery requires three consecutive symptom-free days.',
  'Primary event is the third symptom-free day, within 28 days after receipt.',
  'Patient-reported clinical recovery rather than a laboratory surrogate; hospitalizations/deaths were uncommon.',
  'NR: No established patient-level minimal important difference is supplied. Design power used a recovery hazard ratio of 1.2, which is not a validated meaningful-change threshold.'
 ], 'Do not present a one-day difference in medians as proven benefit when the primary time-to-event analysis is negative.'),
 ('Table 2; Results/Primary Outcome; Figure 2', [
  'Median recovery time 9 days (95% CI 9–10) with metformin and 10 (9–10) with placebo; adjusted recovery hazard ratio 0.96.',
  'Primary analysis denominators 1,443 and 1,548, total 2,991. This time-to-event estimand is not a simple event-rate contrast.',
  'Adjusted hazard ratio 0.96; a value above 1 favors faster recovery in this analysis.',
  'The adjusted between-group time-to-recovery comparison did not establish benefit; subtracting medians is not a substitute for that analysis.',
  '95% Bayesian credible interval 0.89–1.03; posterior probability of efficacy 0.11 versus a prespecified success threshold of 0.95. A sensitivity analysis adjusting baseline symptoms gave 0.98 (0.91–1.05).'
 ], 'The candidate-3 guide quotes Table 2 and explicitly identifies the acute primary outcome.'),
 ('Figure 1; Figure 2 caption; Results/Primary Outcome and Safety', [
  '239 of 2,991 (8.0%) lacked complete primary recovery follow-up; this is distinct from CID day-180 nonresponse.',
  'Text splits those 239 into 87 complete nonresponses and 152 partial responses, while Figure 2 caption gives 71 and 168. Both sum to 239. Follow-up was censored; baseline covariate missingness used conditional mean imputation.',
  '5.9% of analyzed participants did not take study medication; the exposed safety population was 2,815. Complete dose adherence detail in the inaccessible supplement was not verified.',
  '223 randomized participants excluded from the primary analysis, including drug nonreceipt within the required window and administrative eligibility issues; this is not a fully inclusive randomized ITT population.',
  'Modified intention-to-treat includes eligible participants receiving shipment; symptom-free participants on delivery remained included. Safety requires at least one dose.',
  'Participant is the experimental unit; repeated daily surveys do not add independent participants.'
 ], 'Preserve the internal missingness split discrepancy rather than silently choosing one version.'),
 ('Methods/Safety; Results/Safety; Abstract; Supplement 3 link', [
  'Patient-reported events and site confirmation, with special attention to hypoglycemia and lactic acidosis; serious events tracked to day 180.',
  '2,815 participants exposed to at least one dose; the full harms table could not be independently retrieved in Supplement 3.',
  '11 serious events in 10 participants: eight events in seven metformin recipients and three in three placebo recipients. No lactic acidosis. Main text reports five self-reported hypoglycemia episodes in each arm and six site-confirmed episodes (two metformin, four placebo); abstract labels two versus four as participant-reported.',
  'GAP: Complete dose adherence, discontinuation and adverse-event withdrawal table in Supplement 3 was not accessible as a PDF; do not equate unavailable tabulation with zero withdrawals.',
  'Nonserious events through day 28, serious events through day 180; limited exposure and low event counts cannot establish absence of rare harms.'
 ], 'The guide adds no new numerical safety claims from these discordant or incompletely tabulated details.'),
 ('Methods/Statistical Analysis; Results; Figure 2; Discussion/Limitations', [
  'Randomization and masking reduce baseline allocation bias; postrandomization exclusions, self-report, nonresponse, delayed delivery and early generic placebo remain relevant.',
  'Adjustment included age, sex, symptom duration, calendar time, vaccination, region, recruitment pathway and symptom burden. Primary baseline symptoms could sometimes be measured after the first dose; diarrhea from metformin could affect perceived recovery.',
  'GAP: The main report describes prespecification, but the original linked protocol/SAP and supplement bodies were not recovered in this acquisition; a full historical selective-reporting audit remains incomplete.',
  'Secondary and heterogeneous-treatment-effect analyses are exploratory; do not turn a favorable subgroup into a confirmed indication.',
  'Primary interval excludes a large acceleration consistent with the design HR 1.2, but modest effects remain possible. Few hospitalizations/deaths make their estimates imprecise.',
  'Figure 2 and Results disagree on complete versus partial nonresponse; abstract and Safety differ in attribution of hypoglycemia counts. Table 2 healthcare-use interval labeling differs from adjacent prose. Candidate 3 uses the concordant primary recovery estimate only.'
 ], 'These limits qualify interpretation but do not reverse the primary result.'),
 ('Table 1; Eligibility; Discussion/Limitations', [
  'Relevant to acute outpatient COVID-19 in adults aged at least 30 with substantial prior immunity and low hospitalization risk; it does not test treatment of established Long COVID.',
  'A short oral immediate-release course titrated to 1,500 mg daily; results cannot be assumed for prolonged use, another release formulation or an untested schedule.',
  'Recovery time answers acute symptom duration; prevention of later illness needs the companion CID outcome and treating chronic illness needs different trials.',
  'Does not establish effects in children, hospitalized patients, contraindicated populations or higher-risk subgroups too small for precise estimates.'
 ], 'The acute and long-term questions are separated in the guide.'),
 ('Methods/Trial Registration; companion CID DOI 10.1093/cid/ciag335', [
  'ACTIV-6 platform NCT04885530; metformin substudy also indexed as NCT06042855.',
  'Bramante et al., CID 2026, is the long-term follow-up report; the January 2025 medRxiv preprint precedes this peer-reviewed acute report.',
  'The acute and long-term reports share the randomized study family. Their analysis denominators differ (2,991 versus 2,983) and must remain report-specific.',
  'Bounded to candidate-2 citations, the supplied PMID, related records, publisher/PMC and PubMed metadata; this is not a new systematic search for every metformin/COVID study.'
 ], 'Count the two reports as complementary outcomes within one trial family.'),
 ('Byline; Article Information/Funding and Disclosures; Methods/Intervention', [
  'Carolyn T. Bramante, Thomas G. Stewart, David R. Boulware and the ACTIV-6 study team; affiliations and full byline are preserved in the primary record.',
  '90 US sites, coordinated through the ACTIV-6 academic platform including Duke and Vanderbilt; decentralized participant follow-up.',
  'NIH/NCATS 3U24TR001608-06S1; ASPR/BARDA contract 75A50122C00037; Vanderbilt NCATS UL1TR002243 supported REDCap. NCATS participated in design, conduct, analysis, manuscript and submission decisions.',
  'Aurobindo 500-mg immediate-release tablets identified. NR: The inspected main report does not identify a manufacturer donation arrangement; do not infer one from product identity.',
  'Disclosures include NIH support and multiple authors’ outside pharmaceutical grants, consulting, stock interests and an unrelated sepsis-risk patent; details retained in the source. Funding alone is not proof of validity or invalidity.'
 ], 'Disclosure review does not create a clinical reviewer credential or sign-off.'),
 ('PMC12261116; PubMed40658388; linked Supplements 1–5; acquisition.json', [
  'Peer-reviewed JAMA Internal Medicine 2025;185(9):1092–1101, DOI 10.1001/jamainternmed.2025.2570; not the earlier preprint.',
  'Full main report HTML, tables, figure captions, limitations, funding and conflicts read; raw HTML and PubMed XML saved with hashes.',
  'GAP: All five linked supplement URLs returned small HTML bodies, not PDF content. They are retained as failed acquisitions, never marked inspected. Supplements cover protocol, SAP, appendix, investigators and data sharing.',
  'Registration identifiers checked against the report and existing ACTIV-6 family packet. The separate acute SAP body was not independently accessed.',
  'No retraction/correction relation is listed for the primary acute article in the retrieved PubMed record. Related letters/reply are visible in PMC and are not silently treated as a correction. This bounded check is not a guarantee of no future notice.',
  'Primary source and bibliographic checks November 4, 2026; the user-relayed candidate-2 report was supplied in chat, not as a locally accessible full review file.'
 ], 'Source-access gaps remain explicit and do not justify withholding the directly verified primary result.'),
 ('Candidate 3 infection block 4; JAMA Table 2; CID Tables 2–3', [
  'Guide infection chapter now names the acute primary recovery result separately from the CID day-180 primary outcome.',
  'Directly supports the bounded statement that the acute trial did not establish faster recovery with the tested regimen; contradicts labeling day 180 as the acute trial primary.',
  'Observed: adjusted HR 0.96, CrI 0.89–1.03. Authors: no recovery difference in the studied population. Editorial interpretation: do not generalize this to every formulation, population or Long COVID question.'
 ], 'The CID modeled rates and missingness remain supported by explicit Tables 3 and 2 rather than being attributed to JAMA.'),
 ('Synthesis of Q01–Q14', [
  'The acute trial failed to establish a recovery benefit; report its actual primary and keep the long-term endpoint separate.',
  'Very early treatment, higher-risk populations, rare harms and incomplete supplementary verification remain uncertain; none is an established hidden benefit.',
  'A well-controlled, adequately powered trial targeting a distinct population or timing question, with complete prespecified outcomes and accessible protocol/analysis materials, could change the relevant bounded conclusion.'
 ], 'This assessment supports a review candidate, not individualized treatment or release approval.'),
]

def main():
    assert len(groups)==len(Q)==15
    inputs=[];questions={}
    for q,(locator,cells,interpretation) in zip(Q,groups):
        assert len(cells)==len(q['inputFields']),(q['id'],len(cells))
        current=[]
        for field,value in zip(q['inputFields'],cells):
            status='assessed'
            for prefix,state in [('NR:','not_reported'),('GAP:','not_accessible')]:
                if value.startswith(prefix):status=state;value=value[len(prefix):].strip();break
            item={'questionId':q['id'],'field':field,'value':value,'status':status,'locators':[locator]}
            inputs.append(item);current.append(item)
        questions[q['id']]={'answer':' '.join(x['value'] for x in current)+' '+interpretation,'status':'partial' if any(x['status']=='not_accessible' for x in current) else 'assessed','locators':[locator]}
    assert len(inputs)==67
    assets=[{'path':str(RAW/f),'sha256':hashlib.sha256((RAW/f).read_bytes()).hexdigest()} for f in ['ACTIV6-acute-pmc.html','ACTIV6-acute-pubmed.xml']]
    record={'sourceId':'MF-ACTIV6-ACUTE-2025','title':'Metformin and Time to Sustained Recovery in Adults With COVID-19: The ACTIV-6 Randomized Clinical Trial','version':'metformin-assessment-20261104.2','sourceAssets':assets,'questions':questions,'inputs':inputs,'appraisal':'The directly verified acute primary shows no established recovery benefit (aHR 0.96; 95% CrI 0.89–1.03). This report and CID long-term follow-up belong to one trial family. Main-report inconsistencies and unavailable supplement bodies remain disclosed; no human approval is inferred.','completion':'partial','unresolvedInputs':[i['field'] for i in inputs if i['status']=='not_accessible'],'independentVerification':'pending','humanApproval':'pending','release':'private_candidate','plan':'plan.json'}
    (B/'assessments').mkdir(exist_ok=True)
    (B/'assessments/MF-ACTIV6-ACUTE-2025.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n')
    schema=json.loads((OLD/'review.v3.schema.json').read_text());schema['properties']['sourceId']['enum'].append(record['sourceId'])
    schema['properties']['plan']['const']='plan.json'
    (B/'assessment.schema.json').write_text(json.dumps(schema,indent=2)+'\n')
    (B/'review-questions-and-inputs.json').write_bytes((OLD/'review-questions-and-inputs.json').read_bytes())
    print('15 individually authored answers; 67 inputs;',len(record['unresolvedInputs']),'explicit access gaps')

if __name__=='__main__': main()
