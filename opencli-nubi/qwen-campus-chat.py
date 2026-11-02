#!/usr/bin/env python3
"""Adapt the campus Qwen runner to the existing native-chat job contract."""
import argparse,json,os,signal,subprocess,sys,tempfile,time
from pathlib import Path
from campus_runtime import current_browser

p=argparse.ArgumentParser();p.add_argument('--goal',required=True);p.add_argument('--goal-id',required=True);p.add_argument('--task',required=True);p.add_argument('--max-steps',type=int,default=16);p.add_argument('--trace-file',required=True);a=p.parse_args()
trace={'kind':'campus','completed':False,'answer':None,'reported_models':[],'events':[]}
def interrupted(_signum,_frame):raise InterruptedError('cancelled')
signal.signal(signal.SIGTERM,interrupted)
try:
 with current_browser() as runtime_env:
  proc=subprocess.run([sys.executable,str(Path(__file__).with_name('qwen-campus-agent.py')),a.task,'--max-steps',str(a.max_steps)],capture_output=True,text=True,timeout=850,env=runtime_env)
 for line in proc.stdout.splitlines():
  try:item=json.loads(line)
  except ValueError:continue
  if 'tool' in item:trace['events'].append({'type':'campus','name':item['tool'],'error':bool(item.get('error')),'detail':str(item.get('detail',''))[:300]})
  if isinstance(item.get('answer'),str):
   trace['answer']=item['answer'];trace['reported_models']=[item.get('model','')];trace['completed']=proc.returncode==0 and item.get('finish_reason')!='length' and item.get('workflow_state')=='도구 오류 없음'
 if not trace['completed']:
  problems=[e for e in trace['events'] if e.get('error') and e.get('detail')]
  priority=next((e['detail'] for e in problems if '본문이 이미지로만' in e['detail']),None)
  if not priority:priority=next((e['detail'] for e in problems if e.get('name') in ('nubi_outlook_web_draft','nubi_campus_mail_draft')),None)
  trace['error']=trace.get('answer') or priority or '요청을 완료했는지 확인하지 못했어. 연결과 실행 결과를 확인해줘.'
except Exception:
 trace['error']='Qwen 또는 캠퍼스 연결을 확인하지 못했어. 임시보관함과 실행 결과를 먼저 확인해줘.'
target=Path(a.trace_file);target.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
fd,temp=tempfile.mkstemp(prefix='.campus-',dir=str(target.parent));os.fchmod(fd,0o600)
try:
 with os.fdopen(fd,'w') as f:json.dump(trace,f,ensure_ascii=False)
 os.replace(temp,target)
finally:
 if os.path.exists(temp):os.unlink(temp)
sys.exit(0 if trace['completed'] else 1)
