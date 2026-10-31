import json, tempfile, shutil, subprocess, sys, threading
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
runner=Path(__file__).with_name('qwen-goal-agent.py')
requests=[]
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args): pass
 def do_POST(self):
  p=json.loads(self.rfile.read(int(self.headers['Content-Length'])));requests.append(p)
  name='nubi_goal_search' if len(requests)==1 else 'nubi_goal_report'
  a={'goal_id':'a'*36,'provider':self.server.provider,'query':'model independently selected query'} if len(requests)==1 else {'goal_id':'a'*36,'summary':'관측한 후보입니다.','source_urls':['https://example.org/observed']}
  out={'model':self.server.model,'choices':[{'finish_reason':'tool_calls','message':{'role':'assistant','content':None,'tool_calls':[{'id':'call_'+str(len(requests)),'type':'function','function':{'name':name,'arguments':json.dumps(a)}}]}}]}
  raw=json.dumps(out).encode();self.send_response(200);self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
with tempfile.TemporaryDirectory() as d:
 root=Path(d);shutil.copy(runner,root/runner.name)
 (root/'nubi-goal-mcp.py').write_text('''import json,sys
names=['open','search','observe','select','report','explore']
for line in sys.stdin:
 r=json.loads(line);m=r['method']
 if m=='notifications/initialized':continue
 if m=='initialize':out={'protocolVersion':'2024-11-05'}
 elif m=='tools/list':out={'tools':[{'name':'nubi_goal_'+n,'description':n,'inputSchema':{'type':'object'}} for n in names]}
 else:
  name=r['params']['name'];a=r['params']['arguments']
  data={'goal':{'goal_id':'a'*36,'title':'fixture'}} if name=='nubi_goal_open' else {'state':'report_saved' if name=='nubi_goal_report' else 'navigation_requested','echo':a}
  out={'content':[{'type':'text','text':json.dumps(data)}]}
 print(json.dumps({'jsonrpc':'2.0','id':r['id'],'result':out}),flush=True)
''')
 cfg=root/'azrael/providers/api';cfg.mkdir(parents=True);token=root/'token';token.write_text('fixture-only')
 (cfg/'connections.json').write_text(json.dumps({'connections':[{'enabled':True,'models':[{'id':'Qwen3.8-27B-uncensored-FP8'}],'auth':{'kind':'bearerFile','filePath':str(token)},'baseUrl':f'http://127.0.0.1:{server.server_port}'}]}))
 for provider,task,wrong in [('youtube','영상만 찾아줘. 쇼핑은 제외.',False),('11st','쇼핑만 찾아줘. 영상은 제외.',False),('youtube','영상만 찾아줘.',True)]:
  requests.clear();server.provider=provider;server.model='wrong-model' if wrong else 'Qwen3.8-27B-abliterated-AWQ-W4A16'
  trace=root/'trace.json';p=subprocess.run([sys.executable,str(root/runner.name),'--goal','fitness','--azrael-home',str(root),'--task',task,'--trace-file',str(trace)],capture_output=True,text=True,timeout=20)
  t=json.loads(trace.read_text());assert requests
  for req in requests:
   assert req['tool_choice']=='auto'
   assert 'nubi_goal_explore' not in [x['function']['name'] for x in req['tools']]
   assert any(task in x.get('content','') for x in req['messages'] if x['role']=='user')
  actions=[x for x in t['events'] if x['type']=='tool']
  if wrong:
   assert p.returncode==1 and not actions and 'Unexpected served model' in t['error']
  else:
   assert p.returncode==0 and t['completed']
   assert actions[0]['result']['content'] and json.loads(actions[0]['result']['content'][0]['text'])['echo']['provider']==provider
  print(provider, 'wrong-model rejected' if wrong else 'instruction/auto tools/model-selected arguments/report passed')
server.shutdown()
print('3 isolated runner integration cases passed; mocked model/MCP, not live tablet proof')
