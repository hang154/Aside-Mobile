"""Real Blackboard form writes bound to an operator-created exact assignment/file plan.
No guessed endpoints, credentials, local test LMS, or automatic write retries.
"""
import base64,hashlib,json,os,re,time,fcntl
from pathlib import Path
from urllib.parse import urlsplit
HOST='blackboard.unist.ac.kr'
ROOT=Path.home()/'.local/share/nubi-campus/submissions'
def load_plan(plan_id):
 if not re.fullmatch(r'[a-f0-9]{32}',plan_id):raise ValueError('제출 계획 ID가 필요해요.')
 root=Path(os.environ.get('NUBI_BB_SUBMISSION_DIR',str(ROOT))).resolve();path=root/(plan_id+'.json')
 if path.is_symlink():raise ValueError('Unsafe plan')
 plan=json.loads(path.read_text());u=urlsplit(plan['assignment_url'])
 if u.scheme!='https' or u.hostname!=HOST or u.port or u.username or u.password:raise ValueError('정확한 Blackboard 과제 주소가 필요해요.')
 if not plan.get('assignment_title') or not plan.get('course_title'):raise ValueError('과목과 과제명이 필요해요.')
 artifact=Path(plan['artifact_path']);data=artifact.read_bytes()
 if artifact.is_symlink() or not artifact.is_file() or not 0<len(data)<=8*1024*1024:raise ValueError('제출 파일 크기를 확인해 주세요.')
 if hashlib.sha256(data).hexdigest()!=plan['sha256']:raise ValueError('최종 확인 이후 제출 파일이 바뀌었어요.')
 if artifact.suffix.lower() not in ('.pdf','.docx','.pptx','.xlsx','.txt','.py','.zip','.hwpx','.hwp'):raise ValueError('제출 파일 형식을 확인해 주세요.')
 return path,plan,data
SCRIPT=r'''(async()=>{
 const P=PLAN, mode=MODE;
 if(location.origin!=='https://blackboard.unist.ac.kr'||(mode!=='receipt'&&location.href!==P.assignment_url))throw Error('선택한 과제 화면을 먼저 열어 주세요.');
 const docs=[document];for(const f of document.querySelectorAll('iframe'))try{if(f.contentDocument&&f.contentWindow.location.origin===location.origin)docs.push(f.contentDocument)}catch{}
 const visible=e=>!!e.getClientRects().length;
 if(docs.some(d=>[...d.querySelectorAll('input[type=password],input[type=email]')].some(visible)))throw Error('학교 로그인을 완료해 주세요.');
 const pageText=docs.map(d=>d.body.innerText).join('\n');
 if(!pageText.includes(P.assignment_title)||!pageText.includes(P.course_title))throw Error('과목·과제명이 최종 제출 대상과 일치하지 않아요.');
 const files=docs.flatMap(d=>[...d.querySelectorAll('input[type=file]')]);
 const buttons=docs.flatMap(d=>[...d.querySelectorAll('button,input[type=submit]')]).filter(visible).map(e=>({e,text:(e.innerText||e.value||e.getAttribute('aria-label')||'').trim()}));
 const receiptText=docs.flatMap(d=>[...d.querySelectorAll('[role=alert],[role=status],#goodMsg1,.receipt-confirmation,.submission-receipt')]).filter(visible).map(e=>e.innerText).join('\n');
 const receipt=receiptText.match(/(?:confirmation\s*(?:number|id)|submission\s*(?:confirmation|receipt)\s*(?:number|id)?|제출\s*확인\s*(?:번호|ID))\s*[:：#]?\s*([A-Za-z0-9][A-Za-z0-9-]{7,100})/i);
 if(mode==='receipt')return {state:receipt&&pageText.includes(P.filename)?'submitted':'receipt_not_found',confirmation_number:receipt?receipt[1]:null,url:location.href,filename_visible:pageText.includes(P.filename),assignment_title:P.assignment_title};
 if(mode==='inspect')return {state:'observed',assignment_title:P.assignment_title,course_title:P.course_title,url:location.href,file_inputs:files.length,submit_buttons:buttons.filter(b=>/^(submit|제출|제출하기)$/i.test(b.text)).map(b=>b.text),existing_confirmation:receipt?receipt[1]:null};
 if(receipt)throw Error('이미 제출 확인번호가 표시돼요. 제출 이력을 먼저 확인해 주세요.');
 if(files.length!==1)throw Error('단일 파일 첨부란을 확인할 수 없어요. 과제 제출 화면을 열어 주세요.');
 const input=files[0];
 if(mode==='attach'){
  const bytes=Uint8Array.from(atob(DATA),c=>c.charCodeAt(0));const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');if(hash!==P.sha256)throw Error('첨부 데이터 해시 불일치');
  const dt=new DataTransfer();dt.items.add(new File([bytes],P.filename,{type:'application/octet-stream'}));input.files=dt.files;input.dispatchEvent(new Event('input',{bubbles:true}));input.dispatchEvent(new Event('change',{bubbles:true}));
  return {state:'file_selected',filename:input.files[0]?.name,bytes:input.files[0]?.size,url:location.href};
 }
 if(mode==='submit'){
  if(input.files.length!==1||input.files[0].name!==P.filename||input.files[0].size!==P.bytes)throw Error('최종 파일 첨부 상태가 바뀌었어요.');
  const bytes=await input.files[0].arrayBuffer();const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');if(hash!==P.sha256)throw Error('첨부 파일 내용이 바뀌었어요.');
  const matches=buttons.filter(b=>/^(submit|제출|제출하기)$/i.test(b.text));if(matches.length!==1||matches[0].e.disabled)throw Error('활성 제출 버튼 하나를 확인할 수 없어요.');
  matches[0].e.click();return {state:'submit_clicked',url:location.href};
 }
 throw Error('Unknown submission action');
})()'''
def run(rpc,mode,plan_id):
 path,_,_=load_plan(plan_id)
 fd=os.open(str(path)+'.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  return _run_locked(rpc,mode,plan_id)
def _run_locked(rpc,mode,plan_id):
 path,plan,data=load_plan(plan_id)
 if mode not in ('inspect','attach','submit','receipt'):raise ValueError('Unknown action')
 state=plan.get('state','planned')
 if mode=='submit' and state!='file_selected':raise ValueError('파일 확인 후 한 번만 제출할 수 있어요. 제출 시도 후에는 접수 이력을 확인해 주세요.')
 if mode=='attach' and state in ('submit_started','submit_clicked','submitted'):raise ValueError('제출 이력을 먼저 확인해 주세요.')
 public={k:plan[k] for k in ('assignment_url','assignment_title','course_title','sha256')};public.update(filename=Path(plan['artifact_path']).name,bytes=len(data))
 values={'PLAN':json.dumps(public,ensure_ascii=False),'MODE':json.dumps(mode),'DATA':json.dumps(base64.b64encode(data).decode() if mode=='attach' else '')}
 script=re.sub(r'\b(PLAN|MODE|DATA)\b',lambda m:values[m[0]],SCRIPT)
 def save(value):
  plan.update(value);temporary=path.with_suffix('.tmp');temporary.write_text(json.dumps(plan,ensure_ascii=False));temporary.chmod(0o600);temporary.replace(path)
 # Persist before a write: a transport timeout must never silently retry Submit.
 if mode=='submit':save({'state':'submit_started','submit_started_at':time.time()})
 result=rpc('Runtime.evaluate',{'expression':script,'returnByValue':True,'awaitPromise':True}).get('result',{}).get('value')
 if not isinstance(result,dict):raise RuntimeError('제출 화면 응답을 확인해 주세요.')
 if mode in ('attach','submit') or result.get('state')=='submitted':save({'state':result['state'],'last_result':result})
 return result

def definitions():
 return [{'name':'nubi_blackboard_submission_'+mode,'description':desc,'inputSchema':{'type':'object','properties':{'plan_id':{'type':'string','pattern':'^[a-f0-9]{32}$'}},'required':['plan_id'],'additionalProperties':False}} for mode,desc in (
 ('inspect','Inspect the exact real Blackboard assignment from an operator-created submission plan; no write.'),
 ('attach','Select the exact hash-bound final file in the real assignment file input. File selection is not a successful upload/submission.'),
 ('submit','Click the observed exact real Submit button once for an attached final file. Never retries; then verify receipt.'),
 ('receipt','Read actual Blackboard submission confirmation number. No confirmation means not confirmed.'))]
