"""Evidence-linked report and presentation exports from agent supplied content."""
import hashlib
import os
import uuid
from pathlib import Path
from docx import Document
from pptx import Presentation
from pptx.util import Inches, Pt

DEFINITION = {'name':'nubi_campus_report_export','description':'Export a sourced campus report as DOCX and matching PPTX. Supply actual researched content and source URLs; never invent findings or URLs. Use sources=[] for user-supplied content without a URL. Returns review-required drafts, not submitted work.', 'inputSchema':{'type':'object','properties':{'title':{'type':'string','minLength':1,'maxLength':160},'sections':{'type':'array','minItems':1,'maxItems':12,'items':{'type':'object','properties':{'heading':{'type':'string','maxLength':100},'body':{'type':'string','maxLength':1800},'sources':{'type':'array','maxItems':10,'items':{'type':'string','maxLength':2000}}},'required':['heading','body','sources'],'additionalProperties':False}}},'required':['title','sections'],'additionalProperties':False}}

def export_report(root, title, sections):
    if not isinstance(title,str) or not 1<=len(title.strip())<=160: raise ValueError('제목이 필요합니다')
    if not isinstance(sections,list) or not 1<=len(sections)<=12: raise ValueError('본문은 1~12개 절이어야 합니다')
    from urllib.parse import urlsplit
    for section in sections:
        if not isinstance(section,dict) or set(section)!={'heading','body','sources'}: raise ValueError('절 형식이 잘못되었습니다')
        for key,limit in [('heading',100),('body',1800)]:
            if not isinstance(section[key],str) or not 1<=len(section[key].strip())<=limit: raise ValueError('절 제목과 본문을 확인하세요')
        if not isinstance(section['sources'],list) or len(section['sources'])>10: raise ValueError('출처 목록을 확인하세요')
        for url in section['sources']:
            if not isinstance(url,str) or len(url)>2000: raise ValueError('출처 URL 형식 오류')
            parsed=urlsplit(url)
            if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password: raise ValueError('출처는 인증정보 없는 HTTP URL이어야 합니다')
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=True,mode=0o700)
    prefix='nubi-report-'+uuid.uuid4().hex
    paths=[root/(prefix+suffix) for suffix in ('.docx','.pptx')]
    review='검토용 초안 · 사실관계, 인용, 강의 AI 이용 규정 확인 필요'
    doc=Document();doc.add_heading(title,0);doc.add_paragraph(review)
    prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
    intro=prs.slides.add_slide(prs.slide_layouts[0]);intro.shapes.title.text=title;intro.placeholders[1].text=review
    uncited=[]
    for index,section in enumerate(sections,1):
        doc.add_heading(section['heading'],1);doc.add_paragraph(section['body'])
        if not section['sources']:uncited.append(index)
        for url in section['sources']:doc.add_paragraph('출처: '+url)
        # Split long bodies to avoid silently overflowing a single slide.
        text=section['body'];chunks=[]
        while text:
            split=min(420,len(text))
            if split<len(text):
                boundary=text.rfind(' ',0,split)
                if boundary>210:split=boundary
            chunks.append(text[:split]);text=text[split:].lstrip()
        for part,chunk in enumerate(chunks,1):
            slide=prs.slides.add_slide(prs.slide_layouts[1]);slide.shapes.title.text=section['heading']+(f' ({part}/{len(chunks)})' if len(chunks)>1 else '')
            frame=slide.placeholders[1].text_frame;frame.text=chunk
            for paragraph in frame.paragraphs:paragraph.font.size=Pt(22)
            slide.notes_slide.notes_text_frame.text='\n'.join(section['sources']) or '출처 미제공: 검토 필요'
    try:
        for path,artifact in zip(paths,(doc,prs)):
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,'wb') as stream:artifact.save(stream)
    except BaseException:
        for path in paths:path.unlink(missing_ok=True)
        raise
    return {'state':'draft_only','submitted':False,'review_required':True,'uncited_sections':uncited,'source_verification':'caller_supplied_not_independently_verified','files':[{'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size} for path in paths]}
