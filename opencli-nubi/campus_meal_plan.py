"""Meal-name based suggestion and class-aware pre-peak reminder, not crowd measurement."""
from datetime import datetime,timedelta,time
from zoneinfo import ZoneInfo
from campus_meals import daily
KST=ZoneInfo('Asia/Seoul')
PROTEIN=('고기','닭','돼지','소고기','쇠고기','치킨','생선','고등어','삼치','연어','두부','계란','달걀','불고기','돈까스','돈가스','수육','보쌈','제육','오리','참치','갈비')
SPECIAL=('보쌈','수육','특식','스테이크','삼계탕','장어')
DEFINITION={'name':'nubi_campus_meal_plan','description':'Read actual date-matched cafeteria menu and propose arrival/ticket reminder before 11:50 based on supplied class windows and published opening time. Protein is a menu-name proxy, not measured grams. Does not purchase tickets.','inputSchema':{'type':'object','properties':{'day':{'type':'string'},'classes':{'type':'array','maxItems':30,'items':{'type':'object','properties':{'start':{'type':'string','description':'HH:mm Korean local time on day, or ISO timestamp with timezone'},'end':{'type':'string','description':'HH:mm Korean local time on day, or ISO timestamp with timezone'}},'required':['start','end'],'additionalProperties':False}},'walk_minutes':{'type':'integer','minimum':1,'maximum':60},'opening_time':{'type':'string','description':'Confirmed cafeteria/ticket opening HH:mm; required to recommend an actionable slot'},'ticket_advance_supported':{'type':'boolean'}},'required':['day','classes','walk_minutes','opening_time','ticket_advance_supported'],'additionalProperties':False}}
def plan(day,classes,walk_minutes,opening_time,ticket_advance_supported,fetch=None):
    if type(walk_minutes)is not int or not 1<=walk_minutes<=60:raise ValueError('이동시간 오류')
    d=datetime.fromisoformat(day).date();opening=datetime.combine(d,time.fromisoformat(opening_time),KST)
    if not isinstance(classes,list) or len(classes)>30 or type(ticket_advance_supported)is not bool:raise ValueError('시간표/식권 조건 오류')
    windows=[]
    def class_time(value):
        if isinstance(value,str) and len(value)==5 and value[2]==':':
            return datetime.combine(d,time.fromisoformat(value),KST)
        return datetime.fromisoformat(value)
    for w in classes:
        start=class_time(w['start']);end=class_time(w['end'])
        if start.tzinfo is None or end.tzinfo is None or not start<end:raise ValueError('시간대 포함 시간표 필요')
        windows.append((start.astimezone(KST),end.astimezone(KST)))
    result=daily(day,**({'fetch':fetch} if fetch else {}));ranked=[]
    for meal in result['meals']:
        if meal['closed'] or meal['time_type']!='LUNCH':continue
        names=[m['ko'] for sec in meal['sections'] for m in sec['menus']];protein=[n for n in names if any(k in n for k in PROTEIN)];special=[n for n in names if any(k in n for k in SPECIAL)]
        if protein or special:ranked.append({'cafeteria':meal['cafeteria'],'menu_names':names,'protein_proxy_matches':protein,'special_matches':special,'score':len(protein)+10*len(special)})
    ranked.sort(key=lambda x:-x['score']);peak=datetime.combine(d,time(11,50),KST);duration=timedelta(minutes=walk_minutes+10)
    # Latest safe arrival 11:40, ten minutes before stated peak, includes return walking around classes.
    arrival=peak-timedelta(minutes=10);selected=None
    while arrival>=opening:
        leave=arrival-timedelta(minutes=walk_minutes);back=arrival+duration
        if not any(leave<end and start<back for start,end in windows):selected=(leave,arrival,back);break
        arrival-=timedelta(minutes=5)
    return {'state':'planned' if ranked and selected else 'no_prepeak_slot' if ranked else 'no_matching_lunch','day':day,'source':result['source'],'provider_updated_at':result['provider_updated_at'],'recommendations':ranked,'leave_at':selected[0].isoformat() if selected else None,'arrive_at':selected[1].isoformat() if selected else None,'return_at':selected[2].isoformat() if selected else None,'action':'식당에 들러 식권 미리 구매' if ticket_advance_supported else '식당에 일찍 도착','opening_time_source':'user_supplied_confirmed','protein_grams':None,'queue_measurement':False,'peak_proxy':'11:50–12:10 사용자 지정','ticket_purchase_executed':False,'note':'단백질 메뉴명 기반 추천. 실제 함량·혼잡도·사전 식권 판매 여부를 추정하지 않음. 시간표와 운영시간 확인 후 알림 예약.'}
