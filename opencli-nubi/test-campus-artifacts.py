import tempfile,importlib.util,hashlib,json,uuid
from pathlib import Path
spec=importlib.util.spec_from_file_location('jobs',Path(__file__).with_name('nubi-chat-jobs.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Done:
 def poll(self):return 1
with tempfile.TemporaryDirectory() as d:
 root=Path(d);drafts=root/'drafts';drafts.mkdir();file=drafts/'lecture-ko.pdf';file.write_bytes(b'%PDF-fixture');trace=root/'job.json';gid=str(uuid.uuid4());sha=hashlib.sha256(file.read_bytes()).hexdigest()
 body={'kind':'campus','completed':False,'document':{'state':'draft_only','manifest':{'files':[{'name':file.name,'sha256':sha}]}},'artifact_paths':{file.name:str(file)}};trace.write_text(json.dumps(body));q=m.ChatJobs(root/'jobs',{'NUBI_CAMPUS_DRAFT_DIR':str(drafts)});q.jobs['x']={'request':{'goal_id':gid},'process':Done(),'trace':trace}
 assert q.artifact('x',gid,file.name)==b'%PDF-fixture'
 for name,goal in [('../lecture-ko.pdf',gid),(file.name,str(uuid.uuid4()))]:
  try:q.artifact('x',goal,name);raise AssertionError()
  except ValueError:pass
 file.write_bytes(b'tampered')
 try:q.artifact('x',gid,file.name);raise AssertionError()
 except ValueError:pass
 print('PASS generated campus artifact access despite later upload failure, ownership, traversal and hash validation (fixtures)')
