"""Subprocess routing, artifact ownership and tamper protection; fake Qwen only."""
import hashlib,importlib.util,json,os,shutil,sys,tempfile,time,uuid
from pathlib import Path
with tempfile.TemporaryDirectory() as d:
 root=Path(d);shutil.copy(Path(__file__).with_name('nubi-chat-jobs.py'),root/'nubi-chat-jobs.py')
 (root/'qwen-document-agent.py').write_text('''import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser()
for k in ['goal','goal-id','task','max-steps','trace-file']:p.add_argument('--'+k)
a=p.parse_args();w=Path(a.trace_file).with_suffix('')/'artifacts';w.mkdir(parents=True);(w/'budget.docx').write_bytes(b'fixture')
Path(a.trace_file).write_text(json.dumps({'kind':'document','completed':True,'answer':'draft','events':[],'document':{'state':'needs_information','manifest':{'files':[{'name':'budget.docx','sha256':hashlib.sha256(b'fixture').hexdigest()}]}}}))
''')
 spec=importlib.util.spec_from_file_location('docjobs',root/'nubi-chat-jobs.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);old=os.environ.get('NUBI_DOCUMENT_PYTHON');os.environ['NUBI_DOCUMENT_PYTHON']=sys.executable
 try:
  jobs=m.ChatJobs(root/'jobs',os.environ);body={'goal_id':str(uuid.uuid4()),'character':'grades','task':'UIRP 예산서 작성','request_id':str(uuid.uuid4()),'device_session':str(uuid.uuid4())};j=jobs.submit(body)
  for _ in range(50):
   r=jobs.status(j['job_id'])
   if r['state']!='running':break
   time.sleep(.02)
  assert r['kind']=='document' and r['state']=='completed';assert r['document']['state']=='needs_information'
  assert jobs.artifact(j['job_id'],body['goal_id'],'budget.docx')==b'fixture'
  for goal,name in [('wrong','budget.docx'),(body['goal_id'],'../../secret')]:
   try:jobs.artifact(j['job_id'],goal,name)
   except ValueError:pass
   else:raise AssertionError('Invalid artifact scope accepted')
  (root/'jobs'/j['job_id']/'artifacts/budget.docx').write_bytes(b'tampered')
  try:jobs.artifact(j['job_id'],body['goal_id'],'budget.docx')
  except ValueError:pass
  else:raise AssertionError('Tamper accepted')
  jobs.close();print('PASS document subprocess routing, draft state, file download, goal scope, traversal and hash protection (fake Qwen)')
 finally:
  if old is None:os.environ.pop('NUBI_DOCUMENT_PYTHON',None)
  else:os.environ['NUBI_DOCUMENT_PYTHON']=old
