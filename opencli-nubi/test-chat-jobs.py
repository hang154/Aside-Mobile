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
 jobs.close();print('PASS',n,'chat scheduling/idempotency/cancel/scope/validation checks (fake model runner)')
