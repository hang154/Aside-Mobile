"""Create a clearly marked campus application draft with user-supplied facts."""
import os,re,uuid
from pathlib import Path
from docx import Document

def create_application(root,fields):
 required={'notice_title','source','applicant','motivation','experience'}
 if not isinstance(fields,dict) or not set(fields).issubset(required) or not isinstance(fields.get('notice_title'),str) or not fields['notice_title'].strip():raise ValueError('공고 제목이 필요합니다')
 if any(not isinstance(v,str) or len(v)>4000 for v in fields.values()):raise ValueError('문서 항목의 형식을 확인하세요')
 root=Path(root).resolve();root.mkdir(mode=0o700,parents=True,exist_ok=True)
 filename='nubi-campus-application-'+uuid.uuid4().hex+'.docx';p=root/filename
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 missing=[]
 try:
  doc=Document();doc.add_heading('Application draft — review before submission',0)
  for key,label in [('notice_title','Opportunity'),('source','Source'),('applicant','Applicant'),('motivation','Motivation'),('experience','Relevant experience')]:
   value=fields.get(key,'').strip()
   if not value:missing.append(label);value='[To be completed by the applicant]'
   doc.add_heading(label,level=2);doc.add_paragraph(value)
  doc.add_paragraph('This is a draft, not an official application form. Verify eligibility, deadlines, required forms and all facts against the original notice.')
  with os.fdopen(fd,'wb') as f:doc.save(f)
 except BaseException:
  try:os.close(fd)
  except OSError:pass
  p.unlink(missing_ok=True);raise
 return {'state':'draft_only','path':str(p),'missing':missing,'submitted':False}
