#!/usr/bin/env python3
"""Temporary authenticated TLS relay for a foreground Nubi browser (stdlib only)."""
import argparse, hmac, json, queue, secrets, ssl, threading, time, os, importlib.util, signal, sys, re
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

parser = argparse.ArgumentParser()
parser.add_argument('--cert', required=True)
parser.add_argument('--key', required=True)
parser.add_argument('--token-file', required=True)
parser.add_argument('--host', default='0.0.0.0')
parser.add_argument('--port', type=int, default=18444)
parser.add_argument('--chat-dir',help='Enable app chat jobs; local private trace directory')
args = parser.parse_args()
token = open(args.token_file, encoding='ascii').read().strip()
if len(token) < 32:
    raise SystemExit('Token must have at least 32 characters')
queues={};poll_owners={};poll_epochs={};active_device='default'
def device_queue(session):
    with lock:
        if session not in queues:
            if len(queues)>=100:raise RuntimeError('Session limit reached')
            queues[session]=queue.Queue(maxsize=10)
        return queues[session]
results = {}
lock = threading.Lock()
jobs=None
if args.chat_dir:
    spec=importlib.util.spec_from_file_location('nubi_chat_jobs',Path(__file__).with_name('nubi-chat-jobs.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    env=dict(os.environ,NUBI_GOAL_RELAY_TOKEN_FILE=args.token_file,NUBI_GOAL_RELAY_CA_FILE=args.cert,NUBI_GOAL_RELAY_URL='https://127.0.0.1:'+str(args.port))
    jobs=module.ChatJobs(args.chat_dir,env)
spec=importlib.util.spec_from_file_location('nubi_friends',Path(__file__).with_name('nubi-friends.py'));friends_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(friends_module)
friends=friends_module.Friends(str(Path(args.token_file).with_name('friends.sqlite3')))
spec=importlib.util.spec_from_file_location('friend_draft',Path(__file__).with_name('nubi-friend-draft.py'));draft_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(draft_module)
from nubi_group_qwen import GroupQwen
group_qwen=GroupQwen(Path(args.chat_dir or Path(args.token_file).parent)/"group-qwen")
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def respond(self, status, obj):
        raw = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_POST(self):
        if not hmac.compare_digest(self.headers.get('Authorization',''), 'Bearer '+token): return self.respond(401, {'error':'unauthorized'})
        try:
            n = int(self.headers.get('Content-Length','0'))
            if n < 2 or n > 32768: raise ValueError()
            body = json.loads(self.rfile.read(n))
            if not isinstance(body, dict): raise ValueError()
        except Exception: return self.respond(400, {'error':'invalid request'})
        if self.path in ('/group-submit','/group-status'):
            try:
                if self.path=='/group-submit':result=group_qwen.submit(body)
                elif set(body)=={'job_id','device_session'}:result=group_qwen.status(body['job_id'],body['device_session'])
                else:raise ValueError('Invalid group status fields')
                return self.respond(200,result)
            except ValueError as e:return self.respond(400,{'error':str(e)})
        if self.path=='/friends':
            try:
                if body.get('action')=='draft':
                    friends.call(dict(body,action='list'))
                    return self.respond(200,draft_module.draft(body.get('instruction')))
                return self.respond(200,friends.call(body))
            except ValueError as e:return self.respond(200,{'error':str(e)})
            except Exception:return self.respond(200,{'error':'친구 작업 연결을 확인해 주세요'})
        if self.path=='/document-file':
            if jobs is None or set(body)!={'job_id','goal_id','name'}:return self.respond(400,{'error':'invalid document request'})
            try:data=jobs.artifact(body['job_id'],body['goal_id'],body['name'])
            except (ValueError,OSError):return self.respond(404,{'error':'document not available'})
            self.send_response(200);self.send_header('Content-Type','application/octet-stream');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
        if self.path.startswith('/chat-'):
            if jobs is None:return self.respond(503, {'error':'App chat worker not enabled'})
            try:
                if self.path=='/chat-submit':result=jobs.submit(body)
                elif self.path=='/chat-status' and set(body)=={'job_id'}:result=jobs.status(body['job_id'])
                elif self.path=='/chat-cancel' and set(body)=={'job_id'}:
                    result=jobs.cancel(body['job_id'])
                    # Cancelled tool commands must not execute in a later goal.
                    pending=device_queue(jobs.jobs[body['job_id']]['request']['device_session'])
                    while True:
                        try:pending.get_nowait()
                        except queue.Empty:break
                else:raise ValueError('Invalid chat route')
                return self.respond(200,result)
            except ValueError as e:return self.respond(400,{'error':str(e)})
            except RuntimeError as e:return self.respond(409,{'error':str(e)})
        if self.path in ('/claim','/poll'):
            global active_device
            session=body.get('device_session','default');owner=body.get('poll_owner','')
            if not isinstance(session,str) or session!='default' and not re.fullmatch(r'[0-9a-f-]{36}',session):return self.respond(400,{'error':'invalid device session'})
            if not isinstance(owner,str) or owner and not re.fullmatch(r'[0-9a-f-]{36}',owner):return self.respond(400,{'error':'invalid poll owner'})
            if self.path=='/claim':
                epoch=body.get('poll_epoch')
                if not owner or type(epoch) is not int or epoch<1:return self.respond(400,{'error':'poll owner/epoch required'})
                with lock:
                    if epoch<poll_epochs.get(session,0) or epoch==poll_epochs.get(session,0) and poll_owners.get(session)!=owner:return self.respond(409,{'error':'superseded connection claim'})
                    poll_owners[session]=owner;poll_epochs[session]=epoch
                return self.respond(200,{'claimed':True})
            with lock:valid=poll_owners.get(session,'')==owner
            if not valid:return self.respond(409,{'error':'superseded connection'})
            active_device=session
            try:
                command=device_queue(session).get(timeout=15)
                with lock:valid=poll_owners.get(session,'')==owner
                if not valid:
                    device_queue(session).put_nowait(command)
                    command=None
                elif command.get('expires',0)<time.time():command=None
            except queue.Empty:command=None
            return self.respond(200,{'command':command})
        if self.path == '/result':
            id = body.get('id')
            if not isinstance(id,str) or len(id)>64: return self.respond(400, {'error':'invalid id'})
            with lock:
                if len(results)>100: results.clear()
                results[id]=body
            return self.respond(200, {'ok':True})
        # Control is local-only; only the paired device can poll/return results remotely.
        if self.client_address[0] not in ('127.0.0.1','::1'): return self.respond(403, {'error':'local controller only'})
        if self.path == '/command':
            op=body.get('op')
            valid={'goal_open','goal_search','goal_observe','goal_select','goal_report'}
            if op not in valid: return self.respond(400, {'error':'unsupported goal command'})
            id=secrets.token_hex(12); item=dict(body);item['id']=id;item['expires']=time.time()+30
            session=body.pop('_session',active_device)
            if not isinstance(session,str) or session!='default' and not re.fullmatch(r'[0-9a-f-]{36}',session):return self.respond(400,{'error':'invalid device session'})
            item.pop('_session',None)
            job_id=item.pop('_job',None);request_id=item.pop('_request',None)
            if job_id is not None:
                if jobs is None:return self.respond(409,{"error":"chat jobs disabled"})
                with jobs.lock:
                    job=jobs.jobs.get(job_id)
                    if not job or job['cancelled'] or job['process'].poll() is not None or job['request']['device_session']!=session or job['request']['request_id']!=request_id:return self.respond(409,{'error':'stale run lease'})
                item.update(job_id=job_id,request_id=request_id,device_session=session)

            try: device_queue(session).put_nowait(item)
            except queue.Full: return self.respond(429, {'error':'queue full'})
            return self.respond(200, {'id':id})
        if self.path == '/get-result':
            with lock: data=results.pop(body.get('id'),None)
            return self.respond(200, {'result':data})
        return self.respond(404, {'error':'not found'})
server=ThreadingHTTPServer((args.host,args.port),Handler)
ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); ctx.minimum_version=ssl.TLSVersion.TLSv1_2;ctx.load_cert_chain(args.cert,args.key)
server.socket=ctx.wrap_socket(server.socket, server_side=True)
print('Nubi goal TLS relay listening',flush=True)
signal.signal(signal.SIGTERM,lambda signum,frame:sys.exit(0))
try:server.serve_forever()
finally:
    if jobs:jobs.close()
