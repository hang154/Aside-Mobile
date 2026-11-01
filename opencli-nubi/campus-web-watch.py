#!/usr/bin/env python3
"""Best-effort watch of three UNIST boards via existing local CDP.

Requires this computer, ADB and tablet WebView to stay connected. Reads only the
first listing page; does not change the user's page.
"""
import argparse, importlib.util, json, os, re, shlex, subprocess, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import websocket
from campus_notice_store import sync

MODULE=Path(__file__).with_name('campus-notices-mcp.py')
spec=importlib.util.spec_from_file_location('campus_notices_mcp', MODULE)
notices=importlib.util.module_from_spec(spec);spec.loader.exec_module(notices)

def relevant(title,level):
    # A single explicit audience marker can rule out a student level.
    markers=re.findall(r'\[([^\]]+)\]',title)
    audience=set()
    for marker in markers:
        if re.search(r'(?i)(?:\bUG\b|학부)',marker):audience.add('학부')
        if re.search(r'(?i)(?:\bG\b|대학원)',marker):audience.add('대학원')
    return not audience or level in audience

def notify(title,body):
    command='cmd notification post -t '+shlex.quote(title)+' nubi-campus-watch '+shlex.quote(body)
    p=subprocess.run(['adb','shell',command],capture_output=True,text=True,timeout=10)
    if p.returncode: raise RuntimeError('기기 알림 명령 실패')
    for attempt in range(6):
        listing=subprocess.run(['adb','shell','cmd','notification','list'],capture_output=True,text=True,timeout=10)
        if listing.returncode==0 and '|nubi-campus-watch|' in listing.stdout:return
        time.sleep(.5)
    raise RuntimeError('기기 알림 등록 확인 실패')

def fetch_boards(endpoint):
    u=urlparse(endpoint)
    if u.scheme!='http' or u.hostname not in ('127.0.0.1','localhost') or u.username or u.password:raise ValueError('local CDP only')
    with urllib.request.urlopen(endpoint.rstrip('/')+'/json/list',timeout=5) as f:pages=json.load(f)
    matches=[p for p in pages if p.get('type')=='page' and urlparse(p.get('url','')).hostname=='uspace.unist.ac.kr' and urlparse(p.get('url','')).path in ('/uspace/Cabinet/MainPage.bzr','/uspace/Portal/Enterprise/DefaultPage.bzr')]
    if len(matches)!=1:raise RuntimeError('로그인된 학교 게시판 하나를 열어 주세요.')
    target=urlparse(matches[0]['webSocketDebuggerUrl'])
    if target.scheme!='ws' or target.hostname not in ('127.0.0.1','localhost'):raise RuntimeError('예상하지 못한 CDP 주소')
    ws=websocket.create_connection(matches[0]['webSocketDebuggerUrl'],timeout=8,suppress_origin=True)
    try:
        expression=r'''(async()=>{let output=[];for(const id of ['1978','1126','1124']){let response=await fetch('/uspace/Cabinet/MainPage.bzr?cabinetInstanceID='+id,{credentials:'same-origin',cache:'no-store'});if(!response.ok)throw Error('board fetch failed '+id);let doc=new DOMParser().parseFromString(await response.text(),'text/html');let rows=[...doc.querySelectorAll('tr')].map(tr=>{let c=tr.cells;if(c.length!==8)return null;let a=c[4].querySelector('a[onclick*=TitleClick]');if(!a)return null;let m=(a.getAttribute('onclick')||'').match(/TitleClick\('[^']*','(\d+)','(\d+)'/);let title=a.textContent.trim();return m&&title&&m[2]===id?{number:c[1].textContent.trim(),title,posted:c[6].textContent.trim(),id:m[1],board_id:m[2],has_attachment:!!c[2].querySelector('img')}:null}).filter(Boolean);if(!rows.length)throw Error('empty or unauthenticated board '+id);output.push({board_id:id,items:rows})}return output})()'''
        ws.send(json.dumps({'id':1,'method':'Runtime.evaluate','params':{'expression':expression,'awaitPromise':True,'returnByValue':True}}))
        while True:
            response=json.loads(ws.recv())
            if response.get('id')==1:
                if 'error' in response or response.get('result',{}).get('exceptionDetails'):raise RuntimeError('게시판 요청 실패 또는 로그인 만료')
                result=response.get('result',{}).get('result',{}).get('value')
                if not isinstance(result,list) or len(result)!=3:raise RuntimeError('게시판 결과 확인 실패')
                return result
    finally:ws.close()

def run_once(endpoint,db,level,baseline=False):
    pages=fetch_boards(endpoint)
    rows=[row for page in pages for row in page['items']]
    matches=[]
    def send_before_commit(changes):
        matches.extend(r for r in changes if relevant(r['title'],level) and notices.classify(r['title']))
        if matches and not baseline:notify('누비 학교 공지 '+str(len(matches))+'건', matches[0]['title']+' · 원문 대상과 기한 확인')
    # A failed notification rolls back the snapshot so a later run can retry.
    result=sync(db,rows,on_changes=send_before_commit)
    return {'checked_at':result['checked_at'],'scanned':result['scanned'],'boards':[{'board_id':p['board_id'],'rows':len(p['items'])} for p in pages],'changed':len(result['changes']),'relevant_changed_candidates':len(matches),'notification_verified':bool(matches and not baseline),'scope':result['scope']+'; 변경 후보 0은 기존 관련 공지가 없다는 뜻이 아님'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--endpoint',default='http://127.0.0.1:19333');p.add_argument('--db',required=True);p.add_argument('--level',choices=['학부','대학원'],default='학부');p.add_argument('--interval',type=int,default=900);p.add_argument('--once',action='store_true');a=p.parse_args()
    if a.interval<60:raise SystemExit('interval must be at least 60 seconds')
    baseline=not Path(a.db).exists()
    while True:
        try:
            result=run_once(a.endpoint,a.db,a.level,baseline);baseline=False
            print(json.dumps({'state':'ok',**result},ensure_ascii=False),flush=True)
        except Exception as e:
            print(json.dumps({'state':'error','time':datetime.now(timezone.utc).isoformat(),'reason':str(e)},ensure_ascii=False),flush=True)
        if a.once:break
        time.sleep(a.interval)
if __name__=='__main__':main()
