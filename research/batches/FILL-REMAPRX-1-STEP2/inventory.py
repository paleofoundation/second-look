"""Inventory existing records only. Does not mutate evidence, assess sources or import rows."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKET = Path(__file__).resolve().parent
BASE = '92f323f3425fd40c06787d57ff92fa672a418cd0'

def read(name):
    # This is the immutable starting audit; current appraisal accounting is separate.
    return json.loads(subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT,text=True))

# Scope labels reconcile already recorded titles/previews/design/populations.
# They are not new source extraction, an outcome assessment or an effect estimate.
# Missing details remain explicit rather than being inferred from the page title.
SCOPES = {
 'P-D02-ACTIV6-2023': ('Fluvoxamine, higher-dose regimen', 'Acute COVID-19', 'Time to sustained recovery', 'clinical_report', 'Direct acute-infection report; not an established Long COVID treatment result.'),
 'P-REVIVE-2026': ('Fluvoxamine and metformin trial arms; not assumed to be a combination', 'Long COVID fatigue', 'Fatigue', 'quarantined', 'Canonical status is Quarantined; original retracted/republication report is excluded from efficacy support.'),
 'P-D02-SIGMA1-2019': ('Fluvoxamine and Sigma-1 pathway experiments', 'Experimental inflammation and sepsis', 'Inflammatory responses and IRE1-linked cytokine production', 'nonclinical_report', 'Cell/mouse mechanism does not become an acute COVID or Long COVID patient outcome.'),
 'COND-C02-COVIDOUT-2022': ('Separate metformin, ivermectin and fluvoxamine arms', 'Acute COVID-19', 'Primary acute composite outcome', 'clinical_report', 'The sole canonical row for this report belongs to metformin D01; no other drug may inherit its effect or grade.'),
 'P-D06-BREAST-2015': ('Sirolimus plus trastuzumab', 'HER2-positive metastatic breast cancer after progression on trastuzumab', 'Combination activity; exact outcome-specific estimate not recorded in source summary', 'clinical_report', 'Combination and disease setting must remain exact; sirolimus monotherapy benefit cannot be isolated from this record.'),
 'P-D06-AML-2018': ('Sirolimus with intensive chemotherapy', 'High-risk acute myeloid leukemia', 'Remission induction and mTORC1 target inhibition', 'clinical_report', 'Clinical combination/pharmacodynamic endpoints remain separate; not standalone sirolimus efficacy.'),
 'P-D06-PERIODONTAL-2020': ('Rapamycin', 'Periodontal/oral health in aged mice', 'Periodontal inflammation and bone loss over eight weeks', 'nonclinical_report', 'Aged-mouse oral health is neither human periodontitis benefit nor a lifespan endpoint.'),
 'P-D06-PROSTATE-2010': ('Rapamycin before prostatectomy', 'Localized prostate cancer', 'Short-exposure tumor target inhibition', 'mechanistic_report', 'Preoperative pharmacodynamics cannot establish recurrence prevention or survival.'),
 'P-D06-RECTAL-2015': ('Rapamycin plus short-course radiotherapy', 'Primary resectable rectal cancer', 'Tolerability and tumor perfusion', 'clinical_report', 'Combination feasibility/perfusion is not isolated clinical efficacy or survival.'),
 'P-D06-CML-2008': ('Rapamycin', 'Imatinib-resistant chronic myeloid leukemia', 'Exploratory antileukemic activity', 'clinical_report', 'Small uncontrolled exact-disease report; no other leukemia or aging endpoint transfer.'),
 'MECH-D06-AUTOPHAGY-2009': ('Rapamycin-sensitive mTOR signaling experiments', 'Cellular autophagy', 'ULK–Atg13–FIP200 regulation and autophagic flux', 'nonclinical_report', 'Generic cell mechanism is not a clinical cancer, aging or periodontal finding.'),
 'AGING-PEARL-2025': ('Compounded rapamycin, 5 or 10 mg weekly as recorded', 'Human healthspan research', 'Primary visceral adiposity at 48 weeks; selected secondary measures', 'clinical_report', 'Primary null finding retained; healthspan is not lifespan. The recorded N is 114 analyzed completers, not assumed randomized enrollment.'),
 'AGING-RAPA-MICE-2009': ('Rapamycin', 'Mouse lifespan research', 'Lifespan in genetically heterogeneous mice', 'nonclinical_report', 'Direct survival experiment in mice; no human lifespan inference.'),
 'P-D08-ACTIV6-2023': ('Higher-dose ivermectin for six days', 'Acute COVID-19', 'Time to sustained recovery', 'clinical_report', 'Recorded null acute-recovery finding is not a Long COVID or oncology result.'),
 'P-D08-OVARIAN-2009': ('Ivermectin', 'Ovarian cancer and NF2 tumor cell models', 'PAK1 activity and cell growth', 'nonclinical_report', 'Cell-culture growth inhibition is not patient response or survival.'),
 'P-D08-GBM-2016': ('Ivermectin', 'Glioblastoma experimental models', 'Mitochondrial dysfunction, oxidative stress and growth/survival of models', 'nonclinical_report', 'Experimental systems remain distinct from human glioblastoma efficacy.'),
 'P-D08-BREAST-2016': ('Ivermectin', 'Breast cancer models', 'PAK1/Akt signaling, autophagy and growth arrest', 'nonclinical_report', 'Cell/animal mechanisms are not human breast-cancer outcomes.'),
 'P-D08-CRC-2014': ('Ivermectin and related macrocyclic lactones', 'WNT-dependent cancer models including colorectal cancer', 'WNT-TCF signaling and model tumor growth', 'nonclinical_report', 'Exact molecule/model attribution is required; related compounds cannot supply an ivermectin clinical estimate.'),
 'P-D08-HCC-2022': ('Ivermectin plus sorafenib', 'Hepatocellular carcinoma models', 'Experimental growth inhibition and apoptosis', 'nonclinical_report', 'Combination/model record is not human liver-cancer benefit; integrity has not been newly checked or upgraded.'),
 'P-D08-ANTIVIRAL-2023': ('Ivermectin', 'Laboratory SARS-CoV-2 and membrane models', 'Antiviral and membrane-bilayer effects', 'nonclinical_report', 'Recorded concentration/translation limits remain; no patient efficacy inference.'),
 'P-D10-LIVER-2024': ('Self-administered fenbendazole', 'Drug-associated liver injury case', 'Severe liver injury and course after cessation', 'harm_case_report', 'Retain the harm signal; no cancer efficacy conclusion and no causal estimate from a single case.'),
 'P-D10-OVARIAN-2024': ('Fenbendazole', 'Ovarian cancer cell/mouse models', 'Apoptosis and mitotic catastrophe', 'nonclinical_report', 'Preclinical findings do not establish human ovarian-cancer treatment benefit.'),
 'P-D10-LIVER-2026': ('Self-administered fenbendazole during nivolumab/relatlimab treatment', 'Liver injury in a patient with metastatic colon cancer', 'Liver injury and differential attribution', 'harm_case_report', 'Immunotherapy confounding and human case-report scope retained; not a colon-cancer efficacy result.'),
 'MECH-D10-MICROTUBULE-2018': ('Fenbendazole', 'Lung-cancer cell and mouse models; purified bovine tubulin', 'Microtubules, cell division and metabolic readouts', 'nonclinical_report', 'No human cancer trial or safe human anticancer exposure is established by these experiments.'),
 'P-D11-LONGCOVID-2023': ('Guanfacine plus N-acetylcysteine', 'Long COVID cognitive symptoms', 'Reported cognitive improvement and discontinuations', 'clinical_report', 'Twelve-person uncontrolled combination series; cannot isolate guanfacine or infer a comparative effect. Hypotension/dizziness discontinuations remain recorded.'),
 'P-D12-BREAST-2012': ('Maraviroc', 'Basal breast cancer models', 'Invasion and pulmonary metastasis; no in-vitro proliferation reduction', 'nonclinical_report', 'Retain both experimental findings; not a clinical breast-cancer response.'),
 'P-D12-CRC-2016': ('Maraviroc/CCR5 blockade', 'Colorectal cancer liver metastases', 'Tumor-associated macrophages, tumor-cell death and exploratory activity', 'mechanistic_report', 'Human tumor/phase-I pilot evidence requires exact mechanism versus clinical outcome separation; no isolated comparative benefit.'),
 'P-D12-PANCREAS-2018': ('Maraviroc', 'Pancreatic cancer cells', 'CCL5-associated activation and invasion', 'nonclinical_report', 'Cell invasion is not patient survival or treatment response.'),
 'P-D14-VITILIGO-2013': ('Rituximab', 'Active disseminated vitiligo', 'Clinical and skin-biopsy improvement', 'clinical_report', 'Uncontrolled five-patient pilot; improvement cannot be converted into a randomized comparative estimate.'),
 'P-D25-GBM': ('Memantine attribution is page-level; exact regimen not stated in this source record', 'Glioblastoma cells', 'NMDA signaling and temozolomide resistance', 'incomplete_scope', 'Drug and experimental regimen need source-located reconciliation; receptor biology alone cannot supply a memantine patient outcome.'),
 'P-D26-COMBINATION': ('PDE5 inhibitors with chemotherapy; exact sildenafil regimen not stated in this source record', 'Gastrointestinal/genitourinary cancer cell models', 'Chemotherapy killing in cell models', 'incomplete_scope', 'Class/combination title is insufficient for exact sildenafil regimen and human endpoint attribution.'),
 'P-D26-GBM': ('PDE5/sildenafil experimental attribution; observational cohort is distinct', 'Glioblastoma models and tumor cohort', 'Aggressiveness, PDE5 expression and observational clinical outcome', 'mechanistic_report', 'A 69-patient tumor cohort is not a randomized sildenafil treatment comparison.'),
 'MECH-D26-HYPOXIA-2025': ('PDE inhibition; exact regimen is not recorded in canonical source metadata', 'Experimental hypoxia in healthy male volunteers', 'Cerebral blood velocity, regulation and oxygenation', 'mechanistic_report', 'Twelve healthy men are not a disease-treatment population; age discrepancy and outcome distinctions remain unresolved.'),
 'COND-C06-TRPM3-2021': ('Low-dose naltrexone-associated patient-cell investigation', 'ME/CFS natural-killer-cell study', 'TRPM3 ion-channel function', 'mechanistic_report', 'Laboratory patient-cell function is not randomized symptomatic recovery.'),
 'COND-C08-IPGAD-2023': ('No tested drug intervention recorded', 'Persistent genital arousal disorder', 'Clinical phenotype and neurophysiological testing', 'no_intervention_result', 'Condition characterization cannot become a drug treatment-effect row.'),
 'COND-C08-NEURO-2020': ('No comparative drug regimen recorded', 'Persistent genital arousal disorder', 'Neurological lesions and sensory-network observations', 'no_intervention_result', 'Neurological case characterization does not establish a repurposed intervention effect.'),
 'P-D04-CSBD-2022': ('Separate naltrexone and paroxetine arms', 'Compulsive sexual behavior disorder', 'Self-report and clinician-interview symptom outcomes', 'wrong_condition', 'Canonical C07 CSBD findings in 73 men cannot serve C08 PGAD/genitopelvic dysesthesia.'),
 'MF-MYELOMA-MODELS-2018': ('Metformin', 'Myeloma cell lines and mouse xenografts', 'Cell growth, autophagy and cell-cycle arrest', 'nonclinical_report', 'Exact preclinical myeloma record; no patient disease-control result.'),
 'P-D07-MYELOMA-2016': ('Itraconazole plus arsenic trioxide', 'Myeloma NCI-H929 cells and mouse tumors', 'Hedgehog signaling and experimental inhibition', 'nonclinical_report', 'Not itraconazole monotherapy or a human myeloma treatment effect.'),
 'P-D20-MYELOMA': ('Simvastatin', 'Multiple myeloma cell lines', 'Cell death', 'nonclinical_report', 'Cell-line death cannot supply a human myeloma benefit row.'),
 'P-D23-MYELOMA': ('Aspirin versus enoxaparin during lenalidomide-based treatment', 'Selected newly diagnosed myeloma patients at low thromboembolic risk', 'Thromboprophylaxis', 'clinical_report', 'Supportive-care endpoint is not cancer control. Exact comparative values and assessment cannot be invented from the title.'),
 'MECH-D34-HYPHAE-1999': ('Fluconazole in specified susceptible/resistant Candida isolates', 'Laboratory Candida albicans isolates', 'Yeast-to-hypha transition', 'nonclinical_report', 'Morphology under specified conditions is not human tissue invasion or clinical benefit.'),
 'MECH-D34-BIOFILM-2019': ('Fluconazole susceptibility during laboratory biofilm maturation', 'Clinical Candida isolates grown as laboratory biofilms', 'Susceptibility and resistance-associated gene expression', 'nonclinical_report', 'Prevention/eradication and laboratory versus patient outcomes remain distinct; no general biofilm-destroying claim.'),
 'MECH-D07-HEDGEHOG-2010': ('Itraconazole experiments with fluconazole as negative comparator', 'Reporter-cell and mouse tumor models', 'Hedgehog pathway activity', 'negative_comparator_context', 'Retain fluconazole negative-comparator finding; never borrow itraconazole positive cancer findings.'),
 'D31-RAYNAUD-2010': ('Tadalafil added to existing vasodilator therapy', 'Secondary Raynaud phenomenon in scleroderma/mixed connective-tissue disease', 'Raynaud symptoms and digital-ulcer healing', 'clinical_report', 'Positive small crossover report remains separate from the other population/trial; no pooling or generalized benefit.'),
 'D31-RAYNAUD-2009': ('Tadalafil versus placebo', 'Raynaud phenomenon secondary to systemic sclerosis', 'Raynaud condition score and attack frequency/duration', 'clinical_report', 'Recorded null finding retained; not replaced by the positive 2010 report.'),
 'MECH-D31-OXYGENATION-2020': ('Tadalafil', 'Previous small-vessel occlusion stroke', 'Cortical oxygenation signal', 'mechanistic_report', 'NIRS oxygenation signal is not global brain perfusion, cognition or recurrent-stroke benefit.'),
 'MECH-D31-PASTIS-2022': ('Single-dose tadalafil versus placebo', 'Vascular cognitive impairment', 'Prespecified MRI cerebral-perfusion measures', 'mechanistic_report', 'Recorded null perfusion finding does not establish long-term dementia prevention or clinical benefit.'),
 'MF-METPREVENT-2025': ('Metformin versus placebo', 'Older adults with probable sarcopenia and prefrailty/frailty', 'Four-meter walking speed after four months', 'other_exact_scope', 'Existing assessed row is D01/C30 sarcopenia; not a general aging/lifespan row. Retain null walking-speed finding and tolerability limits.'),
 'MF-MASTERS-2019': ('Metformin during progressive resistance training', 'Healthy adults aged at least 65', 'Lean/thigh mass gains and separately measured strength', 'other_exact_scope', 'Existing D01/C30 lean-mass row cannot become a lifespan outcome. Attenuated hypertrophy and nonsignificant strength differences remain distinct.'),
}

PROFILE_NOTES = {
 'D02': 'Acute controlled reports exist, but no D02 outcome assessment is recorded; REVIVE is quarantined. The metformin COVID-OUT row is the wrong drug.',
 'D06': 'Combination, pharmacodynamic, mouse and human healthspan records exist. None has a D06 canonical assessed outcome; the endpoints cannot be combined or called longevity benefit.',
 'D08': 'Acute recovery reports and nonclinical oncology/mechanistic records exist. No D08 assessed outcome; metformin COVID-OUT effects cannot be borrowed.',
 'D10': 'Human liver-injury cases and preclinical tumor records exist. Neither harms cases nor cell/mouse findings establish anticancer benefit; no assessed D10 outcome.',
 'D11': 'Uncontrolled guanfacine plus NAC series exists. No exact combination-specific assessed outcome; do not isolate guanfacine benefit or invent a comparator.',
 'D12': 'Preclinical and exploratory human tumor/phase-I records exist. No exact D12 assessed outcome, and mechanism is not clinical benefit.',
 'D14': 'Five-person uncontrolled vitiligo pilot exists. No exact D14 assessed outcome; no randomized effect can be inferred.',
 'D25': 'Label and laboratory NMDA/temozolomide record only in the linked set; exact memantine experimental scope is incomplete and no patient efficacy row is recorded.',
 'D26': 'Class/combination models, observational tumor analysis and healthy-volunteer physiology exist. They are not interchangeable clinical sildenafil effects; no D26 assessed row.',
 'C06': 'Patient-cell TRPM3 investigation is mechanistic; contextual symptom-care sources are not treatment effects. No C06 assessed outcome.',
 'C08': 'Phenotype/neurological studies are not comparative drug results. Existing naltrexone CSBD outcome belongs to C07, not PGAD C08.',
 'C21': 'Preclinical models, secondary context and supportive thromboprophylaxis report exist. No exact assessed C21 outcome; clot prevention is not tumor control.',
 'C31': 'All five linked sources are context, labels or methods. No comparative repurposed-treatment result is recorded here; no outcome data yet for this table.',
 'D34': 'Labels/guidelines and isolate/biofilm experiments exist; fluconazole negative comparator must not inherit itraconazole findings. No assessed D34 outcome.',
 'D31': 'Positive and null Raynaud crossover reports and distinct brain-physiology studies exist. No exact assessed D31 outcome; preserve conflicting findings and scope.',
 'GOAL-AGING': 'Mouse survival/oral-health and human healthspan/physical-function reports exist. Sarcopenia rows are not general aging/lifespan rows, and no GOAL-AGING assessed row exists.',
}

def main():
    content = read('data/content.json')
    discovery = read('data/discovery-pages.json')
    sources = {source['id']: source for source in content['sources']}
    rows = read('data/reader-evidence.json')['synthesisRows']
    assessments = read('editorial/evidence-assessments.json')['records']
    review_metadata = {record['sourceId']: record for record in read('data/public-review-metadata.json')['records']}
    profiles = [guide for guide in content['guides'] + discovery if guide['type'] in ['Drug', 'Condition'] and not guide.get('synthesisIds')]
    records = []
    for guide in profiles:
        for source_id in guide['sourceIds']:
            source = sources[source_id]
            scope = SCOPES.get(source_id)
            if scope is None:
                assert source.get('sourceType') in ['context', 'review', 'textbook', 'other'], source_id
                scope = ('No intervention effect established by context', source.get('population') or 'Context scope; see recorded title',
                         'Not an original intervention-result record', 'context_only', 'Identity/label/guideline/review/method context does not supply an independent outcome or trial count.')
            drug, condition, endpoint, role, reason = scope
            related = [row for row in rows if source_id in row['sourceIds']]
            meta = review_metadata.get(source_id, {})
            records.append(dict(route=guide['slug'], entityId=guide['entityId'], sourceId=source_id,
                drugRegimenAsRecorded=drug, conditionScopeAsRecorded=condition,
                populationAsRecorded=source.get('population'), populationMissingReason=None if source.get('population') else 'not_recorded_in_canonical_source_metadata',
                endpointScope=endpoint, role=role, decision='exclude_quarantined' if role=='quarantined' else 'no_exact_assessed_outcome_available', reason=reason,
                sourceRecord={key:source.get(key) for key in ['title','sourceType','design','preview','access','status','reviewState','n','randomizedN','intervention','comparator','decisiveLimit']},
                locators=source.get('locators',[]), locatorState='recorded' if source.get('locators') else 'not_recorded',
                existingReviewState=dict(source=source.get('reviewState','not_recorded'),metadata=meta.get('reviewState','not_recorded'),humanApproval=meta.get('humanApproval',source.get('humanApproval','not_recorded')),publicationState=meta.get('publicationState',source.get('publicationState','not_recorded'))),
                sourceRecordSha256=hashlib.sha256(json.dumps(source,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
                otherScopedCanonicalRows=[dict(rowId=row['id'],drugId=row['drugId'],conditionId=row['conditionId'],population=row['population'],endpoint=row['endpoint'],timepoint=row['timepoint']) for row in related]))
    output = dict(schemaVersion=1,order='FILL-REMAPRX-1',step=2,baseCommit=BASE,
        scope='Existing-source/canonical-outcome inventory only; no extraction, new appraisal or scientific import.',
        profileCount=len(profiles),sourceAssociationCount=len(records),distinctSourceCount=len({record['sourceId'] for record in records}),
        reusableExactOutcomeRows=0,newOutcomeRows=0,decision='GATE_ASSESSMENT_OR_PENDING_MODEL_AUTHORIZATION',
        profiles=[dict(route=guide['slug'],entityId=guide['entityId'],guideId=guide['id'],sourceIds=guide['sourceIds'],existingSynthesisIds=guide.get('synthesisIds',[]),
            exactCanonicalRows=[row['id'] for row in rows if (row['drugId'] if guide['type']=='Drug' else row['conditionId'])==guide['entityId']],
            gap=PROFILE_NOTES[guide['entityId']]) for guide in profiles],records=records,
        assessmentInventory=dict(existingRows=len(rows),existingAssessments=len(assessments),existingSummaries=len(read('data/outcome-summaries.json')['records']),newAssessments=0,newGrades=0,approvalOrReleaseChanges=0))
    target=PACKET/'inventory.json'
    encoded=json.dumps(output,ensure_ascii=False,indent=2)+'\n'
    changed=not target.exists() or target.read_text()!=encoded
    if changed:target.write_text(encoded)
    print(json.dumps(dict(profiles=len(profiles),associations=len(records),distinctSources=output['distinctSourceCount'],exactReusableOutcomes=0,changed=changed)))

if __name__ == '__main__':
    main()
