#!/usr/bin/env python3
"""Developer-only Android ChatGPT -> local practice LMS harness. Never targets real courses."""
import argparse,datetime,json,pathlib,re,subprocess,time,xml.etree.ElementTree as ET
p=argparse.ArgumentParser();p.add_argument('--device',required=True);p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--prompt-file',type=pathlib.Path,required=True);p.add_argument('--deadline',required=True);a=p.parse_args()
deadline=datetime.datetime.fromisoformat(a.deadline)
if deadline.tzinfo is None:raise SystemExit('timezone-aware deadline required')
trigger=deadline.timestamp()-3600
if not 0<trigger-time.time()<86400:raise SystemExit('trigger must be within next day')
prompt=a.prompt_file.read_text().strip()
if '00000000' not in prompt or 'practice' not in prompt.lower():raise SystemExit('fixture student and practice-only prompt required')
a.output.mkdir(parents=True,exist_ok=True,mode=0o700)
def adb(*args):return subprocess.check_output(['adb','-s',a.device,*args])
def snapshot():
 adb('shell','uiautomator','dump','/sdcard/nubi-practice-harness.xml');raw=adb('exec-out','cat','/sdcard/nubi-practice-harness.xml');return raw,ET.fromstring(raw)
prior=a.output/'practice-run.json'
if prior.exists():
 old=json.loads(prior.read_text())
 if old.get('state') not in ('SCHEDULED','BLOCKED_DRAFT_OR_SEND_MISMATCH'):raise SystemExit('Prior submission or uncertain click exists; inspect instead of resending')
 if old.get('deadline_at')!=deadline.timestamp():raise SystemExit('Use a fresh output directory for a different deadline')
state={'environment':'LOCAL_PRACTICE_ONLY','state':'SCHEDULED','trigger_at':trigger,'deadline_at':deadline.timestamp(),'no_real_lms':True}
def save():
 tmp=a.output/'practice-run.tmp';tmp.write_text(json.dumps(state,indent=2));tmp.replace(a.output/'practice-run.json')
save()
while time.time()<trigger:time.sleep(min(5,trigger-time.time()))
raw,root=snapshot();drafts=[n for n in root.iter('node') if n.get('text','').strip()==prompt and n.get('package')=='com.openai.chatgpt']
send=[n for n in root.iter('node') if n.get('content-desc') in ('메시지 보내기','Send message') and n.get('enabled')=='true']
if not drafts or len(send)!=1:state['state']='BLOCKED_DRAFT_OR_SEND_MISMATCH';save();raise SystemExit('Prepared practice draft not present; untouched')
nums=list(map(int,re.findall(r'\d+',send[0].get('bounds',''))));assert len(nums)==4
state.update(state='SUBMITTING');save();adb('shell','input','tap',str((nums[0]+nums[2])//2),str((nums[1]+nums[3])//2));state.update(state='GPT_REQUEST_SENT',fired_at=time.time());save()
for _ in range(18):
 time.sleep(10);raw,root=snapshot();texts=[n.get('text','') for n in root.iter('node')];(a.output/'practice-result.xml').write_bytes(raw)
 if any(t.startswith('import unittest') and 'def sum_even' in t for t in texts):state.update(state='GPT_RESULT_OBSERVED',observed_at=time.time());save();break
else:state['state']='RESULT_TIMEOUT';save()
