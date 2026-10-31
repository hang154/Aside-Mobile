#!/usr/bin/env python3
"""Single foreground goal browser over pinned/authenticated HTTPS. Public exploration only."""
import json,os,re,ssl,sys,time,urllib.request
from urllib.parse import urlsplit
url=os.environ.get('NUBI_GOAL_RELAY_URL','https://127.0.0.1:18444').rstrip('/')
u=urlsplit(url)
if u.scheme!='https' or u.hostname not in ('127.0.0.1','localhost','::1') or u.username or u.password or u.path or u.query or u.fragment:raise SystemExit('Local HTTPS controller required')
token=None;context=None
PROVIDERS=['youtube','naverweb','11st','munto','kakaomap','realestate','kmooc','inflearn']
def schema(properties,required):return {'type':'object','properties':properties,'required':required,'additionalProperties':False}
gid={'type':'string','description':'Owned goal_id returned by nubi_goal_open'}
DEFINITIONS=[
 {'name':'nubi_goal_open','description':'Open the native fitness/love/grades/home goal and return its real ID, title and public topic. Call first.','inputSchema':schema({'character':{'type':'string','enum':['fitness','love','grades','home']}},['character'])},
 {'name':'nubi_goal_search','description':'Search an allowlisted public site inside the CURRENT goal on the real tablet. One browser; call observe after each search before another search. Returns navigation requested, not results. munto filters public recommended cards by goal words; kmooc is homepage navigation, not full course search.','inputSchema':schema({'goal_id':gid,'provider':{'type':'string','enum':PROVIDERS},'query':{'type':'string','maxLength':100}},['goal_id','provider','query'])},
 {'name':'nubi_goal_observe','description':'Read actual public result metadata (up to 8) or selected source page title. If not_ready retry once. No video/body analysis. Returns observation_id for selecting a result.','inputSchema':schema({'goal_id':gid},['goal_id'])},
 {'name':'nubi_goal_select','description':'Open one actual result (zero-based index) from the latest observation of this goal. Rejects stale lists. Read-only navigation, never purchase/join. Observe afterward.','inputSchema':schema({'goal_id':gid,'observation_id':{'type':'string'},'index':{'type':'integer','minimum':0,'maximum':7}},['goal_id','observation_id','index'])},
 {'name':'nubi_goal_report','description':'Save your final Korean exploration summary into this native goal. Only use source_urls returned by successful observations. Distinguish candidates from confirmed price/match/course, never claim purchase/payment. After successful report, give final answer without more tools.','inputSchema':schema({'goal_id':gid,'summary':{'type':'string','maxLength':3000},'source_urls':{'type':'array','items':{'type':'string'},'minItems':1,'maxItems':12}},['goal_id','summary','source_urls'])}]
BYNAME={x['name']:x for x in DEFINITIONS}
def validate(name,a):
 if name not in BYNAME or not isinstance(a,dict):raise ValueError('Unknown tool or arguments')
 spec=BYNAME[name]['inputSchema']
 if set(a)!=set(spec['required']):raise ValueError('Exact required arguments only')
 if name=='nubi_goal_open':
  if a['character'] not in ('fitness','love','grades','home'):raise ValueError('Unknown character')
 else:
  if not isinstance(a['goal_id'],str) or not re.fullmatch(r'[0-9a-f-]{36}',a['goal_id']):raise ValueError('Owned goal ID required')
 if name=='nubi_goal_search' and (a['provider'] not in PROVIDERS or not isinstance(a['query'],str) or not 1<=len(a['query'].strip())<=100):raise ValueError('Invalid search')
 if name=='nubi_goal_select' and (type(a['index']) is not int or not 0<=a['index']<=7 or not isinstance(a['observation_id'],str) or len(a['observation_id'])>64):raise ValueError('Invalid selection')
 if name=='nubi_goal_report' and (not isinstance(a['summary'],str) or not 1<=len(a['summary'])<=3000 or not isinstance(a['source_urls'],list) or not 1<=len(a['source_urls'])<=12 or any(not isinstance(x,str) or len(x)>2000 for x in a['source_urls'])):raise ValueError('Invalid report')
def post(path,data):
 global token,context
 if token is None:
  token=open(os.environ['NUBI_GOAL_RELAY_TOKEN_FILE'],encoding='ascii').read().strip();context=ssl.create_default_context(cafile=os.environ['NUBI_GOAL_RELAY_CA_FILE']);context.check_hostname=False
 request=urllib.request.Request(url+path,data=json.dumps(data).encode(),headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'},method='POST')
 with urllib.request.urlopen(request,context=context,timeout=5) as r:return json.load(r)
def call(name,a):
 validate(name,a);identifier=post('/command',{'op':name.removeprefix('nubi_'),**a})['id'];end=time.monotonic()+25
 while time.monotonic()<end:
  result=post('/get-result',{'id':identifier})['result']
  if result is not None:return result
  time.sleep(.3)
 raise TimeoutError('Goal browser must be paired and foreground')
def handle(req):
 ident=req.get('id');method=req.get('method');p=req.get('params') or {}
 if method=='notifications/initialized':return None
 if method=='initialize':return {'jsonrpc':'2.0','id':ident,'result':{'protocolVersion':'2024-11-05','capabilities':{'tools':{}},'serverInfo':{'name':'nubi-goals','version':'0.2.2'}}}
 if method=='tools/list':return {'jsonrpc':'2.0','id':ident,'result':{'tools':DEFINITIONS}}
 if method=='tools/call':
  try:r=call(p.get('name'),p.get('arguments'));result={'isError':'error' in r,'content':[{'type':'text','text':json.dumps(r,ensure_ascii=False)}]}
  except Exception as e:result={'isError':True,'content':[{'type':'text','text':type(e).__name__+': '+str(e)}]}
  return {'jsonrpc':'2.0','id':ident,'result':result}
 return {'jsonrpc':'2.0','id':ident,'error':{'code':-32601,'message':'Method not found'}}
if __name__=='__main__':
 for line in sys.stdin:
  try:
   response=handle(json.loads(line))
   if response is not None:print(json.dumps(response,ensure_ascii=False),flush=True)
  except Exception:print(json.dumps({'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'Invalid request'}}),flush=True)
