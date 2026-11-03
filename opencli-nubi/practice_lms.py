"""Loopback-only practice submission HTTP service with content-addressed receipts."""
import hashlib,json,re,threading,time
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
@contextmanager
def serve(directory):
 root=Path(directory);root.mkdir(parents=True,exist_ok=True,mode=0o700)
 class Handler(BaseHTTPRequestHandler):
  def log_message(self,*args):pass
  def reply(self,status,data):
   raw=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
  def do_POST(self):
   try:
    size=int(self.headers.get('Content-Length','0'))
    if self.path!='/submissions' or not 0<size<30000:raise ValueError('bounded submission required')
    b=json.loads(self.rfile.read(size));code=b['code'];sha=hashlib.sha256(code.encode()).hexdigest()
    if b.get('environment')!='LOCAL_PRACTICE_ONLY' or b.get('student')!='00000000 Nubi Test' or b.get('filename')!='practice.py' or b['proof'].get('sha256')!=sha or b['proof'].get('tests_passed') is not True:raise ValueError('verified practice only')
    ident='TEST-LMS-'+sha[:16];path=root/(ident+'.json')
    if path.exists():receipt=json.loads(path.read_text())
    else:
     receipt={'id':ident,'state':'accepted','sha256':sha,'student':b['student'],'filename':'practice.py','accepted_at':time.time(),'environment':'LOCAL_PRACTICE_ONLY'}
     (root/(ident+'.py')).write_text(code);tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(receipt));tmp.replace(path)
    self.reply(200,receipt)
   except (ValueError,KeyError,TypeError):self.reply(400,{'error':'invalid practice submission'})
  def do_GET(self):
   ident=self.path.removeprefix('/submissions/')
   if self.path.startswith('/submissions/') and re.fullmatch(r'TEST-LMS-[a-f0-9]{16}',ident) and (root/(ident+'.json')).exists():self.reply(200,json.loads((root/(ident+'.json')).read_text()))
   else:self.reply(404,{'error':'not found'})
 server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 try:yield 'http://127.0.0.1:'+str(server.server_port)
 finally:server.shutdown();server.server_close();thread.join()
