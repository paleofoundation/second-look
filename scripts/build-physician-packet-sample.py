"""Render the local NSCLC layout fixture. This never approves or publishes an edition."""
from pathlib import Path
import json,re,html
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("Packet", "/System/Library/Fonts/Supplemental/Arial.ttf"))
pdfmetrics.registerFont(TTFont("Packet-Bold", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"))
pdfmetrics.registerFontFamily("Packet",normal="Packet",bold="Packet-Bold",italic="Packet",boldItalic="Packet-Bold")
ROOT=Path(__file__).resolve().parents[1]
p=json.loads((ROOT/'tests/fixtures/physician-packet-nsclc.json').read_text())
OUT=ROOT.parent/'artifacts/physician-packet-nsclc-v3/output';OUT.mkdir(parents=True,exist_ok=True)
INK=colors.HexColor('#17204D');BLUE=colors.HexColor('#1736F5');MUTED=colors.HexColor('#5B6175');LINE=colors.HexColor('#DCE1EA');PALE=colors.HexColor('#EFF2FF')
styles={
 'body':ParagraphStyle('body',fontName='Packet',fontSize=9.5,leading=14,textColor=INK,spaceAfter=9),
 'title':ParagraphStyle('title',fontName='Packet-Bold',fontSize=25,leading=29,textColor=INK,spaceAfter=9),
 'sub':ParagraphStyle('sub',fontName='Packet',fontSize=10.5,leading=15,textColor=MUTED,spaceAfter=14),
 'h2':ParagraphStyle('h2',fontName='Packet-Bold',fontSize=12,leading=16,textColor=INK,spaceBefore=15,spaceAfter=8),
 'h3':ParagraphStyle('h3',fontName='Packet-Bold',fontSize=15,leading=20,textColor=INK,spaceBefore=15,spaceAfter=4),
 'table':ParagraphStyle('table',fontName='Packet',fontSize=8.5,leading=12,textColor=INK),
 'small':ParagraphStyle('small',fontName='Packet',fontSize=8,leading=11,textColor=MUTED,spaceAfter=7),
 'tiny':ParagraphStyle('tiny',fontName='Packet',fontSize=7.3,leading=10,textColor=MUTED,spaceAfter=6),
 'kicker':ParagraphStyle('kicker',fontName='Packet-Bold',fontSize=8,leading=12,textColor=BLUE,spaceAfter=10),
}
ids={s['id']:i+1 for i,s in enumerate(p['sources'])}
def clean(text):return html.escape(text).replace('≥','&gt;=').replace('–','-')
def P(text,style='body',raw=False):return Paragraph(text if raw else clean(text),styles[style])
def refs(s):return clean(s['text'])+' '+' '.join(f'<super><link href="#source-{ids[i]}" color="#1736F5">[{ids[i]}]</link></super>' for i in s['sourceIds'])
def table(headers,rows,widths):
 data=[[P('<b>'+clean(h)+'</b>','table',True) for h in headers]]+[[P(c,'table',True) for c in row] for row in rows]
 t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('GRID',(0,0),(-1,-1),.45,LINE),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#FAFBFE')])]))
 return t
story=[]
def heading(kicker,title,subtitle=None):
 story.extend([P(kicker,'kicker'),P(title,'title')]);
 if subtitle:story.append(P(subtitle,'sub'))
def nextpage():story.append(PageBreak())
heading('01 / CLINICAL BRIEF',p['title'],'Drug repurposing evidence for a focused clinical discussion')
story.append(P('Edition 3.0 sample  |  Sources checked October 12, 2026  |  Clinical review pending','small'))
story.append(Spacer(1,7))
story.append(table(['Patient / initials','Appointment','Stage / subtype'],[['_____________________','___________________','___________________']],[200,150,182]))
story.append(P('The question for this visit','h2'))
story.append(P('Please assess whether the studies below are relevant to my diagnosis and proposed treatment. If an approach is unsuitable, I would appreciate the specific reason and our agreed next steps. Could additional review or a trial inquiry fit within the treatment timeline you recommend?'))
story.append(P('Clinical context','h2'))
for s in p['summary']:story.append(P(refs(s),raw=True))
story.append(P('Evidence at a glance','h2'))
rows=[]
for s in p['studies']:rows.append([f'<b>{clean(s["intervention"])}</b><br/>{clean(s["title"])}',clean(s['population']),refs(s['meaning'])])
story.append(table(['Intervention / study','Who was studied','Discussion implication'],rows,[150,162,220]))
story.append(Spacer(1,8));story.append(P('Separate studies; these rows do not compare drugs against one another. '+p['scope'],'small'))
for start in range(0,len(p['studies']),2):
 nextpage();heading('02 / EVIDENCE DETAIL','Study findings & limits','Keep the population, comparison and endpoint together.')
 for s in p['studies'][start:start+2]:
  story.extend([P(s['intervention'],'h3'),P(s['title'],'small')])
  context='<b>Population</b> '+clean(s['population'])+'<br/><b>Design</b> '+clean(s['design'])+'<br/><b>Comparison</b> '+clean(s['comparison'])
  story.append(P(context,'small',True))
  rows=[[f'<b>{clean(s.get("primaryLabel","Primary outcome"))}</b>',refs(s['primary'])]]
  if s.get('additional'):rows.append(['<b>Additional findings</b>',refs(s['additional'])])
  rows.extend([['<b>Key limitations</b>',refs(s['limitations'])],['<b>Discussion implication</b>',refs(s['meaning'])]])
  story.append(table(['Read this as','Reported finding or interpretation'],rows,[125,407]))
 story.append(Spacer(1,12));story.append(P('PFS: progression-free survival. OS: overall survival. CI: confidence interval. A hazard ratio is not a percentage-point change in survival. Results from different trials are not a head-to-head comparison.','small'))
categories={'contraindication':'Contraindication / label restriction','precaution':'Precaution / individual review','interaction':'Interaction review','applicability':'Evidence applicability'}
for drug in dict.fromkeys(row['drug'] for row in p['eligibility']):
 nextpage();heading('03 / TREATMENT SUITABILITY','Who should not be considered?',drug+' | Contraindications, precautions and interactions')
 story.append(P('Formal contraindications and label restrictions differ from precautions requiring individual review. Being outside a trial population does not, by itself, establish a contraindication.'))
 rows=[['<b>'+clean(row['label'])+'</b><br/>'+clean(categories[row['category']]),refs(row)] for row in p['eligibility'] if row['drug']==drug]
 story.append(table(['Review area','Who needs exclusion or further review'],rows,[150,382]))
 story.append(P('Before considering this treatment','h2'))
 story.append(P('Ask the treating team to check the exact product label, organ function, allergies, pregnancy or breastfeeding where relevant, and the complete medicine list. Include prescriptions, over-the-counter medicines and supplements.'))
 story.append(P('Selected U.S. label restrictions for oral metformin tablets and itraconazole capsules. This is not the full label or an interaction checker. A short summary cannot establish individual eligibility or justify replacing planned cancer care.','small'))
 story.append(P('Care-team assessment','h2'))
 for _ in range(3):story.extend([Spacer(1,15),P('________________________________________________________________________________','small')])
nextpage();heading('04 / THE CONSULTATION','Safety & next steps')
story.append(P('Points for the care team','h2'));story.append(table(['Review area','Evidence and context'],[['<b>'+clean(s['label'])+'</b>',refs(s)] for i,s in enumerate(p['safety'])],[100,432]))
story.append(P('Questions to resolve together','h2'))
for i,q in enumerate(p['questions']):
 story.append(P(f'<font color="#1736F5"><b>{i+1:02}</b></font>  '+clean(q),raw=True));story.append(Spacer(1,13));story.append(P('________________________________________________________________________________','small'));story.append(Spacer(1,8))
story.append(P('Agreed actions','h2'));story.append(table(['Action / rationale','Responsible person','By when'],[['<br/><br/>','',''],['<br/><br/>','','']],[282,150,100]))
story.append(Spacer(1,15));story.append(P('Keep planned care on schedule unless the treating team changes it. Do not start, stop or substitute a medicine based on this packet.','small'))
nextpage();heading('05 / SOURCES & ACCOUNTABILITY','Trace every finding')
story.append(P(p['coverage'],'small'));story.append(Spacer(1,7))
for i,s in enumerate(p['sources']):
 story.append(P(f'<a name="source-{i+1}"/><b>[{i+1}]</b> '+clean(s['citation']),'small',True))
 story.append(P(f'<link href="{html.escape(s["url"],quote=True)}" color="#1736F5">{clean(s["url"])}</link>','tiny',True))
 story.append(P('Source basis: '+s['basis'],'tiny'));story.append(Spacer(1,5))
story.append(P('Prepared / reviewed by','h2'));story.append(P('Name / qualifications ________________________________________________________','small'));story.append(P('Role / contact ______________________________________________________________','small'));story.append(P('Unsigned design sample. No specialist endorsement or independent clinical approval is represented.','small'))
def pageframe(canvas,doc):
 canvas.saveState();w,h=letter
 canvas.bookmarkPage('page-'+str(doc.page));canvas.addOutlineEntry(['Clinical brief','Itraconazole studies','Metformin studies','Itraconazole contraindications','Metformin contraindications','Safety and next steps','Sources and accountability'][doc.page-1],'page-'+str(doc.page),level=0)
 canvas.setFont('Packet-Bold',15);canvas.setFillColor(INK);canvas.drawString(40,h-33,'RemapRx')
 canvas.setFont('Packet',7);canvas.setFillColor(MUTED);canvas.drawRightString(w-40,h-30,'PHYSICIAN DISCUSSION PACKET')
 canvas.setStrokeColor(BLUE);canvas.setLineWidth(1.5);canvas.line(40,h-43,w-40,h-43)
 canvas.setStrokeColor(LINE);canvas.setLineWidth(.5);canvas.line(40,34,w-40,34)
 canvas.setFont('Packet',7);canvas.drawString(40,22,'DESIGN SAMPLE  |  Clinical review pending  |  NSCLC');canvas.drawRightString(w-40,22,f'{doc.page} / 7');canvas.restoreState()
path=OUT/'remaprx-nsclc-physician-packet-v3.pdf'
doc=SimpleDocTemplate(str(path),pagesize=letter,leftMargin=40,rightMargin=40,topMargin=62,bottomMargin=47,title='NSCLC physician discussion packet - table-led sample',author='RemapRx sample preparation')
doc.build(story,onFirstPage=pageframe,onLaterPages=pageframe)
from pypdf import PdfReader
r=PdfReader(path);assert len(r.pages)==7,f'Expected 7 pages, got {len(r.pages)}'
print(path)
