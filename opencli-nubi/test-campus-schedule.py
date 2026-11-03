import json,subprocess,sys
from pathlib import Path
from campus_schedule import propose
from campus_task import local_schedule_only

def person(name,*windows):return {'name':name,'windows':[{'start':s,'end':e} for s,e in windows]}
a=person('A',('2026-11-03T13:00:00+09:00','2026-11-03T15:00:00+09:00'),('2026-11-03T14:00:00+09:00','2026-11-03T16:00:00+09:00'))
b=person('B',('2026-11-03T05:30:00+00:00','2026-11-03T06:00:00+00:00'))
r=propose(30,[a,b]);assert len(r['candidates'])==1 and r['candidates'][0]['start']=='2026-11-03T14:30:00+09:00';assert not r['invitations_sent']
assert propose(31,[a,b])['state']=='no_common_window'
c=person('C',('2026-11-03T15:00:00+09:00','2026-11-03T16:00:00+09:00'));assert propose(5,[b,c])['state']=='no_common_window'
for duration,people in [(True,[a,b]),(0,[a,b]),(30,[a,a]),(30,[a]),(30,[a,person('B',('2026-11-03T14:00:00','2026-11-03T15:00:00'))]),(30,[a,person('B',('2026-11-03T15:00:00+09:00','2026-11-03T14:00:00+09:00'))])]:
 try:propose(duration,people);raise AssertionError('invalid accepted')
 except ValueError:pass
assert local_schedule_only('팀 일정. 사용자 제공 가능 시간만 계산해')
assert not local_schedule_only('블랙보드 일정을 조회하고 팀 일정 계산해')
request={'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'nubi_team_schedule_propose','arguments':{'duration_minutes':30,'participants':[a,b]}}}
response=subprocess.run([sys.executable,str(Path(__file__).with_name('campus-document-local-mcp.py'))],input=json.dumps(request)+'\n',text=True,capture_output=True,check=True)
r=json.loads(json.loads(response.stdout)['result']['content'][0]['text']);assert r['candidates'][0]['start']=='2026-11-03T14:30:00+09:00'
print('PASS team availability intersection, timezone, merge, no overlap, invalid inputs, MCP roundtrip')
