#!/usr/bin/env python3
"""Read authenticated Blackboard DOM over the local app CDP. Includes exact-target submission tools."""
import json,os,re,sys,time,urllib.request,base64,hashlib
from pathlib import Path
from urllib.parse import urlsplit
import websocket
HOST='blackboard.unist.ac.kr'
def inspect(endpoint,mode,source_url=None,plan_id=None):
 u=urlsplit(endpoint)
 if u.scheme!='http' or u.hostname not in ('127.0.0.1','localhost') or u.username or u.password or u.query or u.fragment:raise ValueError('Local CDP endpoint required')
 with urllib.request.urlopen(endpoint.rstrip('/')+'/json/list',timeout=5) as response:pages=json.load(response)
 target=os.environ.get('NUBI_CDP_TARGET_ID')
 pages=[p for p in pages if p.get('type')=='page' and (not target or p.get('id')==target) and not p.get('url','').startswith('file:')]
 if len(pages)!=1:raise RuntimeError('누비의 연결된 학교 브라우저 하나를 열어 주세요.')
 wsurl=pages[0]['webSocketDebuggerUrl'];parsed=urlsplit(wsurl)
 if parsed.scheme!='ws' or parsed.hostname not in ('127.0.0.1','localhost'):raise ValueError('Unexpected CDP socket')
 ws=websocket.create_connection(wsurl,timeout=10,suppress_origin=True);seq=0
 def rpc(method,params):
  nonlocal seq
  seq+=1;ident=seq;ws.send(json.dumps({'id':ident,'method':method,'params':params}))
  while True:
   row=json.loads(ws.recv())
   if row.get('id')==ident:
    if row.get('error') or row.get('result',{}).get('exceptionDetails'):raise RuntimeError('Blackboard DOM 판독 실패')
    return row.get('result',{})
 try:
  if mode.startswith('submission_'):
   from blackboard_submission import run
   return run(rpc,mode.removeprefix('submission_'),plan_id)
  if mode=='open':
   rpc('Page.navigate',{'url':'https://'+HOST+'/'});time.sleep(3)
   rpc('Runtime.evaluate',{'expression':"(()=>{const b=document.getElementById('unist-portal-login');if(b&&b.getClientRects().length)b.click()})()"});time.sleep(3)
  if mode in ('status','calendar','materials','attempt','todo_list','keepalive','notices'):
   asset=Path(__file__).resolve().parents[1]/'mobile-aside-mvp/app/src/main/assets/blackboard_tools.js'
   result=rpc('Runtime.evaluate',{'expression':asset.read_text()+'\nNubiBBTools.run('+json.dumps({'mode':mode})+')','returnByValue':True,'awaitPromise':True})['result'].get('value')
   if not isinstance(result,dict):raise RuntimeError('Blackboard tool response unavailable')
   return result
  script="""(()=>{const visible=e=>!!e.getClientRects().length;const host=location.hostname;
  if(host!=='blackboard.unist.ac.kr')return {state:'sso_unverified',host,reason:'포털 세션 자동 연결 미확인. 별도 로그인창은 입력하지 않음.'};
  if([...document.querySelectorAll('input[type=password],input[type=email]')].some(visible))return {state:'reauthentication_required',reason:'포털 세션으로 인증된 Blackboard 데이터를 확인하지 못함.'};
  const courses=[...document.querySelectorAll('a[href]')].filter(visible).filter(a=>/\\/courses?\\//.test(a.getAttribute('href')||'')).map(a=>({title:(a.innerText||a.getAttribute('aria-label')||'').trim().slice(0,250),url:a.href})).filter(a=>a.title&&new URL(a.url).hostname===host).slice(0,40);
  const nodes=[...document.querySelectorAll('article,[role=listitem],.activity-item,.stream-entry')].filter(visible);
  const activity=nodes.map(e=>({text:(e.innerText||'').trim().slice(0,1800),url:location.href})).filter(e=>/assignment|announcement|exam|due|message|과제|공지|시험|기한|팀/i.test(e.text)).slice(0,40);
  const attachments=[...document.querySelectorAll('a[href]')].filter(visible).filter(a=>/\\.(pdf|docx|pptx|hwpx|hwp)(?:[?#]|$)|bbcswebdav/i.test(a.href)).map(a=>({name:(a.innerText||'').trim().slice(0,250),url:a.href})).filter(a=>new URL(a.url).protocol==='https:'&&new URL(a.url).hostname===host).slice(0,30);
  const evidence=courses.length||activity.length||[...document.querySelectorAll('button,a')].filter(visible).some(a=>/로그아웃|sign out|log out|logout/i.test(a.innerText||a.getAttribute('aria-label')||''));
  return {state:evidence?'observed':'unverified',url:location.href,courses,activity,attachments,scope:'현재 보이는 DOM. 전체 과목·모든 과제 동기화 아님. 제출·성적·읽지 않은 메시지는 별도 확인 필요.'};})()"""
  result=rpc('Runtime.evaluate',{'expression':script,'returnByValue':True})['result'].get('value')
  if not isinstance(result,dict):raise RuntimeError('Blackboard 화면 응답이 없어요.')
  if mode=='download_pdf':
   asset=Path(__file__).resolve().parents[1]/'mobile-aside-mvp/app/src/main/assets/blackboard_tools.js'
   materials=rpc('Runtime.evaluate',{'expression':asset.read_text()+';NubiBBTools.run({mode:"materials"})','returnByValue':True,'awaitPromise':True})['result'].get('value',{})
   if materials.get('state')=='observed':result['attachments']=materials.get('items',[])
   if result.get('state')!='observed' or not any(x.get('url')==source_url for x in result.get('attachments',[])):raise ValueError('현재 보이는 강의자료 링크만 다운로드할 수 있어요.')
   script='''(async()=>{const response=await fetch(SOURCE,{method:'GET',credentials:'same-origin',redirect:'follow'});if(!['blackboard.unist.ac.kr','prod01-apne2-prod01-xythos.prod.files.blackboard.com'].includes(new URL(response.url).hostname))throw Error('Unexpected download host');if(!response.ok)throw Error('download failed');if(Number(response.headers.get('content-length'))>8*1024*1024)throw Error('file too large');const bytes=new Uint8Array(await response.arrayBuffer());if(bytes.length>8*1024*1024)throw Error('file too large');let binary='';for(let n=0;n<bytes.length;n+=8192)binary+=String.fromCharCode(...bytes.subarray(n,n+8192));return btoa(binary)})()'''.replace('SOURCE',json.dumps(source_url))
   raw=rpc('Runtime.evaluate',{'expression':script,'returnByValue':True,'awaitPromise':True})['result'].get('value')
   data=base64.b64decode(raw,validate=True)
   if not data.startswith(b'%PDF-'):raise ValueError('다운로드 응답이 실제 PDF가 아니에요. 로그인이나 파일 형식을 확인해 주세요.')
   sha=hashlib.sha256(data).hexdigest();root=Path(os.environ.get('NUBI_CAMPUS_DRAFT_DIR',str(Path.home()/'.local/share/nubi-campus/drafts'))).expanduser().resolve();root.mkdir(parents=True,exist_ok=True,mode=0o700);path=root/('lecture-'+sha+'.pdf')
   if path.is_symlink():raise ValueError('Unsafe local file')
   if not path.exists():
    with path.open('xb') as f:f.write(data)
    path.chmod(0o600)
   return {'state':'downloaded','source_url':source_url,'path':str(path),'sha256':sha,'bytes':len(data)}
  return result
 finally:ws.close()
def definitions():
 from blackboard_submission import definitions as submission_definitions
 return submission_definitions()+[{'name':'nubi_blackboard_'+mode,'description':description,'inputSchema':{'type':'object','properties':{},'additionalProperties':False}} for mode,description in [('open','Open Blackboard using the existing portal WebView session, then check visible authentication. Never enters credentials.'),('notices','Read actual open Blackboard announcement text and observed navigation links; missing DOM means unavailable.'),('calendar','Read authenticated Blackboard calendar deadlines and synchronize local todo cache; no submission.'),('materials','Recursively list actual same-origin course material links with depth and size limits.'),('attempt','Read current assignment instructions and own submission links; no writes.'),('todo_list','Read locally imported Blackboard tasks.'),('status','Read current Blackboard course links and authentication state.'),('keepalive','Check existing Blackboard session only while the document is visible; cannot bypass server expiry.'),('read','Read actually visible courses, activity announcements, assignment/exam hints and attachment links. Never submits. Empty means unverified, not no assignments.')]]
def main():
 for line in sys.stdin:
  ident=None
  try:
   r=json.loads(line);ident=r.get('id');method=r.get('method');p=r.get('params') or {}
   if ident is None:continue
   if method=='initialize':out={'protocolVersion':'2024-11-05','capabilities':{'tools':{}},'serverInfo':{'name':'nubi-blackboard','version':'0.1'}}
   elif method=='tools/list':out={'tools':definitions()+[{'name':'nubi_blackboard_download_pdf','description':'Download an exact currently observed same-origin Blackboard PDF link into the private lecture folder. GET only; rejects login pages and files over 8MiB.','inputSchema':{'type':'object','properties':{'source_url':{'type':'string'}},'required':['source_url'],'additionalProperties':False}}]}
   elif method=='tools/call' and p.get('name','').startswith('nubi_blackboard_submission_'):
    args=p.get('arguments') or {}
    if set(args)!={'plan_id'}:raise ValueError('정확한 제출 계획이 필요해요.')
    data=inspect(os.environ.get('NUBI_CDP_ENDPOINT','http://127.0.0.1:19333'),p['name'].removeprefix('nubi_blackboard_'),plan_id=args['plan_id']);out={'isError':data.get('state')=='receipt_not_found','content':[{'type':'text','text':json.dumps(data,ensure_ascii=False)}]}
   elif method=='tools/call' and p.get('name')=='nubi_blackboard_download_pdf':
    args=p.get('arguments') or {}
    if set(args)!={'source_url'}:raise ValueError('현재 관측한 PDF 링크가 필요해요.')
    data=inspect(os.environ.get('NUBI_CDP_ENDPOINT','http://127.0.0.1:19333'),'download_pdf',args['source_url']);out={'content':[{'type':'text','text':json.dumps(data,ensure_ascii=False)}]}
   elif method=='tools/call' and p.get('name') in tuple(t['name'] for t in definitions()):
    if p.get('arguments') not in ({},None):raise ValueError('No arguments accepted')
    data=inspect(os.environ.get('NUBI_CDP_ENDPOINT','http://127.0.0.1:19333'),p['name'].removeprefix('nubi_blackboard_'));out={'isError':data.get('state')!='observed','content':[{'type':'text','text':json.dumps(data,ensure_ascii=False)}]}
   elif method=='ping':out={}
   else:raise ValueError('Unknown tool')
   print(json.dumps({'jsonrpc':'2.0','id':ident,'result':out},ensure_ascii=False),flush=True)
  except Exception as e:print(json.dumps({'jsonrpc':'2.0','id':ident,'error':{'code':-32602,'message':str(e)}},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
