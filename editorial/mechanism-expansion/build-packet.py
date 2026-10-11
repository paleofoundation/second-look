"""Build the bounded mechanism packet from inspected primary full texts.

Only editorial outputs are written. Root owns canonical integration and release.
"""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import re
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
DATE = '2026-10-11'

class CitationMeta(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = {}
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta' and attrs.get('name', '').startswith('citation_'):
            self.values.setdefault(attrs['name'], []).append(attrs.get('content'))

def metadata(stem, extension):
    path = BASE / (stem + extension)
    if extension == '.html':
        p = CitationMeta(); p.feed(path.read_text())
        vals = p.values
        return {'title': vals['citation_title'][0], 'doi': vals.get('citation_doi', [None])[0],
                'authors': vals.get('citation_author', []), 'pmid': vals.get('citation_pmid', [None])[0]}
    root = ET.parse(path).getroot()
    meta = root.find('front/article-meta')
    ids = {x.get('pub-id-type'): x.text for x in meta.findall('article-id')}
    authors = []
    for c in meta.findall('contrib-group/contrib'):
        n = c.find('name')
        if n is not None:
            authors.append(' '.join(filter(None, [n.findtext('given-names'), n.findtext('surname')])))
    return {'title': ''.join(meta.find('title-group/article-title').itertext()), 'doi': ids.get('doi'),
            'authors': authors, 'pmid': ids.get('pmid')}

records = []
def record(id, drug, stem, pmc, year, scope, model, exposure, locator, observation,
           tested, proposed, limits, preview, design='Mechanistic laboratory study', n=None,
           existing=False, extension='.html', outcomes=None):
    path = BASE / (stem + extension)
    records.append(dict(id=id, drugId=drug, stem=stem, pmc=pmc, year=year, conditionScope=scope,
        model=model, exposure=exposure, nativeLocator=locator, observation=observation,
        directlyTested=tested, sourceProposed=proposed, translationLimits=limits,
        preview=preview, design=design, n=n, existing=existing, extension=extension,
        sourceHash=hashlib.sha256(path.read_bytes()).hexdigest(), outcomes=outcomes or []))

record('MECH-D07-HEDGEHOG-2010','D07','itraconazole-hedgehog-2010','PMC4039177',2010,
    ['C19','Hedgehog-dependent tumor models'],
    'Shh-Light2/NIH-3T3 reporter cells, pathway-mutant cells and mouse tumor allografts',
    'Reporter IC50 approximately 0.8 µM in 0.5% serum; fluconazole comparison reached 50-fold this concentration.',
    'Results and Discussion; Figures 1B,D, 2D,E and 4A–E; Experimental Procedures: Hh pathway activity assays',
    'Reporter suppression and reduced Smoothened ciliary accumulation; fluconazole lacked detectable Hedgehog inhibition in this assay.',
    ['Pathway reporter, mutant bypass and localization assays'],
    ['Action at Smoothened is supported by pathway mapping; direct binding was a proposal, not measured binding affinity.'],
    ['Model-specific pathway inhibition is not a cancer-treatment outcome. Serum conditions materially changed potency.'],
    'Itraconazole suppressed Hedgehog signaling in reporter and tumor models, with experiments locating its action near Smoothened. Fluconazole did not share this activity in the tested assay.')

record('MECH-D07-CHOLESTEROL-2010','D07','itraconazole-cholesterol-2010','PMC2842052',2010,
    ['Angiogenesis rationale across cancer indications'], 'Human umbilical-vein endothelial cells (HUVECs)',
    'Itraconazole 2 µM for 24 hours in cholesterol localization/rescue experiments; cholesterol/cyclodextrin comparator.',
    'Results: Itraconazole Inhibits Cholesterol Trafficking; Proper Cholesterol Trafficking Is Essential; Figures 3–5; Materials and Methods',
    'Cholesterol accumulated in endolysosomes. Cholesterol delivery partially rescued mTOR readouts and proliferation; NPC1/NPC2 knockdown reproduced pathway effects.',
    ['Filipin/LAMP1 localization, phosphoproteins, proliferation, cholesterol rescue and NPC1/2 knockdown'],
    ['Cholesterol trafficking contributes causally to mTOR suppression; the exact molecular target was unresolved in this paper.'],
    ['Endothelial-cell assays do not establish tumor oxygenation, survival benefit or patient exposure at the target.'],
    'Endothelial-cell experiments linked blocked intracellular cholesterol transport to reduced mTOR signaling and proliferation. Rescue experiments strengthened the proposed connection.')

record('MECH-D07-NPC1-2017','D07','itraconazole-npc1-2017','PMC5791891',2017,
    ['Angiogenesis rationale across cancer indications'], 'HEK293T and A549 target-binding assays; HUVEC signaling and tube formation',
    'Photoaffinity probe 200 nM for 1 hour; itraconazole competitor 10 µM. HUVEC tube experiment: itraconazole 5 µM for 6 hours.',
    'Results: Itraconazole Binds Directly to NPC1 (Figure 2); AMPK Activation and NPC Induction (Figures 4–5); main-text assay descriptions',
    'Probe labeling was competed by itraconazole and disrupted by NPC1 P691S mutation. Combined AMPK activation and cholesterol-transport inhibition suppressed endothelial tube formation.',
    ['Live-cell affinity labeling/competition, mutation and parallel-pathway perturbations'],
    ['Exact binding pose and interruption of cholesterol handoff are docking-based proposals.'],
    ['Cell and binding studies; clinical benefit was not tested. Supplementary methods and raw images need separate appraisal.'],
    'Live-cell binding experiments identified NPC1 as an itraconazole target. The report linked cholesterol trafficking and a parallel AMPK pathway to suppression of endothelial growth.')

record('MECH-D10-MICROTUBULE-2018','D10','fenbendazole-2018','PMC6085345',2018,
    ['C14'], 'Human lung-cancer cell lines, purified bovine tubulin and A549 mouse xenografts',
    'Cells commonly 1 µM for 24–48 hours; purified tubulin assay 10 µM; mouse xenograft oral dose 1 mg/mouse.',
    'Results: FZ destabilizes tubulin network; FZ treatment results in early G2/M block; Figures 1, 3–8; Methods: tubulin assay and nude mice',
    'Microtubule disruption, mitotic arrest and apoptosis accompanied altered p53 localization and lower glucose uptake.',
    ['Tubulin polymerization/localization, cell-cycle flow cytometry, p53 transfection and metabolic assays'],
    ['Several pathways may contribute; the report does not establish one necessary mechanism for every tumor.'],
    ['No human cancer trial or safe human anticancer exposure was established. Laboratory selectivity is not clinical safety.'],
    'Fenbendazole altered microtubules, cell division and metabolic readouts in lung-cancer models. These experiments explain a research rationale without establishing treatment benefit in people.',
    extension='.xml')

record('MECH-D34-HYPHAE-1999','D34','fluconazole-hyphae-1999','PMC89204',1999,
    ['Candida albicans morphology'], 'Susceptible and resistant clinical Candida albicans isolates',
    'Fluconazole 10 µg/mL during 48-hour growth and 3-hour hyphal induction; concentration-response experiments also reported.',
    'Materials and Methods: hyphal induction; Results: Fluconazole inhibits hyphal formation; Figures 1–5; Discussion',
    'Combined growth/induction exposure inhibited hyphae in susceptible isolates; resistant isolates retained filamentation. Growth inhibition alone did not fully explain the pattern.',
    ['Microscopic hyphal counts, susceptibility comparisons and methionine-incorporation assay'],
    ['Ergosterol limitation as the explanation for altered morphology was proposed.'],
    ['Hyphal morphology is not direct measurement of human tissue invasion; results depended on strain, medium and exposure timing.'],
    'Fluconazole inhibited hyphal development in susceptible Candida isolates under specified laboratory conditions. Resistant isolates could retain this invasive-growth trait.')

record('MECH-D34-BIOFILM-2019','D34','fluconazole-biofilm-2019','PMC6863221',2019,
    ['Candida albicans biofilms'], '23 clinical Candida albicans isolates; eight selected for gene-expression measurements',
    'Biofilms aged 2–48 hours; susceptibility series 0.5–256 mg/L fluconazole; gene-expression challenge 32 mg/L.',
    'Methods: Antifungal susceptibility testing and gene expression; Results: Table 2 and Figures 2–4; Discussion',
    'Biofilm maturation reduced susceptibility. Early efflux-gene expression and drug-induced ERG11 expression differed by strain and stage.',
    ['Susceptibility, biomass and gene-expression assays'],
    ['Transporter involvement was inferred from expression patterns; this study did not prove every resistance mechanism by gene knockout.'],
    ['Plate biofilms and a nonstandardized biofilm inoculum limit clinical interpretation; prevention is distinct from eradication.'],
    'Clinical Candida isolates became less susceptible to fluconazole as laboratory biofilms matured. The experiment does not support describing fluconazole as a general biofilm-destroying drug.', n=23)

record('MF-PD-MECHANISM-2016','D01','metformin-parkinson-2016','PMC5043649',2016,
    ['C24'], 'MPTP/probenecid-treated male mice and MPP+-injured SH-SY5Y cells',
    'Mouse drinking water 5 mg/mL; cell experiments metformin 2 mM before MPP+ 200 µM for 48 hours.',
    'Animals and Treatment; Cell Culture and Treatments; Figures 2, 4–5 and Results sections s18, s20–s21',
    'AMPK/autophagy-associated changes accompanied protection; Compound C and 3-methyladenine attenuated cellular protection and mitochondrial readouts.',
    ['Phosphoproteins, LC3/p62, viability, mitochondrial dyes and pharmacological inhibitor experiments'],
    ['AMPK-dependent recycling contributes to protection; inhibitor specificity limits causal certainty.'],
    ['Toxin injury and millimolar culture exposure do not establish human Parkinson benefit.'],
    'Mouse and cell experiments tested an AMPK–autophagy explanation for protection against toxin-induced neuronal injury.', existing=True, extension='.xml')

record('P-D08-CRC-2014','D08','ivermectin-wnt-2014','PMC4287931',2014,
    ['C16'], 'Colon-cancer lines, patient-derived cells and immunodeficient-mouse xenografts',
    'TCF rescue at ivermectin 0.5–1 µM; cyclodextrin-formulated drug 10 mg/kg/day intraperitoneally in xenografts.',
    'Results: Direct activation of TCF rescues; Ivermectin selectively represses TCF-dependent xenograft growth; Figures 4–5; Mouse xenografts',
    'Forced TCF activation rescued low-dose effects; TCF-dependent DLD1 xenografts responded, while TCF-independent CC14 xenografts did not.',
    ['Genetic pathway rescue, growth readouts and model-dependent xenograft comparison'],
    ['Higher concentrations may engage additional mechanisms.'],
    ['Injected experimental formulation and tumor models are not equivalent to oral use or clinical cancer efficacy.'],
    'Genetic rescue experiments supported a WNT–TCF mechanism in selected colorectal-cancer models. Different xenografts responded differently.', existing=True, extension='.xml')

record('P-D06-PERIODONTAL-2020','D06','sirolimus-periodontal-2020','PMC7220376',2020,
    ['C10'], 'Aged female mice at two facilities, with young controls',
    'Encapsulated rapamycin 42 ppm in food for 8 weeks; matched encapsulation vehicle.',
    'Results and Figures 2–4; Materials and Methods: Animal studies; Encapsulated rapamycin feeding',
    'Bone recovery accompanied lower RANKL/OPG, fewer TRAP-positive cells and altered inflammatory readouts.',
    ['Longitudinal microCT, histology and protein assays'],
    ['Inflammation/bone-resorption changes may explain periodontal improvement; mediation and autophagy dependence were not established.'],
    ['Female mice, pooled samples for some protein assays and surrogate tissue outcomes limit human extrapolation.'],
    'In aging mice, rapamycin-associated periodontal bone recovery was accompanied by changes in inflammation and bone-resorption markers.', existing=True, extension='.xml')

record('MECH-D06-AUTOPHAGY-2009','D06','sirolimus-autophagy-2009','PMC2663920',2009,
    ['Parent cellular mechanism'], 'HEK293T, HeLa and mouse embryonic fibroblast cells',
    'Rapamycin 100 nM for 4 hours in LC3 flux assays; 2–24 hours for microscopy; 50 nM for 1-hour labeling.',
    'Methods: Cell Culture; Autophagy Assays; Results/Figures 3, 5–7',
    'Rapamycin changed ULK/Atg13 phosphorylation and autophagic flux; ULK/Atg13 disruption diminished the response.',
    ['Kinase assays, gene silencing/knockout and LC3/p62 assays with lysosomal inhibitors'],
    ['mTOR–ULK regulation links nutrient signals with autophagy initiation.'],
    ['A cellular mechanism cannot establish lifespan, anticancer or periodontal benefit in people.'],
    'Genetic and biochemical experiments linked rapamycin-sensitive mTOR signaling to ULK–Atg13–FIP200 regulation and autophagic flux.')

record('MECH-D26-HYPOXIA-2025','D26','sildenafil-hypoxia-2025','PMC11765346',2025,
    ['Acute experimental hypoxia'], '12 healthy male volunteers',
    'Two 50-mg oral doses per sildenafil visit; normoxia then 14% inspired oxygen; crossover with 7-day washout.',
    'Methods: Participants and Experimental design; Results: Cerebrovascular function; Table 2, Figures 3–4',
    'Some autoregulation/reactivity measures improved; cortical oxygenation indices showed no significant drug effect in Table 2.',
    ['Doppler velocity, near-infrared spectroscopy and carbon-dioxide reactivity'],
    ['A lower Doppler velocity may reflect dilation; velocity alone does not establish volumetric flow.'],
    ['Small healthy-male laboratory experiment; no disease-treatment outcome. Age values differ between abstract and Methods and need reconciliation.'],
    'A crossover experiment separated cerebral blood-velocity, regulation and oxygenation measurements. Changes in vascular regulation did not establish a general oxygenation benefit.',
    design='Randomized double-blind placebo-controlled crossover physiology experiment',n=12)

record('MECH-D31-OXYGENATION-2020','D31','tadalafil-oxygenation-2020','PMC7530832',2020,
    ['Cerebral small-vessel disease after lacunar stroke'], '20 participants with previous small-vessel occlusion stroke (17 men, 3 women)',
    'Single oral tadalafil 20 mg versus placebo, crossover visits at least 1 week apart; measurements to 3 hours.',
    'Materials and Methods: Trial design and NIRS; Results: NIRS, Figure 4B; Discussion: Limitations',
    'At 180 minutes cortical oxygen saturation increased 1.57 percentage points; no significant overall Doppler velocity or peripheral endothelial effect.',
    ['Near-infrared oxygen saturation, Doppler and EndoPAT'],
    ['Improved perfusion was an interpretation of the oxygenation signal, not directly measured regional volumetric flow.'],
    ['Small pilot; NIRS superficial/possibly extracranial; no cognition or recurrent-stroke benefit demonstrated.'],
    'A small crossover trial detected a modest cortical oxygenation signal after tadalafil. It did not establish a general increase in brain blood flow or a clinical benefit.',
    design='Randomized double-blind placebo-controlled crossover pilot trial',n=20,
    outcomes=[{'name':'Cortical oxygen saturation difference at 180 min','estimate':1.57,'unit':'percentage points','uncertainty':{'type':'SD','value':3.02},'p':0.018}])

record('MECH-D31-PASTIS-2022','D31','tadalafil-pastis-2022','PMC10078742',2022,
    ['Cerebral small-vessel disease / vascular cognitive impairment rationale'],
    '65 randomized; 59 commenced; 55 completed; 53 had complete usable cerebral-blood-flow data',
    'Single oral tadalafil 20 mg versus placebo; crossover visits at least 7 days apart; arterial-spin-labeling MRI.',
    'Methods: trial design, imaging and statistical analysis; Results: Figure 1C, Figure 3 and Table 2; Discussion',
    'No significant treatment effect on subcortical cerebral blood flow; white-matter-lesion estimate 0.95 mL/min/100 g, P=0.096.',
    ['MRI perfusion and blood-pressure measurements'],
    ['A chronic dosing effect remains a separate hypothesis, not excluded by a single-dose study.'],
    ['A short mechanistic trial cannot establish dementia prevention or long-term treatment benefit.'],
    'PASTIS directly measured brain perfusion by MRI. A single tadalafil dose did not significantly increase the prespecified subcortical blood-flow measures.',
    design='Randomized double-blind placebo-controlled crossover trial',n=55,
    outcomes=[{'name':'White-matter-hyperintensity perfusion treatment effect','estimate':0.95,'unit':'mL/min/100 g','uncertainty':None,'p':0.096,'missingState':'confidence interval not extracted'}])

def prose(sentences):
    return {'text':' '.join(s[0] for s in sentences),
            'sourceIds':list(dict.fromkeys(y for _,xs in sentences for y in xs)),
            'sentences':[{'text':s,'sources':ids} for s,ids in sentences]}
def question(id,title,sentences):
    return dict(id=id,title=title,**prose(sentences))

drugs = [
 {'drugId':'D07','questions':[
   question('hedgehog-cellular','Hedgehog signaling and Smoothened',[
     ('Hedgehog signaling can sustain the growth of some tumors. In cell experiments, itraconazole reduced pathway activity and prevented Smoothened from accumulating in the primary cilium, a signaling compartment on the cell surface.',['MECH-D07-HEDGEHOG-2010']),
     ('Pathway-mapping experiments placed its action near Smoothened, although this study did not directly establish a binding site. Fluconazole did not share the Hedgehog effect under the tested conditions.',['MECH-D07-HEDGEHOG-2010'])]),
   question('cholesterol-transport','Cholesterol transport and blood-vessel growth',[
     ('In endothelial-cell experiments, itraconazole caused cholesterol transport inhibition. Cholesterol became trapped in endolysosomes while mTOR signaling and proliferation fell; supplying cholesterol to the cell membrane partly reversed these effects.',['MECH-D07-CHOLESTEROL-2010']),
     ('Later binding and competition experiments identified the cholesterol-transport protein NPC1 as a target, alongside a separate VDAC1–AMPK pathway. These mechanisms help explain the anti-angiogenesis rationale, but do not establish cancer benefit in patients.',['MECH-D07-NPC1-2017'])])]},
 {'drugId':'D10','questions':[
   question('microtubules-apoptosis','Microtubules, cell division and apoptosis',[
     ('In lung-cancer models, fenbendazole partly disrupted microtubules, arrested cell division and increased apoptosis. Experiments also found altered p53 activity and glucose handling.',['MECH-D10-MICROTUBULE-2018']),
     ('The results support several possible contributors to cancer-cell injury. Cell cultures and mouse xenografts do not establish an effective or safe anticancer exposure in people.',['MECH-D10-MICROTUBULE-2018'])])]},
 {'drugId':'D34','questions':[
   question('hyphal-growth','Hyphal growth and invasiveness',[
     ('Fluconazole inhibited the yeast-to-hypha transition in susceptible Candida albicans isolates when present during both growth and hyphal induction. Resistant isolates could still form hyphae.',['MECH-D34-HYPHAE-1999']),
     ('This is evidence about fungal morphology under laboratory conditions. It does not by itself show that tissue invasion is prevented in patients.',['MECH-D34-HYPHAE-1999'])]),
   question('biofilm-resistance','Biofilms and resistance',[
     ('Fluconazole should not be described as a general biofilm-destroying drug. In experiments with clinical Candida albicans isolates, maturing biofilms became less susceptible, with changes in efflux-pump and drug-target gene expression.',['MECH-D34-BIOFILM-2019']),
     ('Preventing early biofilm development and removing an established biofilm are different questions; susceptibility of free-floating yeast does not settle either one.',['MECH-D34-BIOFILM-2019'])]),
   question('azole-specificity','Why fluconazole and itraconazole differ',[
     ('Shared antifungal action does not mean identical repurposing mechanisms. In the original Hedgehog screening experiments, itraconazole suppressed the pathway while fluconazole showed no detectable inhibition at the tested concentrations.',['MECH-D07-HEDGEHOG-2010'])])]},
 {'drugId':'D01','questions':[
   question('autophagy-causality','Testing the autophagy explanation',[
     ('The Parkinson disease experiments went beyond measuring autophagy markers: blocking AMPK or autophagy weakened metformin-associated protection in toxin-injured cells. Mitochondrial damage and oxidative-stress measurements changed as well.',['MF-PD-MECHANISM-2016']),
     ('That supports a causal contribution in this model, with limits from inhibitor specificity and the experimental exposure. It does not establish that the same process improves Parkinson disease in people.',['MF-PD-MECHANISM-2016'])])]},
 {'drugId':'D08','questions':[
   question('wnt-causal-tests','Testing the WNT–TCF explanation',[
     ('In colorectal-cancer experiments, forcing TCF signaling back on rescued cells from some low-concentration ivermectin effects. Ivermectin also inhibited TCF-dependent mouse xenografts but not a TCF-independent comparison model.',['P-D08-CRC-2014']),
     ('This is stronger mechanistic evidence than an association between a pathway marker and cell death. Its relevance still depends on tumor biology, exposure and formulation; it does not establish clinical cancer benefit.',['P-D08-CRC-2014'])])]},
 {'drugId':'D06','questions':[
   question('mtor-autophagy','mTOR and autophagy',[
     ('Rapamycin-sensitive mTOR signaling regulates the ULK–Atg13–FIP200 machinery that helps initiate autophagy. In cell experiments, rapamycin increased autophagic flux, and disrupting ULK or Atg13 weakened that response.',['MECH-D06-AUTOPHAGY-2009']),
     ('This explains a cellular recycling mechanism; whether changing it helps a particular disease requires separate evidence.',['MECH-D06-AUTOPHAGY-2009'])]),
   question('periodontal-mechanism-depth','Inflammation and periodontal bone',[
     ('In aged mice, rapamycin-associated periodontal bone recovery accompanied a lower RANKL/OPG ratio, fewer bone-resorbing osteoclast markers and altered inflammatory signaling.',['P-D06-PERIODONTAL-2020']),
     ('The study did not establish that autophagy caused the bone improvement, and mouse tissue findings do not establish human periodontal benefit.',['P-D06-PERIODONTAL-2020'])])]},
 {'drugId':'D26','questions':[
   question('perfusion-oxygenation','Blood flow and tissue oxygenation',[
     ('Preserving cGMP supplies a rationale for studying vascular function, but vasodilation, blood-flow velocity and tissue oxygenation are different measurements. A controlled sildenafil experiment in healthy men exposed to low oxygen measured these separately.',['CTX-D26-LABEL','MECH-D26-HYPOXIA-2025']),
     ('Some measures of cerebral vascular regulation improved, while the reported cortical oxygenation measures did not show a significant drug effect. This does not support a general claim that sildenafil increases local oxygenation in every condition.',['MECH-D26-HYPOXIA-2025'])])]},
 {'drugId':'D31','questions':[
   question('cerebral-perfusion','Cerebral perfusion and oxygenation',[
     ('A small tadalafil trial after small-vessel stroke found a modest increase in cortical oxygen saturation at three hours. That near-infrared signal was a surrogate for local perfusion, with no significant overall change in the Doppler blood-velocity measure.',['MECH-D31-OXYGENATION-2020']),
     ('PASTIS then measured brain perfusion directly with MRI and found no significant increase in the prespecified subcortical measures after a single dose. These studies test a vascular rationale; they do not establish improved cognition or prevention of another stroke.',['MECH-D31-PASTIS-2022','MECH-D31-OXYGENATION-2020'])])]},
]

canonical = json.loads((ROOT/'data/content.json').read_text())
sources_by_id = {x['id']:x for x in canonical['sources']}
identities = {str(x.get('doi','')).lower():x['id'] for x in canonical['sources'] if x.get('doi')}
urls = {x['url']:x['id'] for x in canonical['sources']}
sources=[]; ledger=[]
for r in records:
    meta=metadata(r['stem'],r['extension'])
    url='https://pmc.ncbi.nlm.nih.gov/articles/'+r['pmc']+'/'
    duplicate=identities.get((meta.get('doi') or '').lower()) or urls.get(url)
    assert not duplicate or duplicate==r['id'], (r['id'],duplicate)
    if not r['existing']:
        sources.append(dict(id=r['id'], **meta, url=url, year=r['year'],
            design=r['design'],population=r['model'],n=r['n'],access='Full text inspected',
            sourceType='Primary research',reviewState='pending',hasReviewDraft=False,
            status='Full text inspected · Review pending',preview=r['preview'],
            decisiveLimit=' '.join(r['translationLimits']),
            locators=[{'section':r['nativeLocator'],'table_figure':r['nativeLocator'],
                       'basis':'Original full-text methods and results inspected; dedicated appraisal pending.'}]))
    ledger.append(dict(sourceId=r['id'],drugId=r['drugId'],conditionScope=r['conditionScope'],
        tier='PRIMARY',sourceUrl=url,sourceFile=r['stem']+r['extension'],sourceHash=r['sourceHash'],
        access='full_text_inspected',sourceIdentity=meta,sourceVersion='PMC manuscript/article version retrieved '+DATE,
        modelSpeciesTissue=r['model'],exposure=r['exposure'],nativeLocator=r['nativeLocator'],
        observation=r['observation'],causalSteps=[{'basis':'tested','step':x,'locator':r['nativeLocator']} for x in r['directlyTested']]+
            [{'basis':'source_proposed','step':x,'locator':r['nativeLocator']} for x in r['sourceProposed']],
        editorialInference='Biological plausibility is distinct from clinical benefit; no human dose inferred.',
        translationLimits=r['translationLimits'],outcomes=r['outcomes'],
        extractionStatus='bounded_mechanism_extraction_complete',appraisalStatus='pending',humanApproval=None,
        deduplication={'canonicalSourceIDReused':r['existing'],'canonicalDOIURLMatch':duplicate,
                      'scope':'Canonical content.json plus current editorial/source-correction inputs; broader historical offline corpus not exhaustively indexed.'},
        sourceIntegrity={'sourcePageInspected':True,'date':DATE,'externalCorrectionRetractionRegistryAudit':'not_checked',
                         'supplements':'not_extracted','fundingConflicts':'not_extracted'}))

packet={'schemaVersion':1,'date':DATE,'integrationMode':'append questions by ID; retain all existing summary/originalAction/questions',
        'sources':sources,'drugs':drugs,
        'existingSourceUpdates':[{'id':r['id'],'access':'Full text inspected','locators':[{'section':r['nativeLocator'],'table_figure':r['nativeLocator'],'basis':'Original full-text methods/results inspected on '+DATE}]} for r in records if r['existing']],
        'notes':'The prose is bounded mechanism synthesis. New cited papers remain pending dedicated Q01–Q15 appraisal; no human approval is claimed.'}
packet['sourceGuideClosures']=[{'drugId':d['drugId'],
    'guideIds':[g['id'] for g in canonical['guides'] if g.get('entityId')==d['drugId'] and g.get('type')=='Drug'],
    'addSourceIds':list(dict.fromkeys(i for q in d['questions'] for i in q['sourceIds']))} for d in drugs]
(BASE/'mechanism-additions.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
(BASE/'source-extraction-ledger.json').write_text(json.dumps({'schemaVersion':1,'date':DATE,'records':ledger},ensure_ascii=False,indent=2)+'\n')

questions=json.loads((BASE/'review-question-input-map.json').read_text())['questions']
input_lines=[]
for r in records:
    if r['existing']: continue
    for q in questions:
        qid=q['id']
        values = {
          'Q01': {'objective':r['conditionScope'],'claim_outcome':r['observation'],'prespecification':None},
          'Q02': {'population_species':r['model'],'experimental_unit':'individual participant / independent experiment as applicable; complete assay-level counts not extracted'},
          'Q03': {'route_exposure_schedule':r['exposure'],'identity_formulation':r['drugId'],'followup':'See native locator; full intervention table not yet extracted'},
          'Q04': {'comparator':None,'availableExperimentalTests':r['directlyTested'],'randomization_blinding':'Design recorded in source metadata; complete comparator/allocation audit pending'},
          'Q05': {'endpoint_class':'mechanistic/surrogate','instrument':'See source-extraction-ledger.json entry','clinical_threshold':None},
          'Q06': {'arm_results':r['outcomes'],'complete_numeric_extraction':False},
          'Q07': {'experimental_unit':'See source-extraction-ledger.json; assay-level replication/missingness audit pending'},
          'Q08': {'harms_ascertainment':None,'patient_safety_inference':'Mechanistic results cannot establish clinical safety'},
          'Q09': {'bias_domains':r['translationLimits'],'formal_appraisal':None},
          'Q10': {'limits':r['translationLimits'],'target_guide':'drug '+r['drugId']},
          'Q11': {'study_family':r['id'],'independence':'No duplicated canonical DOI/URL identified; replication/overlap search incomplete'},
          'Q12': {'authors':metadata(r['stem'],r['extension'])['authors'],'funding':None,'conflicts':None},
          'Q13': {'source_version':'PMC full text retrieved '+DATE,'access':'full_text_inspected','supplements':None,'corrections_retractions':None},
          'Q14': {'claim_links':['DrugMechanism:'+r['drugId']],'observed':r['directlyTested'],'source_proposed':r['sourceProposed']},
          'Q15': {'bounded_takeaway':r['preview'],'unknowns':r['translationLimits'],'clinical_recommendation':None}
        }
        gaps={
          'Q01':'Prespecification/protocol comparison not checked.',
          'Q02':'Full eligibility, setting and per-assay biological/technical counts not extracted.',
          'Q03':'Full formulation/co-intervention inventory not extracted.',
          'Q04':'Full allocation, masking and timing audit not extracted.',
          'Q05':'Complete outcome hierarchy and instrument limitations not appraised.',
          'Q06':'All arms, numerical estimates and uncertainty require figure/table extraction.',
          'Q07':'Missing data, exclusions and experimental-unit accounting not appraised.',
          'Q08':'Harms ascertainment and denominators not extracted; preclinical reports cannot settle human safety.',
          'Q09':'Formal design-appropriate bias appraisal not completed.',
          'Q10':'Clinical exposure matching requires pharmacokinetic/context sources.',
          'Q11':'Independent replication and related-report search not complete.',
          'Q12':'Funding, supplied materials and conflict declarations not extracted.',
          'Q13':'External correction/retraction checks and supplements not reconciled.',
          'Q14':'Mechanism claims mapped; full guide/outcome claim appraisal pending.',
          'Q15':'Final synthesis awaits Q01–Q14 completion; no treatment recommendation inferred.'}
        input_lines.append(dict(paperId=r['id'],questionId=qid,questionSetVersion='one-match-1.14-Q01-Q15',
            field='question_input_map',value_or_null=values[qid],status='partial',reason=gaps[qid],
            sourceId=r['id'],sourceHash=r['sourceHash'],nativeLocator=r['nativeLocator'],
            extractionBasis='Inspected original full-text methods/results; pointers refer to bounded extraction, not completed review.',
            verificationState='input_extraction_only; reviewState=pending; humanApproval=null',
            nextAction='Complete missing fields and dedicated design-appropriate appraisal before marking review released.'))
(BASE/'review-inputs.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in input_lines))

coverage=[]
for drug in ['D01','D06','D07','D08','D10','D26','D31','D34']:
    scope=[r for r in records if r['drugId']==drug]
    coverage.append({'drugId':drug,'sourceIds':[r['id'] for r in scope],
        'status':'bounded_full_text_mechanism_expansion','allMechanismsCovered':False,
        'newSources':sum(not r['existing'] for r in scope),'existingSourcesReused':sum(r['existing'] for r in scope),
        'gaps':['Dedicated review appraisal pending','Supplementary-material extraction and independent replication checks pending']})
(BASE/'coverage-ledger.json').write_text(json.dumps({'date':DATE,'drugs':coverage,'newSourceCount':len(sources),'fullTextReportsInspected':len(records),'Q01_Q15ReviewInputCount':len(input_lines)},indent=2)+'\n')

manifest=[]
for r in records:
    p=BASE/(r['stem']+r['extension'])
    manifest.append({'sourceId':r['id'],'path':p.name,'sha256':r['sourceHash'],'bytes':p.stat().st_size,
       'url':'https://pmc.ncbi.nlm.nih.gov/articles/'+r['pmc']+'/',
       'acquisitionSurface':'Europe PMC fullTextXML' if r['extension']=='.xml' else 'PMC public article HTML',
       'date':DATE})
(BASE/'fulltext-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

all_ids=set(sources_by_id)|{s['id'] for s in sources}|{'CTX-D34-LABEL'}
assert len(sources)==len({s['id'] for s in sources})
for d in drugs:
    assert all(i in all_ids for q in d['questions'] for i in q['sourceIds'])
for s in sources:
    assert {x['questionId'] for x in input_lines if x['paperId']==s['id']}=={f'Q{i:02}' for i in range(1,16)}
    assert s['reviewState']=='pending' and isinstance(s['locators'],list)
print(json.dumps({'reportsInspected':len(records),'newSources':len(sources),'existingSourcesReused':sum(r['existing'] for r in records),'drugRecords':len(drugs),'questionAdditions':sum(len(d['questions']) for d in drugs),'reviewInputRows':len(input_lines),'validation':'PASS'},indent=2))
