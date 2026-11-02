"""Authenticated relay-owned chat jobs. One real browser, one runner at a time."""
import json, os, re, subprocess, sys, threading, time, uuid
from pathlib import Path

class ChatJobs:
 def __init__(self, directory, env):
  self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=True);self.directory.chmod(0o700)
  self.env=env;self.jobs={};self.lock=threading.RLock();self.active=None
 def submit(self, body):
  required={'goal_id','character','task','request_id','device_session'}
  if set(body)!=required or any(not isinstance(body[k],str) for k in required) or not isinstance(body['task'],str) or not 1<=len(body['task'].strip())<=2000 or body['character'] not in ('fitness','love','grades','home','career','travel') or not re.fullmatch(r'[0-9a-f-]{36}',body['goal_id']) or not re.fullmatch(r'[0-9a-f-]{36}',body['request_id']) or not re.fullmatch(r'[0-9a-f-]{36}',body['device_session']):raise ValueError('Invalid chat request')
  with self.lock:
   for j in self.jobs.values():
    if j['request']==body:
     return self.status(j['id'])
    if j['request']['request_id']==body['request_id']:raise ValueError('Request ID conflict')
   if self.active and self.jobs[self.active]['process'].poll() is None:raise RuntimeError('Another goal is browsing; stop it first')
   if len(self.jobs)>=100:raise RuntimeError('Session job limit reached; restart relay')
   ident=uuid.uuid4().hex;trace=self.directory/(ident+'.json');log=(self.directory/(ident+'.log')).open('w')
   current=body['task'].split('현재 사용자 지시:',1)[-1]
   transit=bool(re.search(r'KTX|코레일|버스|지하철|대중교통|기차.{0,15}(시간|운행|조회)|이동.{0,15}(경로|소요)',current,re.I))
   campus=not transit and (current.startswith('[학교 실행]') or bool(re.search(r'UNIST|유니스트|학사|장학|학교\s*(공지|메일|포털)|수강|예비수강|COOP|인턴십|Outlook|아웃룩',current,re.I)))
   document=bool(re.search(r'예산서|지원요청서|연구지원금|문서\s*작성|서류\s*작성|docx|hwpx|sharepoint|uirp|l시리즈',current,re.I))
   interpreter=os.environ.get('NUBI_DOCUMENT_PYTHON',str(Path.home()/'.local/share/nubi-documents/venv/bin/python')) if document and not campus and not transit else sys.executable
   runner='qwen-transit-chat.py' if transit else 'qwen-campus-chat.py' if campus else 'qwen-document-agent.py' if document else 'qwen-goal-agent.py'
   cmd=[interpreter,str(Path(__file__).with_name(runner)),'--goal',body['character'],'--goal-id',body['goal_id'],'--task',current.strip() if campus else body['task'],'--max-steps','16','--trace-file',str(trace)]
   try:p=subprocess.Popen(cmd,stdout=log,stderr=log,env=dict(self.env,NUBI_GOAL_DEVICE_SESSION=body['device_session'],NUBI_GOAL_JOB_ID=ident,NUBI_GOAL_REQUEST_ID=body['request_id']),start_new_session=True)
   finally:log.close()
   self.jobs[ident]={'id':ident,'request':dict(body),'process':p,'trace':trace,'cancelled':False,'started':time.monotonic()};self.active=ident
   return self.status(ident)
 def status(self, ident):
  with self.lock:
   j=self.jobs.get(ident)
   if j is None:raise ValueError('Unknown chat job')
   code=j['process'].poll()
   if code is None and time.monotonic()-j['started']>900:
    self._stop(j);j['cancelled']=True;code=j['process'].poll()
   trace={}
   try:trace=json.loads(j['trace'].read_text())
   except (OSError,ValueError):pass
   if trace.get('expires_at',0)>0 and time.time()*1000>=trace['expires_at']:
    trace['completed']=False;trace['answer']=None;trace['error']='경로 결과의 보관 시간이 지났어요. 새로 조회해 주세요.'
   progress=[];items=[];source_page=None
   try:progress=json.loads(j['trace'].with_suffix('').joinpath('progress.json').read_text())
   except (OSError,ValueError):pass
   for e in trace.get('events',[]):
    if e.get('type') in ('campus','transit'):progress.append(('확인 필요 · ' if e.get('error') else '실행 · ')+str(e.get('name','')))
    if e.get('type')=='model':
     for c in e.get('calls',[]):
      try:a=json.loads(c.get('arguments','{}'))
      except ValueError:a={}
      if c.get('name')=='nubi_goal_search':progress.append('검색 · '+str(a.get('provider',''))+' · '+str(a.get('query','')))
      elif c.get('name')=='nubi_goal_select':progress.append('선택한 원문 열기')
    if e.get('type')=='tool':
     try:v=json.loads(e['result']['content'][0]['text'])
     except (KeyError,ValueError,IndexError,TypeError):continue
     if v.get('state')=='results_observed':items=v.get('items',[])[:8];progress.append('실제 선택지 '+str(len(items))+'개 읽음')
     if v.get('state')=='source_observed':source_page=v.get('page');progress.append('원문 제목 확인')
     if v.get('state')=='not_ready':progress.append('페이지 준비 중')
   state='cancelled' if j['cancelled'] else 'running' if code is None else 'completed' if code==0 and trace.get('completed') else 'failed'
   result={'job_id':ident,'request_id':j['request']['request_id'],'goal_id':j['request']['goal_id'],'character':j['request']['character'],'state':state,'progress':progress[-12:],'answer':trace.get('answer') if state=='completed' else None,'error':trace.get('error','모델 응답 또는 연결을 확인해줘.') if state=='failed' else None,'items':items,'source_page':source_page,'reported_models':sorted(set(trace.get('reported_models',[])))}
   if trace.get('expires_at'):result['expires_at']=trace['expires_at']
   if trace.get('kind')=='document':
    result['kind']='document';result['document']=trace.get('document',{});result['document'].pop('artifacts',None)
   if result['error'] is None:result.pop('error')
   return result
 def _stop(self,j):
  import signal
  if j['process'].poll() is None:
   os.killpg(j['process'].pid,signal.SIGTERM)
   try:j['process'].wait(timeout=3)
   except subprocess.TimeoutExpired:os.killpg(j['process'].pid,signal.SIGKILL);j['process'].wait(timeout=3)
 def cancel(self, ident):
  with self.lock:
   j=self.jobs.get(ident)
   if not j:raise ValueError('Unknown chat job')
   if j['process'].poll() is None:self._stop(j);j['cancelled']=True
   return self.status(ident)
 def close(self):
  with self.lock:
   for j in self.jobs.values():self._stop(j)

 def artifact(self,ident,goal_id,name):
  with self.lock:
   j=self.jobs.get(ident)
   if not j or j['request']['goal_id']!=goal_id or name not in ('budget.docx','budget.hwpx','audit.json','preview.txt'):raise ValueError('Unknown goal document')
   if j['process'].poll()!=0:raise ValueError('Document job is not complete')
   trace=json.loads(j['trace'].read_text())
   if trace.get('kind')!='document' or not trace.get('completed'):raise ValueError('No document output')
   import hashlib
   expected=next((f for f in trace['document']['manifest']['files'] if f['name']==name),None)
   path=j['trace'].with_suffix('')/'artifacts'/name
   data=path.read_bytes()
   if not expected or len(data)>8*1024*1024 or hashlib.sha256(data).hexdigest()!=expected['sha256']:raise ValueError('Document hash mismatch')
   return data
