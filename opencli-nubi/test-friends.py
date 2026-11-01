import importlib.util,tempfile,unittest,concurrent.futures
from pathlib import Path
spec=importlib.util.spec_from_file_location('friends',Path(__file__).with_name('nubi-friends.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Checks(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=str(Path(self.tmp.name)/'friends.db');self.s=m.Friends(self.path)
  self.a=self.s.call({'action':'register','name':'A'});self.b=self.s.call({'action':'register','name':'B'});self.c=self.s.call({'action':'register','name':'C'})
 def tearDown(self):self.s.db.close();self.tmp.cleanup()
 def call(self,who,action,**kw):return self.s.call(dict(who,action=action,**kw))
 def link(self):
  code=self.call(self.a,'invite')['invite'];self.call(self.b,'accept',invite=code);return code
 def test_auth(self):
  with self.assertRaises(ValueError):self.call(dict(self.a,account_key='bad'),'list')
 def test_invite_single_use(self):
  code=self.link()
  with self.assertRaises(ValueError):self.call(self.c,'accept',invite=code)
 def test_self(self):
  code=self.call(self.a,'invite')['invite']
  with self.assertRaises(ValueError):self.call(self.a,'accept',invite=code)
 def test_expiry(self):
  code=self.call(self.a,'invite')['invite'];self.s.db.execute('UPDATE invites SET expires=0');self.s.db.commit()
  with self.assertRaises(ValueError):self.call(self.b,'accept',invite=code)
 def test_unconnected(self):
  with self.assertRaises(ValueError):self.call(self.a,'send',recipient=self.b['account_id'],text='test',message_id='x'*20)
 def test_message_flow_and_acl(self):
  self.link();mid='x'*20;self.call(self.a,'send',recipient=self.b['account_id'],text='Saturday lunch?',message_id=mid)
  self.assertEqual([],self.call(self.c,'list')['messages'])
  with self.assertRaises(ValueError):self.call(self.a,'respond',message_id=mid,state='accepted')
  self.call(self.b,'respond',message_id=mid,state='accepted');self.assertEqual('accepted',self.call(self.a,'list')['messages'][0]['state'])
  with self.assertRaises(ValueError):self.call(self.b,'respond',message_id=mid,state='declined')
 def test_idempotent_send(self):
  self.link()
  def send(_):return self.call(self.a,'send',recipient=self.b['account_id'],text='Hi',message_id='x'*20)
  with concurrent.futures.ThreadPoolExecutor(4) as pool:list(pool.map(send,range(8)))
  self.assertEqual(1,len(self.call(self.b,'list')['messages']))
  with self.assertRaises(ValueError):self.call(self.a,'send',recipient=self.b['account_id'],text='Changed',message_id='x'*20)
 def test_restart_and_disconnect(self):
  self.link();self.s.db.close();self.s=m.Friends(self.path);self.assertEqual(1,len(self.call(self.b,'list')['friends']));self.call(self.a,'disconnect',recipient=self.b['account_id']);self.assertEqual([],self.call(self.b,'list')['friends'])
if __name__=='__main__':unittest.main()
