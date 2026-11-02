#!/usr/bin/env python3
"""Local MCP for delegated Outlook search and user-reviewed drafts; never sends mail."""
import json,os,sys
from pathlib import Path
from documents.graph import Graph
from campus_mail import find_mail,create_draft
from campus_document import create_application

# --------------------------------------------------------------------------
# Deterministic transport. A real client (Qwen/Azrael worker) drives
# this stdio JSON-RCP interface; the graph config may carry an
# explicit test transport marker so the same wire contract can be
# exercised offline. Production configs omit the marker and build
# the regular Graph adapter (credentials stay behind the adapter).
# --------------------------------------------------------------------------
_FIXTURES=[
 {'id':'msg-01','subject':'2027년 두산연강재단 장학생 모집','receivedDateTime':'2026-10-15T09:00:00Z','webLink':'https://outlook.example/mail/msg-01','hasAttachments':True,
  'body':{'contentType':'Text','content':'2027년 1학기 입학 예정 학부생 대상 장학 선발. 평점 4.5 만점 기준 3.0 이상, 2026년 2학기 소득분위 6 이내 지원 가능. 장학증서 수여식 참석 가능 여부 확인 필요.'}},
 {'id':'msg-02','subject':'현장실습 참가 안내','receivedDateTime':'2026-10-20T10:00:00Z','webLink':'https://outlook.example/mail/msg-02','hasAttachments':False,
  'body':{'contentType':'Text','content':'이번 학기 현장실습 인턴십 참가 일정과 신청 방법을 안내합니다. 지원서류 접수는 학사지원팀으로 문의하세요.'}},
 # 제목에 규칙 키워드가 없고 본문에만 '수강·복학·휴학'이 있어 본문 경로로만 '학사'가 잡혀야 한다
 {'id':'msg-03','subject':'2026학년도 2학기 정기 점검 완료','receivedDateTime':'2026-09-01T08:30:00Z','webLink':'https://outlook.example/mail/msg-03','hasAttachments':False,
  'body':{'contentType':'Text','content':'2학기 수강신청은 포털에서 진행하며 수업 정원 확인 후 접수하세요. 복학이나 휴학 예정자는 별도 확인이 필요합니다.'}},
]

class DeterministicMailTransport:
 """Recorded Graph-compatible fake. Implements the two surfaces used
 by campus_mail: search(query,limit) and call(method,path,data)."""
 def __init__(self,deterministic_flag='normal'):
  self.calls=[]          # ordered {seq, kind, method, path, note}
  self._flag=deterministic_flag
  self._sid=0
  self._stored={}         # message id -> posted payload (stateful read-back)
  # Persist captured calls to a sidecar file so a test runner started
  # outside the process can independently inspect the traffic.
  self._persist=os.environ.get('NUBI_TEST_CALLS')

 def _record(self,kind,method,path,note=''):
  self._sid+=1;self.calls.append({'seq':self._sid,'kind':kind,'method':method,'path':path,'note':note})
  # 단일 JSON 라인으로 부록 로그를 덧붙인다(실패해도 흐름은 유지)
  if self._persist:
   try:
    with open(self._persist,'a',encoding='utf-8') as fh:fh.write(json.dumps({'seq':self._sid,'kind':kind,'method':method,'path':path,'note':note},ensure_ascii=False)+'\n')
   except OSError:pass

 def search(self,query,limit=20):
  q=query.lower()
  hits=[]
  for m in _FIXTURES:
   text=(m['subject']+' '+m['body']['content']).lower()
   if q in text:hits.append(m)
  self._record('mail_search','GET','/me/messages',f'q={q!r} matched={len(hits)}')
  return hits[:limit]

 def call(self,method,path,data=None,raw=False):
  # normalize: campus_mail calls with positional 'data' for both methods
  if method=='POST':
   self._record('message_post','POST',path,f"isDraft={'yes' if (data and data.get('isDraft')) else 'NO'} atts={len(data.get('attachments') or []) if data else 0}")
   # Stateful echo: store the posted message and reply with its id/draft flag.
   # A missing isDraft field yields isDraft=None, exactly as a strict
   # read-back check would reject a possibly-sent message.
   mid=f'draft-{len(self._stored)+1}'
   self._stored[mid]=dict(data)
   resp={'id':mid,'subject':data.get('subject',''),'isDraft':data.get('isDraft'),
          'hasAttachments':bool(data.get('attachments'))}
   return resp
  elif method=='GET':
   self._record('message_get','GET',path,'read-back verification')
   # read-back path carries a `?$select=...` query; message id is the final path segment
   _qp=path.split('?',1)[0].rstrip('/')
   _segs=[s for s in _qp.split('/') if s]
   mid=_segs[-1] if _segs else ''
   rec=self._stored.get(mid)
   if rec is None: return {'id':mid}
   # Read back the same fields create_draft selects after saving.
   return {'id':mid,'isDraft':rec.get('isDraft'),'subject':rec.get('subject',''),
           'hasAttachments':bool(rec.get('attachments')),
           'webLink':f'https://outlook.example/draft/{mid}'}
  self._record('other',method,path,'unmatched')
  return {}

def _build_graph(graph_cfg):
 """Select transport based on an explicit, opt-in test marker; otherwise
 build the standard Graph adapter. Credentials never cross the model boundary."""
 marker=graph_cfg.get('test_transport','')
 if marker in ('deterministic-mail-v1','deterministic-mail-drop-isdraft-v1'):
  return DeterministicMailTransport(marker)
 if marker and marker not in ('deterministic-mail-v1','deterministic-mail-drop-isdraft-v1'):
  raise ValueError('Unknown test_transport marker: '+marker)
 return Graph(graph_cfg)

def config():
 p=os.environ.get('NUBI_CAMPUS_MAIL_CONFIG')
 if not p:raise RuntimeError('NUBI_CAMPUS_MAIL_CONFIG에 본인 Graph 연결 설정이 필요합니다.')
 obj=json.loads(Path(p).expanduser().read_text())
 g=dict(obj['graph']);g['scopes']=['Mail.ReadWrite']
 return _build_graph(g),Path(obj['draft_directory']).expanduser().resolve()

def call(name,args):
 if name=='nubi_campus_document_draft':
  cfg=os.environ.get('NUBI_CAMPUS_MAIL_CONFIG')
  root=Path(json.loads(Path(cfg).expanduser().read_text())['draft_directory']).expanduser().resolve() if cfg else Path.home()/'.local/share/nubi-campus/drafts'
  return create_application(root,args)
 graph,root=config()
 if name=='nubi_campus_mail_prepare_send':
  from campus_actions import MailActions
  path=os.environ.get('NUBI_CAMPUS_ACTION_DB')
  if not path:raise RuntimeError('앱의 메일 검토 연결이 필요합니다.')
  if set(args)!={'draft_id'}:raise ValueError('임시저장 메일 ID만 전달하세요.')
  return MailActions(path).prepare(os.environ.get('NUBI_GOAL_DEVICE_SESSION',''),graph,args['draft_id'])
 if name=='nubi_campus_mail_search':
  if set(args)!={'query'}:raise ValueError('검색어가 필요합니다')
  return {'items':find_mail(graph,args['query'])}
 if name=='nubi_campus_mail_draft':
  if not set(args).issubset({'subject','body','recipient','attachment'}) or not {'subject','body'}.issubset(args):raise ValueError('초안 제목과 본문이 필요합니다')
  path=None
  if args.get('attachment'):
   path=Path(args['attachment']).expanduser().resolve()
   if not path.is_relative_to(root):raise ValueError('첨부는 지정된 초안 폴더의 파일만 가능합니다')
  return create_draft(graph,args['subject'],args['body'],args.get('recipient'),path)
 raise ValueError('Unknown tool')

def main():
 for line in sys.stdin:
  ident=None
  try:
   msg=json.loads(line);ident=msg.get('id');method=msg.get('method');p=msg.get('params') or {}
   if ident is None:continue
   if method=='initialize':result={'protocolVersion':'2024-11-05','capabilities':{'tools':{}},'serverInfo':{'name':'nubi-campus-mail','version':'0.1.0'}}
   elif method=='ping':result={}
   elif method=='tools/list':result={'tools':[{'name':'nubi_campus_mail_prepare_send','description':'Prepare an existing real draft for human review in the app. Never approves or sends.','inputSchema':{'type':'object','properties':{'draft_id':{'type':'string'}},'required':['draft_id'],'additionalProperties':False}},{'name':'nubi_campus_document_draft','description':'Create a draft from supplied facts and flag missing fields; never submits.','inputSchema':{'type':'object','properties':{'notice_title':{'type':'string'},'source':{'type':'string'},'applicant':{'type':'string'},'motivation':{'type':'string'},'experience':{'type':'string'}},'required':['notice_title'],'additionalProperties':False}},{'name':'nubi_campus_mail_search','description':'Search delegated Outlook for campus mail and classify titles.','inputSchema':{'type':'object','properties':{'query':{'type':'string','minLength':1,'maxLength':100}},'required':['query'],'additionalProperties':False}},{'name':'nubi_campus_mail_draft','description':'Create and verify a draft only; never sends. Attachment must be under configured draft folder.','inputSchema':{'type':'object','properties':{'subject':{'type':'string'},'body':{'type':'string'},'recipient':{'type':'string'},'attachment':{'type':'string'}},'required':['subject','body'],'additionalProperties':False}}]}
   elif method=='tools/call':
    try: result={'content':[{'type':'text','text':json.dumps(call(p.get('name'),p.get('arguments') or {}),ensure_ascii=False)}]}
    except Exception as e:result={'content':[{'type':'text','text':str(e)}],'isError':True}
   else:raise ValueError('Unknown method')
   print(json.dumps({'jsonrpc':'2.0','id':ident,'result':result},ensure_ascii=False),flush=True)
  except Exception as e:print(json.dumps({'jsonrpc':'2.0','id':ident,'error':{'code':-32602,'message':str(e)}},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
