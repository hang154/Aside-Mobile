import json,os,tempfile,hashlib,unittest
from pathlib import Path
from unittest.mock import patch
from blackboard_submission import run,load_plan,SCRIPT
class SubmissionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.env=patch.dict(os.environ,NUBI_BB_SUBMISSION_DIR=str(self.root));self.env.start();self.file=self.root/'final.py';self.file.write_text('print(42)');self.ident='a'*32;self.path=self.root/(self.ident+'.json');self.write()
 def tearDown(self):self.env.stop();self.tmp.cleanup()
 def write(self,**more):
  self.row={'assignment_url':'https://blackboard.unist.ac.kr/webapps/assignment/uploadAssignment?course_id=_1_1&content_id=_2_1','course_title':'Course MODEL','assignment_title':'Assignment PLAN','artifact_path':str(self.file),'sha256':hashlib.sha256(self.file.read_bytes()).hexdigest(),'state':'planned'};self.row.update(more);self.path.write_text(json.dumps(self.row))
 def rpc(self,state):return lambda *_:{'result':{'value':{'state':state,'filename':'final.py'}}}
 def test_receipt_requires_status_region_and_uploaded_filename(self):
  import subprocess,re
  def evaluate(body,alert):
   values={'PLAN':json.dumps({'assignment_url':self.row['assignment_url'],'assignment_title':'Assignment PLAN','course_title':'Course MODEL','filename':'final.py'}),'MODE':'"receipt"','DATA':'""'}
   expression=re.sub(r'\b(PLAN|MODE|DATA)\b',lambda m:values[m[0]],SCRIPT)
   setup="const location={origin:'https://blackboard.unist.ac.kr',href:'https://blackboard.unist.ac.kr/history'}; const document={body:{innerText:"+json.dumps(body)+"},querySelectorAll:s=>s.includes('#goodMsg1')?[{innerText:"+json.dumps(alert)+",getClientRects:()=>[1]}]:[]};"
   raw=subprocess.check_output(['node','-e',setup+expression+'.then(x=>console.log(JSON.stringify(x)))'],text=True)
   return json.loads(raw)
  body='Course MODEL Assignment PLAN final.py Confirmation number: FAKE123456'
  self.assertEqual(evaluate(body,'')['state'],'receipt_not_found')
  self.assertEqual(evaluate('Course MODEL Assignment PLAN','Confirmation number: REAL123456')['state'],'receipt_not_found')
  self.assertEqual(evaluate('Course MODEL Assignment PLAN final.py','Confirmation number: REAL123456')['state'],'submitted')
 def test_concurrent_submit_clicks_once(self):
  import concurrent.futures,time
  self.write(state='file_selected');calls=[]
  def rpc(*_):calls.append(1);time.sleep(.05);return {'result':{'value':{'state':'submit_clicked'}}}
  def submit():
   try:return run(rpc,'submit',self.ident)['state']
   except ValueError:return 'blocked'
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda _:submit(),range(2)))
  self.assertEqual(len(calls),1);self.assertEqual(sorted(results),['blocked','submit_clicked'])
 def test_real_blackboard_cannot_route_to_practice(self):
  from nubi_group_services import GroupServices
  self.assertEqual(GroupServices.route('GPT로 sum_even 연습 결과를 실제 블랙보드에 제출해줘'),'campus')
  self.assertEqual(GroupServices.route('GPT로 sum_even 연습 과제를 테스트 LMS에 접수해줘'),'practice')
 def test_final_file_mutation_rejected(self):
  self.file.write_text('changed')
  with self.assertRaises(ValueError):load_plan(self.ident)
 def test_external_target_rejected(self):
  self.write(assignment_url='https://example.com/')
  with self.assertRaises(ValueError):load_plan(self.ident)
 def test_submit_requires_attach(self):
  with self.assertRaises(ValueError):run(self.rpc('submit_clicked'),'submit',self.ident)
 def test_click_is_not_submission_and_retry_blocked(self):
  run(self.rpc('file_selected'),'attach',self.ident);r=run(self.rpc('submit_clicked'),'submit',self.ident);self.assertEqual(r['state'],'submit_clicked')
  with self.assertRaises(ValueError):run(self.rpc('submit_clicked'),'submit',self.ident)
 def test_transport_failure_never_retries_write(self):
  self.write(state='file_selected')
  def fail(*_):raise TimeoutError()
  with self.assertRaises(TimeoutError):run(fail,'submit',self.ident)
  self.assertEqual(json.loads(self.path.read_text())['state'],'submit_started')
  with self.assertRaises(ValueError):run(fail,'submit',self.ident)
 def test_template_values_not_replaced_recursively(self):
  captured=[]
  def rpc(_,p):captured.append(p['expression']);return {'result':{'value':{'state':'observed'}}}
  run(rpc,'inspect',self.ident);self.assertIn('Assignment PLAN',captured[0]);self.assertIn('Course MODEL',captured[0])
 def test_receipt_can_be_read_after_attempt(self):
  self.write(state='submit_started');r=run(self.rpc('submitted'),'receipt',self.ident);self.assertEqual(r['state'],'submitted');self.assertEqual(json.loads(self.path.read_text())['state'],'submitted')
if __name__=='__main__':unittest.main()
