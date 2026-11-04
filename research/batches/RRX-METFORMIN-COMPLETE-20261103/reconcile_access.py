import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent
p=B/'source-access.json';data=json.loads(p.read_text());sources={s['sourceId']:s for s in data['sources']}
for receipt,key,sid,role in [
 ('mechanism-final-receipt.json','OWEN-2000-mirror','OWEN-2000','full_report_pdf'),
 ('source-identity-receipt.json','MF-COLON-MECHANISM-2010-fullpdf','MF-COLON-MECHANISM-2010','mixed_pdf_relevant_pages_5_to_10'),
 ('final-recovery-receipt.json','ABRILLA-2021-pubmed','ABRILLA-2021','abstract_metadata_only')]:
 r=next(x for x in json.loads((B/receipt).read_text()) if x['id']==key)
 assert r['status']==200
 a={k:r[k] for k in ['path','sha256','url']};a['role']=role
 if role!='abstract_metadata_only':assert Path(a['path']).read_bytes().startswith(b'%PDF')
 if not any(x['sha256']==a['sha256'] for x in sources[sid]['assets']):sources[sid]['assets'].append(a)
sources['MF-COLON-MECHANISM-2010']['assetNote']='Mixed grant-archive PDF: pages 1–4 are another paper; pages 5–10 are Hosono 2010 pp1077–1082, visually read. Final reference page 1083 and supplementary Figure S1 absent. No efficacy extraction from the unrelated pages.'
sources['MF-LABEL-IR-2025']['versionNote']='Stable source ID retained; current SPL effectiveTime 20261026, retrieved November 3, 2026.'
sources['MF-LABEL-ER-2025']['versionNote']='Stable source ID retained; current SPL effectiveTime 20260625, retrieved November 3, 2026.'
sources['COND-C15-MA32-METABOLIC']['assetNote']='MOESM1 is an interaction table and MOESM2 a reporting summary, not the main trial protocol/SAP.'
for sid,title,doi in [
 ('REVIVE-REPLACEMENT','The Effect of Fluvoxamine and Metformin for Fatigue in Patients With Long COVID: An Adaptive Randomized Trial (replacement report)','10.7326/ANNALS-26-02144'),
 ('REVIVE-NOTICE','Notice of Retraction and Republication: The Effect of Fluvoxamine and Metformin for Fatigue in Patients With Long COVID','10.7326/ANNALS-26-03050'),
 ('COVIDOUT-CORRECTION','Correction to Lancet Infectious Diseases 2023;23:1119–29 (COVID-OUT)','10.1016/S1473-3099(23)00562-5')]:
 sources[sid].update(title=title,doi=doi,url='https://doi.org/'+doi)
p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
