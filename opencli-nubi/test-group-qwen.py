from pathlib import Path
import sys,tempfile,uuid,time,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from nubi_group_qwen import GroupQwen,MODEL
with tempfile.TemporaryDirectory() as d:
 calls=[]
 def mock(messages,json_mode=False):
  calls.append(messages)
  return (json.dumps({'agents':['love','grades'],'intro':'같이 해볼게'},ensure_ascii=False) if json_mode else '담당 답변 내용'),MODEL
 q=GroupQwen(d,mock);b={'request_id':str(uuid.uuid4()),'device_session':str(uuid.uuid4()),'text':'연애와 학교','history':[]};x=q.submit(b);y=q.submit(b);assert x['job_id']==y['job_id']
 while q.status(x['job_id'],b['device_session'])['state']=='running':time.sleep(.01)
 result=q.status(x['job_id'],b['device_session']);assert result['state']=='completed' and len(calls)==4 and len(result['messages'])==4
 try:q.status(x['job_id'],str(uuid.uuid4()));raise AssertionError('cross-session')
 except ValueError:pass
 try:q.submit(dict(b,text='다른 내용'));raise AssertionError('conflict')
 except ValueError:pass
 assert '담당 답변 내용' in calls[-1][-1]['content']
 print('PASS deduplication, ownership, sequential collaborator context and synthesis')
# Actual configured endpoint, no tool execution; explicitly opt in.
if '--live' not in sys.argv:raise SystemExit(0)
q=GroupQwen(Path(__import__('os').environ.get('NUBI_GROUP_TEST_DIR',str(Path.home()/'.local/state/nubi-group-test'))) / 'private-jobs');session=str(uuid.uuid4());tests=[('love','썸 타는 친구에게 시험 끝나고 커피 마시자고 할 짧고 자연스러운 문자 초안 두 개만 써줘.'),('grades','블랙보드 연결이 안 돼. 포털 로그인을 재사용할 때 무엇을 확인해야 해? 연결했다고 말하지 말고 확인 순서만 알려줘.'),('mixed','시험 끝나고 애인과 여행 가고 싶어. 공부 마무리, 데이트, KTX 이동, 예산을 각 담당이 나눠서 계획해줘. 실제 조회 없이 준비 계획만.'),('fitness-career','운동 루틴을 유지하면서 취업 면접을 준비하는 하루 계획을 건강이와 든든이가 같이 짜줘.')]
rows=[]
for case,text in tests:
 x=q.submit({'request_id':str(uuid.uuid4()),'device_session':session,'text':text,'history':[]});start=time.monotonic()
 while True:
  x=q.status(x['job_id'],session)
  if x['state']!='running':break
  if time.monotonic()-start>500:raise TimeoutError(case)
  time.sleep(1)
 rows.append({'case':case,**x});(Path(__import__('os').environ.get('NUBI_GROUP_TEST_DIR',str(Path.home()/'.local/state/nubi-group-test'))) / 'model-responses.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print(case,x['state'],[m['role'] for m in x['messages']],flush=True)
 assert x['state']=='completed',x
 assert x['reported_models'] and all(m==MODEL for m in x['reported_models'])
 if case=='mixed':assert len(set(m['role'] for m in x['messages'])-{'nubi'})>=3
print('PASS actual Qwen model responses across four scenarios')
