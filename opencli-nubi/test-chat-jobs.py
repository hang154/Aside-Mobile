"""Real subprocess scheduling with fake model runner; no live model/device calls."""
import importlib.util,json,os,shutil,tempfile,time,uuid
from pathlib import Path
with tempfile.TemporaryDirectory() as d:
 root=Path(d);source=Path(__file__).with_name('nubi-chat-jobs.py');shutil.copy(source,root/source.name)
 (root/'qwen-goal-agent.py').write_text('''import argparse,json,time
p=argparse.ArgumentParser()
for k in ['goal','goal-id','task','max-steps','trace-file']:p.add_argument('--'+k)
a=p.parse_args();time.sleep(0.3)
open(a.trace_file,'w').write(json.dumps({'completed':True,'answer':a.task,'reported_models':['Qwen3.8-27B-abliterated-AWQ-W4A16'],'events':[]}))
if a.task=='wait':time.sleep(60)
''')
 shutil.copy(root/'qwen-goal-agent.py',root/'qwen-campus-chat.py')
 shutil.copy(root/'qwen-goal-agent.py',root/'qwen-transit-chat.py')
 spec=importlib.util.spec_from_file_location('chatjobs',root/source.name);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);jobs=m.ChatJobs(root/'traces',dict(os.environ));n=0
 def body(task):return {'goal_id':str(uuid.uuid4()),'character':'fitness','task':task,'request_id':str(uuid.uuid4()),'device_session':str(uuid.uuid4())}
 a=body('wait');j=jobs.submit(a);assert 'error' not in j and j['state']=='running';n+=1
 assert jobs.submit(a)['job_id']==j['job_id'];n+=1
 try:jobs.submit(body('other'))
 except RuntimeError:n+=1
 else:raise AssertionError('parallel browser accepted')
 try:jobs.submit(dict(a,task='conflict'))
 except ValueError:n+=1
 else:raise AssertionError('request ID reused')
 assert jobs.cancel(j['job_id'])['state']=='cancelled';n+=1
 b=body('follow user instruction');j=jobs.submit(b)
 for _ in range(30):
  r=jobs.status(j['job_id'])
  if r['state']!='running':break
  time.sleep(.1)
 assert r['state']=='completed' and r['answer']==b['task'] and r['goal_id']==b['goal_id'];n+=1
 for invalid in [dict(b,goal_id=None),dict(b,character='other'),dict(b,task=''),dict(b,task='x'*2001),dict(b,extra=True)]:
  try:jobs.submit(invalid)
  except ValueError:n+=1
  else:raise AssertionError('invalid request accepted')
 try:jobs.status('foreign')
 except ValueError:n+=1
 else:raise AssertionError('foreign job accepted')
 assert r['request_id']==b['request_id'];n+=1
 for character in ['career','travel']:
  request=dict(body('wait'),character=character);job=jobs.submit(request);assert job['character']==character;n+=1;jobs.cancel(job['job_id'])
 for task in ['[학교 실행]\n포털 게시판 공지 목록 조회','[학교 실행]\n'+('조건 확인 '*150),'장학 공지 찾아줘']:
  request=body(task);job=jobs.submit(request);assert jobs.jobs[job['job_id']]['process'].args[1].endswith('qwen-campus-chat.py');n+=1
  for _ in range(30):
   result=jobs.status(job['job_id'])
   if result['state']!='running':break
   time.sleep(.1)
  assert result['state']=='completed' and result['answer']==task.strip();n+=1
 for task in ['UNIST 버스 언제 와?', '내일 KTX 시간표 조회', '강남 지하철 도착', '대중교통 경로 확인']:
  request=body(task);job=jobs.submit(request);assert jobs.jobs[job['job_id']]['process'].args[1].endswith('qwen-transit-chat.py');n+=1
  for _ in range(30):
   result=jobs.status(job['job_id'])
   if result['state']!='running':break
   time.sleep(.1)
  assert result['state']=='completed' and result['answer']==task;n+=1
 trace_path=jobs.jobs[job['job_id']]['trace'];trace_path.write_text(json.dumps({'completed':True,'answer':'old route','expires_at':1,'events':[]}));expired=jobs.status(job['job_id']);assert expired['state']=='failed' and expired['answer'] is None;n+=1;assert expired['expires_at']==1;n+=1
 jobs.close();print('PASS',n,'chat scheduling/idempotency/cancel/scope/validation checks (fake model runner)')
