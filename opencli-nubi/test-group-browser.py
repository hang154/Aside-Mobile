import tempfile,uuid,json,time,threading
from nubi_group_qwen import GroupQwen,MODEL
with tempfile.TemporaryDirectory() as d:
 def completion(messages,json_mode=False):return json.dumps({'agents':['fitness'],'intro':'찾아볼게요.','action':'search'},ensure_ascii=False),MODEL
 def browser(j,role,progress,cancel):
  assert role=='fitness';assert j['goals'][role];progress('nubi_goal_observe')
  return {'state':'completed','answer':'실제로 관측한 후보','sources':['https://www.youtube.com/watch?v=fixture'],'items':[{'title':'fixture','url':'https://www.youtube.com/watch?v=fixture'}],'reported_models':[MODEL]}
 q=GroupQwen(d,completion,browser);body={'request_id':str(uuid.uuid4()),'device_session':str(uuid.uuid4()),'text':'운동 영상 찾아줘','history':[],'goals':{'fitness':str(uuid.uuid4())}}
 x=q.submit(body)
 while q.status(x['job_id'],body['device_session'])['state']=='running':time.sleep(.01)
 r=q.status(x['job_id'],body['device_session']);assert r['state']=='completed' and r['execution']['sources'] and r['progress'];assert not q.permits(x['job_id'],body['request_id'],body['device_session'],body['goals']['fitness'])
 body=dict(body,request_id=str(uuid.uuid4()));q.browser=lambda *args:{'state':'failed','error':'로그인 필요'};x=q.submit(body)
 while q.status(x['job_id'],body['device_session'])['state']=='running':time.sleep(.01)
 r=q.status(x['job_id'],body['device_session']);assert r['state']=='failed' and '로그인 필요' in r['error']
 entered=threading.Event();release=threading.Event()
 def blocked(*args):entered.set();release.wait(2);return json.dumps({'agents':['fitness'],'intro':'안내','action':'search'}),MODEL
 q.completion=blocked;body=dict(body,request_id=str(uuid.uuid4()));x=q.submit(body);entered.wait(2);assert q.cancel(x['job_id'],body['device_session'])['state']=='cancelled';release.set();time.sleep(.05);assert q.status(x['job_id'],body['device_session'])['state']=='cancelled'
 print('PASS research delegation, observed-source results, visible execution failure, cancellation and lease expiry (fixtures)')
