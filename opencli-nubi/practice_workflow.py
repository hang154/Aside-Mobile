"""Real ChatGPT WebView response -> isolated checks -> durable local practice LMS.
Never addresses a real course or submits student work to a school.
"""
import ast,hashlib,importlib.util,json,os,re,subprocess,sys,time,urllib.request
from pathlib import Path
PROMPT='Local practice exercise only, fixture student 00000000 Nubi Test. Write Python 3 function sum_even(values) returning the sum of even integers, including negatives and zero. Include exactly four unittest tests: empty input, mixed odd/even, negative values, duplicate even values. Return one complete Python code block beginning import unittest and ending unittest.main() guarded by __name__. No external imports except unittest. No files, network, input, or package installation. This is a local test LMS exercise, not a real graded assignment.'
DEFINITION={'name':'nubi_practice_complete','description':'Use actual ChatGPT in the current Nubi chat browser to generate the sum_even local practice exercise, independently verify it in a sandbox, upload the verified file to a loopback test LMS, then read its durable receipt. Never submits to a real school. Returns authentication_required if ChatGPT needs user login.','inputSchema':{'type':'object','properties':{},'required':[],'additionalProperties':False}}
def verify(code,root):
 if not isinstance(code,str) or not 20<len(code)<20000:raise ValueError('bounded code required')
 tree=ast.parse(code)
 banned={'eval','exec','open','compile','__import__','globals','locals','getattr','setattr','breakpoint','input','help','exit','quit','vars','dir','type','object','super'}
 for n in ast.walk(tree):
  if isinstance(n,(ast.Import,ast.ImportFrom)) and not (isinstance(n,ast.Import) and len(n.names)==1 and n.names[0].name=='unittest' and n.names[0].asname is None):raise ValueError('only unittest import allowed')
  if isinstance(n,ast.Attribute) and n.attr not in {'TestCase','assertEqual','main'}:raise ValueError('attribute blocked')
  if isinstance(n,ast.Name) and (n.id in banned or n.id.startswith('__') and n.id!='__name__'):raise ValueError('name blocked')
  if isinstance(n,(ast.While,ast.With,ast.AsyncWith,ast.Try,ast.Lambda,ast.Global,ast.Nonlocal)):raise ValueError('unsupported exercise syntax')
 tests=[n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
 if len(tests)!=4:raise ValueError('four actual unittest methods required')
 root.mkdir(parents=True,exist_ok=True,mode=0o700);p=root/'practice.py';p.write_text(code);p.chmod(0o600)
 base=['bwrap','--unshare-all','--die-with-parent','--ro-bind','/usr','/usr','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--dir','/work','--ro-bind',str(p),'/work/practice.py','--chdir','/work','/usr/bin/python3','-I']
 own=subprocess.run(base+['practice.py'],capture_output=True,text=True,timeout=10);(root/'tests.log').write_text(own.stdout+own.stderr)
 if own.returncode or not re.search(r'Ran 4 tests',own.stderr):raise ValueError('model tests failed')
 extra='import runpy\nf=runpy.run_path("/work/practice.py")["sum_even"]\nassert f([0,-10,11,100])==90\nassert f([2,2,2])==6\nassert f([])==0\nprint("PASS 3 independent cases")'
 other=subprocess.run(base+['-c',extra],capture_output=True,text=True,timeout=10);(root/'independent.log').write_text(other.stdout+other.stderr)
 if other.returncode:raise ValueError('independent tests failed')
 return {'sha256':hashlib.sha256(code.encode()).hexdigest(),'model_tests':4,'independent_tests':3,'sandbox':'bubblewrap no network read-only runtime','tests_passed':True}
def command(action,**args):
 spec=importlib.util.spec_from_file_location('practice_transport',Path(__file__).with_name('nubi-goal-mcp.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 ident=m.post('/command',{'op':'goal_gpt','goal_id':os.environ['NUBI_GOAL_ID'],'action':action,**args})['id']
 for _ in range(70):
  out=m.post('/get-result',{'id':ident}).get('result')
  if out is not None:
   if out.get('error'):raise RuntimeError(out['error'])
   return out
  time.sleep(.3)
 raise TimeoutError('device browser timed out')
def complete(root):
 root=Path(root);root.mkdir(parents=True,exist_ok=True,mode=0o700)
 # A retried job never sends another prompt after an uncertain submission.
 statefile=root/'gpt-state.json'
 state=json.loads(statefile.read_text()) if statefile.exists() else {}
 if state.get('sending') and not state.get('sent'):raise RuntimeError('uncertain GPT submission; inspect instead of retrying')
 if not state.get('sent'):
  command('open');observed={}
  for _ in range(25):
   time.sleep(1);command('dismiss_cookie');observed=command('read')
   if observed.get('auth'):return {'state':'authentication_required','service':'ChatGPT','url':'https://chatgpt.com/'}
   if observed.get('composer'):break
  if not observed.get('composer'):return {'state':'authentication_required','service':'ChatGPT','url':'https://chatgpt.com/','reason':'composer unavailable'}
  state={'sending':True,'at':time.time()};statefile.write_text(json.dumps(state))
  sent=command('send',prompt=PROMPT)
  if sent.get('state') not in ('sent','already_sent'):raise RuntimeError('GPT send unconfirmed')
  state['sent']=True;statefile.write_text(json.dumps(state))
 elif state.get('sending') and not state.get('sent'):raise RuntimeError('uncertain GPT submission; inspect instead of retrying')
 for _ in range(90):
  time.sleep(2);observed=command('read')
  if not observed.get('busy') and observed.get('code') and 'unittest.main()' in '\n'.join(observed['code']):break
 else:raise TimeoutError('ChatGPT response deadline')
 command('reveal_answer')
 code='\n\n'.join(observed['code']).strip()+'\n';(root/'gpt-response.json').write_text(json.dumps(observed,ensure_ascii=False));proof=verify(code,root)
 # Actual HTTP upload and independent GET against a loopback-only practice LMS.
 from practice_lms import serve
 with serve(root.parent/'test-lms') as base:
  body={'environment':'LOCAL_PRACTICE_ONLY','student':'00000000 Nubi Test','filename':'practice.py','code':code,'proof':proof}
  request=urllib.request.Request(base+'/submissions',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'},method='POST')
  with urllib.request.urlopen(request,timeout=5) as f:receipt=json.load(f)
  with urllib.request.urlopen(base+'/submissions/'+receipt['id'],timeout=5) as f:confirmed=json.load(f)
  if confirmed!=receipt or confirmed['sha256']!=proof['sha256']:raise ValueError('receipt mismatch')
 out={'state':'completed','provider':'ChatGPT website / model label not exposed','proof':proof,'receipt':receipt,'source_url':observed['url'],'official_blackboard_submission':False}
 (root/'verified-result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));return out
