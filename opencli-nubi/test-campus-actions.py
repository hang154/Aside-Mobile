"""Real SQLite approval state machine; deterministic Graph, never sends actual mail."""
import copy,tempfile,uuid,concurrent.futures
from pathlib import Path
from campus_actions import MailActions
class Graph:
 def __init__(self):self.posts=0;self.change=False;self.fail=False
 def call(self,method,path,data=None):
  if method=='POST':
   self.posts+=1
   if self.fail:raise TimeoutError('ambiguous')
   return {'http_status':202}
  return {'id':'draft-1','isDraft':True,'subject':'changed' if self.change else '학사 상담 요청','body':{'content':'검토할 본문'},'toRecipients':[{'emailAddress':{'address':'test@example.invalid'}}],'changeKey':'v1'}
with tempfile.TemporaryDirectory() as t:
 a=MailActions(Path(t)/'actions.db');g=Graph();owner=str(uuid.uuid4());p=a.prepare(owner,g,'draft-1');assert a.list(str(uuid.uuid4()))==[]
 try:a.send(str(uuid.uuid4()),p['id'],p['digest'],g);raise AssertionError()
 except ValueError:pass
 assert g.posts==0
 g.change=True
 try:a.send(owner,p['id'],p['digest'],g);raise AssertionError()
 except ValueError:pass
 assert g.posts==0
 g.change=False
 def send():
  try:return a.send(owner,p['id'],p['digest'],g)['state']
  except ValueError:return 'blocked'
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:r=list(pool.map(lambda _:send(),range(2)))
 assert sorted(r)==['accepted','blocked'] and g.posts==1,r
 assert a.prepare(owner,g,'draft-1')['state']=='accepted'
 b=MailActions(Path(t)/'unknown.db');g=Graph();g.fail=True;p=b.prepare(owner,g,'draft-1');assert b.send(owner,p['id'],p['digest'],g)['state']=='outcome_unknown'
 try:b.send(owner,p['id'],p['digest'],g);raise AssertionError()
 except ValueError:pass
 assert g.posts==1
 c=MailActions(Path(t)/'cancel.db');g=Graph();p=c.prepare(owner,g,'draft-1');assert c.cancel(owner,p['id'])['state']=='cancelled';assert g.posts==0
 print('PASS owner isolation, content binding, concurrent duplicate send protection, unknown outcome and cancellation (Graph fixture)')
