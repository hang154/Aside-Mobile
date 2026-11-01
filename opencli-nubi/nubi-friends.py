"""Persistent invite-only companion messaging. Account secrets are independent of relay pairing."""
import sqlite3, secrets, hashlib, time, threading
class Friends:
 def __init__(self,path):
  self.db=sqlite3.connect(path,check_same_thread=False);self.lock=threading.RLock()
  self.db.executescript('CREATE TABLE IF NOT EXISTS accounts(id TEXT PRIMARY KEY, secret TEXT,name TEXT);CREATE TABLE IF NOT EXISTS invites(code TEXT PRIMARY KEY,owner TEXT,expires REAL);CREATE TABLE IF NOT EXISTS links(a TEXT,b TEXT,PRIMARY KEY(a,b));CREATE TABLE IF NOT EXISTS messages(id TEXT PRIMARY KEY,sender TEXT,recipient TEXT,text TEXT,state TEXT,created REAL);');self.db.commit()
 def call(self,b):
  with self.lock,self.db:
   op=b.get('action')
   if op=='register':
    name=str(b.get('name','누비 사용자')).strip()
    if not 1<=len(name)<=40:raise ValueError('이름을 확인해 주세요')
    uid=secrets.token_hex(16);key=secrets.token_urlsafe(32)
    self.db.execute('INSERT INTO accounts VALUES(?,?,?)',(uid,hashlib.sha256(key.encode()).hexdigest(),name));return {'account_id':uid,'account_key':key,'name':name}
   uid=b.get('account_id');row=self.db.execute('SELECT secret,name FROM accounts WHERE id=?',(uid,)).fetchone()
   if not row or not secrets.compare_digest(row[0],hashlib.sha256(str(b.get('account_key','')).encode()).hexdigest()):raise ValueError('계정 인증을 확인해 주세요')
   if op=='invite':
    self.db.execute('DELETE FROM invites WHERE owner=? OR expires<?',(uid,time.time()));code=secrets.token_urlsafe(18);self.db.execute('INSERT INTO invites VALUES(?,?,?)',(code,uid,time.time()+600));return {'invite':code,'expires_in':600}
   if op=='accept':
    found=self.db.execute('SELECT owner FROM invites WHERE code=? AND expires>?',(b.get('invite'),time.time())).fetchone()
    if not found or found[0]==uid:raise ValueError('유효한 다른 계정의 초대가 필요해요')
    other=found[0];self.db.execute('DELETE FROM invites WHERE code=?',(b['invite'],))
    self.db.executemany('INSERT OR IGNORE INTO links VALUES(?,?)',[(uid,other),(other,uid)]);return {'connected':True}
   if op=='list':
    friends=[{'id':r[0],'name':r[1]} for r in self.db.execute('SELECT b,name FROM links JOIN accounts ON accounts.id=links.b WHERE a=? LIMIT 50',(uid,))]
    messages=[dict(zip(['id','sender','recipient','text','state','created'],r)) for r in self.db.execute('SELECT * FROM messages WHERE sender=? OR recipient=? ORDER BY created DESC LIMIT 10',(uid,uid))];return {'friends':friends,'messages':messages}
   if op=='send':
    other=b.get('recipient');text=b.get('text','');mid=b.get('message_id')
    if not isinstance(text,str) or not 1<=len(text.strip())<=2000 or not isinstance(mid,str) or not 16<=len(mid)<=64:raise ValueError('메시지를 확인해 주세요')
    if not self.db.execute('SELECT 1 FROM links WHERE a=? AND b=?',(uid,other)).fetchone():raise ValueError('연결된 친구에게만 보낼 수 있어요')
    old=self.db.execute('SELECT sender,recipient,text FROM messages WHERE id=?',(mid,)).fetchone()
    if old and tuple(old)!=(uid,other,text):raise ValueError('메시지 식별자가 충돌했어요')
    self.db.execute('INSERT OR IGNORE INTO messages VALUES(?,?,?,?,?,?)',(mid,uid,other,text,'proposed',time.time()));return {'message_id':mid,'state':self.db.execute('SELECT state FROM messages WHERE id=?',(mid,)).fetchone()[0]}
   if op=='respond':
    state=b.get('state')
    if state not in ('accepted','declined'):raise ValueError('수락 또는 거절을 선택해 주세요')
    cur=self.db.execute("UPDATE messages SET state=? WHERE id=? AND recipient=? AND state='proposed'",(state,b.get('message_id'),uid))
    if cur.rowcount!=1:raise ValueError('응답할 수 없는 제안이에요')
    return {'state':state}
   if op=='disconnect':
    other=b.get('recipient');self.db.execute('DELETE FROM links WHERE (a=? AND b=?) OR (a=? AND b=?)',(uid,other,other,uid));return {'disconnected':True}
   raise ValueError('지원하지 않는 친구 작업이에요')
