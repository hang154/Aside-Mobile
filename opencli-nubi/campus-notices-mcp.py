#!/usr/bin/env python3
"""Read the currently visible UNIST portal home notice list from a tablet WebView.
The CDP endpoint must be supplied explicitly; no credentials are read or stored.
"""
import json, os, re, sys, time, urllib.request
from datetime import datetime, timezone
from urllib.parse import urlparse
import websocket
from campus_notice_store import sync as sync_notices
from campus_relevance import doosan_2027

RULES = [
 ('학점교류', r'학점\s*교류|계절\s*학기.*학점'), ('복학', r'복학'),
 ('시험', r'기말|시험|자격\s*시험'), ('전공', r'전공\s*(신청|변경)'),
 ('인턴십', r'인턴|현장실습'), ('졸업', r'졸업|학위논문'),
 ('장학', r'장학'), ('수강신청', r'수강|수업\s*정원'),
 ('캠프', r'캠프'), ('행사', r'축전|축제|행사|강연|세미나'),
 ('시설', r'화장실|사용\s*불가|시설'), ('휴학', r'휴학|중도포기'),
 ('지원사업', r'지원사업|모집')]

def classify(title):
 return [name for name, pattern in RULES if re.search(pattern,title,re.I)]

def read_portal(endpoint, selection=None):
 u=urlparse(endpoint)
 if u.scheme!='http' or u.hostname not in ('127.0.0.1','localhost') or u.username or u.password: raise ValueError('CDP endpoint must be local HTTP')
 with urllib.request.urlopen(endpoint.rstrip('/')+'/json/list',timeout=5) as f: pages=json.load(f)
 candidates=[p for p in pages if p.get('type')=='page' and urlparse(p.get('url','')).hostname=='portal.unist.ac.kr']
 if len(candidates)!=1: raise RuntimeError('열려 있는 UNIST 포털 페이지를 하나만 선택해 주세요.')
 wsurl=candidates[0]['webSocketDebuggerUrl']; parsed=urlparse(wsurl)
 if parsed.hostname not in ('127.0.0.1','localhost') or parsed.scheme!='ws': raise RuntimeError('Unexpected CDP endpoint')
 ws=websocket.create_connection(wsurl,timeout=8,suppress_origin=True)
 sequence=0
 def call(method,params=None):
  nonlocal sequence
  sequence+=1; ident=sequence; ws.send(json.dumps({'id':ident,'method':method,'params':params or {}}))
  while True:
   item=json.loads(ws.recv())
   if item.get('id')==ident:
    if 'error' in item: raise RuntimeError('CDP: '+str(item['error'].get('message','error')))
    return item['result']
 try:
  tree=call('Page.getFrameTree')['frameTree']
  def frames(node):
   yield node['frame']
   for child in node.get('childFrames',[]): yield from frames(child)
  matches=[f for f in frames(tree) if f.get('name')=='contentAreaFrame' and urlparse(f.get('url','')).hostname=='portal.unist.ac.kr']
  if len(matches)!=1: raise RuntimeError('포털 홈 공지 프레임을 찾지 못했어요.')
  ctx=call('Page.createIsolatedWorld',{'frameId':matches[0]['id'],'worldName':'nubi-campus-notices'})['executionContextId']
  expression=r'''(()=>{const visible=e=>!!(e.getClientRects().length && getComputedStyle(e).visibility!=='hidden');
   const rows=[];for(const a of document.querySelectorAll('a[href*="go_board_view"]')){
    if(!visible(a)) continue;const tr=a.closest('tr');if(!tr)continue;
    const cells=Array.from(tr.querySelectorAll(':scope > td'));const date=cells.map(x=>x.innerText.trim()).find(x=>/^\d{4}-\d{2}-\d{2}$/.test(x));
    const match=(a.getAttribute('href')||'').match(/oid:(\d+)\^cabinetInstanceID:(\d+)/);
    const title=a.innerText.trim();const path=(a.getAttribute('href')||'').match(/go_board_view\('([^']+)'\)/)?.[1]; if(title && date && match && path) rows.push({title,posted:date,id:match[1],board_id:match[2],path});
   } return rows.slice(0,40)})()'''
  result=call('Runtime.evaluate',{'contextId':ctx,'returnByValue':True,'expression':expression})
  if result.get('exceptionDetails'): raise RuntimeError('공지 목록 판독 실패')
  rows=result.get('result',{}).get('value')
  if not isinstance(rows,list): raise RuntimeError('공지 목록을 읽지 못했어요.')
  if selection is not None:
   if not isinstance(selection,dict) or set(selection)!={'id','title'}:raise ValueError('현재 미리보기의 ID와 제목이 필요해요.')
   selected=next((r for r in rows if r['id']==selection['id'] and r['title']==selection['title']),None)
   if not selected:raise RuntimeError('공지 목록이 바뀌었어요. 다시 조회하세요.')
   path=selected['path']
   if not path.startswith('/uspace/ssoagent/ssologingateway.jsp?targetURL=/Cabinet/MainPage.bzr&'):raise RuntimeError('예상하지 못한 공지 경로예요.')
   call('Page.navigate',{'url':'https://uspace.unist.ac.kr'+path})
   return {'state':'navigation_requested','id':selected['id'],'title':selected['title']}
  for r in rows:r.pop('path',None);r['category_candidates']=classify(r['title']);r['truncated']=r['title'].endswith(('...','…'))
  return {'source':'UNIST 포털 홈의 현재 표시된 공지','checked_at':datetime.now(timezone.utc).isoformat(),'scope':'현재 선택된 탭의 홈 미리보기만; 전체 게시판 아님','items':rows}
 finally:ws.close()

def read_detail(endpoint, mode="detail", args=None):
 u=urlparse(endpoint)
 if u.scheme!='http' or u.hostname not in ('127.0.0.1','localhost') or u.username or u.password: raise ValueError('CDP endpoint must be local HTTP')
 with urllib.request.urlopen(endpoint.rstrip('/')+'/json/list',timeout=5) as f: pages=json.load(f)
 candidates=[p for p in pages if p.get('type')=='page' and urlparse(p.get('url','')).hostname=='uspace.unist.ac.kr' and re.sub(r'/+', '/', urlparse(p.get('url','')).path)=='/uspace/Cabinet/MainPage.bzr']
 if len(candidates)!=1: raise RuntimeError('누비 브라우저에서 UNIST 공지 상세를 먼저 열어 주세요.')
 wsurl=candidates[0]['webSocketDebuggerUrl']; parsed=urlparse(wsurl)
 if parsed.hostname not in ('127.0.0.1','localhost') or parsed.scheme!='ws': raise RuntimeError('Unexpected CDP endpoint')
 ws=websocket.create_connection(wsurl,timeout=8,suppress_origin=True); sequence=0
 def call(method,params=None):
  nonlocal sequence
  sequence+=1; ident=sequence;ws.send(json.dumps({'id':ident,'method':method,'params':params or {}}))
  while True:
   item=json.loads(ws.recv())
   if item.get('id')==ident:
    if 'error' in item:raise RuntimeError('CDP request failed')
    return item['result']
 try:
  tree=call('Page.getFrameTree')['frameTree']
  def frames(node):
   yield node['frame']
   for child in node.get('childFrames',[]):yield from frames(child)
  all_frames=list(frames(tree));root=all_frames[0]
  if re.sub(r'/+', '/', urlparse(root.get('url','')).path)!='/uspace/Cabinet/MainPage.bzr':raise RuntimeError('공지 상세 화면이 아닙니다.')
  body_frames=[f for f in all_frames if f.get('name','').endswith('_viewBody_Content') and (urlparse(f.get('url','')).hostname=='uspace.unist.ac.kr' or (f.get('url')=='about:blank' and f.get('securityOrigin')=='https://uspace.unist.ac.kr'))]
  def evaluate(frame,expression):
   ctx=call('Page.createIsolatedWorld',{'frameId':frame['id'],'worldName':'nubi-campus-detail'})['executionContextId']
   result=call('Runtime.evaluate',{'contextId':ctx,'returnByValue':True,'expression':expression})
   if result.get('exceptionDetails'):raise RuntimeError('공지 본문 판독 실패')
   return result.get('result',{}).get('value')
  if mode in ('list','open'):
   expression=r"""(()=>[...document.querySelectorAll('tr')].map(tr=>{let c=tr.cells;if(c.length!==8)return null;let a=c[4].querySelector('a[onclick*=TitleClick]');if(!a)return null;let m=(a.getAttribute('onclick')||'').match(/TitleClick\('[^']*','(\d+)','(\d+)'/);let title=a.innerText.trim();return m&&title?{number:c[1].innerText.trim(),title,posted:c[6].innerText.trim(),id:m[1],board_id:m[2],has_attachment:!!c[2].querySelector('img')}:null}).filter(Boolean).slice(0,100))()"""
   rows=evaluate(root,expression)
   if not isinstance(rows,list):raise RuntimeError('게시판 목록을 읽지 못했어요.')
   if mode=='open':
    if not isinstance(args,dict) or set(args)!={'id','title'} or not re.fullmatch(r'\d{1,30}',str(args.get('id',''))) or not isinstance(args.get('title'),str) or len(args['title'])>500:raise ValueError('현재 목록에서 받은 공지 ID와 제목이 필요해요.')
    row=next((r for r in rows if r['id']==args['id'] and r['title']==args['title']),None)
    if not row:raise RuntimeError('공지 목록이 바뀌었어요. 목록을 다시 조회하세요.')
    target=json.dumps(args,ensure_ascii=False)
    click="(()=>{let arg="+target+";let a=[...document.querySelectorAll('tr')].map(x=>x.cells.length===8?x.cells[4].querySelector('a[onclick*=TitleClick]'):null).find(x=>x&&x.innerText.trim()===arg.title&&(x.getAttribute('onclick')||'').includes(\"'\"+arg.id+\"'\"));if(!a)return false;a.click();return true})()"
    if not evaluate(root,click):raise RuntimeError('선택한 공지가 바뀌었어요.')
    return {'state':'navigation_requested','id':row['id'],'title':row['title'],'note':'본문 로딩 후 nubi_portal_notice_detail 호출'}
   for row in rows:row['category_candidates']=classify(row['title'])
   return {'source':'UNIST 현재 게시판 목록','checked_at':datetime.now(timezone.utc).isoformat(),'scope':'현재 페이지의 표시된 게시글','items':rows}
  if len(body_frames)!=1:
   for _ in range(8):
    time.sleep(.5)
    refreshed=list(frames(call('Page.getFrameTree')['frameTree']))
    body_frames=[f for f in refreshed if f.get('name','').endswith('_viewBody_Content') and (urlparse(f.get('url','')).hostname=='uspace.unist.ac.kr' or (f.get('url')=='about:blank' and f.get('securityOrigin')=='https://uspace.unist.ac.kr'))]
    if len(body_frames)==1:break
   if len(body_frames)!=1:raise RuntimeError('공지 본문 프레임을 찾지 못했어요.')
  head=evaluate(root,"(()=>{const rows=[...document.querySelectorAll('tr')];let get=k=>{let r=rows.find(x=>x.cells.length>1&&x.cells[0].innerText.trim()===k);return r?.cells[1]?.innerText.trim()||''};return {title:get('제목'),posted:get('작성일'),attachments:get('첨부파일')}})()")
  body=evaluate(body_frames[0],"(()=>({text:(document.body?.innerText||'').trim().slice(0,20000),images:document.body?.querySelectorAll('img').length||0}))()")
  if not head or not head.get('title') or not isinstance(body,dict) or (not body.get('text') and not body.get('images')):raise RuntimeError('제목 또는 본문이 비었어요. 로딩 상태를 확인하세요.')
  return {'source':'UNIST 포털 게시글 상세','checked_at':datetime.now(timezone.utc).isoformat(),'title':head['title'],'posted':head['posted'],'attachments':head['attachments'],'body':body['text'],'embedded_image_count':body['images'],'body_note':'이미지 내용은 읽지 않았습니다. 원문 이미지 확인이 필요합니다.' if body['images'] else '', 'category_candidates':classify(head['title'])}
 finally:ws.close()

def read_board_page(endpoint, page_number):
 if not isinstance(page_number,int) or isinstance(page_number,bool) or not 1<=page_number<=100:raise ValueError('페이지는 1~100 사이의 정수여야 합니다.')
 u=urlparse(endpoint)
 if u.scheme!='http' or u.hostname not in ('127.0.0.1','localhost') or u.username or u.password:raise ValueError('CDP endpoint must be local HTTP')
 with urllib.request.urlopen(endpoint.rstrip('/')+'/json/list',timeout=5) as f:pages=json.load(f)
 candidates=[p for p in pages if p.get('type')=='page' and urlparse(p.get('url','')).hostname=='uspace.unist.ac.kr' and urlparse(p.get('url','')).path=='/uspace/Cabinet/MainPage.bzr']
 if len(candidates)!=1:raise RuntimeError('포털 게시판 목록 하나를 열어 주세요.')
 target=urlparse(candidates[0]['webSocketDebuggerUrl'])
 if target.scheme!='ws' or target.hostname not in ('127.0.0.1','localhost'):raise RuntimeError('Unexpected CDP endpoint')
 ws=websocket.create_connection(candidates[0]['webSocketDebuggerUrl'],timeout=12,suppress_origin=True)
 try:
  expr=r'''(async()=>{let f=document.getElementById('bzrForm');if(!f||!f.querySelector('a[onclick*=TitleClick]'))throw Error('먼저 게시판 목록을 여세요');let a=new URL(f.action);if(a.origin!==location.origin||a.pathname!=='/uspace/Cabinet/MainPage.bzr')throw Error('예상하지 못한 게시판');let b=new URLSearchParams(new FormData(f));b.set('SELECTED_NUMBER_HIDDEN_ID',PAGE);b.set('bzr_event_MainPage_superMain_main_list_listPager_webPager_webPager_indexClick','true');let r=await fetch(a.href,{method:'POST',credentials:'same-origin',body:b});if(!r.ok)throw Error('게시판 요청 실패');let d=new DOMParser().parseFromString(await r.text(),'text/html');let rows=[...d.querySelectorAll('tr')].map(tr=>{let c=tr.cells;if(c.length!==8)return null;let a=c[4].querySelector('a[onclick*=TitleClick]');if(!a)return null;let m=(a.getAttribute('onclick')||'').match(/TitleClick\('[^']*','(\d+)','(\d+)'/);let title=a.textContent.trim();return m&&title?{number:c[1].textContent.trim(),title,posted:c[6].textContent.trim(),id:m[1],board_id:m[2],has_attachment:!!c[2].querySelector('img')}:null}).filter(Boolean);let selected=d.querySelector('[name=SELECTED_NUMBER_HIDDEN_ID]')?.value;return {selected,items:rows}})()'''.replace('PAGE',json.dumps(str(page_number-1)))
  ws.send(json.dumps({'id':1,'method':'Runtime.evaluate','params':{'expression':expr,'awaitPromise':True,'returnByValue':True}}))
  while True:
   reply=json.loads(ws.recv())
   if reply.get('id')==1:break
  if 'error' in reply or reply.get('result',{}).get('exceptionDetails'):raise RuntimeError('게시판 페이지 조회 실패')
  out=reply.get('result',{}).get('result',{}).get('value')
  if not isinstance(out,dict) or not out.get('items') or out.get('selected')!=str(page_number-1):raise RuntimeError('요청한 페이지 결과를 확인하지 못했습니다.')
  for row in out['items']:row['category_candidates']=classify(row['title'])
  return {'source':'UNIST 현재 게시판','page':page_number,'checked_at':datetime.now(timezone.utc).isoformat(),'items':out['items']}
 finally:ws.close()

def search_board(endpoint, query, page_number=1):
 """Search the current board through its own form; do not navigate the WebView."""
 if not isinstance(query,str) or not 1<=len(query.strip())<=80:raise ValueError('검색어는 1~80자여야 합니다.')
 if not isinstance(page_number,int) or isinstance(page_number,bool) or not 1<=page_number<=100:raise ValueError('페이지는 1~100 사이여야 합니다.')
 u=urlparse(endpoint)
 if u.scheme!='http' or u.hostname not in ('127.0.0.1','localhost') or u.username or u.password:raise ValueError('local CDP only')
 with urllib.request.urlopen(endpoint.rstrip('/')+'/json/list',timeout=5) as f:pages=json.load(f)
 candidates=[p for p in pages if p.get('type')=='page' and urlparse(p.get('url','')).hostname=='uspace.unist.ac.kr' and urlparse(p.get('url','')).path=='/uspace/Cabinet/MainPage.bzr']
 if len(candidates)!=1:raise RuntimeError('학교 게시판 목록 하나를 열어 주세요.')
 target=urlparse(candidates[0]['webSocketDebuggerUrl'])
 if target.scheme!='ws' or target.hostname not in ('127.0.0.1','localhost'):raise RuntimeError('unexpected CDP address')
 ws=websocket.create_connection(candidates[0]['webSocketDebuggerUrl'],timeout=20,suppress_origin=True)
 try:
  expr=r'''(async()=>{let q=QUERY, page=PAGE, f=document.getElementById('bzrForm');if(!f||!f.querySelector('a[onclick*=TitleClick]'))throw Error('게시판 목록 필요');let a=new URL(f.action);if(a.origin!==location.origin||a.pathname!=='/uspace/Cabinet/MainPage.bzr')throw Error('잘못된 게시판 주소');let id=f.querySelector('[name=bzr_viewState_MainPage_superMain_main_list_listBody_cabinetInstanceID]')?.value;if(!['1126','1978','1124'].includes(id))throw Error('지원하지 않는 게시판');let b=new URLSearchParams(new FormData(f));b.set('MainPage_superMain_main_list_listSearch_Title',q);b.set('bzr_event_MainPage_superMain_main_list_listSearch_searchButton_CLICK_EVENT','true');let fetchDoc=async(body)=>{let r=await fetch(a.href,{method:'POST',credentials:'same-origin',cache:'no-store',body});if(!r.ok)throw Error('게시판 검색 실패');return new DOMParser().parseFromString(await r.text(),'text/html')};let d=await fetchDoc(b);if(d.querySelector('[name=MainPage_superMain_main_list_listSearch_Title]')?.value!==q)throw Error('검색 적용 확인 실패');if(page>1){let pf=d.getElementById('bzrForm');if(!pf)throw Error('검색 페이지 상태 없음');let pb=new URLSearchParams(new FormData(pf));pb.set('SELECTED_NUMBER_HIDDEN_ID',String(page-1));pb.set('bzr_event_MainPage_superMain_main_list_listPager_webPager_webPager_indexClick','true');d=await fetchDoc(pb);if(d.querySelector('[name=SELECTED_NUMBER_HIDDEN_ID]')?.value!==String(page-1)||d.querySelector('[name=MainPage_superMain_main_list_listSearch_Title]')?.value!==q)throw Error('검색 페이지 확인 실패')}let rows=[...d.querySelectorAll('tr')].map(tr=>{let c=tr.cells;if(c.length!==8)return null;let a=c[4].querySelector('a[onclick*=TitleClick]');if(!a)return null;let m=(a.getAttribute('onclick')||'').match(/TitleClick\('[^']*','(\d+)','(\d+)'/);let title=a.textContent.trim();return m&&m[2]===id&&title?{number:c[1].textContent.trim(),title,posted:c[6].textContent.trim(),id:m[1],board_id:m[2],has_attachment:!!c[2].querySelector('img')}:null}).filter(Boolean);let next=[...d.querySelectorAll('a[onclick*=clickPager]')].some(x=>{let m=(x.getAttribute('onclick')||'').match(/clickPager\('(\d+)'/);return m&&+m[1]>=page});return {board_id:id,items:rows,has_next:next}})()'''.replace('QUERY',json.dumps(query.strip(),ensure_ascii=False)).replace('PAGE',str(page_number))
  ws.send(json.dumps({'id':1,'method':'Runtime.evaluate','params':{'expression':expr,'awaitPromise':True,'returnByValue':True}}))
  while True:
   reply=json.loads(ws.recv())
   if reply.get('id')==1:break
  if 'error' in reply or reply.get('result',{}).get('exceptionDetails'):raise RuntimeError('게시판 검색 또는 로그인 상태 확인 실패')
  out=reply.get('result',{}).get('result',{}).get('value')
  if not isinstance(out,dict) or not isinstance(out.get('items'),list):raise RuntimeError('검색 결과 확인 실패')
  for row in out['items']:row['category_candidates']=classify(row['title'])
  return {'source':'UNIST 현재 게시판의 제목 검색','query':query.strip(),'page':page_number,'checked_at':datetime.now(timezone.utc).isoformat(),'scope':'현재 게시판의 서버 측 제목 검색 결과 한 페이지; 본문·첨부 내용은 별도 확인',**out}
 finally:ws.close()

def open_searched_notice(endpoint,query,notice_id,title,page_number=1):
 """Re-run a title search in the browser and open a verified page result."""
 if not isinstance(notice_id,str) or not re.fullmatch(r'\d{1,30}',notice_id) or not isinstance(title,str) or not title or len(title)>500:raise ValueError('검색 결과의 정확한 ID와 제목이 필요합니다.')
 result=search_board(endpoint,query,page_number)
 if not any(row['id']==notice_id and row['title']==title for row in result['items']):raise RuntimeError('지정된 검색 페이지에 해당 공지가 없습니다.')
 first_ids={row['id'] for row in search_board(endpoint,query,1)['items']} if page_number>1 else set()
 with urllib.request.urlopen(endpoint.rstrip('/')+'/json/list',timeout=5) as f:pages=json.load(f)
 candidates=[p for p in pages if p.get('type')=='page' and urlparse(p.get('url','')).hostname=='uspace.unist.ac.kr' and urlparse(p.get('url','')).path=='/uspace/Cabinet/MainPage.bzr']
 if len(candidates)!=1:raise RuntimeError('학교 게시판 목록 하나를 열어 주세요.')
 ws=websocket.create_connection(candidates[0]['webSocketDebuggerUrl'],timeout=8,suppress_origin=True)
 try:
  expr="(()=>{let x=document.querySelector('[name=MainPage_superMain_main_list_listSearch_Title]'),b=document.getElementById('MainPage_superMain_main_list_listSearch_searchButton');if(!x||!b)return false;x.value="+json.dumps(query.strip(),ensure_ascii=False)+";b.click();return true})()"
  ws.send(json.dumps({'id':1,'method':'Runtime.evaluate','params':{'expression':expr,'returnByValue':True}}))
  while True:
   reply=json.loads(ws.recv())
   if reply.get('id')==1:break
  if not reply.get('result',{}).get('result',{}).get('value'):raise RuntimeError('검색 화면을 열지 못했습니다.')
 finally:ws.close()
 if page_number>1:
  for _ in range(20):
   time.sleep(.5)
   try:
    first=read_detail(endpoint,'list')['items']
    if first and {row['id'] for row in first}==first_ids:break
   except RuntimeError:pass
  else:raise RuntimeError('검색 결과 화면을 확인하지 못했습니다.')
  ws=websocket.create_connection(candidates[0]['webSocketDebuggerUrl'],timeout=8,suppress_origin=True)
  try:
   expr="(()=>{let f=window.bzr_framework_control_pager_WebPager_clickPager;if(typeof f!=='function')return false;f("+json.dumps(str(page_number-1))+",'bzr_event_MainPage_superMain_main_list_listPager_webPager_webPager_indexClick');return true})()"
   ws.send(json.dumps({'id':1,'method':'Runtime.evaluate','params':{'expression':expr,'returnByValue':True}}))
   while True:
    reply=json.loads(ws.recv())
    if reply.get('id')==1:break
   if not reply.get('result',{}).get('result',{}).get('value'):raise RuntimeError('검색 페이지 이동을 시작하지 못했습니다.')
  finally:ws.close()
 for _ in range(20):
  time.sleep(.5)
  try:
   rows=read_detail(endpoint,'list')['items']
   if any(row['id']==notice_id and row['title']==title for row in rows):return read_detail(endpoint,'open',{'id':notice_id,'title':title})
  except RuntimeError:pass
 raise RuntimeError('검색 결과 화면에서 선택한 공지를 확인하지 못했습니다.')

def main():
 for line in sys.stdin:
  try:
   msg=json.loads(line); ident=msg.get('id'); method=msg.get('method'); p=msg.get('params') or {}
   if ident is None:continue
   if method=='initialize': result={'protocolVersion':'2024-11-05','capabilities':{'tools':{}},'serverInfo':{'name':'nubi-campus-notices','version':'0.1.0'}}
   elif method=='ping':result={}
   elif method=='tools/list':result={'tools':[{'name':'nubi_doosan_2027_relevance','description':'Evaluate verified scholarship criteria using supplied student facts; missing information is unknown.','inputSchema':{'type':'object','properties':{'level':{'type':'string'},'nationality':{'type':'string'},'year_2027_spring':{'type':'integer'},'enrolled_both_2027_terms':{'type':'boolean'},'income_bracket_2026_fall':{'type':'integer'},'ceremony_available':{'type':'boolean'},'gpa':{'type':'number'},'gpa_scale':{'type':'number'}},'additionalProperties':False}},{'name':'nubi_portal_visible_notices','description':'Read the currently visible UNIST portal home notice preview; not a complete board or background monitor.','inputSchema':{'type':'object','properties':{},'additionalProperties':False}},{'name':'nubi_portal_preview_open','description':'Open a notice from the current portal preview by exact ID and title','inputSchema':{'type':'object','properties':{'id':{'type':'string'},'title':{'type':'string'}},'required':['id','title'],'additionalProperties':False}},{'name':'nubi_portal_board_sync','description':'Compare the visible UNIST board page with a local snapshot','inputSchema':{'type':'object','properties':{},'additionalProperties':False}},{'name':'nubi_portal_board_list','description':'Read the current UNIST board page','inputSchema':{'type':'object','properties':{},'additionalProperties':False}},{'name':'nubi_portal_board_open','description':'Open a notice from the current board by exact id and title','inputSchema':{'type':'object','properties':{'id':{'type':'string'},'title':{'type':'string'}},'required':['id','title'],'additionalProperties':False}},{'name':'nubi_portal_notice_detail','description':'Read the currently open UNIST portal notice detail and body; never submit or change it.','inputSchema':{'type':'object','properties':{},'additionalProperties':False}}]}
   elif method=='tools/call' and p.get('name')=='nubi_campus_board_search_open':
    try:
     args=p.get('arguments') or {}
     if not {'query','id','title'}<=set(args) or set(args)-{'query','id','title','page'}:raise ValueError('검색어와 정확한 ID·제목이 필요합니다.')
     result={'content':[{'type':'text','text':json.dumps(open_searched_notice(os.environ.get('NUBI_CDP_ENDPOINT','http://127.0.0.1:19333'),args['query'],args['id'],args['title'],args.get('page',1)),ensure_ascii=False)}]}
    except Exception as e:result={'content':[{'type':'text','text':str(e)}],'isError':True}
   elif method=='tools/call' and p.get('name')=='nubi_campus_board_search':
    try:
     args=p.get('arguments') or {}
     if set(args)-{'query','page'}:raise ValueError('지원하지 않는 검색 인자')
     result={'content':[{'type':'text','text':json.dumps(search_board(os.environ.get('NUBI_CDP_ENDPOINT','http://127.0.0.1:19333'),args.get('query'),args.get('page',1)),ensure_ascii=False)}]}
    except Exception as e:result={'content':[{'type':'text','text':str(e)}],'isError':True}
   elif method=='tools/call' and p.get('name')=='nubi_portal_board_page':
    try:result={'content':[{'type':'text','text':json.dumps(read_board_page(os.environ.get('NUBI_CDP_ENDPOINT','http://127.0.0.1:19333'),(p.get('arguments') or {}).get('page')),ensure_ascii=False)}]}
    except Exception as e:result={'content':[{'type':'text','text':str(e)}],'isError':True}
   elif method=='tools/call' and p.get('name')=='nubi_doosan_2027_relevance':
    try:result={'content':[{'type':'text','text':json.dumps(doosan_2027(p.get('arguments') or {}),ensure_ascii=False)}]}
    except Exception as e:result={'content':[{'type':'text','text':str(e)}],'isError':True}
   elif method=='tools/call' and p.get('name') in ('nubi_portal_visible_notices','nubi_portal_notice_detail','nubi_portal_board_list','nubi_portal_board_open','nubi_portal_preview_open','nubi_portal_board_sync') and (p.get('arguments',{})=={} or p.get('name') in ('nubi_portal_board_open','nubi_portal_preview_open')):
    try: result={'content':[{'type':'text','text':json.dumps(read_portal(os.environ.get('NUBI_CDP_ENDPOINT','http://127.0.0.1:19333'),p.get('arguments',{}) if p.get('name')=='nubi_portal_preview_open' else None) if p.get('name') in ('nubi_portal_visible_notices','nubi_portal_preview_open') else sync_notices(os.environ.get('NUBI_NOTICE_DB',os.path.expanduser('~/.local/share/nubi-campus/notices.sqlite')),read_detail(os.environ.get('NUBI_CDP_ENDPOINT','http://127.0.0.1:19333'),'list')['items']) if p.get('name')=='nubi_portal_board_sync' else read_detail(os.environ.get('NUBI_CDP_ENDPOINT','http://127.0.0.1:19333'),{'nubi_portal_notice_detail':'detail','nubi_portal_board_list':'list','nubi_portal_board_open':'open'}[p.get('name')],p.get('arguments',{})),ensure_ascii=False)}]}
    except Exception as e:result={'content':[{'type':'text','text':str(e)}],'isError':True}
   else:raise ValueError('Unknown method or invalid arguments')
   if method=='tools/list':
    result['tools'].append({'name':'nubi_portal_board_page','description':'Read a numbered page of the currently open UNIST board without changing the visible page.','inputSchema':{'type':'object','properties':{'page':{'type':'integer','minimum':1,'maximum':100}},'required':['page'],'additionalProperties':False}})
    result['tools'].append({'name':'nubi_campus_board_search','description':'Search titles across the currently open UNIST board with its server-side search form; returns one page and has_next. This does not read notice bodies.','inputSchema':{'type':'object','properties':{'query':{'type':'string','minLength':1,'maxLength':80},'page':{'type':'integer','minimum':1,'maximum':100}},'required':['query'],'additionalProperties':False}})
    result['tools'].append({'name':'nubi_campus_board_search_open','description':'Open an exact ID and title from a specified page of nubi_campus_board_search. Then call nubi_portal_notice_detail to read the body.','inputSchema':{'type':'object','properties':{'query':{'type':'string','minLength':1,'maxLength':80},'id':{'type':'string'},'title':{'type':'string'},'page':{'type':'integer','minimum':1,'maximum':100}},'required':['query','id','title'],'additionalProperties':False}})
   print(json.dumps({'jsonrpc':'2.0','id':ident,'result':result},ensure_ascii=False),flush=True)
  except Exception as e:print(json.dumps({'jsonrpc':'2.0','id':locals().get('ident'),'error':{'code':-32602,'message':str(e)}},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
