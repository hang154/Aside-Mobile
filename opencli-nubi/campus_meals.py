"""Read-only adapter for the meal.hexa.pro API published by HeXA-UNIST/meal_client.
No ticket purchase, live inventory or queue data is exposed by this adapter.
"""
import json,urllib.request,urllib.error,time
from datetime import datetime,date,timedelta
from zoneinfo import ZoneInfo
BASE='https://meal.hexa.pro'
DEFINITION={'name':'nubi_campus_meals','description':'Read actual UNIST cafeteria menus from the current 밥먹어U public API, matched to the exact Korean date. Returns source/update time and keyword matches. Inventory, queue length and ticket purchase are unknown.','inputSchema':{'type':'object','properties':{'day':{'type':'string','description':'Exact Korean date YYYY-MM-DD; omitted means today'},'keyword':{'type':'string','maxLength':40}},'additionalProperties':False}}
def fetch_json(url):
    request=urllib.request.Request(url,headers={'User-Agent':'Nubi/0.6.20 (+UNIST campus meal integration)','Accept':'application/json','Origin':BASE})
    # Fixed published host; redirects are rejected to retain the source boundary.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):return None
    with urllib.request.build_opener(NoRedirect()).open(request,timeout=15) as response:
        body=response.read(1048577)
        if len(body)>1048576:raise ValueError('식단 응답 크기 초과')
        return json.loads(body)
def daily(day=None,keyword='',fetch=fetch_json):
    if day is None:day=datetime.now(ZoneInfo('Asia/Seoul')).date().isoformat()
    if not isinstance(day,str):raise ValueError('한국 날짜 YYYY-MM-DD가 필요해요')
    target=date.fromisoformat(day)
    if target.isoformat()!=day or not isinstance(keyword,str) or len(keyword)>40:raise ValueError('날짜와 검색어를 확인해 주세요')
    monday=(target-timedelta(days=target.weekday())).isoformat();url=BASE+'/v2/menu/'+monday
    root=fetch(url)
    if not isinstance(root,dict) or root.get('week',{}).get('startDate')!=monday or not isinstance(root.get('data'),list):raise ValueError('요청한 주의 식단인지 확인하지 못했어요')
    rows=[]
    for cafeteria in root['data']:
        for meal in cafeteria.get('meals',[]):
            if meal.get('date')!=day:continue
            sections=[]
            for group in meal.get('menusByType',[]):
                for section in group.get('sections',[]):
                    menus=[{'ko':m['ko'],'en':m.get('en'),'allergens':m.get('allergens')} for m in section.get('menus',[]) if isinstance(m,dict) and isinstance(m.get('ko'),str)]
                    if menus:sections.append({'menu_type':group.get('menuType'),'section':section.get('sectionType'),'title':section.get('sectionTitle'),'calorie':section.get('calorie'),'menus':menus})
            haystack=' '.join(m['ko'] for section in sections for m in section['menus'])
            rows.append({'cafeteria':cafeteria.get('cafeteria'),'day':day,'time_type':meal.get('timeType'),'closed':meal.get('isClosed'),'sections':sections,'keyword_match':bool(keyword and keyword in haystack)})
    return {'state':'observed' if rows else 'not_published','day':day,'source':url,'provider':'밥먹어U / HeXA-UNIST','provider_updated_at':root.get('lastUpdated'),'fetched_at':datetime.now(ZoneInfo('Asia/Seoul')).isoformat(),'is_current_week':root.get('week',{}).get('isCurrentWeek'),'keyword':keyword,'meals':rows,'queue_minutes':None,'inventory':None,'ticket_purchase_executed':False,'existing_ticket_state':'not_queried','note':'메뉴 정보이며 실시간 대기·재고·식권 구매 결과가 아닙니다.'}
