#!/usr/bin/env python3
"""stdio MCP document workflow with server-owned config/destination/workspace."""
import json,os,sys,uuid
from pathlib import Path
from documents.pipeline import run
TOOLS=[{'name':'nubi_document_run','description':'Read configured Outlook sources/templates, ask Qwen to author a cited budget, check arithmetic and missing facts, generate DOCX/HWPX, then upload only ready documents to the configured SharePoint folder and verify remote bytes. Missing information returns a draft, never fabricated totals or signatures.','inputSchema':{'type':'object','properties':{'instruction':{'type':'string','minLength':1,'maxLength':2000},'profile':{'type':'string','enum':['lseries','uirp','general']}},'required':['instruction','profile'],'additionalProperties':False}}]
for line in sys.stdin:
 q={}
 try:
  q=json.loads(line)
  if 'id' not in q:continue
  m=q['method'];p=q.get('params',{})
  if m=='initialize':r={'protocolVersion':'2024-11-05','capabilities':{'tools':{}},'serverInfo':{'name':'nubi-documents','version':'0.1'}}
  elif m=='tools/list':r={'tools':TOOLS}
  elif m=='tools/call':
   a=p.get('arguments',{})
   if p.get('name')!='nubi_document_run' or set(a)!={'instruction','profile'} or not isinstance(a['instruction'],str) or not 1<=len(a['instruction'])<=2000:raise ValueError('Invalid document tool arguments')
   root=Path(os.environ.get('NUBI_DOCUMENT_WORKSPACE',str(Path.home()/'.local/state/nubi-documents/jobs')));work=root/uuid.uuid4().hex
   data=run(a['instruction'],a['profile'],os.environ.get('NUBI_DOCUMENT_CONFIG',str(Path.home()/'.config/nubi-documents/config.json')),work)
   r={'content':[{'type':'text','text':json.dumps(data,ensure_ascii=False)}]}
  else:raise ValueError('Unsupported MCP method')
  out={'jsonrpc':'2.0','id':q['id'],'result':r}
 except Exception as e:out={'jsonrpc':'2.0','id':q.get('id'),'error':{'code':-32602,'message':type(e).__name__+': '+str(e)}}
 print(json.dumps(out,ensure_ascii=False),flush=True)
