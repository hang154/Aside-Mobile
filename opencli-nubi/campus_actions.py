"""User-reviewed Outlook draft dispatch. Model tools may prepare, never approve.
A timeout is an unknown outcome, never permission to send again.
"""
import hashlib,json,os,sqlite3,time,uuid
from pathlib import Path
from documents.graph import esc
class MailActions:
 def __init__(self,path):
  self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
  with self.db() as db:db.execute('CREATE TABLE IF NOT EXISTS actions(id TEXT PRIMARY KEY,owner TEXT NOT NULL,draft TEXT NOT NULL,state TEXT NOT NULL,digest TEXT NOT NULL,snapshot TEXT NOT NULL,expires REAL NOT NULL,reason TEXT, UNIQUE(owner,draft))')
  self.path.chmod(0o600)
  with self.db() as db:db.execute('CREATE UNIQUE INDEX IF NOT EXISTS one_mailbox_draft ON actions(draft)')
 def db(self):return sqlite3.connect(self.path,timeout=10)
 def snapshot(self,graph,draft):
  m=graph.call('GET','/me/messages/'+esc(draft)+'?$select=id,isDraft,subject,body,toRecipients,ccRecipients,bccRecipients,hasAttachments,changeKey')
  if m.get('isDraft') is not True:raise ValueError('발송 가능한 임시저장 메일인지 확인하지 못했어요.')
  recipients={k:m.get(k,[]) for k in ('toRecipients','ccRecipients','bccRecipients')}
  if not recipients['toRecipients']:raise ValueError('실제 수신자를 먼저 지정해 주세요.')
  attachments=[]
  if m.get('hasAttachments'):
   for a in graph.attachments(draft):
    if a.get('@odata.type')!='#microsoft.graph.fileAttachment' or a.get('size',0)>2*1024*1024:raise ValueError('첨부는 2MiB 이하 파일만 검증할 수 있어요.')
    data=graph.download_attachment(draft,a['id']);attachments.append({'id':a['id'],'name':a['name'],'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
  snap={'id':m['id'],'subject':m.get('subject',''),'body':m.get('body',{}),'recipients':recipients,'attachments':attachments,'change_key':m.get('changeKey','')}
  raw=json.dumps(snap,ensure_ascii=False,sort_keys=True,separators=(',',':'));return snap,hashlib.sha256(raw.encode()).hexdigest()
 def prepare(self,owner,graph,draft):
  if not isinstance(owner,str) or not __import__('re').fullmatch(r'[a-f0-9-]{36}',owner):raise ValueError('연결된 기기 소유권이 필요해요.')
  snap,digest=self.snapshot(graph,draft)
  if len(json.dumps(snap,ensure_ascii=False).encode())>90000:raise ValueError('메일 검토 내용이 너무 커요. 첨부나 본문을 나눠 주세요.')
  with self.db() as db:
   other=db.execute('SELECT owner FROM actions WHERE draft=?',(draft,)).fetchone()
   if other and other[0]!=owner:raise ValueError('다른 기기에서 검토한 동일 메일이에요. 해당 기기의 처리 결과를 먼저 확인해 주세요.')
   row=db.execute('SELECT id,state,digest,expires FROM actions WHERE owner=? AND draft=?',(owner,draft)).fetchone()
   if row:
    if row[1] not in ('review','expired','cancelled'):return {'id':row[0],'state':row[1],'reason':'이미 발송 요청된 메일은 자동으로 다시 보내지 않아요.'}
    ident=row[0]
    db.execute('UPDATE actions SET state=?,digest=?,snapshot=?,expires=?,reason=NULL WHERE id=?',('review',digest,json.dumps(snap,ensure_ascii=False),time.time()+900,ident))
   else:
    ident=uuid.uuid4().hex;db.execute('INSERT INTO actions VALUES (?,?,?,?,?,?,?,?)',(ident,owner,draft,'review',digest,json.dumps(snap,ensure_ascii=False),time.time()+900,None))
  return {'id':ident,'state':'review','digest':digest,'note':'앱의 검토 화면에서 사람이 승인해야 발송할 수 있어요.'}
 def list(self,owner):
  with self.db() as db:
   rows=db.execute('SELECT id,state,digest,snapshot,expires,reason FROM actions WHERE owner=? ORDER BY rowid DESC LIMIT 20',(owner,)).fetchall()
  return [{'id':r[0],'state':'expired' if r[1]=='review' and r[4]<time.time() else r[1],'digest':r[2],'message':json.loads(r[3]),'expires':r[4],'reason':r[5]} for r in rows]
 def send(self,owner,ident,digest,graph):
  # This method is only exposed to the authenticated native review UI, not MCP.
  with self.db() as db:
   db.execute('BEGIN IMMEDIATE');r=db.execute('SELECT draft,state,digest,expires FROM actions WHERE id=? AND owner=?',(ident,owner)).fetchone()
   if not r:raise ValueError('다른 기기의 메일이거나 없는 검토 항목이에요.')
   if r[1]!='review':raise ValueError('이미 요청됐거나 취소된 항목이에요. 중복 발송하지 않아요.')
   if digest!=r[2] or r[3]<time.time():raise ValueError('승인 내용이 다르거나 15분 검토 시간이 지났어요. 다시 준비해 주세요.')
   db.execute("UPDATE actions SET state='checking' WHERE id=?",(ident,))
  try:
   _,current=self.snapshot(graph,r[0])
   if current!=digest:raise ValueError('검토 후 메일 내용 또는 첨부가 바뀌었어요. 다시 준비해 주세요.')
  except Exception:
   with self.db() as db:db.execute("UPDATE actions SET state='review',reason='발송 전 내용 확인 실패. 발송하지 않음.' WHERE id=?",(ident,))
   raise
  with self.db() as db:db.execute("UPDATE actions SET state='sending' WHERE id=?",(ident,))
  try:
   accepted=graph.call('POST','/me/messages/'+esc(r[0])+'/send')
   if not isinstance(accepted,dict) or accepted.get('http_status')!=202:raise RuntimeError('발송 접수 응답 미확인')
  except Exception:
   with self.db() as db:db.execute("UPDATE actions SET state='outcome_unknown',reason='발송 응답 미확인. 보낸 편지함을 확인하기 전 재발송 금지.' WHERE id=?",(ident,))
   return {'state':'outcome_unknown','id':ident}
  with self.db() as db:db.execute("UPDATE actions SET state='accepted',reason='Graph가 발송 요청을 접수함. 수신자 도착은 미확인.' WHERE id=?",(ident,))
  return {'state':'accepted','id':ident,'note':'발송 요청 접수. 수신자 도착 확인은 별개예요.'}
 def cancel(self,owner,ident):
  with self.db() as db:
   n=db.execute("UPDATE actions SET state='cancelled' WHERE id=? AND owner=? AND state IN ('review','expired')",(ident,owner)).rowcount
  if not n:raise ValueError('이미 발송 중인 요청은 취소 성공으로 표시할 수 없어요.')
  return {'id':ident,'state':'cancelled'}
