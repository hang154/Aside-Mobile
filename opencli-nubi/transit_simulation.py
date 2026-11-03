"""Explicit, stateless practice of a bus delay and a virtual train change."""
from datetime import timedelta
from zoneinfo import ZoneInfo
from transit_connection import instant, evaluate

DEFINITION={'name':'nubi_transit_simulate_change','description':'SIMULATION ONLY: use user-supplied bus station ETA, delay, and hypothetical trains to simulate changing an existing virtual ticket. Never calls a booking service and never cancels or purchases a real ticket. All timestamps must include timezone.','inputSchema':{'type':'object','properties':{'observed_at':{'type':'string'},'station_arrival':{'type':'string'},'delay_minutes':{'type':'integer','minimum':0,'maximum':240},'boarding_minutes':{'type':'integer','minimum':1,'maximum':120},'uncertainty_minutes':{'type':'integer','minimum':0,'maximum':120},'existing_train_id':{'type':'string'},'trains':{'type':'array','minItems':1,'maxItems':100,'items':{'type':'object','properties':{'id':{'type':'string'},'departure':{'type':'string'}},'required':['id','departure'],'additionalProperties':False}}},'required':['observed_at','station_arrival','delay_minutes','boarding_minutes','uncertainty_minutes','existing_train_id','trains'],'additionalProperties':False}}

def simulate(observed_at,station_arrival,delay_minutes,boarding_minutes,uncertainty_minutes,existing_train_id,trains):
    if type(delay_minutes) is not int or not 0<=delay_minutes<=240:raise ValueError('가상 지연 시간을 확인해 주세요')
    if not isinstance(existing_train_id,str) or not existing_train_id:raise ValueError('기존 가상 열차 ID가 필요해요')
    if not isinstance(trains,list) or sum(isinstance(t,dict) and t.get('id')==existing_train_id for t in trains)!=1:raise ValueError('기존 가상 열차가 목록에 한 번 있어야 해요')
    observed=instant(observed_at); delayed=instant(station_arrival)+timedelta(minutes=delay_minutes)
    result=evaluate(observed_at,delayed.isoformat(),trains,boarding_minutes,uncertainty_minutes,now=observed)
    candidates=result.get('candidates',[])
    existing=next((x for x in candidates if x['id']==existing_train_id),None)
    existing_departure=instant(next(t['departure'] for t in trains if t['id']==existing_train_id))
    selected=existing or next((t for t in candidates if instant(t['departure'])>existing_departure),None)
    result.update({'simulation':True,'state':'results' if selected else 'no_results','delay_minutes':delay_minutes,'station_arrival_before_delay':station_arrival,'delayed_station_arrival':delayed.isoformat(),'existing_virtual_train_id':existing_train_id,'selected_virtual_train_id':selected['id'] if selected else None,'virtual_change':bool(selected and not existing),'virtual_confirmation':bool(selected),'transactions_executed':False,'existing_ticket_cancelled':False,'note':'가상 시뮬레이션입니다. 실제 버스 운행, 좌석·수수료, 예매·취소·결제를 확인하거나 실행하지 않았습니다.'})
    return result


def format_result(data):
    selected=data.get('selected_virtual_train_id')
    kst=lambda t: instant(t).astimezone(ZoneInfo('Asia/Seoul')).isoformat()
    lines=['가상 513번 지연·열차 변경 시뮬레이션',f"가상 지연: {data['delay_minutes']}분",f"지연 후 가상 울산역 도착: {kst(data['delayed_station_arrival'])}",f"승차 준비 완료: {kst(data['ready_at'])}",f"기존 가상 열차: {data['existing_virtual_train_id']}"]
    if selected:
        row=next(t for t in data['candidates'] if t['id']==selected)
        lines += [f"선택한 가상 열차: {selected} · 출발 {kst(row['departure'])} · 여유 {row['margin_minutes']}분",'가상 변경 결과: '+('다음 열차로 변경' if data['virtual_change'] else '기존 열차 유지')]
    else:lines.append('이용 가능한 다음 가상 열차가 없습니다.')
    lines.append('입력된 시각을 사용한 가상 결과입니다. 실제 좌석·수수료·예약·취소·결제는 확인하거나 실행하지 않았습니다.')
    return '\n'.join(lines)
