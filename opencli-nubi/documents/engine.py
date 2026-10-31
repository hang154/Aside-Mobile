"""Budget authoring with cited facts, Decimal arithmetic and explicit readiness.
No model code, filenames, credentials, destinations or arbitrary URLs are executed.
"""
import hashlib,json,re,subprocess,zipfile
from decimal import Decimal,InvalidOperation
from pathlib import Path
from lxml import etree
from docx import Document
from docx.shared import Pt

LIMIT=16*1024*1024

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_text(path):
 p=Path(path);suffix=p.suffix.lower()
 if p.stat().st_size>LIMIT:raise ValueError('Document too large')
 if suffix in ('.docx','.hwpx'):
  with zipfile.ZipFile(p) as z:
   if sum(i.file_size for i in z.infolist())>64*1024*1024:raise ValueError('Expanded document too large')
   if z.testzip():raise ValueError('Corrupt document archive')
   parts=['word/document.xml'] if suffix=='.docx' else sorted(n for n in z.namelist() if re.fullmatch(r'Contents/section\d+\.xml',n))
   text=[]
   for name in parts:
    root=etree.fromstring(z.read(name),etree.XMLParser(resolve_entities=False,no_network=True))
    # Preserve paragraphs/cells, including Korean tables, rather than concatenate runs.
    for e in root.xpath('//*[local-name()="p"]'):
     t=''.join(e.xpath('.//*[local-name()="t"]/text()'))
     if t:text.append(t)
   return '\n'.join(text)
 if suffix=='.hwp':
  r=subprocess.run(['hwp5txt',str(p)],capture_output=True,timeout=60,check=True)
  return r.stdout.decode('utf-8')
 if suffix in ('.txt','.md','.csv','.json'):return p.read_text(encoding='utf-8')
 raise ValueError('Supported input: DOCX, HWPX, HWP5, text/JSON')

def decimal(value):
 if isinstance(value,bool):raise ValueError('Boolean is not money')
 try:d=Decimal(str(value).replace(',',''))
 except InvalidOperation:raise ValueError('Invalid number')
 if not d.is_finite() or d<0 or d>Decimal('100000000000'):raise ValueError('Number outside budget bounds')
 return d

def evidence(fact,sources,numeric=False):
 if not isinstance(fact,dict) or 'value' not in fact or not isinstance(fact.get('refs'),list):return False
 value=fact['value']
 if value is None or value=='':return False
 quotes=[]
 for ref in fact['refs']:
  if not isinstance(ref,dict):return False
  src=sources.get(ref.get('source_id'));quote=ref.get('quote','')
  if src is None or not isinstance(quote,str) or not quote.strip() or quote not in src['text']:return False
  quotes.append(quote)
 if not quotes:return False
 if numeric:
  try:n=decimal(value)
  except (ValueError,TypeError):return False
  # A numerical field must literally occur in cited evidence; conversions are separate facts.
  numbers=[]
  for q in quotes:
   for token in re.findall(r'(?<![\d.])[\d,]+(?:\.\d+)?(?![\d.])',q):
    try:numbers.append(decimal(token))
    except ValueError:pass
  return n in numbers
 return isinstance(value,str) and len(value)<=4000

LABELS={'program':'프로그램','team':'팀명','research_topic':'연구주제','advisor':'지도교수','advisor_department':'지도교수 소속','activity':'학회·활동명','location':'참가 장소','period':'활동·사용 기간','people':'참가 인원','purpose':'신청 목적 및 필요성','date':'작성일','applicant':'신청자','registered_bank':'학교 등록 은행','registered_account':'학교 등록 계좌번호','application_bank':'신청서 은행','application_account':'신청서 계좌번호'}
REQUIRED={
 'uirp':['program','team','research_topic','advisor','activity','location','period','people','purpose','date'],
 'lseries':['applicant','period','purpose','registered_bank','registered_account','application_bank','application_account','date'],
 'general':['applicant','purpose','period','date']}

def audit(plan,sources,profile):
 if profile not in REQUIRED:raise ValueError('Unknown document profile')
 if not isinstance(plan,dict) or not isinstance(plan.get('fields'),dict) or not isinstance(plan.get('items'),list):raise ValueError('Invalid budget plan')
 if len(plan['items'])>30:raise ValueError('Too many expense lines')
 fields=plan['fields'];issues=[];rows=[];totals={}
 if any(not isinstance(v,dict) for v in fields.values()) or any(not isinstance(v,dict) for v in plan['items']):raise ValueError('Every field/item must be a structured fact')
 for key in REQUIRED[profile]:
  if not evidence(fields.get(key),sources,numeric=key=='people'):issues.append('필수 근거 누락: '+LABELS.get(key,key))
 for key,fact in fields.items():
  if fact.get('value') not in (None,'') and not evidence(fact,sources,numeric=key=='people'):issues.append('출처 검증 실패: '+LABELS.get(key,key))
 for key in ['program','team','applicant','advisor','registered_bank','registered_account','application_bank','application_account','date']:
  f=fields.get(key,{})
  if f.get('value'):
   norm=lambda x:re.sub(r'[^\w]','',x)
   quote=' '.join(ref.get('quote','') for ref in f.get('refs',[]) if isinstance(ref,dict))
   if norm(str(f['value'])) not in norm(quote):issues.append('값과 인용 근거 불일치: '+LABELS.get(key,key))
   if key.endswith('_account') and len(re.sub(r'\D','',str(f['value'])))<8:issues.append('계좌번호 전체 근거 필요: '+LABELS.get(key,key))
 if profile=='uirp' and fields.get('program',{}).get('value') not in ('UIRP','AICP'):issues.append('프로그램 구분 미확인')
 if profile=='lseries':
  for a,b in [('registered_bank','application_bank'),('registered_account','application_account')]:
   x=fields.get(a,{}).get('value');y=fields.get(b,{}).get('value')
   if x and y and re.sub(r'[\s-]','',x)!=re.sub(r'[\s-]','',y):issues.append('학교 등록 계좌와 신청 계좌 불일치: '+LABELS.get(a,a))
 for i,item in enumerate(plan['items']):
  prefix=f'항목 {i+1}'
  if any(not isinstance(item.get(k),dict) for k in ('label','unit_price','quantity')):raise ValueError(prefix+' 구조 오류: 항목/단가/수량은 인용 근거가 있는 fact 객체여야 함')
  label=item.get('label');currency=item.get('currency','')
  valid=evidence(label,sources) and evidence(item.get('unit_price'),sources,True) and evidence(item.get('quantity'),sources,True)
  if not valid:issues.append(prefix+' 금액/수량/항목 근거 미확인')
  if currency not in ('KRW','USD','EUR','JPY','CNY'):issues.append(prefix+' 통화 미확인');currency='UNKNOWN'
  # Currency must also be supported in the same cited amount text, not just a model label.
  refs=item.get('unit_price',{}).get('refs',[]);q=' '.join(r.get('quote','') for r in refs if isinstance(r,dict))
  markers={'KRW':['KRW','원','₩'],'USD':['USD','$','달러'],'EUR':['EUR','€'],'JPY':['JPY','엔','円'],'CNY':['CNY','위안']}
  if not any(m in q for m in markers.get(currency,[])):valid=False;issues.append(prefix+' 통화 근거 미확인')
  try:amount=decimal(item['unit_price']['value'])*decimal(item['quantity']['value'])
  except (KeyError,TypeError,ValueError):amount=None
  if amount is not None and valid:
   totals[currency]=totals.get(currency,Decimal(0))+amount
  else:amount=None
  if currency!='KRW':issues.append(prefix+' 실제 원화 정산금액 필요 (통화 합산 안 함)')
  rows.append({'label':label.get('value') if isinstance(label,dict) else '미확인','currency':currency,'unit_price':item.get('unit_price',{}).get('value'),'quantity':item.get('quantity',{}).get('value'),'amount':str(amount) if amount is not None else None,'evidence_valid':valid})
 if not rows:issues.append('예산 항목 없음')
 if profile=='uirp' or plan.get('requires_signature',True) is not False:issues.append('서명/승인 확인 필요 (자동 서명 안 함)')
 issues.extend('추가 확인: '+str(x)[:200] for x in plan.get('missing',[])[:30])
 field_validity={k:evidence(f,sources,numeric=k=='people') for k,f in fields.items()}
 if profile=='uirp' and not field_validity.get('activity'):
  field_validity['period']=False;issues.append('실제 참가 활동과 기간 확인 필요 (신청 접수기간과 구분)')
 return {'field_validity':field_validity,'profile':profile,'state':'ready' if not issues else 'needs_information','issues':list(dict.fromkeys(issues)),'rows':rows,'totals':{c:str(n) for c,n in totals.items()},'fields':fields}

def value(a,key):
 f=a['fields'].get(key,{})
 return str(f.get('value') or '미확인') if a.get('field_validity',{}).get(key) else '미확인'
def lines(a):
 out=['예산서 / 지원요청서', '상태: '+('검산 완료' if a['state']=='ready' else '초안 · 미확인 사항 있음')]
 for k in REQUIRED[a['profile']]:out.append(LABELS.get(k,k)+': '+value(a,k))
 out+=['예산 내역 (단가 × 수량)', '항목 | 통화 | 단가 | 수량 | 금액']
 out+=[' | '.join(str(r.get(k) if r.get(k) is not None else '미확인') for k in ['label','currency','unit_price','quantity','amount']) for r in a['rows']]
 out+=['합계 '+c+': '+v for c,v in a['totals'].items()]
 if a['issues']:out+=['확인할 사항']+a['issues']
 return out

def cell_text(cell,text):
 # Preserve cell/paragraph formatting and table geometry, including merged cells.
 p=cell.paragraphs[0]
 for child in list(p._p):
  if child.tag.endswith('}r'):p._p.remove(child)
 p.add_run(text)
 for extra in list(cell.paragraphs)[1:]:cell._tc.remove(extra._p)

def render_uirp_template(path,a):
 d=Document(path)
 if len(d.tables)!=6 or d.tables[4].cell(0,0).text!='번호' or '프로그램' not in d.tables[1].cell(0,0).text:raise ValueError('UIRP template layout changed')
 if len(a['rows'])>6:raise ValueError('Official UIRP form supports 6 expense rows')
 for ti,r,c,k in [(1,0,1,'program'),(1,0,4,'team'),(1,1,1,'research_topic'),(1,2,2,'advisor'),(1,2,4,'advisor_department'),(2,0,1,'activity'),(2,1,1,'location'),(2,1,3,'period'),(2,2,3,'people'),(3,1,0,'purpose'),(5,0,1,'date')]:cell_text(d.tables[ti].cell(r,c),value(a,k))
 total=a['totals'].get('KRW','미확인');cell_text(d.tables[2].cell(2,1),'₩ '+total)
 for i in range(6):
  vals=[str(i+1),'','','','','']
  if i<len(a['rows']):
   x=a['rows'][i];vals=[str(i+1),x['label'],x['label'],str(x['unit_price'] or '미확인'),str(x['quantity'] or '미확인'),str(x['amount'] or '미확인')]
   if x['currency']!='KRW':vals[3:]=['미확인 (원화 정산 필요)',str(x['quantity'] or '미확인'),'미확인']
  for c,v in enumerate(vals):cell_text(d.tables[4].cell(i+1,c),v)
 # All these cells are merged in the official source.
 cell_text(d.tables[4].cell(7,2),total+' 원')
 if a['state']!='ready':d.add_paragraph('초안 · 제출 전 확인 필요\n'+'\n'.join(a['issues']))
 return d

def render(plan,sources,profile,out,template=None):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);out.chmod(0o700)
 a=audit(plan,sources,profile);text=lines(a)
 d=render_uirp_template(template,a) if template and profile=='uirp' else Document()
 if not(template and profile=='uirp'):
  d.add_heading(text[0],0)
  for s in text[1:]:d.add_paragraph(s)
 for st in ['Normal']:
  d.styles[st].font.name='맑은 고딕';d.styles[st].font.size=Pt(10)
 # Sources outside the official table avoid inventing a signature or modifying fixed labels.
 d.add_paragraph().add_run('작성 근거').bold=True
 for ident,src in sources.items():d.add_paragraph(ident+' · '+src.get('title','')+'\n'+src.get('url',''))
 docx=out/'budget.docx';d.save(docx)
 from hwpx import HwpxDocument
 h=HwpxDocument.new()
 for s in text:h.add_paragraph(s)
 h.add_paragraph('작성 근거')
 for ident,src in sources.items():h.add_paragraph(ident+' · '+src.get('title','')+' '+src.get('url',''))
 h.save_to_path(out/'budget.hwpx')
 # Structural/text round-trip and independently computed arithmetic; not a visual rendering claim.
 for p in [docx,out/'budget.hwpx']:
  rt=read_text(p)
  for currency,total in a['totals'].items():
   if total not in rt:raise ValueError('Rendered budget total missing')
 (out/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
 (out/'audit.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
 (out/'preview.txt').write_text('\n'.join(text)+'\n')
 files=[]
 for name in ['budget.docx','budget.hwpx','audit.json','preview.txt']:
  p=out/name;files.append({'name':name,'sha256':digest(p),'size':p.stat().st_size})
 manifest={'state':a['state'],'issues':a['issues'],'totals':a['totals'],'files':files,'input_hash':hashlib.sha256(json.dumps({'plan':plan,'sources':sources},sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'template_sha256':digest(template) if template else None}
 (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');return manifest
