#!/usr/bin/env python3
"""Navigate the foreground Nubi WebView to authenticated campus workflows."""
import json,os,sys,time,urllib.request
from urllib.parse import urlparse
import websocket
preferred_target=None

def open_workspace(endpoint,destination):
 global preferred_target
 u=urlparse(endpoint)
 if u.scheme!='http' or u.hostname not in ('127.0.0.1','localhost') or u.username or u.password:raise ValueError('local CDP only')
 paths={'scholarship':'https://uspace.unist.ac.kr/uspace/Cabinet/MainPage.bzr?cabinetInstanceID=1126','academic':'https://uspace.unist.ac.kr/uspace/Cabinet/MainPage.bzr?cabinetInstanceID=1978','general':'https://uspace.unist.ac.kr/uspace/Cabinet/MainPage.bzr?cabinetInstanceID=1124','outlook':'https://sso-token.unist.ac.kr/email','course':'https://portal.unist.ac.kr/irj/portal','enrollment':'https://portal.unist.ac.kr/irj/portal'}
 if destination not in paths:raise ValueError('지원하지 않는 화면')
 with urllib.request.urlopen(endpoint.rstrip('/')+'/json/list',timeout=5) as f:pages=json.load(f)
 found=[p for p in pages if p.get('type')=='page' and p.get('id')==preferred_target] if preferred_target else []
 for page in ([] if found else pages):
  if page.get('type')!='page':continue
  target=urlparse(page.get('webSocketDebuggerUrl',''))
  if target.scheme!='ws' or target.hostname not in ('127.0.0.1','localhost'):continue
  ws=None
  try:
   ws=websocket.create_connection(page['webSocketDebuggerUrl'],timeout=2,suppress_origin=True)
   ws.send(json.dumps({'id':1,'method':'Runtime.evaluate','params':{'expression':'document.visibilityState','returnByValue':True}}))
   while True:
    r=json.loads(ws.recv())
    if r.get('id')==1:break
   if r.get('result',{}).get('result',{}).get('value')=='visible':found.append(page)
  except (OSError,websocket.WebSocketException):continue
  finally:
   if ws:ws.close()
 if not found:
  # The user's chat may be in another app; prefer the single previously
  # authenticated U-Space workspace and leave other hidden pages untouched.
  found=[p for p in pages if p.get('type')=='page' and ((urlparse(p.get('url','')).hostname=='uspace.unist.ac.kr' and urlparse(p.get('url','')).path=='/uspace/Cabinet/MainPage.bzr') or urlparse(p.get('url','')).hostname in ('outlook.office.com','outlook.office365.com','outlook.cloud.microsoft'))]
 if len(found)!=1:raise RuntimeError('연결된 누비 브라우저 화면을 하나로 확인하지 못했습니다.')
 preferred_target=found[0]['id']
 ws=websocket.create_connection(found[0]['webSocketDebuggerUrl'],timeout=8,suppress_origin=True);seq=0
 def call(method,params=None):
  nonlocal seq
  seq+=1;ident=seq;ws.send(json.dumps({'id':ident,'method':method,'params':params or {}}))
  while True:
   r=json.loads(ws.recv())
   if r.get('id')==ident:
    if 'error' in r:raise RuntimeError('브라우저 요청 실패')
    return r['result']
 def evaluate(e):
  out=call('Runtime.evaluate',{'expression':e,'returnByValue':True})
  if out.get('exceptionDetails'):raise RuntimeError('화면 검사 실패')
  return out.get('result',{}).get('value')
 try:
  nav=call('Page.navigate',{'url':paths[destination]})
  if nav.get('errorText'):raise RuntimeError('화면 이동 실패')
  for attempt in range(20):
   time.sleep(.7)
   try:
    state=evaluate("({host:location.hostname,title:document.title,ready:document.readyState,body:!!document.body})")
    if state and state.get('ready')!='loading' and state.get('body'):
     if destination in ('scholarship','academic','general') and state['host']=='uspace.unist.ac.kr':
      board=evaluate("(()=>{let f=document.querySelector('#bzrForm');let u=f?new URL(f.action):null;return u?.searchParams.get('cabinetInstanceID')||null})()")
      expected={'scholarship':'1126','academic':'1978','general':'1124'}[destination]
      if board==expected:return {'state':'opened','destination':destination,'board_id':board}
     elif destination=='outlook' and state['host'] in ('outlook.office.com','outlook.office365.com','outlook.cloud.microsoft'):
      if evaluate("!!document.querySelector('input[role=combobox][aria-label*=검색]')"):return {'state':'opened','destination':destination}
     elif destination in ('course','enrollment') and state['host']=='portal.unist.ac.kr':break
     elif state['host'] in ('fs.unist.ac.kr','login.microsoftonline.com'):return {'state':'authentication_required','destination':destination}
   except RuntimeError:pass
  else:raise RuntimeError('요청한 화면을 확인하지 못했습니다.')
  if destination in ('course','enrollment'):
   for attempt in range(20):
    if evaluate("(()=>{let e=document.querySelector('#tabIndex1');if(!e||e.getAttribute('title')!=='학사')return false;e.click();return true})()"):break
    time.sleep(.5)
   else:raise RuntimeError('학사 메뉴를 찾지 못했습니다.')
   for attempt in range(15):
    time.sleep(.5)
    clicked=evaluate("(()=>{let a=[...document.querySelectorAll('[title=수강][subtabindex]')];if(a.length!==1)return false;a[0].click();return true})()")
    if clicked:break
   if not clicked:raise RuntimeError('수강 메뉴를 찾지 못했습니다.')
   for attempt in range(20):
    time.sleep(.5)
    if evaluate("document.title.startsWith('개설강좌 조회')"):break
   else:raise RuntimeError('개설강좌 조회 화면을 확인하지 못했습니다.')
   if destination=='course':return {'state':'opened','destination':'course','note':'학년도·학기·전공은 현재 화면의 선택값입니다.'}
   if not evaluate("(()=>{let a=[...document.querySelectorAll('[nodetitle]')].filter(x=>x.getAttribute('nodetitle')==='수강관리');if(a.length!==1)return false;a[0].click();return true})()"):raise RuntimeError('수강관리 메뉴를 찾지 못했습니다.')
   for attempt in range(20):
    time.sleep(.5)
    if evaluate("document.title.startsWith('예비수강신청')"):break
   else:raise RuntimeError('예비수강신청 화면을 확인하지 못했습니다.')
   def frames(node):
    yield node['frame']
    for child in node.get('childFrames',[]):yield from frames(child)
   for attempt in range(15):
    tree=call('Page.getFrameTree')['frameTree'];candidates=[f for f in frames(tree) if f.get('name')=='isolatedWorkArea' and urlparse(f.get('url','')).hostname=='s4hana.unist.ac.kr' and '/ZCMW5220' in urlparse(f.get('url','')).path]
    if len(candidates)==1:
     ctx=call('Page.createIsolatedWorld',{'frameId':candidates[0]['id']})['executionContextId']
     r=call('Runtime.evaluate',{'contextId':ctx,'expression':"(document.body?.innerText||'').split('\\n').map(x=>x.trim()).filter(x=>/학사력 기간|^20[0-9]{2} .*학기:/.test(x)).slice(0,4)",'returnByValue':True})
     lines=r.get('result',{}).get('value')
     if isinstance(lines,list) and lines:return {'state':'opened','destination':'enrollment','visible_status':lines,'note':'예비수강신청 화면만 열었고 신청은 하지 않았습니다.'}
    time.sleep(.5)
   return {'state':'opened','destination':'enrollment','visible_status':[],'note':'예비수강신청 화면을 열었지만 기간을 확인하지 못했습니다.'}
 finally:ws.close()

def main():
 for line in sys.stdin:
  ident=None
  try:
   m=json.loads(line);ident=m.get('id');method=m.get('method');p=m.get('params') or {}
   if ident is None:continue
   if method=='initialize':result={'protocolVersion':'2024-11-05','capabilities':{'tools':{}},'serverInfo':{'name':'nubi-campus-navigation','version':'0.1'}}
   elif method=='ping':result={}
   elif method=='tools/list':result={'tools':[{'name':'nubi_campus_open','description':'Open one campus board, Outlook, or course page. For 예비수강신청 and its application period, destination MUST be enrollment; course is only 개설강좌 조회. Enrollment only navigates, never registers. May temporarily pause the board monitor.','inputSchema':{'type':'object','properties':{'destination':{'type':'string','enum':['scholarship','academic','general','outlook','course','enrollment']}},'required':['destination'],'additionalProperties':False}}]}
   elif method=='tools/call' and p.get('name')=='nubi_campus_open':
    try:
     args=p.get('arguments') or {}
     if set(args)!={'destination'}:raise ValueError('화면 선택이 필요합니다.')
     result={'content':[{'type':'text','text':json.dumps(open_workspace(os.environ.get('NUBI_CDP_ENDPOINT','http://127.0.0.1:19333'),args['destination']),ensure_ascii=False)}]}
    except Exception as e:result={'content':[{'type':'text','text':str(e)}],'isError':True}
   else:raise ValueError('Unknown method')
   print(json.dumps({'jsonrpc':'2.0','id':ident,'result':result},ensure_ascii=False),flush=True)
  except Exception as e:print(json.dumps({'jsonrpc':'2.0','id':ident,'error':{'code':-32602,'message':str(e)}},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
