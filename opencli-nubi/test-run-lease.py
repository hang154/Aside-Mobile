"""Isolated real TLS relay + fake subprocess: job/request/session envelopes and cancellation."""
import concurrent.futures,json,os,secrets,shutil,socket,ssl,subprocess,sys,tempfile,time,urllib.request,urllib.error,uuid
from pathlib import Path
source=Path(__file__).parent
with tempfile.TemporaryDirectory(prefix='nubi-lease-') as temporary:
 root=Path(temporary)
 for name in ['nubi-goal-relay.py','nubi-chat-jobs.py','nubi-friends.py','nubi-friend-draft.py']:shutil.copy(source/name,root/name)
 (root/'qwen-goal-agent.py').write_text('import time;time.sleep(45)\n')
 token=secrets.token_urlsafe(32);(root/'token').write_text(token)
 subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(root/'key'),'--out',str(root/'cert'),'-days','1','-subj','/CN=localhost'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
 server=subprocess.Popen([sys.executable,str(root/'nubi-goal-relay.py'),'--host','127.0.0.1','--port',str(port),'--cert',str(root/'cert'),'--key',str(root/'key'),'--token-file',str(root/'token'),'--chat-dir',str(root/'jobs')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 context=ssl.create_default_context(cafile=str(root/'cert'));context.check_hostname=False
 def post(path,data,bearer=token):
  request=urllib.request.Request(f'https://127.0.0.1:{port}'+path,data=json.dumps(data).encode(),headers={'Authorization':'Bearer '+bearer,'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(request,context=context,timeout=20) as response:return response.status,json.load(response)
  except urllib.error.HTTPError as e:return e.code,json.load(e)
 n=0
 try:
  for attempt in range(40):
   try:status,_=post('/get-result',{}) ;break
   except (OSError,urllib.error.URLError):time.sleep(.1)
  assert post('/command',{'op':'goal_open'},'wrong')[0]==401;n+=1
  session=str(uuid.uuid4());request=str(uuid.uuid4());goal=str(uuid.uuid4())
  status,job=post('/chat-submit',{'device_session':session,'goal_id':goal,'request_id':request,'character':'travel','task':'공개 여행 자료 탐색'})
  assert status==200 and job['request_id']==request;n+=1
  command={'op':'goal_open','character':'travel','_session':session,'_job':job['job_id'],'_request':request}
  assert post('/command',dict(command,_request='foreign'))[0]==409;n+=1
  assert post('/command',dict(command,_session=str(uuid.uuid4())))[0]==409;n+=1
  assert post('/command',command)[0]==200;n+=1
  status,polled=post('/poll',{'device_session':session});envelope=polled['command']
  assert envelope['job_id']==job['job_id'] and envelope['request_id']==request and envelope['device_session']==session and '_job' not in envelope;n+=1
  owner1=str(uuid.uuid4());owner2=str(uuid.uuid4())
  assert post('/claim',{'device_session':session,'poll_owner':owner1,'poll_epoch':1})[0]==200;n+=1
  with concurrent.futures.ThreadPoolExecutor() as pool:
   old=pool.submit(post,'/poll',{'device_session':session,'poll_owner':owner1})
   time.sleep(.2)
   assert post('/claim',{'device_session':session,'poll_owner':owner2,'poll_epoch':2})[0]==200;n+=1
   assert post('/claim',{'device_session':session,'poll_owner':owner1,'poll_epoch':1})[0]==409;n+=1
   assert post('/command',command)[0]==200
   assert old.result()[1]['command'] is None;n+=1
  assert post('/poll',{'device_session':session,'poll_owner':owner2})[1]['command']['job_id']==job['job_id'];n+=1
  assert post('/poll',{'device_session':session,'poll_owner':owner1})[0]==409;n+=1
  assert post('/chat-cancel' ,{'job_id':job['job_id']})[1]['state']=='cancelled';n+=1
  assert post('/command',command)[0]==409;n+=1
  print('PASS',n,'real TLS relay lease checks (fake model runner; no tablet)')
 finally:
  server.terminate();server.wait(timeout=10)
