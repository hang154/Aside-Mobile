#!/usr/bin/env python3
import hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
from docx import Document
from pptx import Presentation
from campus_report import export_report
from campus_task import local_report_only
assert local_report_only("사용자 제공 내용만 보고서와 발표자료로 생성해")
assert local_report_only("[학교 자동화] 블랙보드 팀플 확인\n사용자 제공 맥락:\n사용자 제공 내용만 보고서 생성\n로그인이나 지원 도구가 없으면 알려줘")
assert not local_report_only("사용자 제공 내용만 보고서로 만들고 메일로 보내")
assert not local_report_only("블랙보드 자료를 검색해서 보고서를 작성해")
with tempfile.TemporaryDirectory() as directory:
    root=Path(directory)
    sections=[{'heading':'검증 대상','body':'가속도와 운동 분석. '*100,'sources':['https://example.org/paper']},{'heading':'검토 사항','body':'직접 확인할 사항','sources':[]}]
    result=export_report(root,'팀 발표 테스트',sections)
    assert result['uncited_sections']==[2] and result['review_required'] and not result['submitted']
    paths=[Path(f['path']) for f in result['files']]
    assert all(p.stat().st_mode&0o777==0o600 for p in paths)
    assert all(hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'] for p,f in zip(paths,result['files']))
    doc=Document(paths[0]);assert any('https://example.org/paper' in p.text for p in doc.paragraphs)
    prs=Presentation(paths[1]);assert len(prs.slides)>3
    assert 'https://example.org/paper' in prs.slides[1].notes_slide.notes_text_frame.text
    assert all(len(s.placeholders[1].text)<=420 for s in list(prs.slides)[1:])
    before=set(root.iterdir())
    for section in [dict(heading='x',body='x',sources=['file:///etc/passwd']),dict(heading='x',body='x',sources=['https://user:secret@example.org']),dict(heading='x',body='',sources=[])]:
        try:export_report(root,'제목',[section]);raise AssertionError('invalid input accepted')
        except ValueError:pass
    assert before==set(root.iterdir())
    requests=[{'jsonrpc':'2.0','id':1,'method':'tools/list'},{'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'nubi_campus_report_export','arguments':{'title':'MCP 검증','sections':sections}}}]
    proc=subprocess.run([sys.executable,str(Path(__file__).with_name('campus-document-local-mcp.py'))],input='\n'.join(json.dumps(r) for r in requests)+'\n',text=True,capture_output=True,env={**os.environ,'NUBI_CAMPUS_DRAFT_DIR':directory},check=True)
    replies=[json.loads(line)['result'] for line in proc.stdout.splitlines()]
    assert any(t['name']=='nubi_campus_report_export' for t in replies[0]['tools'])
    assert len(json.loads(replies[1]['content'][0]['text'])['files'])==2
print('PASS report DOCX/PPTX roundtrip, source notes, pagination, permissions, digest, invalid inputs, MCP export')
