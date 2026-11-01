#!/usr/bin/env python3
"""Local-only document drafts; no credentials, no external submission."""
import json,os,sys
from pathlib import Path
from campus_document import create_application

def main():
 root=Path(os.environ.get('NUBI_CAMPUS_DRAFT_DIR',str(Path.home()/'.local/share/nubi-campus/drafts'))).expanduser().resolve()
 definition={'name':'nubi_local_document_draft','description':'Create a DOCX application draft from supplied facts only. Missing fields are explicitly marked; does not submit.','inputSchema':{'type':'object','properties':{'notice_title':{'type':'string'},'source':{'type':'string'},'applicant':{'type':'string'},'motivation':{'type':'string'},'experience':{'type':'string'}},'required':['notice_title'],'additionalProperties':False}}
 for line in sys.stdin:
  ident=None
  try:
   m=json.loads(line);ident=m.get('id');method=m.get('method');p=m.get('params') or {}
   if ident is None:continue
   if method=='initialize':result={'protocolVersion':'2024-11-05','capabilities':{'tools':{}},'serverInfo':{'name':'nubi-campus-local-documents','version':'0.1'}}
   elif method=='ping':result={}
   elif method=='tools/list':result={'tools':[definition]}
   elif method=='tools/call' and p.get('name')=='nubi_local_document_draft':
    try:result={'content':[{'type':'text','text':json.dumps(create_application(root,p.get('arguments') or {}),ensure_ascii=False)}]}
    except Exception as e:result={'content':[{'type':'text','text':str(e)}],'isError':True}
   else:raise ValueError('Unknown method')
   print(json.dumps({'jsonrpc':'2.0','id':ident,'result':result},ensure_ascii=False),flush=True)
  except Exception as e:print(json.dumps({'jsonrpc':'2.0','id':ident,'error':{'code':-32602,'message':str(e)}},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
