"""Bound group-chat research to the existing read-only on-device MCP browser."""
import json,os,signal,subprocess,sys,time
from pathlib import Path
class GroupBrowser:
 def __init__(self,env):self.env=dict(env)
 def __call__(self,job,role,progress,cancel):
  root=Path(job['_directory']);trace=root/(job['job_id']+'-browser.json');log=root/(job['job_id']+'-browser.log')
  task=job['text']+'\n공개 웹의 읽기 전용 조회만 수행. 로그인·메일 발송·신청·구매·예약은 실행하지 마. 지원하지 않는 작업은 정확히 한계를 밝혀. 실시간 시간표·요금은 일반 검색으로 확인됐다고 주장하지 마.'
  env=dict(self.env,NUBI_GOAL_DEVICE_SESSION=job['device_session'],NUBI_GOAL_GROUP_ID=job['job_id'],NUBI_GOAL_REQUEST_ID=job['request_id'])
  cmd=[sys.executable,str(Path(__file__).with_name('qwen-goal-agent.py')),'--goal',role,'--goal-id',job['goals'][role],'--task',task[:2000],'--max-steps','12','--timeout','40','--trace-file',str(trace)]
  with log.open('w') as output:
   os.chmod(log,0o600);proc=subprocess.Popen(cmd,stdout=output,stderr=output,env=env,start_new_session=True);start=time.monotonic();last=''
   try:
    while proc.poll() is None:
     if cancel.is_set() or time.monotonic()-start>240:raise TimeoutError('사용자가 중지했거나 공개 탐색 240초 제한을 초과했어요.')
     try:
      data=json.loads(trace.read_text());events=data.get('events',[])
      for e in events[-3:]:
       if e.get('type')=='tool':
        label=e.get('name','')
        if label!=last:progress(label);last=label
     except (OSError,ValueError):pass
     cancel.wait(.5)
   finally:
    if proc.poll() is None:
     os.killpg(proc.pid,signal.SIGTERM)
     try:proc.wait(timeout=3)
     except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=3)
  try:data=json.loads(trace.read_text())
  except (OSError,ValueError):raise RuntimeError('탐색 실행 기록을 받지 못했어요. 앱을 화면에 열고 연결을 확인해 주세요.')
  sources=[];items=[];failures=[]
  for e in data.get('events',[]):
   if e.get('type')!='tool':continue
   try:r=json.loads(e['result']['content'][0]['text'])
   except (KeyError,TypeError,ValueError,IndexError):continue
   if e['result'].get('isError'):failures.append(str(r)[:160])
   if r.get('state')=='results_observed':
    for item in r.get('items',[]):
     if isinstance(item,dict) and item.get('url'):
      sources.append(item['url']);items.append({k:item[k] for k in ('title','url','priceText','kind') if k in item})
   if r.get('state')=='source_observed' and r.get('page',{}).get('url'):sources.append(r['page']['url'])
  sources=list(dict.fromkeys(sources))[:12]
  if proc.returncode!=0 or not data.get('completed') or not sources:
   return {'state':'failed','error':'실제 탐색을 완료하지 못했어요. '+str(data.get('error') or '관측된 결과·출처가 없어 완료로 처리하지 않았어요.')[:220],'sources':sources,'items':items[:8],'failures':failures,'reported_models':data.get('reported_models',[])}
  return {'state':'completed','answer':data['answer'],'sources':sources,'items':items[:8],'reported_models':data['reported_models'],'limits':'공개 페이지의 제목·링크·표시 가격 조회. 로그인·거래·영상 내용·최종 가격은 미검증.'}
