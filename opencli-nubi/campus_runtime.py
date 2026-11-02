"""Bind campus tools to the selected current Nubi app, without reading credentials."""
import os,subprocess,urllib.request,json
from contextlib import contextmanager
PACKAGE='ai.decisionos.nubi.travelpilot.goals'
@contextmanager
def current_browser(env=None):
 env=dict(os.environ if env is None else env)
 # Explicit local endpoint remains supported for existing deployments.
 if env.get('NUBI_CDP_ENDPOINT'):
  yield env;return
 adb=env.get('NUBI_ADB','/tmp/aside-android-build/sdk/platform-tools/adb')
 serial=env.get('NUBI_ANDROID_SERIAL')
 if not serial:
  rows=subprocess.check_output([adb,'devices'],text=True,timeout=10).splitlines()[1:]
  devices=[r.split()[0] for r in rows if len(r.split())>=2 and r.split()[1]=='device']
  if len(devices)!=1:raise RuntimeError('NUBI_ANDROID_SERIAL로 실행 기기를 지정해 주세요.')
  serial=devices[0]
 prefix=[adb,'-s',serial];pid=subprocess.check_output(prefix+['shell','pidof',PACKAGE],text=True,timeout=10).strip().split()
 if len(pid)!=1 or not pid[0].isdigit():raise RuntimeError('최신 누비 앱을 먼저 열어 주세요.')
 port=subprocess.check_output(prefix+['forward','tcp:0','localabstract:webview_devtools_remote_'+pid[0]],text=True,timeout=10).strip()
 if not port.isdigit():raise RuntimeError('누비 브라우저 연결을 만들지 못했습니다.')
 try:
  endpoint='http://127.0.0.1:'+port
  with urllib.request.urlopen(endpoint+'/json/list',timeout=5) as response:pages=json.load(response)
  pages=[p for p in pages if p.get('type')=='page']
  if len(pages)!=1:raise RuntimeError('누비 연결창을 닫고 브라우저 하나만 남겨 주세요.')
  env.update(NUBI_CDP_ENDPOINT=endpoint,NUBI_CDP_TARGET_ID=pages[0]['id'],NUBI_ANDROID_SERIAL=serial)
  yield env
 finally:
  subprocess.run(prefix+['forward','--remove','tcp:'+port],capture_output=True,timeout=10)
