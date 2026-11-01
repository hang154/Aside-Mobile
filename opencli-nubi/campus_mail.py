"""Campus Outlook classification and draft-only Microsoft Graph actions."""
import base64, re
from pathlib import Path
from documents.graph import esc

RULES=[('장학',r'장학|scholarship'),('인턴십',r'인턴|현장실습|internship|\bcoop\b'),('상담',r'전공\s*상담|상담\s*신청|advising'),('세미나',r'강연|세미나|seminar|lecture'),('지원사업',r'지원사업|연구비|grant'),('시험',r'기말|시험|exam'),('학사',r'복학|휴학|수강|학점\s*교류|졸업')]
def classify(subject,preview=''):
 text=(subject+' '+preview)[:4000]
 return [name for name,pattern in RULES if re.search(pattern,text,re.I)]

def find_mail(graph,query,limit=20):
 if not isinstance(query,str) or not query.strip() or len(query)>100:raise ValueError('검색어는 1~100자여야 합니다')
 records=graph.search(query,limit=limit)
 items=[]
 for r in records:
  if not r.get('id'):continue
  # delegated Graph search selects `body` ({content type,content}); accept legacy flat bodyPreview too
  body=r.get('body');body_text=(str(body.get('content') or '')) if isinstance(body,dict) else str(r.get('bodyPreview') or body or '')
  items.append({'id':r['id'],'subject':r.get('subject',''),'received':r.get('receivedDateTime',''),'url':r.get('webLink',''),'has_attachments':r.get('hasAttachments',False),'categories':classify(r.get('subject',''),body_text[:4000])})
 return items

def create_draft(graph,subject,body,recipient=None,attachment=None):
 if not subject or len(subject)>240 or not body or len(body)>15000:raise ValueError('제목 또는 본문을 확인하세요')
 if recipient and not re.fullmatch(r'[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+',recipient):raise ValueError('수신자 주소가 올바르지 않습니다')
 attachments=[]
 if attachment:
  p=Path(attachment)
  if not p.is_file() or p.stat().st_size>2*1024*1024:raise ValueError('첨부파일이 없거나 2MiB를 초과합니다')
  attachments=[{'@odata.type':'#microsoft.graph.fileAttachment','name':p.name,'contentBytes':base64.b64encode(p.read_bytes()).decode('ascii')}]
 data={'subject':subject,'body':{'contentType':'Text','content':body},'toRecipients':([{'emailAddress':{'address':recipient}}] if recipient else []),'isDraft':True,'attachments':attachments}
 result=graph.call('POST','/me/messages',data)
 if not result.get('id') or not result.get('isDraft',False):raise RuntimeError('임시저장 확인 실패; 중복 생성을 막기 위해 자동 재시도하지 않습니다')
 verify=graph.call('GET','/me/messages/'+esc(result['id'])+'?$select=id,isDraft,subject,hasAttachments,webLink')
 if not verify.get('isDraft') or verify.get('subject')!=subject or bool(verify.get('hasAttachments'))!=bool(attachments):raise RuntimeError('임시보관함의 저장 결과를 재확인하지 못했습니다')
 return {'state':'draft_saved','id':verify['id'],'subject':verify['subject'],'has_attachment':verify.get('hasAttachments',False),'web_link':verify.get('webLink','')}
