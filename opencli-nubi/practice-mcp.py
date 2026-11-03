#!/usr/bin/env python3
"""Bounded local practice MCP; no real school submission tool exists here."""
import json,os,sys
from practice_workflow import DEFINITION,complete
for line in sys.stdin:
 try:
  q=json.loads(line);m=q.get('method');r=None
  if m=='initialize':r={'protocolVersion':'2024-11-05','capabilities':{'tools':{}},'serverInfo':{'name':'nubi-practice','version':'0.6.28'}}
  elif m=='tools/list':r={'tools':[DEFINITION]}
  elif m=='tools/call':
   try:
    p=q.get('params',{})
    if p.get('name')!=DEFINITION['name'] or p.get('arguments',{})!={}:raise ValueError('bounded practice tool required')
    result=complete(os.environ['NUBI_PRACTICE_OUTPUT']);r={'isError':result.get('state')!='completed','content':[{'type':'text','text':json.dumps(result,ensure_ascii=False)}]}
   except Exception as e:r={'isError':True,'content':[{'type':'text','text':json.dumps({'state':'failed','error':type(e).__name__+': '+str(e)[:220]})}]}
  elif m and m.startswith('notifications/'):continue
  else:raise ValueError('unknown method')
  print(json.dumps({'jsonrpc':'2.0','id':q.get('id'),'result':r},ensure_ascii=False),flush=True)
 except Exception:print(json.dumps({'jsonrpc':'2.0','id':None,'error':{'code':-32600,'message':'invalid request'}}),flush=True)
