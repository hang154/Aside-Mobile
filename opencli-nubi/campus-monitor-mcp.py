#!/usr/bin/env python3
"""Expose the existing campus web monitor status and explicit check to MCP."""
import importlib.util,json,os,sqlite3,subprocess,sys
from pathlib import Path
source=Path(__file__).with_name('campus-web-watch.py');spec=importlib.util.spec_from_file_location('campus_web_watch',source);watch=importlib.util.module_from_spec(spec);spec.loader.exec_module(watch)
database=Path(os.environ.get('NUBI_WATCH_DB',str(Path.home()/'.local/share/nubi-campus/web-watch-three.sqlite'))).expanduser()
endpoint=os.environ.get('NUBI_CDP_ENDPOINT','http://127.0.0.1:19333')

def status():
 p=subprocess.run(['systemctl','--user','is-active','nubi-campus-web-watch.service'],capture_output=True,text=True,timeout=5)
 result={'service_active':p.returncode==0,'dependency':'컴퓨터 전원·태블릿 USB/ADB·로그인된 U-Space WebView','coverage':'학사·장학·전체 공지 첫 페이지의 제목·게시일·첨부 표시','interval_minutes':15}
 if database.exists():
  with sqlite3.connect('file:'+str(database)+'?mode=ro',uri=True) as db:
   result['last_checked'],result['tracked_unique_notices']=db.execute('SELECT MAX(updated),COUNT(*) FROM notices').fetchone()
 else:result.update(last_checked=None,tracked_unique_notices=0)
 return result

def main():
 definitions=[{'name':'nubi_campus_monitor_status','description':'Check local campus monitor process, last snapshot time and limitations.','inputSchema':{'type':'object','properties':{},'additionalProperties':False}},{'name':'nubi_campus_monitor_check','description':'Explicitly recheck three connected UNIST board first pages, compare snapshots and alert for matching changes.','inputSchema':{'type':'object','properties':{},'additionalProperties':False}}]
 for line in sys.stdin:
  ident=None
  try:
   msg=json.loads(line);ident=msg.get('id');method=msg.get('method');p=msg.get('params') or {}
   if ident is None:continue
   if method=='initialize':result={'protocolVersion':'2024-11-05','capabilities':{'tools':{}},'serverInfo':{'name':'nubi-campus-monitor','version':'0.1'}}
   elif method=='ping':result={}
   elif method=='tools/list':result={'tools':definitions}
   elif method=='tools/call' and p.get('name') in ('nubi_campus_monitor_status','nubi_campus_monitor_check'):
    try:
     if p.get('arguments') not in (None,{}):raise ValueError('이 도구는 인자를 받지 않습니다.')
     value=status() if p['name']=='nubi_campus_monitor_status' else watch.run_once(endpoint,str(database),'학부',not database.exists())
     result={'content':[{'type':'text','text':json.dumps(value,ensure_ascii=False)}]}
    except Exception as e:result={'content':[{'type':'text','text':str(e)}],'isError':True}
   else:raise ValueError('Unknown method')
   print(json.dumps({'jsonrpc':'2.0','id':ident,'result':result},ensure_ascii=False),flush=True)
  except Exception as e:print(json.dumps({'jsonrpc':'2.0','id':ident,'error':{'code':-32602,'message':str(e)}},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
