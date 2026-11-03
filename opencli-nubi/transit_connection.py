"""Compare observed station arrival with supplied train departures, without transactions."""
from datetime import datetime,timedelta,timezone
import math
DEFINITION={'name':'nubi_transit_connection_evaluate','description':'Compare a fresh observed station arrival ETA against supplied train departures. Requires timezone-aware timestamps; stale or uncertain inputs block the decision. No reservation, cancellation or payment.','inputSchema':{'type':'object','properties':{'observed_at':{'type':'string'},'station_arrival':{'type':'string'},'trains':{'type':'array','minItems':1,'maxItems':100,'items':{'type':'object','properties':{'id':{'type':'string'},'departure':{'type':'string'}},'required':['id','departure'],'additionalProperties':False}},'boarding_minutes':{'type':'integer','minimum':1,'maximum':120},'uncertainty_minutes':{'type':'integer','minimum':0,'maximum':120}},'required':['observed_at','station_arrival','trains','boarding_minutes','uncertainty_minutes'],'additionalProperties':False}}
def instant(value):
    if not isinstance(value,str):raise ValueError('시간대 포함 ISO 시각이 필요해요')
    t=datetime.fromisoformat(value)
    if t.tzinfo is None:raise ValueError('시간대 포함 ISO 시각이 필요해요')
    return t.astimezone(timezone.utc)
def evaluate(observed_at,station_arrival,trains,boarding_minutes,uncertainty_minutes,now=None):
    now=now or datetime.now(timezone.utc);observed=instant(observed_at);arrival=instant(station_arrival)
    for value,low in [(boarding_minutes,1),(uncertainty_minutes,0)]:
        if type(value) is not int or not low<=value<=120:raise ValueError('승차 준비·불확실 시간 범위를 확인해 주세요')
    age=(now-observed).total_seconds()
    if age< -30 or age>120:return {'state':'stale_observation','message':'2분 이내의 실제 이동 도착 예측을 다시 조회해 주세요.','transactions_executed':False}
    if arrival<observed or arrival-now>timedelta(days=2):raise ValueError('역 도착 예측 시각을 확인해 주세요')
    if not isinstance(trains,list) or not 1<=len(trains)<=100:raise ValueError('실제로 조회한 열차 목록이 필요해요')
    ready=arrival+timedelta(minutes=boarding_minutes+uncertainty_minutes);candidates=[];misses=[];ids=set()
    for train in trains:
        if not isinstance(train,dict) or set(train)!={'id','departure'} or not isinstance(train['id'],str) or not 1<=len(train['id'])<=80 or train['id'] in ids:raise ValueError('열차 ID가 비었거나 중복됩니다')
        ids.add(train['id']);departure=instant(train['departure'])
        if departure<now:continue
        row={'id':train['id'],'departure':train['departure'],'margin_minutes':math.floor((departure-ready).total_seconds()/60),'seat_state':'unknown'}
        (candidates if departure>=ready else misses).append(row)
    candidates.sort(key=lambda r:instant(r['departure']));misses.sort(key=lambda r:instant(r['departure']))
    return {'state':'results' if candidates else 'no_results','ready_at':ready.isoformat(),'candidates':candidates,'cannot_reach':misses,'source_quality':'caller_supplied_eta_and_timetable_not_independently_verified','requires_live_seat_and_fee_check':True,'transactions_executed':False,'existing_ticket_cancelled':False,'note':'GPS 속도만으로 실제 도로·버스 ETA를 계산하지 않습니다. 기존 표를 취소하거나 새 표를 결제하지 않았습니다.'}
