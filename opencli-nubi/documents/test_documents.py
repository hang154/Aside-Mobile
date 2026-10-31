import copy,json,tempfile,unittest
from pathlib import Path
from documents.engine import audit,render,read_text
from documents.graph import Graph
from documents.pipeline import run,MODEL

def fact(v,q=None):return {'value':v,'refs':[{'source_id':'user','quote':q or str(v)}]}
def fixture():
 s={'user':{'title':'검증 지시','text':'홍길동 연구 예산 2026-11-01 2026년 11월 행사 참가비 10000원 수량 2','url':''}}
 p={'fields':{k:fact(v) for k,v in {'applicant':'홍길동','purpose':'연구 예산','period':'2026년 11월','date':'2026-11-01'}.items()},'items':[{'label':fact('행사 참가비'),'currency':'KRW','unit_price':fact('10000','10000원'),'quantity':fact('2','수량 2')}],'missing':[],'requires_signature':False}
 return p,s
class Documents(unittest.TestCase):
 def test_exact_decimal_sum(self):
  p,s=fixture();a=audit(p,s,'general');self.assertEqual(a['state'],'ready');self.assertEqual(a['totals'],{'KRW':'20000'})
 def test_invented_amount(self):
  p,s=fixture();p['items'][0]['unit_price']['value']='9000';a=audit(p,s,'general');self.assertEqual(a['state'],'needs_information');self.assertEqual(a['totals'],{})
 def test_bare_model_prices_rejected(self):
  p,s=fixture();p['items'][0]['unit_price']='10000'
  with self.assertRaisesRegex(ValueError,'fact'):audit(p,s,'general')
 def test_non_object_references(self):
  p,s=fixture();p['fields']['applicant']['refs']=['mail']
  self.assertEqual(audit(p,s,'general')['state'],'needs_information')
 def test_missing_quote(self):
  p,s=fixture();p['fields']['applicant']['refs'][0]['quote']='없는 이름';self.assertNotEqual(audit(p,s,'general')['state'],'ready')
 def test_currency_not_combined(self):
  p,s=fixture();s['user']['text']+=' USD 220';x=copy.deepcopy(p['items'][0]);x['currency']='USD';x['unit_price']=fact('220','USD 220');p['items'].append(x);a=audit(p,s,'general');self.assertEqual(a['totals'],{'KRW':'20000','USD':'440'});self.assertNotEqual(a['state'],'ready')
 def test_signature_not_fabricated(self):
  p,s=fixture();p['requires_signature']=True;self.assertNotEqual(audit(p,s,'general')['state'],'ready')
 def test_account_mismatch(self):
  p,s=fixture();s['user']['text']+=' 은행 123-456 999-888'
  for k,v in {'registered_bank':'은행','application_bank':'은행','registered_account':'123-456','application_account':'999-888'}.items():p['fields'][k]=fact(v)
  self.assertTrue(any('불일치' in v for v in audit(p,s,'lseries')['issues']))
 def test_roundtrip_docx_hwpx(self):
  p,s=fixture()
  with tempfile.TemporaryDirectory() as d:
   m=render(p,s,'general',d);self.assertEqual(m['state'],'ready')
   for ext in ('docx','hwpx'):
    txt=read_text(Path(d)/('budget.'+ext));self.assertIn('20000',txt);self.assertIn('홍길동',txt)
 def test_graph_upload_verified(self):
  calls=[]
  def transport(method,url,data,raw):
   calls.append((method,url,data))
   if method=='GET' and 'select=' in url:return {'id':'folder','folder':{},'webUrl':'https://example.sharepoint.com/sites/Test/Docs'}
   if method=='POST':self.assertEqual(data['item']['@microsoft.graph.conflictBehavior'],'fail');return {'uploadUrl':'https://example.sharepoint.com/upload/session'}
   if method=='PUT':self.assertEqual(data,b'abc');return {'id':'item','size':3,'webUrl':'https://example.sharepoint.com/sites/Test/Docs/b.docx'}
   return b'abc'
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'budget.docx';p.write_bytes(b'abc');r=Graph({},transport).upload(p,{'drive_id':'drive','folder_id':'folder','hostname':'example.sharepoint.com'},'budget.docx');self.assertTrue(r['verified']);self.assertEqual(len(calls),4)
 def test_upload_wrong_folder_host(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'b';p.write_bytes(b'abc')
   with self.assertRaises(ValueError):Graph({},lambda *args:{'folder':{},'webUrl':'https://other.sharepoint.com'}).upload(p,{'drive_id':'drive','folder_id':'folder','hostname':'example.sharepoint.com'},'b')
 def test_upload_readback_mismatch(self):
  def transport(m,u,d,r):
   if 'select=' in u:return {'folder':{},'webUrl':'https://example.sharepoint.com'}
   if m=='POST':return {'uploadUrl':'https://example.sharepoint.com/session'}
   if m=='PUT':return {'id':'item','size':3}
   return b'bad'
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'b';p.write_bytes(b'abc')
   with self.assertRaises(RuntimeError):Graph({},transport).upload(p,{'drive_id':'drive','folder_id':'folder','hostname':'example.sharepoint.com'},'b')
 def pipeline_fixture(self,no_upload=False):
  plan,sources=fixture()
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'sources.json').write_text(json.dumps({'sources':{'mail':{'title':'공식 안내','text':'연구 예산','url':''}}}));(p/'config.json').write_text(json.dumps({'profiles':{'general':{'source_manifest':str(p/'sources.json'),'allow_upload':no_upload,'target':{'drive_id':'x'} if no_upload else None}}}))
   r=run(sources['user']['text']+(' 업로드하지 마' if no_upload else ''),'general',p/'config.json',p/'job',planner=lambda *a:(plan,MODEL));self.assertEqual(r['state'],'draft_only' if no_upload else 'needs_destination');self.assertTrue((p/'job/artifacts/budget.docx').exists())
 def test_single_command_pipeline(self):self.pipeline_fixture()
 def test_no_upload_directive(self):self.pipeline_fixture(True)
if __name__=='__main__':unittest.main()
