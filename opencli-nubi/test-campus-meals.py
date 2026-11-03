import json,sys,subprocess
from pathlib import Path
from campus_meals import daily
from campus_task import local_meal_only,wants_meal_plan,answer_needs_review,echoed_request
fixture={'week':{'startDate':'2026-11-02','isCurrentWeek':True},'lastUpdated':'2026-11-02T01:00:00+09:00','data':[{'cafeteria':'STUDENT','meals':[{'date':'2026-11-02','timeType':'LUNCH','isClosed':False,'menusByType':[{'menuType':'KOREAN','sections':[{'sectionType':'REGULAR','menus':[{'ko':'보쌈','en':'Bossam','allergens':[10]}]}]}]},{'date':'2026-11-03','timeType':'LUNCH','menusByType':[]}]}]}
r=daily('2026-11-02','보쌈',fetch=lambda url:fixture);assert len(r['meals'])==1 and r['meals'][0]['keyword_match'] and r['meals'][0]['sections'][0]['menus'][0]['allergens']==[10]
assert r['queue_minutes'] is None and r['inventory'] is None and r['ticket_purchase_executed'] is False and r['existing_ticket_state']=='not_queried'
assert daily('2026-11-04','',fetch=lambda url:fixture)['state']=='not_published'
try:daily('2026-11-09','',fetch=lambda url:fixture);raise AssertionError('wrong week accepted')
except ValueError:pass
assert echoed_request('2026-11-03 UNIST 학식에서 단백질 메뉴와 출발 시간 알려줘', '2026-11-03 UNIST 학식에서 단백질 메뉴와 출발 시간 알려줘.')
assert answer_needs_review('2026-11-03 UNIST 학식에서 단백질 메뉴와 출발 시간 알려줘', '2026-11-03 UNIST 학식에서 단백질 메뉴와 출발 시간 알려줘.', {'nubi_campus_meal_plan'})
assert local_meal_only('UNIST 오늘 학식 식단 조회해줘') and not local_meal_only('포털 식단 게시판 읽어줘')
assert local_meal_only('학식 특식 출발 알림 예약해줘') and wants_meal_plan('학식 특식 출발 알림 예약해줘')
assert not local_meal_only('학식 먹고 KTX 예약해줘') and not wants_meal_plan('오늘 학식 식단 조회')
assert not answer_needs_review('오늘 학식 식단 조회','대기와 품절 확인 불가',{'nubi_campus_meals'})
assert answer_needs_review('오늘 학식 식단 조회','식단을 확인했어요',set())
assert answer_needs_review('학식 출발 시간 계획', '식단만 조회', {'nubi_campus_meals'})
assert not answer_needs_review('학식 출발 시간 계획', '시간 계산', {'nubi_campus_meal_plan'})
for day in ['2026-02-30','20261102',12]:
 try:daily(day,fetch=lambda url:fixture);raise AssertionError('invalid date')
 except ValueError:pass
request={'jsonrpc':'2.0','id':1,'method':'tools/list'}
p=subprocess.run([sys.executable,str(Path(__file__).with_name('campus-document-local-mcp.py'))],input=json.dumps(request)+'\n',text=True,capture_output=True,check=True);assert any(t['name']=='nubi_campus_meals' for t in json.loads(p.stdout)['result']['tools'])
print('PASS exact-date/week meal parsing, unknown inventory/queue, allergen retention, missing publication and MCP listing')

assert not wants_meal_plan('2026-11-03 UNIST 점심 학식 실제 메뉴 조회해줘. 메뉴에서 단백질 메뉴를 골라줘.')
assert not answer_needs_review('학식에서 단백질 메뉴 골라줘','돈육바베큐폭찹을 추천해.',{'nubi_campus_meals'})
