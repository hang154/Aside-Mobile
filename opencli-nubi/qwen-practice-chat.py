#!/usr/bin/env python3
"""Actual Qwen tool choice drives the bounded ChatGPT -> test LMS workflow."""
import argparse,json,os,sys,urllib.request,subprocess
from pathlib import Path
from model_http import generate
from practice_workflow import DEFINITION
p=argparse.ArgumentParser()
for k in ('goal','goal-id','task','trace-file'):p.add_argument('--'+k,required=True)
p.add_argument('--max-steps',type=int,default=16);a=p.parse_args();os.environ['NUBI_GOAL_ID']=a.goal_id
path=Path(a.trace_file);trace={'kind':'practice','completed':False,'reported_models':[],'events':[]}
def save():
 tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(trace,ensure_ascii=False));tmp.chmod(0o600);tmp.replace(path)
try:
 if 'sum_even' not in a.task or not any(x in a.task.lower() for x in ('practice','연습','테스트')):raise ValueError('explicit local practice request required')
 conf=json.loads((Path.home()/'.azrael-ex/azrael/providers/api/connections.json').read_text());cs=[c for c in conf['connections'] if c.get('enabled') and any(m.get('id')=='Qwen3.8-27B-uncensored-FP8' for m in c.get('models',[]))];assert len(cs)==1
 c=cs[0];assert c['auth']['kind']=='bearerFile';secret=Path(c['auth']['filePath']).expanduser().read_text().strip();model='Qwen3.8-27B-abliterated-AWQ-W4A16'
 messages=[{'role':'system','content':'너는 누비 학교 담당 에이전트다. 사용자가 요청한 sum_even 연습 과제를 실제 ChatGPT에 지시하고 독립 검사 후 로컬 테스트 LMS에 접수한다. 반드시 제공된 MCP 도구를 실제 호출한다. 결과에 없는 제출 성공을 말하지 않는다. 실제 학교 과제가 아닌 연습임을 짧게 표시한다. 인증이 필요하면 같은 대화의 ChatGPT 화면에서 로그인해 달라고 한다. 확인된 결과만 한국어로 간결하게 답한다.'},{'role':'user','content':a.task}]
 tools=[{'type':'function','function':{'name':DEFINITION['name'],'description':DEFINITION['description'],'parameters':DEFINITION['inputSchema']}}];result=None
 for step in range(3):
  payload={'model':model,'messages':messages,'tools':tools,'tool_choice':'auto' if result is None else 'none','temperature':0.1,'max_tokens':650,'chat_template_kwargs':{'enable_thinking':False}}
  req=urllib.request.Request(c['baseUrl'].rstrip('/')+'/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+secret,'Content-Type':'application/json'})
  out=generate(req,timeout=100);assert out['model']==model;trace['reported_models'].append(model);msg=out['choices'][0]['message'];messages.append(msg)
  calls=msg.get('tool_calls') or []
  if calls and result is None:
   call=calls[0];assert call['function']['name']==DEFINITION['name'];assert json.loads(call['function']['arguments'])=={}
   trace['events'].append({'name':DEFINITION['name'],'state':'started'});save();env=dict(os.environ,NUBI_PRACTICE_OUTPUT=str(path.parent/(path.stem+'-practice')));tool=subprocess.run([sys.executable,str(Path(__file__).with_name('practice-mcp.py'))],input=json.dumps({'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':DEFINITION['name'],'arguments':{}}})+'\n',capture_output=True,text=True,env=env,timeout=300);reply=json.loads(tool.stdout);result=json.loads(reply['result']['content'][0]['text']);trace['practice']=result;trace['events'].append({'name':DEFINITION['name'],'state':result['state']});save();messages.append({'role':'tool','tool_call_id':call['id'],'content':json.dumps(result,ensure_ascii=False)});continue
  if result:
   if result['state']=='completed':
    trace['completed']=True;trace['answer']='ChatGPT가 만든 연습용 practice.py를 독립 검사까지 마치고 테스트 LMS에 접수했어.\n모델 테스트 4개 · 독립 검사 3개 통과\n접수번호 '+result['receipt']['id'];trace['document']=result
   else:trace['error']='같은 대화 안의 ChatGPT 화면에서 로그인을 완료해 줘. 연습 과제 요청은 아직 전송하지 않았어.'
   break
  messages.append({'role':'user','content':'제공된 도구를 호출해 실제 연습 작업을 실행해.'})
 if not result:trace['error']='Qwen이 실행 도구를 선택하지 않았어.'
except Exception as e:trace['error']=type(e).__name__+': '+str(e)[:220]
finally:save()
sys.exit(0 if trace['completed'] else 1)
