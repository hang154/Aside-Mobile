from pathlib import Path
import xml.etree.ElementTree as ET,ast,subprocess,json,hashlib
import argparse
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=a.output.resolve();root=ET.parse(r/'practice-result.xml');texts=[n.get('text','') for n in root.iter('node')];candidates=[t for t in texts if t.startswith('import unittest') and 'def sum_even' in t];assert len(candidates)==1
code=candidates[0]+'\n';tree=ast.parse(code)
for n in ast.walk(tree):
 if isinstance(n,(ast.Import,ast.ImportFrom)):assert isinstance(n,ast.Import) and [x.name for x in n.names]==['unittest']
 if isinstance(n,ast.Attribute):assert n.attr in {'TestCase','assertEqual','main'}
 if isinstance(n,ast.Name):assert n.id not in {'eval','exec','open','compile','__import__','globals','locals','getattr','setattr','breakpoint','input'}
p=r/'scenario-practice.py';p.write_text(code)
# Read-only filesystem and no network; model text is not executed in the agent environment.
cmd=['bwrap','--unshare-all','--die-with-parent','--ro-bind','/usr','/usr','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--dir','/work','--ro-bind',str(p),'/work/practice.py','--chdir','/work','/usr/bin/python3','-I','practice.py']
x=subprocess.run(cmd,capture_output=True,text=True,timeout=10);(r/'practice-tests.log').write_text(x.stdout+x.stderr);assert x.returncode==0,x.stderr
# Independently authored edge cases, beyond the model's own test assertions.
extra='import runpy\nf=runpy.run_path("/work/practice.py")["sum_even"]\nassert f([0,-10,11,100])==90\nassert f([2,2,2])==6\nassert f([])==0\nprint("PASS 3 independent edge cases")'
cmd[-3:]=['/usr/bin/python3','-I','-c',extra];y=subprocess.run(cmd,capture_output=True,text=True,timeout=10);assert y.returncode==0,y.stderr;(r/'practice-independent.log').write_text(y.stdout+y.stderr)
proof={'model':'ChatGPT Android app / model label not exposed','source':'actual Android UI response','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'tests_passed':True,'model_unittests':4,'independent_cases':3,'environment':'local practice only','ui_warning':'Too many requests text also present; no second request sent'};(r/'scenario-practice-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
