#!/usr/bin/env python3
"""Drive only explicit requests from the filming APK using the real Qwen/MCP runner.
All receipts come from tool execution. Writes recipient-free draft only. No sending.
"""
import argparse,hashlib,json,os,subprocess,sys,time,urllib.request
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--once',action='store_true');a=p.parse_args()
repo=Path(__file__).resolve().parents[1];out=Path(a.output).resolve();out.mkdir(mode=0o700,parents=True,exist_ok=True)
pkg='ai.decisionos.nubi.groupchat.goals';serial='R5CX407XACF';base=['adb','-s',serial];private='files/investor-demo/';started=time.time();seen=set()
def read(name):
 r=subprocess.run(base+['exec-out','run-as',pkg,'cat',private+name],capture_output=True)
 return r.stdout if r.returncode==0 else b''
def put(name,data):
 if isinstance(data,str):data=data.encode()
 subprocess.run(base+['shell','run-as',pkg,'sh','-c',"'cat > "+private+name+".tmp && mv "+private+name+".tmp "+private+name+"'"],input=data,check=True,stdout=subprocess.DEVNULL)
def status(id,**data):put('status.json',json.dumps({'id':id,**data},ensure_ascii=False))
labels={'nubi_campus_open':'공식 학교 서비스를 열었어요','nubi_portal_board_list':'장학 게시판 목록을 읽었어요','nubi_portal_board_open':'공지 원문을 선택했어요','nubi_campus_board_search_open':'검색한 공지를 열었어요','nubi_portal_notice_detail':'공지 본문과 지원 조건을 확인했어요','nubi_outlook_web_search':'학사메일에서 공고를 찾았어요','nubi_outlook_web_read':'선택한 메일 본문을 읽었어요','nubi_local_document_draft':'신청서 DOCX 초안을 만들었어요','nubi_outlook_web_draft':'Outlook 임시저장 결과를 확인했어요'}
while True:
 try:r=json.loads(read('request.json'))
 except (ValueError,TypeError):time.sleep(1);continue
 id=r.get('id');task=r.get('task','')
 if id in seen or r.get('createdAt',0)<started*1000 or not task.strip():time.sleep(.5);continue
 seen.add(id);events=[];status(id,state='running',phase='Qwen · 실제 브라우저에 연결 중',log='')
 pid=subprocess.check_output(base+['shell','pidof',pkg],text=True).strip();port=subprocess.check_output(base+['forward','tcp:0','localabstract:webview_devtools_remote_'+pid],text=True).strip()
 try:
  ep='http://127.0.0.1:'+port
  pages=json.load(urllib.request.urlopen(ep+'/json/list'));candidates=[x for x in pages if x.get('type')=='page' and x.get('url','').startswith('https://')]
  if len(candidates)!=1:raise RuntimeError('Close other school browser windows before filming')
  env=dict(os.environ,NUBI_CDP_ENDPOINT=ep,NUBI_CDP_TARGET_ID=candidates[0]['id'])
  proc=subprocess.Popen([sys.executable,str(repo/'opencli-nubi/qwen-campus-agent.py'),task,'--max-steps','20','--timeout','90'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env)
  final=None
  with (out/(id+'.jsonl')).open('w') as trace:
   for line in proc.stdout:
    trace.write(line);trace.flush()
    try:e=json.loads(line)
    except ValueError:continue
    if e.get('tool'):
     events.append(e);tool=e['tool'];phase=labels.get(tool,'Qwen · '+tool)
     if e.get('error'):phase='확인 필요 · '+tool
     status(id,state='running',phase=phase,log='\n'.join(('✓ ' if not x.get('error') else '! ')+x['tool'] for x in events))
    if isinstance(e.get('answer'),str):final=e
  err=proc.stderr.read();code=proc.wait();(out/(id+'.stderr')).write_text(err)
  if final is None:raise RuntimeError('Qwen returned no final response; '+err[-200:])
  artifacts=final.get('artifacts',[])
  for f in artifacts:
   path=Path(f['path']);data=path.read_bytes()
   if path.suffix=='.docx':put('application.docx',data);(out/(id+'-application.docx')).write_bytes(data)
  receipt={'id':id,'task':task,'state':'completed' if code==0 and final.get('workflow_state')=='도구 오류 없음' else 'failed','phase':'실제 실행 완료 · 출처와 결과 확인' if code==0 and final.get('workflow_state')=='도구 오류 없음' else '실행 결과 · 확인이 필요한 항목 있음','answer':final['answer'],'log':'\n'.join(('✓ ' if not x.get('error') else '! ')+x['tool'] for x in events),'model':final.get('model'),'artifact_count':len(artifacts),'events':events,'exit_code':code}
  status(id,**{k:v for k,v in receipt.items() if k!='id'});(out/(id+'-receipt.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2));print(json.dumps({'id':id,'state':receipt['state'],'artifacts':len(artifacts),'events':len(events)}),flush=True)
 except Exception as e:status(id,state='failed',phase='실행 확인 필요',answer=str(e),log='');print(str(e),file=sys.stderr)
 finally:subprocess.run(base+['forward','--remove','tcp:'+port],capture_output=True)
 if a.once:break
