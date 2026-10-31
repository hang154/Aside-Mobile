#!/usr/bin/env python3
"""App-compatible document worker. Artifacts are private; missing facts stay missing."""
import argparse,json,os,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
from documents.pipeline import run,MODEL
p=argparse.ArgumentParser();p.add_argument('--goal',required=True);p.add_argument('--goal-id',required=True);p.add_argument('--task',required=True);p.add_argument('--max-steps');p.add_argument('--trace-file',required=True);a=p.parse_args()
trace={'goal':a.goal,'started_at':datetime.now(timezone.utc).isoformat(),'completed':False,'answer':None,'events':[],'reported_models':[],'kind':'document','goal_id':a.goal_id}
try:
 cfg=os.environ.get('NUBI_DOCUMENT_CONFIG',str(Path.home()/'.config/nubi-documents/config.json'))
 task=a.task.split('현재 사용자 지시:',1)[-1].strip()
 profile='lseries' if any(w in task.lower() for w in ['l시리즈','lseries']) else 'uirp' if any(w in task.lower() for w in ['uirp','aicp']) else 'general'
 work=Path(a.trace_file).with_suffix('');result=run(task,profile,cfg,work)
 trace['document']=result;trace['reported_models']=[result['model']];trace['completed']=True
 status={'draft_only':'요청대로 문서를 작성하고 검산했어. 업로드는 하지 않았어.','uploaded':'작성·검산·업로드 및 원격 파일 재확인을 마쳤어.','needs_information':'문서 초안을 만들었어. 아래 근거가 부족해 제출 가능한 상태는 아니야.','needs_destination':'문서는 생성했어. 업로드 연결과 대상 폴더가 필요해.'}[result['state']]
 details=result['manifest']['issues'][:10]
 trace['answer']=status+'\n'+('\n'.join('• '+v for v in details))+'\n파일: budget.docx, budget.hwpx'
 if result['uploads']:trace['answer']+='\n'+'\n'.join(r['web_url'] or r['id'] for r in result['uploads'])
except Exception as e:
 trace['error']=type(e).__name__+': '+str(e)
 import traceback;Path(a.trace_file).with_suffix('.error.log').write_text(traceback.format_exc())
finally:
 trace['ended_at']=datetime.now(timezone.utc).isoformat();Path(a.trace_file).write_text(json.dumps(trace,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'completed':trace['completed'],'error':trace.get('error')},ensure_ascii=False));sys.exit(0 if trace['completed'] else 1)
