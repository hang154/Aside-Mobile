"""Existing service MCP runners behind the shared friends-room contract.
Model planning remains in GroupQwen; each service runner uses the configured real Qwen.
"""
import json,os,re,signal,subprocess,sys,time
from pathlib import Path
class GroupServices:
 def __init__(self,env):self.env=dict(env)
 @staticmethod
 def route(text):
  # Real Blackboard requests must never be satisfied by the practice LMS.
  if re.search(r'블랙보드|blackboard',text,re.I) and re.search(r'제출|submit|upload',text,re.I) and not re.search(r'(블랙보드|blackboard).{0,20}(하지\s*마|금지|do not)',text,re.I):return 'campus'
  if 'sum_even' in text and re.search(r'practice|연습|테스트',text,re.I) and re.search(r'GPT|지피티',text,re.I):return 'practice'
  if re.search(r'KTX|SRT|코레일|513\s*번|버스|지하철|대중교통|택시|택시비|날씨|기온|미세먼지|대기질|관광지|항공편|항공기|비행기|여객선|선박.{0,15}(시간|운항|조회)|(기차|열차).{0,15}(시간|운행|조회|찾)|이동.{0,15}(경로|소요)',text,re.I):return 'transit'
  if re.search(r'블랙보드|blackboard|과제|강의자료|오픈북|시험|UNIST|유니스트|학식|식단|특식|밥먹어|학사|장학|학교\s*(공지|메일|포털)|수강|Outlook|아웃룩',text,re.I):return 'campus'
  if re.search(r'예산서|지원요청서|문서\s*작성|서류\s*작성|docx|hwpx|sharepoint|uirp|l시리즈',text,re.I):return 'document'
  return None
 def __call__(self,job,role,progress,cancel):
  kind=self.route(job['text'])
  if not kind:return None
  root=Path(job['_directory']);trace=root/(job['job_id']+'-service.json');log=root/(job['job_id']+'-service.log')
  runner={'transit':'qwen-transit-chat.py','campus':'qwen-campus-chat.py','document':'qwen-document-agent.py','practice':'qwen-practice-chat.py'}[kind]
  preferred=Path.home()/'.local/share/nubi-documents/venv/bin/python'
  python=str(preferred) if kind!='transit' and preferred.is_file() else sys.executable
  env=dict(self.env,NUBI_GOAL_DEVICE_SESSION=job['device_session'],NUBI_GOAL_GROUP_ID=job['job_id'],NUBI_GOAL_REQUEST_ID=job['request_id'])
  cmd=[python,str(Path(__file__).with_name(runner)),'--goal',role,'--goal-id',job['goals'][role],'--task',job['text'],'--max-steps','16','--trace-file',str(trace)]
  labels={'practice':'GPT에 연습 과제를 부탁하고 있어.','transit':'이동 시간표를 확인하고 있어.','campus':'학교 정보를 확인하고 있어.','document':'필요한 문서를 작성하고 있어.'}
  progress(labels[kind])
  with log.open('w') as f:
   os.chmod(log,0o600);proc=subprocess.Popen(cmd,stdout=f,stderr=f,env=env,start_new_session=True);start=time.monotonic();seen=0
   try:
    while proc.poll() is None:
     if cancel.is_set() or time.monotonic()-start>850:raise TimeoutError('서비스 실행이 중지됐거나 제한 시간을 초과했어요.')
     try:
      data=json.loads(trace.read_text());events=data.get('events',[])
      for e in events[seen:]:
       if e.get('name'):progress('연결 상태를 확인하고 있어.' if e.get('error') else labels[kind])
      seen=len(events)
     except (OSError,ValueError):pass
     cancel.wait(.5)
   finally:
    if proc.poll() is None:
     os.killpg(proc.pid,signal.SIGTERM)
     try:proc.wait(timeout=3)
     except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=3)
  try:data=json.loads(trace.read_text())
  except (OSError,ValueError):return {'state':'failed','error':'서비스 실행 기록을 받지 못했어요. 결과를 확인한 뒤 재시도해 주세요.'}
  success=proc.returncode==0 and data.get('completed') and data.get('answer')
  if data.get('virtual_ticket'):data.pop('rail_journey',None)
  return {'state':'completed' if success else 'failed','answer':data.get('answer') if success else None,'error':data.get('error','요청한 결과를 확인하지 못했어요.') if not success else None,'sources':[],'items':[],'reported_models':data.get('reported_models',[]),'service':kind,'taxi_estimate':data.get('taxi_estimate'),'rail_request':kind=='transit' and bool(re.search(r'KTX|SRT|코레일|기차|열차',job['text'],re.I)),'document':data.get('document'),'rail_journey':data.get('rail_journey') if success else None,'limits':''}
