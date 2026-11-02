#!/usr/bin/env python3
"""Drive only explicit requests from the filming APK using the real Qwen/MCP runner.
All receipts come from tool execution. Writes recipient-free draft only. No sending.
"""
import argparse,hashlib,json,os,subprocess,sys,time,urllib.request,websocket
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
labels={'nubi_campus_open':'Opened the official university service','nubi_portal_board_list':'Read scholarship notices','nubi_portal_board_open':'Selected the original notice','nubi_campus_board_search_open':'Opened the matching notice','nubi_portal_notice_detail':'Read the notice and eligibility requirements','nubi_outlook_web_search':'Searched university email','nubi_outlook_web_read':'Read the selected email','nubi_local_document_draft':'Created the DOCX application draft','nubi_outlook_web_draft':'Verified the saved Outlook draft'}
while True:
 try:r=json.loads(read('request.json'))
 except (ValueError,TypeError):time.sleep(1);continue
 id=r.get('id');task=r.get('task','')
 if id in seen or r.get('createdAt',0)<started*1000 or not task.strip():time.sleep(.5);continue
 seen.add(id);events=[];status(id,state='running',phase='Qwen · Connecting to your live browser',log='')
 viewport_ws=None
 pid=subprocess.check_output(base+['shell','pidof',pkg],text=True).strip();port=subprocess.check_output(base+['forward','tcp:0','localabstract:webview_devtools_remote_'+pid],text=True).strip()
 try:
  ep='http://127.0.0.1:'+port
  pages=json.load(urllib.request.urlopen(ep+'/json/list'));candidates=[x for x in pages if x.get('type')=='page' and x.get('url','').startswith('https://')]
  if len(candidates)!=1:raise RuntimeError('Close other school browser windows before filming')
  if r.get('scene')=='mail':
   viewport_ws=websocket.create_connection(candidates[0]['webSocketDebuggerUrl'],suppress_origin=True,timeout=10)
   viewport_ws.send(json.dumps({'id':9901,'method':'Emulation.setDeviceMetricsOverride','params':{'width':1100,'height':1500,'deviceScaleFactor':1,'mobile':False}}))
   while json.loads(viewport_ws.recv()).get('id')!=9901:pass
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
     if e.get('error'):phase='Needs review · '+tool
     status(id,state='running',phase=phase,log='\n'.join(('✓ ' if not x.get('error') else '! ')+x['tool'] for x in events))
    if isinstance(e.get('answer'),str):final=e
  err=proc.stderr.read();code=proc.wait();(out/(id+'.stderr')).write_text(err)
  if final is None:raise RuntimeError('Qwen returned no final response; '+err[-200:])
  artifacts=final.get('artifacts',[])
  for f in artifacts:
   path=Path(f['path']);data=path.read_bytes()
   if path.suffix=='.docx':put('application.docx',data);(out/(id+'-application.docx')).write_bytes(data)
  model_answer=final['answer']
  succeeded={event['tool'] for event in events if not event.get('error')}
  if artifacts and {'nubi_outlook_web_read','nubi_outlook_web_draft'}.issubset(succeeded):
   final['answer']='Read the selected university email body.\nCreated an English DOCX application draft.\nSaved and verified an Outlook draft with the DOCX attached.\nRecipient empty; not sent.\nApplicant details still require your review.\nSource attachment names were listed; their contents were not read.'
  receipt={'model_answer':model_answer,'id':id,'task':task,'state':'completed' if code==0 and final.get('workflow_state')=='도구 오류 없음' else 'failed','phase':'Completed · Source-backed results' if code==0 and final.get('workflow_state')=='도구 오류 없음' else 'Finished · Some items need review','answer':final['answer'],'log':'\n'.join(('✓ ' if not x.get('error') else '! ')+x['tool'] for x in events)+'\n\n'+final['answer'],'model':final.get('model'),'artifact_count':len(artifacts),'events':events,'exit_code':code}
  status(id,**{k:v for k,v in receipt.items() if k!='id'});(out/(id+'-receipt.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2));print(json.dumps({'id':id,'state':receipt['state'],'artifacts':len(artifacts),'events':len(events)}),flush=True)
 except Exception as e:status(id,state='failed',phase='Execution needs review',answer=str(e),log='');print(str(e),file=sys.stderr)
 finally:
  if viewport_ws:viewport_ws.close()
  subprocess.run(base+['forward','--remove','tcp:'+port],capture_output=True)
 if a.once:break
