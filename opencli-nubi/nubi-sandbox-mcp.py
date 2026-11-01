#!/usr/bin/env python3
"""Local stdio MCP client for the authenticated foreground browser relay."""
import json, os, ssl, sys, time, urllib.request
from urllib.parse import urlsplit
url=os.environ.get('NUBI_RELAY_URL','https://127.0.0.1:18453').rstrip('/')
u=urlsplit(url)
if u.scheme!='https' or u.hostname not in ('127.0.0.1','localhost','::1') or u.username or u.password or u.path or u.query or u.fragment:
    raise SystemExit('NUBI_RELAY_URL must be a localhost HTTPS URL')
token=open(os.environ['NUBI_RELAY_TOKEN_FILE'],encoding='ascii').read().strip()
context=ssl.create_default_context(cafile=os.environ['NUBI_RELAY_CA_FILE']);context.check_hostname=False

def post(path,data):
    req=urllib.request.Request(url+path,data=json.dumps(data).encode(),headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,context=context,timeout=5) as response: return json.load(response)
def call(op,params):
    command={'op':op}
    if params: raise ValueError('No arguments expected')
    identifier=post('/command',command)['id'];end=time.monotonic()+25
    while time.monotonic()<end:
        result=post('/get-result',{'id':identifier})['result']
        if result is not None: return result
        time.sleep(0.5)
    raise TimeoutError('Device did not answer; foreground pairing required')

def handle(req):
    id=req.get('id');method=req.get('method');p=req.get('params') or {}
    if method=='initialize': return {'jsonrpc':'2.0','id':id,'result':{'protocolVersion':'2024-11-05','capabilities':{'tools':{}},'serverInfo':{'name':'nubi-network-relay','version':'0.1'}}}
    if method=='notifications/initialized': return None
    if method=='tools/list': return {'jsonrpc':'2.0','id':id,'result':{'tools':[
      {'name':'nubi_sandbox_observe','description':'Read the current counter in the paired Nubi sandbox fixture app.','inputSchema':{'type':'object','properties':{},'additionalProperties':False}},
      {'name':'nubi_sandbox_click','description':'Press the Increase counter button in the paired sandbox fixture app; this changes only the disposable test counter.','inputSchema':{'type':'object','properties':{},'additionalProperties':False}}]}}
    if method=='tools/call':
        name=p.get('name'); args=p.get('arguments') or {}
        try:
            if not isinstance(args,dict) or name not in ('nubi_sandbox_observe','nubi_sandbox_click'): raise ValueError('Unknown tool or invalid arguments')
            result=call('fixture_click' if name.endswith('click') else 'fixture_observe',args)
            return {'jsonrpc':'2.0','id':id,'result':{'content':[{'type':'text','text':json.dumps(result,ensure_ascii=False)}],'isError':'error' in result}}
        except Exception as e: return {'jsonrpc':'2.0','id':id,'result':{'content':[{'type':'text','text':str(e)}],'isError':True}}
    return {'jsonrpc':'2.0','id':id,'error':{'code':-32601,'message':'Method not found'}}
for line in sys.stdin:
    try:
        response=handle(json.loads(line))
        if response is not None: print(json.dumps(response,ensure_ascii=False),flush=True)
    except Exception: print(json.dumps({'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'Invalid request'}}),flush=True)
