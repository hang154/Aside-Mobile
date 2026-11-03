#!/usr/bin/env python3
"""Operator entrypoint: bind a user's explicit real assignment and final file.
Does not open, attach or submit anything. Invoke only with a user-selected target.
"""
import argparse,hashlib,json,os,uuid
from pathlib import Path
from blackboard_submission import ROOT,load_plan
p=argparse.ArgumentParser();p.add_argument('--assignment-url',required=True);p.add_argument('--course-title',required=True);p.add_argument('--assignment-title',required=True);p.add_argument('--file',required=True);a=p.parse_args()
artifact=Path(a.file).expanduser().resolve();data=artifact.read_bytes()
root=Path(os.environ.get('NUBI_BB_SUBMISSION_DIR',str(ROOT)));root.mkdir(parents=True,exist_ok=True,mode=0o700);ident=uuid.uuid4().hex;path=root/(ident+'.json')
row={'assignment_url':a.assignment_url,'course_title':a.course_title,'assignment_title':a.assignment_title,'artifact_path':str(artifact),'sha256':hashlib.sha256(data).hexdigest(),'state':'planned'}
with path.open('x') as f:os.chmod(path,0o600);json.dump(row,f,ensure_ascii=False)
try:load_plan(ident)
except Exception:path.unlink();raise
print(json.dumps({'plan_id':ident,'assignment_title':a.assignment_title,'filename':artifact.name,'sha256':row['sha256'],'state':'planned'},ensure_ascii=False))
