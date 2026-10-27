"""Consumer Guide Theme 0.1.1. Local deterministic PDF renderer; no network or source ingestion."""
from pathlib import Path
import argparse,hashlib,html,json,re
from functools import partial
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,PageBreak,KeepTogether,LongTable,TableStyle,Flowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

PACKAGE=Path(__file__).resolve().parents[1]
VERSION='0.1.1'
hashfile=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BLOCKS={'paragraph','heading','kicker','callout','notice','source','toc','table','figure','faq','worksheet','bibliography','contributors','entry'}
def load(path):return json.loads(Path(path).read_text())
def dump(path,value):Path(path).write_text(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
def plain(text):return re.sub('<[^>]+>',' ',text)
def validate(data,config):
 for key in ['schemaVersion','productId','edition','title','audience','scope','notice','decisiveLimits','release','contributors','sources','chapters','previewChapterIds','summary']:
  if key not in data:raise ValueError('Missing manuscript field '+key)
 assert data['schemaVersion']=='consumer-guide-manuscript-1.0'
 ids=[x['id']for x in data['chapters']];assert len(ids)==len(set(ids)) and ids
 assert set(data['previewChapterIds'])<=set(ids) and 0<len(data['previewChapterIds'])<len(ids),'Preview must be a deliberate proper subset'
 assert data['edition'].get('version') and data['edition'].get('updated') and data['edition'].get('evidenceCutoff')
 assert data['release']['status']=='draft','This0.1.1 renderer produces private drafts only; it cannot activate a release'
 if data['release']['status']=='released':
  for field in ['humanEditorial','qualifiedIndependent','legal','accessibility','readerTest']:
   assert data['release'].get(field)=='APPROVED','Unapproved release gate: '+field
 def blockcheck(b):
  assert b['type']in BLOCKS,'Unsupported component '+b['type']
  if b.get('text') and ('orcid.org/' in b['text'] or re.search(r'\d{4}-\d{4}-\d{4}-\d{3}[\dX]',b['text'])):raise ValueError('Use structured contributors for every displayed ORCID')
  if b['type']=='table':
   assert b.get('headers') and all(len(row)==len(b['headers'])for row in b['rows'])
  if b['type']=='figure':assert b.get('alt') and b.get('caption')
  if b['type']=='entry':
   for inner in b['blocks']:blockcheck(inner)
 for chapter in data['chapters']:
  assert chapter.get('title')
  for b in chapter['blocks']:blockcheck(b)
 for b in data['summary']['blocks']:blockcheck(b)
 for key in ['brand','palette','page','summaryPage']:assert key in config
 for key in ['main','accent','pale','ink']:assert re.fullmatch(r'#[0-9a-fA-F]{6}',config['palette'][key])
 for size in [config['page'],config['summaryPage']]:assert len(size)==2 and min(size)>200
 for person in data['contributors']:
  if person.get('orcid'):orcid_identity(person['orcid'])
 for source in data['sources']:
  if source.get('url'):assert re.match(r'^https?://',source['url']),'Source URLs must be HTTP(S)'
 for chapter in data['chapters']:
  for url in re.findall(r'href=[\"\']([^\"\']+)',json.dumps(chapter).replace('\\\"','\"')):
   assert url.startswith(('https://','http://','#')),'Unsupported link scheme'
 sourceids=[s['id']for s in data['sources']];assert len(sourceids)==len(set(sourceids))
 for claim in data.get('claimLedger',[]):assert set(claim['sourceIds'])<=set(sourceids)


ORCID_GREEN='#A6CE39'
def orcid_identity(value):
 value=re.sub(r'^https?://orcid\.org/','',value.strip(),flags=re.I).rstrip('/')
 if not re.fullmatch(r'\d{4}-\d{4}-\d{4}-\d{3}[\dX]',value,re.I):raise ValueError('Invalid supplied ORCID identifier')
 value=value.upper()
 return value,'https://orcid.org/'+value

class OrcidCredit(Flowable):
 """One linked green vector iD mark plus selectable canonical identifier.
 Geometry is adapted from the existing authorized host's OrcidLink SVG.
 """
 def __init__(self,value,ink,records):
  Flowable.__init__(self);self.identifier,self.url=orcid_identity(value)
  self.label='ORCID iD '+self.identifier;self.size=12;self.height=14;self.spaceAfter=7
  self.width=self.size+5+pdfmetrics.stringWidth(self.label,'GuideBody',9)
  self.ink=ink;self.records=records
 def draw(self):
  c=self.canv;c.saveState();c.translate(0,self.size);c.scale(self.size/256,-self.size/256)
  c.setFillColor(HexColor(ORCID_GREEN));c.circle(128,128,128,fill=1,stroke=0)
  c.setFillColor(HexColor('#ffffff'));c.rect(70,80,16,106,fill=1,stroke=0);c.circle(78,55,10,fill=1,stroke=0)
  p=c.beginPath();p.moveTo(111,80);p.lineTo(152,80);p.curveTo(191,80,211,105,211,133);p.curveTo(211,161,191,186,152,186);p.lineTo(111,186);p.close()
  p.moveTo(127,95);p.lineTo(127,171);p.lineTo(151,171);p.curveTo(180,171,195,155,195,133);p.curveTo(195,111,180,95,151,95);p.close()
  c.drawPath(p,fill=1,stroke=0,fillMode=0);c.restoreState()
  c.saveState();c.setFillColor(HexColor(self.ink));c.setFont('GuideBody',9);c.drawString(self.size+5,3,self.label)
  c.linkURL(self.url,(0,0,self.width,self.height),relative=1,thickness=0);c.restoreState()
  self.records.append({'page':c.getPageNumber(),'identifier':self.identifier,'url':self.url,'logoColor':ORCID_GREEN,'logoPoints':self.size,'linkedMarkAndIdentifier':True})

class TraceArt(Flowable):
 """Original vector art: three linked reading steps. Decorative; adjacent text describes its meaning."""
 def __init__(self,width,palette):Flowable.__init__(self);self.width=width;self.height=27;self.palette=palette
 def draw(self):
  c=self.canv;c.setStrokeColor(HexColor(self.palette['main']));c.setLineWidth(1)
  x0=0
  for i,label in enumerate(['Question','Source','Limits']):
   x=x0+i*91;c.setFillColor(HexColor(self.palette['pale']));c.roundRect(x,2,77,22,4,fill=1,stroke=1)
   c.setFillColor(HexColor(self.palette['main']));c.setFont('GuideBody',8);c.drawCentredString(x+38.5,10,label)
   if i<2:c.line(x+78,13,x+89,13)

class GuideDoc(BaseDocTemplate):
 def __init__(self,path,**kwargs):
  self.bookmarks=[];super().__init__(str(path),**kwargs)
 def afterFlowable(self,flowable):
  if hasattr(flowable,'guideAnchor'):
   self.canv.bookmarkPage(flowable.guideAnchor);self.canv.addOutlineEntry(flowable.getPlainText(),flowable.guideAnchor,0,False)
   self.bookmarks.append({'id':flowable.guideAnchor,'title':flowable.getPlainText(),'page':self.page})

def render_variant(data,config,variant,out):
 palette=config['palette'];width,height=config['summaryPage']if variant=='summary'else config['page'];margin=config.get('margin',32)
 for name in ['Inter','Lora']:
  pdfmetrics.registerFont(TTFont('GuideBody'if name=='Inter'else'GuideTitle',str(PACKAGE/'assets/fonts'/f'{name}-Regular.ttf')))
 pdfmetrics.registerFontFamily('GuideBody',normal='GuideBody',bold='GuideBody',italic='GuideBody',boldItalic='GuideBody')
 body=config.get('bodySize',10.8);lead=config.get('leading',14.6)
 styles={
 'paragraph':ParagraphStyle('body',fontName='GuideBody',fontSize=body,leading=lead,textColor=HexColor(palette['ink']),spaceAfter=8),
 'heading':ParagraphStyle('heading',fontName='GuideTitle',fontSize=12.5,leading=16,textColor=HexColor(palette['main']),spaceBefore=2,spaceAfter=6,keepWithNext=True),
 'kicker':ParagraphStyle('kicker',fontName='GuideBody',fontSize=8.5,leading=11,textColor=HexColor(palette['main']),spaceAfter=10,keepWithNext=True),
 'callout':ParagraphStyle('callout',fontName='GuideBody',fontSize=10.2,leading=14,textColor=HexColor(palette['ink']),backColor=HexColor(palette['pale']),borderPadding=6,spaceBefore=4,spaceAfter=12),
 'notice':ParagraphStyle('notice',fontName='GuideBody',fontSize=9.5,leading=12.5,textColor=HexColor(palette['ink']),spaceBefore=4,spaceAfter=9),
 'source':ParagraphStyle('source',fontName='GuideBody',fontSize=9,leading=11.5,textColor=HexColor(palette['ink']),spaceAfter=7),
 'title':ParagraphStyle('title',fontName='GuideTitle',fontSize=21,leading=25,textColor=HexColor(palette['main']),spaceAfter=16,keepWithNext=True),
 'cell':ParagraphStyle('cell',fontName='GuideBody',fontSize=8.8,leading=11.5,textColor=HexColor(palette['ink'])),
 }
 selected=data['chapters']if variant=='full'else [x for x in data['chapters']if x['id']in data['previewChapterIds']]if variant=='preview'else [{'id':'summary','title':data['summary']['title'],'blocks':data['summary']['blocks']}]
 selectedids={x['id']for x in selected};story=[];features=[];orcidCredits=[]
 def para(txt,kind='paragraph'):return Paragraph(txt,styles[kind])
 def heading(title,anchor=None):
  p=para(title,'title'if anchor else'heading')
  if anchor:p.guideAnchor=anchor
  return p
 def table(headers,rows,widths=None):
  total=width-2*margin
  table=LongTable([[para(html.escape(str(c)),'cell')for c in row]for row in [headers]+rows],colWidths=[total*x/sum(widths)for x in widths]if widths else [total/len(headers)]*len(headers),repeatRows=1,hAlign='LEFT',splitByRow=1)
  table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor(palette['pale'])),('LINEBELOW',(0,0),(-1,0),1,HexColor(palette['main'])),('LINEBELOW',(0,1),(-1,-1),.3,HexColor('#dddddd')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));return [table,Spacer(1,10)]
 def blocks(items):
  result=[]
  for b in items:
   kind=b['type'];features.append(kind)
   if kind in ['paragraph','heading','kicker','callout','notice','source']:result.append(para(b['text'],kind))
   elif kind=='toc':
    for item in b['items']:
     label=html.escape(item['title']);target=item['chapterId']
     result.append(para(f'<link href="#{target}" color="{palette["main"]}">{label}</link>'if target in selectedids else label+' (full guide)','source'))
   elif kind=='table':result+=table(b['headers'],b['rows'],b.get('widths'))
   elif kind=='entry':result.append(heading(b['title']));result+=blocks(b['blocks'])
   elif kind=='figure':
    # No remote images or source-article figures. The original theme diagram is data-selected.
    assert b.get('asset')=='trace-diagram','Only original bundled vector diagram is supported'
    result.append(KeepTogether([para(b['title'],'heading'),TraceArt(width-2*margin,palette),para('Image description: '+html.escape(b['alt']),'source'),para(html.escape(b['caption']),'source')]))
   elif kind=='faq':
    result.append(heading(b['question']));result.append(para(b['answer']))
   elif kind=='worksheet':
    result.append(heading(b['title']))
    for prompt in b['prompts']:result.append(para(html.escape(prompt)+'<br/>________________________________________________','source'))
   elif kind=='bibliography':
    for s in data['sources']:
     txt=f'[{s["label"]}] '+html.escape(s['title'])
     if s.get('url'):txt=f'<link href="{html.escape(s["url"],quote=True)}" color="{palette["main"]}">{txt}</link>'
     result.append(para(txt+'<br/>'+html.escape(s['locator']+' | '+s['role']),'source'))
   elif kind=='contributors':
    for person in data['contributors']:
     txt=html.escape(person['name']+' - '+person['role']+'. '+person['status'])
     credit=[para(txt,'source')]
     if person.get('orcid'):credit.append(OrcidCredit(person['orcid'],palette['ink'],orcidCredits))
     result.append(KeepTogether(credit))
  return result
 for index,chapter in enumerate(selected):
  if index:story.append(PageBreak())
  story.append(heading(html.escape(chapter['title']),chapter['id']))
  if index==0:
   story.append(TraceArt(width-2*margin,palette));story.append(Spacer(1,8))
  story+=blocks(chapter['blocks'])
 # The same single source of notice and decisive limits is enforced in all three variants.
 if variant=='summary':
  story.append(para(data['notice'],'notice'))
  for limit in data['decisiveLimits']:story.append(para(limit,'source'))
  correction=html.escape(data['correctionRoute'],quote=True)
  correction_link=f'<link href="{correction}">Corrections and edition updates</link>'if correction.startswith(('https://','http://'))else correction
  policy=html.escape(data.get('policyRoute',''),quote=True)
  policy_link=f' | <link href="{policy}">Educational-use policy</link>'if policy.startswith(('https://','http://'))else''
  story.append(para('Edition '+html.escape(data['edition']['version'])+'; evidence checked '+html.escape(data['edition']['evidenceCutoff'])+'. '+correction_link+policy_link,'source'))
  story+=blocks([{'type':'contributors'}])
 def page_chrome(c,doc):
  c.saveState();c.setFillColor(HexColor(palette['main']));c.rect(0,height-23,width,23,fill=1,stroke=0)
  c.setFillColor(HexColor('#ffffff'));c.setFont('GuideBody',7.8);c.drawString(margin,height-15,config['brand'])
  c.setFont('GuideBody',7);c.drawRightString(width-margin,height-15,'PRIVATE SYNTHETIC FIXTURE'if data.get('synthetic')else'PRIVATE EDITORIAL DRAFT')
  c.setFillColor(HexColor(palette['accent']));c.rect(margin,height-43,30,3,fill=1,stroke=0)
  c.setFillColor(HexColor(palette['main']));c.setFont('GuideBody',7)
  c.drawString(margin,20,f'{variant.title()} | {data["edition"]["version"]} | {data["edition"]["updated"]}');c.drawRightString(width-margin,20,str(doc.page));c.restoreState()
 filename=f'{data["slug"]}-{data["edition"]["version"]}-{variant}.pdf';path=out/filename
 doc=GuideDoc(path,pagesize=(width,height),leftMargin=margin,rightMargin=margin,topMargin=56,bottomMargin=38,title=data['title']+' - '+variant,author='; '.join(x['name']+' ('+x['role']+')'for x in data['contributors']),subject='Private draft; clinical, legal, editorial and accessibility release gates remain separate.')
 frame=Frame(margin,38,width-2*margin,height-94,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0,id='body')
 doc.addPageTemplates(PageTemplate(id='guide',frames=frame,onPage=page_chrome))
 def deterministic_canvas(*args,**kwargs):
  kwargs['invariant']=1
  return canvas.Canvas(*args,**kwargs)
 doc.build(story,canvasmaker=deterministic_canvas)
 reader=PdfReader(path);text='\n'.join(x.extract_text()or''for x in reader.pages)
 annotations=[]
 for i,page in enumerate(reader.pages,1):
  for raw in page.get('/Annots',[]):
   a=raw.get_object();annotations.append({'page':i,'kind':str(a.get('/Subtype')),'uri':str(a.get('/A',{}).get('/URI','')),'destinationPage':next((j for j,pg in enumerate(reader.pages,1) if a.get('/Dest') and hasattr(a['/Dest'][0],'idnum') and a['/Dest'][0].idnum==pg.indirect_reference.idnum),None)})
 return {'file':filename,'sha256':hashfile(path),'bytes':path.stat().st_size,'pages':len(reader.pages),'textCharacters':len(text),'bookmarks':doc.bookmarks,'linkAnnotations':annotations,'components':sorted(set(features)),'orcidCredits':orcidCredits,'tagged':False,'pdfUaCertified':False}

def render_all(manuscript,configfile,out):
 data=load(manuscript);config=load(configfile);validate(data,config);out=Path(out);out.mkdir(parents=True,exist_ok=True)
 assets={variant:render_variant(data,config,variant,out)for variant in ['full','preview','summary']}
 report={'schemaVersion':'consumer-guide-render-manifest-1.0','rendererVersion':VERSION,'productId':data['productId'],'edition':data['edition'],'synthetic':data.get('synthetic',False),'release':data['release'],'manuscriptSha256':hashfile(manuscript),'configSha256':hashfile(configfile),'rendererSha256':hashfile(__file__),'fontHashes':{p.name:hashfile(p)for p in sorted((PACKAGE/'assets/fonts').glob('*.ttf'))},'assets':assets,'accessibility':'HOLD: selectable text/bookmarks; untagged PDF and reading order not certified','verification':'Generated; every-page visual inspection recorded separately'}
 dump(out/'render-manifest.json',report);return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--manuscript',required=True);p.add_argument('--config',required=True);p.add_argument('--out',required=True);a=p.parse_args();r=render_all(a.manuscript,a.config,a.out);print(json.dumps({'productId':r['productId'],'assets':{k:{'file':v['file'],'pages':v['pages'],'sha256':v['sha256']}for k,v in r['assets'].items()}}))
