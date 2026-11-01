"""Local notice snapshot comparison; never treats missing rows as deleted."""
import hashlib, json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path

def sync(path, rows, on_changes=None):
 if not isinstance(rows,list) or not rows:raise ValueError('Empty or invalid board results; previous snapshot retained')
 for r in rows:
  if not isinstance(r,dict) or not all(isinstance(r.get(k),str) and r[k] for k in ('board_id','id','title','posted')):raise ValueError('Invalid notice; previous snapshot retained')
  if not r['board_id'].isdigit() or not r['id'].isdigit():raise ValueError('Invalid notice ID')
 path=Path(path);path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
 with sqlite3.connect(path) as db:
  os.chmod(path,0o600)
  db.execute('CREATE TABLE IF NOT EXISTS notices (board_id TEXT NOT NULL, id TEXT NOT NULL, fingerprint TEXT NOT NULL, title TEXT NOT NULL, posted TEXT NOT NULL, updated TEXT NOT NULL, PRIMARY KEY(board_id,id))')
  changes=[];now=datetime.now(timezone.utc).isoformat()
  for r in rows:
   payload={k:r.get(k) for k in ('title','posted','has_attachment')};fingerprint=hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
   old=db.execute('SELECT fingerprint FROM notices WHERE board_id=? AND id=?',(r['board_id'],r['id'])).fetchone()
   state='new' if old is None else 'unchanged' if old[0]==fingerprint else 'changed'
   db.execute('INSERT INTO notices VALUES (?,?,?,?,?,?) ON CONFLICT(board_id,id) DO UPDATE SET fingerprint=excluded.fingerprint,title=excluded.title,posted=excluded.posted,updated=excluded.updated',(r['board_id'],r['id'],fingerprint,r['title'],r['posted'],now))
   if state!='unchanged':changes.append({'board_id':r['board_id'],'id':r['id'],'title':r['title'],'posted':r['posted'],'state':state})
  if on_changes is not None:on_changes(changes)
  return {'checked_at':now,'scanned':len(rows),'changes':changes,'scope':'현재 게시판 페이지의 제목·게시일·첨부 표시만 비교; 본문 변경 미감지'}
