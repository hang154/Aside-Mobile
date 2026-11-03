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

from nubi_group_services import GroupServices
assert GroupServices.route('UNIST 울산역 방향 513번의 실제 다음 출발 시각을 조회해줘')=='transit'

# A real execution request must not be downgraded to a prompt-writing answer.
with tempfile.TemporaryDirectory() as d:
 def completion(messages,json_mode=False):return json.dumps({'agents':['grades'],'intro':'초안 설명','action':'talk'},ensure_ascii=False),MODEL
 calls=[]
 def execute(j,role,progress,cancel):
  calls.append(role);return {'state':'completed','answer':'fixture accepted','reported_models':[MODEL]}
 q=GroupQwen(d,completion,execute);b={'request_id':str(uuid.uuid4()),'device_session':str(uuid.uuid4()),'text':'GPT로 sum_even 연습 과제를 테스트 LMS까지 실행해줘. 실제 학교 제출은 하지 마.','history':[],'goals':{'grades':str(uuid.uuid4())}}
 x=q.submit(b)
 while q.status(x['job_id'],b['device_session'])['state']=='running':time.sleep(.01)
 assert calls==['grades'] and q.status(x['job_id'],b['device_session'])['state']=='completed'
 print('PASS explicit practice execution cannot become a draft-only response (fixture)')

# Keep independent specialist calls in the audit, but do not repeat identical chat bubbles.
with tempfile.TemporaryDirectory() as d:
 def completion(messages,json_mode=False):
  return (json.dumps({'agents':['grades','fitness'],'intro':'확인할게.','action':'search'}) if json_mode else '같은 실제 결과'),MODEL
 q=GroupQwen(d,completion,lambda *a:{'state':'completed','answer':'같은 실제 결과','reported_models':[MODEL]})
 b={'request_id':str(uuid.uuid4()),'device_session':str(uuid.uuid4()),'text':'학식 실제 조회','history':[],'goals':{'grades':str(uuid.uuid4()),'fitness':str(uuid.uuid4())}}
 x=q.submit(b)
 while q.status(x['job_id'],b['device_session'])['state']=='running':time.sleep(.01)
 r=q.status(x['job_id'],b['device_session']);assert r['state']=='completed'
 assert len([m for m in r['messages'] if m['actual'] and m['text']=='같은 실제 결과'])==1
 assert any(c['role']=='fitness' for c in q.jobs[x['job_id']]['calls'])
 print('PASS duplicate specialist bubble suppressed while model call audit retained (fixture)')
