#!/usr/bin/env python3
"""Temporary authenticated TLS relay for a foreground Nubi browser (stdlib only)."""
import argparse, hmac, json, queue, secrets, ssl, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

parser = argparse.ArgumentParser()
parser.add_argument('--cert', required=True)
parser.add_argument('--key', required=True)
parser.add_argument('--token-file', required=True)
parser.add_argument('--host', default='0.0.0.0')
parser.add_argument('--port', type=int, default=18443)
args = parser.parse_args()
token = open(args.token_file, encoding='ascii').read().strip()
if len(token) < 32:
    raise SystemExit('Token must have at least 32 characters')
commands = queue.Queue(maxsize=10)
results = {}
lock = threading.Lock()
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
        if self.path == '/poll':
            try:
                command = commands.get(timeout=15)
                if command.get('expires',0) < time.time(): command = None
            except queue.Empty: command = None
            return self.respond(200, {'command':command})
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
            op=body.get('op'); url=body.get('url','')
            if op not in ('navigate','observe','search') or (op=='navigate' and (not isinstance(url,str) or len(url)>500)) or (op=='search' and (not isinstance(body.get('query'),str) or not body['query'].strip() or len(body['query'])>100)): return self.respond(400, {'error':'unsupported command'})
            id=secrets.token_hex(12); item={'id':id,'op':op,'expires':time.time()+30}
            if op=='navigate': item['url']=url
            if op=='search': item['query']=body['query'].strip()
            try: commands.put_nowait(item)
            except queue.Full: return self.respond(429, {'error':'queue full'})
            return self.respond(200, {'id':id})
        if self.path == '/get-result':
            with lock: data=results.pop(body.get('id'),None)
            return self.respond(200, {'result':data})
        return self.respond(404, {'error':'not found'})
server=ThreadingHTTPServer((args.host,args.port),Handler)
ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); ctx.minimum_version=ssl.TLSVersion.TLSv1_2;ctx.load_cert_chain(args.cert,args.key)
server.socket=ctx.wrap_socket(server.socket, server_side=True)
print('Nubi TLS relay listening',flush=True)
server.serve_forever()
