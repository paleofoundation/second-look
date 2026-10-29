"""Build correction batch for metformin completeness items 5, 23-27."""
import json, copy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

with open(ROOT / 'data/content.json') as f:
    content = json.load(f)
with open(ROOT / 'data/public-mechanisms.json') as f:
    mechanisms_data = json.load(f)

met = next(g for g in content['guides'] if g.get('id') == 'G-METFORMIN')
d01 = next(d for d in mechanisms_data['drugs'] if d.get('drugId') == 'D01')

new_sources = [
    {
        "id": "MF-LABEL-IR-2025",
        "title": "Metformin hydrochloride tablets, USP: U.S. prescribing information",
        "url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=30658e19-8e6e-49aa-a007-e414224797c5",
        "year": 2025,
        "access": "full_text_html",
        "sourceType": "context",
        "sourceTier": "official_label",
        "design": "Official U.S. prescribing information",
        "population": "People receiving immediate-release metformin hydrochloride tablets for type 2 diabetes",
        "preview": "U.S. prescribing information for immediate-release metformin tablets; covers labeled adult dosing (500 mg BID or 850 mg QD start; titration +500 mg/week or +850 mg/2 weeks; max 2,550 mg/day), pediatric dosing ages 10 and older (500 mg BID start; max 2,000 mg/day), and renal impairment dose restrictions.",
        "locators": [
            {"section": "2.1 Recommended Dosing Schedule for Adults"},
            {"section": "2.2 Recommended Dosing Schedule for Pediatric Patients (10 years and older)"},
            {"section": "2.3 Patients with Renal Impairment"}
        ],
        "reviewState": "pending",
        "hasReviewDraft": False
    },
    {
        "id": "MF-LABEL-ER-2025",
        "title": "Metformin hydrochloride extended-release tablets, USP: U.S. prescribing information",
        "url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=96c8a89d-99db-24b1-e053-2a95a90ac2b8",
        "year": 2025,
        "access": "full_text_html",
        "sourceType": "context",
        "sourceTier": "official_label",
        "design": "Official U.S. prescribing information",
        "population": "Adults receiving extended-release metformin hydrochloride tablets for type 2 diabetes",
        "preview": "U.S. prescribing information for extended-release metformin tablets; covers labeled adult dosing (500 mg once daily with evening meal; +500 mg/week; max 2,000 mg once daily), switching from immediate-release, and renal impairment restrictions.",
        "locators": [
            {"section": "2.1 Recommended Dosing Schedule"},
            {"section": "2.2 Patients with Renal Impairment"},
            {"section": "4 Contraindications"}
        ],
        "reviewState": "pending",
        "hasReviewDraft": False
    },
    {
        "id": "OWEN-2000",
        "title": "Evidence that metformin exerts its anti-diabetic effects through inhibition of complex 1 of the mitochondrial respiratory chain",
        "url": "https://pubmed.ncbi.nlm.nih.gov/10839993/",
        "year": 2000,
        "pmid": "10839993",
        "authors": "Owen MR, Doran E, Halestrap AP",
        "design": "Preclinical: hepatoma cell-line and isolated rat hepatocyte experiments",
        "population": "Hepatoma cell lines and rat hepatocytes (preclinical, non-clinical)",
        "sourceType": "primary",
        "preview": "Demonstrated time-dependent complex I inhibition by metformin at 50 micromolar in intact hepatoma cells (13 percent reduction at 24 h, 30 percent at 60 h); sub-mitochondrial particles required approximately 79 mM for half-maximal inhibition; succinate oxidation unaffected, confirming complex I selectivity.",
        "locators": [
            {"section": "Results"},
            {"section": "Discussion"}
        ],
        "reviewState": "pending",
        "hasReviewDraft": False
    },
    {
        "id": "EL-MIR-2000",
        "title": "Dimethylbiguanide inhibits cell respiration via an indirect effect targeted on the respiratory chain complex I",
        "url": "https://pubmed.ncbi.nlm.nih.gov/10617608/",
        "year": 2000,
        "pmid": "10617608",
        "doi": "10.1074/jbc.275.1.223",
        "authors": "El-Mir MY, Nogueira V, Fontaine E, Averet N, Rigoulet M, Leverve X",
        "design": "Preclinical: hepatocyte respiration and cell-permeabilization experiments",
        "population": "Isolated rat hepatocytes and sub-cellular fractions (preclinical, non-clinical)",
        "sourceType": "primary",
        "preview": "Showed metformin inhibits complex I respiration only in intact cells, not in permeabilized hepatocytes or isolated mitochondria, demonstrating an indirect cell-signaling mechanism; temperature-dependent; complex I substrates affected, complex II and IV substrates unaffected.",
        "locators": [
            {"section": "Results"},
            {"section": "Conclusions"}
        ],
        "reviewState": "pending",
        "hasReviewDraft": False
    },
    {
        "id": "ABRILLA-2021",
        "title": "Metformin extended-release versus metformin immediate-release for adults with type 2 diabetes mellitus: A systematic review and meta-analysis of randomized controlled trials",
        "url": "https://pubmed.ncbi.nlm.nih.gov/33887354/",
        "year": 2021,
        "pmid": "33887354",
        "doi": "10.1016/j.diabres.2021.108824",
        "authors": "Abrilla AA, Pajes ANNI, Jimeno CA",
        "design": "Systematic review and meta-analysis of 9 randomized controlled trials",
        "population": "2,609 adults with type 2 diabetes",
        "n": 2609,
        "randomizedN": 2609,
        "sourceType": "primary",
        "preview": "Nine RCTs in 2,609 adults with type 2 diabetes; ER metformin produced statistically worse but likely clinically similar HbA1c lowering compared with IR; ER reduced dyspepsia but not overall gastrointestinal intolerance (diarrhea, abdominal discomfort, nausea).",
        "locators": [
            {"section": "Results"},
            {"section": "Conclusion"}
        ],
        "reviewState": "pending",
        "hasReviewDraft": False
    },
    {
        "id": "INZUCCHI-2014",
        "title": "Metformin in patients with type 2 diabetes and kidney disease: a systematic review",
        "url": "https://pubmed.ncbi.nlm.nih.gov/25536258/",
        "year": 2014,
        "pmid": "25536258",
        "doi": "10.1001/jama.2014.15298",
        "authors": "Inzucchi SE, Lipska KJ, Mayo H, Bailey CJ, McGuire DK",
        "design": "Systematic review",
        "population": "Adults with type 2 diabetes and chronic kidney disease",
        "sourceType": "primary",
        "preview": "JAMA systematic review; lactic acidosis rates not substantially increased at eGFR 30 to 60 mL/min/1.73 m2; cautious metformin use with monitoring and dose reduction warranted in mild-to-moderate chronic kidney disease.",
        "locators": [
            {"section": "Results"},
            {"section": "Conclusions"}
        ],
        "reviewState": "pending",
        "hasReviewDraft": False
    }
]

new_dosing_questions = [
    {
        "id": "dosing-ir-label",
        "question": "What are the labeled starting dose and titration schedule for immediate-release metformin?",
        "answer": "The U.S. prescribing information for immediate-release metformin tablets lists a starting dose of 500 mg twice daily or 850 mg once daily, taken with meals. The dose is increased by 500 mg each week or by 850 mg every two weeks, based on glycemic control and tolerability, up to a maximum of 2,550 mg per day in divided doses. The label notes that doses above 2,000 mg per day may be better tolerated when divided into three doses taken with meals. These are the labeled regimens for type 2 diabetes; repurposing trials used their own schedules.",
        "sources": ["MF-LABEL-IR-2025"],
        "sentences": [
            {
                "text": "The U.S. prescribing information for immediate-release metformin tablets lists a starting dose of 500 mg twice daily or 850 mg once daily, taken with meals.",
                "sources": ["MF-LABEL-IR-2025"]
            },
            {
                "text": "The dose is increased by 500 mg each week or by 850 mg every two weeks, based on glycemic control and tolerability, up to a maximum of 2,550 mg per day in divided doses.",
                "sources": ["MF-LABEL-IR-2025"]
            },
            {
                "text": "The label notes that doses above 2,000 mg per day may be better tolerated when divided into three doses taken with meals. These are the labeled regimens for type 2 diabetes; repurposing trials used their own schedules.",
                "sources": ["MF-LABEL-IR-2025"]
            }
        ]
    },
    {
        "id": "dosing-er-label",
        "question": "What is the labeled starting dose and maximum for extended-release metformin?",
        "answer": "The U.S. prescribing information for extended-release metformin tablets recommends starting at 500 mg once daily with the evening meal. The dose is increased by 500 mg each week based on glycemic control and tolerability, up to a maximum of 2,000 mg once daily with the evening meal. The label states that patients already receiving immediate-release metformin may switch to the same total daily dose as extended-release taken once daily. The extended-release label does not include a pediatric dosing section.",
        "sources": ["MF-LABEL-ER-2025"],
        "sentences": [
            {
                "text": "The U.S. prescribing information for extended-release metformin tablets recommends starting at 500 mg once daily with the evening meal.",
                "sources": ["MF-LABEL-ER-2025"]
            },
            {
                "text": "The dose is increased by 500 mg each week based on glycemic control and tolerability, up to a maximum of 2,000 mg once daily with the evening meal.",
                "sources": ["MF-LABEL-ER-2025"]
            },
            {
                "text": "The label states that patients already receiving immediate-release metformin may switch to the same total daily dose as extended-release taken once daily. The extended-release label does not include a pediatric dosing section.",
                "sources": ["MF-LABEL-ER-2025"]
            }
        ]
    },
    {
        "id": "dosing-ir-vs-er",
        "question": "Do immediate-release and extended-release metformin have the same efficacy and tolerability?",
        "answer": "A 2021 systematic review and meta-analysis of nine randomized controlled trials in 2,609 adults with type 2 diabetes found that extended-release metformin produced statistically worse but likely clinically similar HbA1c lowering compared with immediate-release. Extended-release reduced dyspepsia relative to immediate-release but did not significantly reduce overall gastrointestinal intolerance, including diarrhea, abdominal discomfort, and nausea. The U.S. prescribing information for each formulation describes its own dosing regimen and does not assert equivalent glycemic efficacy across formulations.",
        "sources": ["ABRILLA-2021", "MF-LABEL-IR-2025", "MF-LABEL-ER-2025"],
        "sentences": [
            {
                "text": "A 2021 systematic review and meta-analysis of nine randomized controlled trials in 2,609 adults with type 2 diabetes found that extended-release metformin produced statistically worse but likely clinically similar HbA1c lowering compared with immediate-release.",
                "sources": ["ABRILLA-2021"]
            },
            {
                "text": "Extended-release reduced dyspepsia relative to immediate-release but did not significantly reduce overall gastrointestinal intolerance, including diarrhea, abdominal discomfort, and nausea.",
                "sources": ["ABRILLA-2021"]
            },
            {
                "text": "The U.S. prescribing information for each formulation describes its own dosing regimen and does not assert equivalent glycemic efficacy across formulations.",
                "sources": ["MF-LABEL-IR-2025", "MF-LABEL-ER-2025"]
            }
        ]
    },
    {
        "id": "dosing-renal-adjustment",
        "question": "How should metformin dosing be adjusted based on kidney function?",
        "answer": "Both the immediate-release and extended-release U.S. prescribing information require assessment of kidney function (eGFR) before starting metformin and periodically during treatment. Starting metformin is not recommended when eGFR is 30 to 45 mL/min/1.73 m2; metformin is contraindicated and should be discontinued when eGFR falls below 30 mL/min/1.73 m2. A 2014 systematic review in JAMA of metformin in type 2 diabetes and kidney disease found that lactate concentrations are not substantially increased at eGFR values of 30 to 60 mL/min/1.73 m2, and concluded that cautious use with dose monitoring is warranted in mild-to-moderate chronic kidney disease.",
        "sources": ["MF-LABEL-IR-2025", "MF-LABEL-ER-2025", "INZUCCHI-2014"],
        "sentences": [
            {
                "text": "Both the immediate-release and extended-release U.S. prescribing information require assessment of kidney function (eGFR) before starting metformin and periodically during treatment.",
                "sources": ["MF-LABEL-IR-2025", "MF-LABEL-ER-2025"]
            },
            {
                "text": "Starting metformin is not recommended when eGFR is 30 to 45 mL/min/1.73 m2; metformin is contraindicated and should be discontinued when eGFR falls below 30 mL/min/1.73 m2.",
                "sources": ["MF-LABEL-IR-2025", "MF-LABEL-ER-2025"]
            },
            {
                "text": "A 2014 systematic review in JAMA of metformin in type 2 diabetes and kidney disease found that lactate concentrations are not substantially increased at eGFR values of 30 to 60 mL/min/1.73 m2, and concluded that cautious use with dose monitoring is warranted in mild-to-moderate chronic kidney disease.",
                "sources": ["INZUCCHI-2014"]
            }
        ]
    },
    {
        "id": "dosing-pediatric",
        "question": "What does the U.S. label say about metformin dosing in children?",
        "answer": "The U.S. prescribing information for immediate-release metformin tablets includes an indication for type 2 diabetes in children aged 10 years and older. The labeled starting dose for this age group is 500 mg twice daily with meals, increased by 500 mg each week based on glycemic control and tolerability, with a maximum of 2,000 mg per day in divided doses. The extended-release U.S. prescribing information covers adult dosing only and does not include a pediatric dosing section.",
        "sources": ["MF-LABEL-IR-2025", "MF-LABEL-ER-2025"],
        "sentences": [
            {
                "text": "The U.S. prescribing information for immediate-release metformin tablets includes an indication for type 2 diabetes in children aged 10 years and older.",
                "sources": ["MF-LABEL-IR-2025"]
            },
            {
                "text": "The labeled starting dose for this age group is 500 mg twice daily with meals, increased by 500 mg each week based on glycemic control and tolerability, with a maximum of 2,000 mg per day in divided doses.",
                "sources": ["MF-LABEL-IR-2025"]
            },
            {
                "text": "The extended-release U.S. prescribing information covers adult dosing only and does not include a pediatric dosing section.",
                "sources": ["MF-LABEL-ER-2025"]
            }
        ]
    }
]

complex_i_pathway = {
    "id": "metformin-complex-i",
    "title": "Complex I inhibition and energy sensing",
    "text": "Two preclinical studies in cells and isolated mitochondria show that metformin inhibits complex I of the mitochondrial respiratory chain, the enzyme that initiates electron transfer during cellular respiration. In intact hepatoma cells, 50 micromolar metformin produced time-dependent inhibition of complex I activity, reducing glutamate oxidation by 13 percent after 24 hours and 30 percent after 60 hours; succinate oxidation, which enters at complex II, was unaffected, confirming selectivity for complex I. In a complementary study using isolated rat hepatocytes, inhibition of cell respiration by metformin occurred only in intact cells and not in permeabilized cells or isolated mitochondria, demonstrating that the mechanism requires an indirect, cell-mediated signaling step rather than direct drug contact with the enzyme. In isolated sub-mitochondrial particles, half-maximal inhibition required approximately 79 mM, far above therapeutic plasma concentrations, while the effect appeared at 50 micromolar in intact cells, consistent with intracellular drug accumulation. Reduced flux through complex I lowers cellular ATP production and is proposed to be one upstream trigger for the AMPK activation described in other pathway studies. These are preclinical findings from cell lines, isolated hepatocytes, and sub-cellular fractions; they do not establish the concentrations, tissue distribution, or extent of complex I inhibition during therapeutic metformin treatment in people.",
    "sourceIds": ["OWEN-2000", "EL-MIR-2000"],
    "sentences": [
        {
            "text": "Two preclinical studies in cells and isolated mitochondria show that metformin inhibits complex I of the mitochondrial respiratory chain, the enzyme that initiates electron transfer during cellular respiration.",
            "sources": ["OWEN-2000", "EL-MIR-2000"]
        },
        {
            "text": "In intact hepatoma cells, 50 micromolar metformin produced time-dependent inhibition of complex I activity, reducing glutamate oxidation by 13 percent after 24 hours and 30 percent after 60 hours; succinate oxidation, which enters at complex II, was unaffected, confirming selectivity for complex I.",
            "sources": ["OWEN-2000"]
        },
        {
            "text": "In a complementary study using isolated rat hepatocytes, inhibition of cell respiration by metformin occurred only in intact cells and not in permeabilized cells or isolated mitochondria, demonstrating that the mechanism requires an indirect, cell-mediated signaling step rather than direct drug contact with the enzyme.",
            "sources": ["EL-MIR-2000"]
        },
        {
            "text": "In isolated sub-mitochondrial particles, half-maximal inhibition required approximately 79 mM, far above therapeutic plasma concentrations, while the effect appeared at 50 micromolar in intact cells, consistent with intracellular drug accumulation.",
            "sources": ["OWEN-2000"]
        },
        {
            "text": "Reduced flux through complex I lowers cellular ATP production and is proposed to be one upstream trigger for the AMPK activation described in other pathway studies.",
            "sources": ["OWEN-2000", "EL-MIR-2000"]
        },
        {
            "text": "These are preclinical findings from cell lines, isolated hepatocytes, and sub-cellular fractions; they do not establish the concentrations, tissue distribution, or extent of complex I inhibition during therapeutic metformin treatment in people.",
            "sources": ["OWEN-2000", "EL-MIR-2000"]
        }
    ]
}

sections = copy.deepcopy(met['sections'])
for s in sections:
    if s['id'] == 'dosing':
        s['questions'] = new_dosing_questions
        break

d01_updated = copy.deepcopy(d01)
# Avoid duplicates if re-run after a partial apply
if not any(p['id'] == complex_i_pathway['id'] for p in d01_updated['pathways']):
    d01_updated['pathways'].append(complex_i_pathway)

guide_update = {
    "guideId": "G-METFORMIN",
    "description": met['description'],
    "sections": sections
}

batch = {
    "sources": new_sources,
    "mechanisms": [d01_updated],
    "guides": [guide_update]
}

out_path = ROOT / 'research/batches/FILL-REMAPRX-MET-20261029/BATCH.json'
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(batch, f, ensure_ascii=False, indent=2)
    f.write('\n')

print('Batch written to:', out_path)
print('Sources:', len(batch['sources']))
print('Mechanisms:', len(batch['mechanisms']))
print('Guides:', len(batch['guides']))
