#!/usr/bin/env python3
"""Read current UNIST course search results from an existing tablet WebView."""
import json, os, re, sys, time, urllib.request
from datetime import datetime, timezone
from urllib.parse import urlparse
import websocket

def refresh_current(endpoint):
    u=urlparse(endpoint)
    if u.scheme!='http' or u.hostname not in ('127.0.0.1','localhost') or u.username or u.password:raise ValueError('CDP는 로컬 HTTP 주소만 사용할 수 있습니다.')
    with urllib.request.urlopen(endpoint.rstrip('/')+'/json/list',timeout=5) as f:pages=json.load(f)
    candidates=[p for p in pages if p.get('type')=='page' and urlparse(p.get('url','')).hostname=='portal.unist.ac.kr' and p.get('title','').startswith('개설강좌 조회')]
    if len(candidates)!=1:raise RuntimeError('로그인된 포털의 개설강좌 조회 화면 하나를 열어 주세요.')
    url=candidates[0]['webSocketDebuggerUrl'];target=urlparse(url)
    if target.scheme!='ws' or target.hostname not in ('127.0.0.1','localhost'):raise RuntimeError('예상하지 못한 디버깅 주소입니다.')
    ws=websocket.create_connection(url,timeout=8,suppress_origin=True);seq=0
    def call(method,params=None):
        nonlocal seq
        seq+=1;ident=seq;ws.send(json.dumps({'id':ident,'method':method,'params':params or {}}))
        while True:
            r=json.loads(ws.recv())
            if r.get('id')==ident:
                if 'error' in r:raise RuntimeError('강좌 화면 접근 실패')
                return r['result']
    def frames(tree):
        yield tree['frame']
        for child in tree.get('childFrames',[]):yield from frames(child)
    try:
        frameset=list(frames(call('Page.getFrameTree')['frameTree']))
        candidates=[f for f in frameset if f.get('name')=='isolatedWorkArea' and urlparse(f.get('url','')).hostname=='s4hana.unist.ac.kr' and '/ZCMW5223' in urlparse(f.get('url','')).path]
        if len(candidates)!=1:raise RuntimeError('개설강좌 조회 화면이 아닙니다.')
        ctx=call('Page.createIsolatedWorld',{'frameId':candidates[0]['id'],'worldName':'nubi-course-refresh'})['executionContextId']
        expression="(()=>{let b=[...document.querySelectorAll('[role=button]')].filter(x=>x.getAttributeNames().some(n=>n.includes('v_main.btn_majo')));if(b.length!==1)return false;b[0].click();return true})()"
        result=call('Runtime.evaluate',{'contextId':ctx,'expression':expression,'returnByValue':True})
        if result.get('exceptionDetails') or result.get('result',{}).get('value') is not True:raise RuntimeError('강좌 검색 버튼을 확인하지 못했습니다.')
    finally:ws.close()
    for attempt in range(8):
        time.sleep(1)
        try:return snapshot(endpoint)
        except RuntimeError:
            if attempt==7:raise

def snapshot(endpoint, query=''):
    u = urlparse(endpoint)
    if u.scheme != 'http' or u.hostname not in ('127.0.0.1', 'localhost') or u.username or u.password:
        raise ValueError('CDP는 로컬 HTTP 주소만 사용할 수 있습니다.')
    if not isinstance(query, str) or len(query) > 100:
        raise ValueError('과목 검색어는 100자 이내여야 합니다.')
    with urllib.request.urlopen(endpoint.rstrip('/') + '/json/list', timeout=5) as f:
        pages = json.load(f)
    candidates = [p for p in pages if p.get('type') == 'page' and urlparse(p.get('url','')).hostname == 'portal.unist.ac.kr' and p.get('title','').startswith('개설강좌 조회')]
    if len(candidates) != 1:
        raise RuntimeError('로그인된 포털의 개설강좌 조회 화면 하나를 열어 주세요.')
    wsurl = candidates[0]['webSocketDebuggerUrl']; parsed = urlparse(wsurl)
    if parsed.scheme != 'ws' or parsed.hostname not in ('127.0.0.1', 'localhost'):
        raise RuntimeError('예상하지 못한 디버깅 주소입니다.')
    ws = websocket.create_connection(wsurl, timeout=8, suppress_origin=True); seq = 0
    def call(method, params=None):
        nonlocal seq
        seq += 1; ident = seq
        ws.send(json.dumps({'id': ident, 'method': method, 'params': params or {}}))
        while True:
            result = json.loads(ws.recv())
            if result.get('id') == ident:
                if 'error' in result: raise RuntimeError('화면을 읽지 못했습니다.')
                return result['result']
    def frames(tree):
        yield tree['frame']
        for child in tree.get('childFrames', []): yield from frames(child)
    try:
        all_frames = list(frames(call('Page.getFrameTree')['frameTree']))
        found = [f for f in all_frames if f.get('name') == 'isolatedWorkArea' and urlparse(f.get('url','')).hostname == 's4hana.unist.ac.kr' and '/ZCMW5223' in urlparse(f.get('url','')).path]
        if len(found) != 1: raise RuntimeError('개설강좌 조회 화면의 결과 프레임을 찾지 못했습니다.')
        ctx = call('Page.createIsolatedWorld', {'frameId': found[0]['id'], 'worldName':'nubi-courses'})['executionContextId']
        expression = r'''(()=>{const rows=[...document.querySelectorAll('tr')].map(r=>[...r.cells].map(c=>c.innerText.trim())).filter(c=>c.length===15 && /^[A-Z]{2,5}[0-9]{5}$/.test(c[5]) && /^\d+$/.test(c[9]) && /^\d+$/.test(c[10]));const values=[...document.querySelectorAll('input,select')].filter(e=>e.offsetParent).map(e=>e.value);return {academic_year:values.find(v=>/^\d{4}학년도$/.test(v))||null,semester:values.find(v=>/^\d\s*학기$/.test(v))||null,rows:rows.map(c=>({department:c[4],code:c[5],title:c[6],instructor:c[7],credits:c[8],capacity:Number(c[9]),available:Number(c[10]),schedule:c[11],program:c[12]}))};})()'''
        result = call('Runtime.evaluate', {'contextId':ctx,'expression':expression,'returnByValue':True})
        if result.get('exceptionDetails'): raise RuntimeError('강좌 목록 판독 실패')
        page = result.get('result',{}).get('value')
        if not isinstance(page, dict) or not isinstance(page.get('rows'), list): raise RuntimeError('강좌 조회 결과를 읽지 못했습니다.')
        rows = page['rows']
        if not rows: raise RuntimeError('읽을 수 있는 강좌 결과가 없습니다. 조회 조건을 선택하고 검색해 주세요.')
        matching = [r for r in rows if query.casefold() in (r['code']+' '+r['title']+' '+r['department']).casefold()]
        return {'source':'UNIST 포털 개설강좌 조회의 현재 결과', 'checked_at':datetime.now(timezone.utc).isoformat(), 'scope':'현재 검색 결과만; 여석과 신청 가능 여부는 변동', 'academic_year':page.get('academic_year'), 'semester':page.get('semester'), 'total_visible':len(rows), 'items':matching}
    finally:
        ws.close()

def main():
    for line in sys.stdin:
        ident = None
        try:
            m=json.loads(line); ident=m.get('id'); method=m.get('method'); params=m.get('params') or {}
            if ident is None: continue
            if method == 'initialize': result={'protocolVersion':'2024-11-05','capabilities':{'tools':{}},'serverInfo':{'name':'nubi-campus-courses','version':'0.1.0'}}
            elif method == 'ping': result={}
            elif method == 'tools/list': result={'tools':[{'name':'nubi_course_visible_results','description':'Read and filter currently displayed UNIST course results. Does not search or register.','inputSchema':{'type':'object','properties':{'query':{'type':'string','maxLength':100}},'additionalProperties':False}},{'name':'nubi_course_refresh_current','description':'Search the currently selected year, semester and major on the open UNIST course search page. Does not register.','inputSchema':{'type':'object','properties':{},'additionalProperties':False}}]}
            elif method == 'tools/call' and params.get('name') == 'nubi_course_refresh_current':
                try:
                    if params.get('arguments') not in (None,{}):raise ValueError('지원하지 않는 인자입니다.')
                    value=refresh_current(os.environ.get('NUBI_CDP_ENDPOINT','http://127.0.0.1:19333'))
                    result={'content':[{'type':'text','text':json.dumps(value,ensure_ascii=False)}]}
                except Exception as exc: result={'content':[{'type':'text','text':str(exc)}],'isError':True}
            elif method == 'tools/call' and params.get('name') == 'nubi_course_visible_results':
                try:
                    args=params.get('arguments') or {}
                    if set(args)-{'query'}: raise ValueError('지원하지 않는 검색 인자입니다.')
                    value=snapshot(os.environ.get('NUBI_CDP_ENDPOINT','http://127.0.0.1:19333'),args.get('query',''))
                    result={'content':[{'type':'text','text':json.dumps(value,ensure_ascii=False)}]}
                except Exception as exc: result={'content':[{'type':'text','text':str(exc)}],'isError':True}
            else: raise ValueError('지원하지 않는 요청입니다.')
            print(json.dumps({'jsonrpc':'2.0','id':ident,'result':result},ensure_ascii=False),flush=True)
        except Exception as exc:
            print(json.dumps({'jsonrpc':'2.0','id':ident,'error':{'code':-32602,'message':str(exc)}},ensure_ascii=False),flush=True)
if __name__ == '__main__': main()
