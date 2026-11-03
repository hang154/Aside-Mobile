"""TAGO express-bus terminal resolution and planned timetable lookup."""
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from nubi_transit import TransitError

DEFINITION = {'name': 'nubi_transit_express_bus_journey', 'description': '고속버스 터미널명과 날짜로 TAGO 예정 시간표와 운임을 조회합니다. 좌석 및 예약 여부는 제공하지 않습니다.', 'inputSchema': {'type': 'object', 'properties': {k: {'type': 'string'} for k in ('departure_terminal', 'arrival_terminal', 'date', 'after_time')}, 'required': ['departure_terminal', 'arrival_terminal', 'date'], 'additionalProperties': False}}
INTERCITY_DEFINITION = dict(DEFINITION, name='nubi_transit_intercity_bus_journey', description='시외버스 터미널명과 날짜로 TAGO 예정 시간표와 운임을 조회합니다. 좌석 및 예약 여부는 제공하지 않습니다.')
SOURCE = 'https://www.data.go.kr/data/15098522/openapi.do'

def requested_after(text):
    match = re.search(r'(오전|오후)?\s*(\d{1,2})(?:시(?:\s*(\d{1,2})분)?|:(\d{2}))\s*이후', text)
    if not match: return None
    period, hour, minute, colon = match.groups(); hour = int(hour); minute = int(minute or colon or 0)
    if period:
        if not 1 <= hour <= 12: return None
        hour = hour % 12 + (12 if period == '오후' else 0)
    if hour > 23 or minute > 59: return None
    return f'{hour:02d}:{minute:02d}'

def format_journeys(journeys):
    parts = []
    for data in journeys:
        label = '시외버스' if data['operation'] == 'intercity_bus_journey' else '고속버스'
        lines = [f"{label} · {data['departure']['terminalNm']} → {data['arrival']['terminalNm']}", f"{data['date']} · {data['after_time']} 이후 계획 시간표"]
        for n, row in enumerate(data['items'][:3], 1):
            clock = lambda value: str(value)[8:10] + ':' + str(value)[10:12]
            fare = row.get('charge')
            price = f"{int(fare):,}원" if str(fare).isdigit() else '요금 정보 없음'
            lines.append(f"{n}. {clock(row['depPlandTime'])} → {clock(row['arrPlandTime'])} · {price} · {row.get('gradeNm', '')}")
        if not data['items']: lines.append('해당 조건에 맞는 운행편이 없어.')
        lines.append('출처: ' + data['source_url']); parts.append('\n'.join(lines))
    return '\n\n'.join(parts)

def query(client, departure_terminal, arrival_terminal, date, after_time='00:00'):
    return _query(client, departure_terminal, arrival_terminal, date, after_time, False)

def intercity_query(client, departure_terminal, arrival_terminal, date, after_time='00:00'):
    return _query(client, departure_terminal, arrival_terminal, date, after_time, True)

def _query(client, departure_terminal, arrival_terminal, date, after_time, intercity):
    base = 'SuburbsBusInfo/' if intercity else 'ExpBusInfo/'
    terminal_path = 'GetSuberbsBusTrminlList' if intercity else 'GetExpBusTrminlList'
    timetable_path = 'GetStrtpntAlocFndSuberbsBusInfo' if intercity else 'GetStrtpntAlocFndExpbusInfo'
    label = '시외버스' if intercity else '고속버스'
    for name in (departure_terminal, arrival_terminal):
        if not isinstance(name, str) or not re.fullmatch(r'[가-힣A-Za-z0-9 ()·.-]{1,50}', name):
            raise TransitError('invalid_arguments', '터미널명을 확인해 주세요.')
    try:
        if not isinstance(date, str) or not re.fullmatch(r'\d{8}', date): raise ValueError()
        datetime.strptime(date, '%Y%m%d')
        if not isinstance(after_time, str) or not re.fullmatch(r'\d{2}:\d{2}', after_time): raise ValueError()
        datetime.strptime(after_time, '%H:%M')
    except ValueError:
        raise TransitError('invalid_arguments', '출발일 YYYYMMDD와 시각 HH:mm을 확인해 주세요.') from None

    def request(path, params):
        data, observed, cached = client.request('tago', base + path, params, 300)
        body = data.get('response', data)['body']
        return client.rows(data), int(body.get('totalCount', len(client.rows(data)))), observed, cached

    def terminal(name):
        found = []
        for page in range(1, 101):
            rows, total, _, _ = request(terminal_path, {'terminalNm': name, 'pageNo': page, 'numOfRows': 100})
            found.extend(x for x in rows if x.get('terminalNm') == name)
            if page * 100 >= total: break
        else: raise TransitError('provider_error', '터미널 목록 페이지 상한을 초과했어요.')
        if len(found) != 1: raise TransitError('selection_required', '터미널명을 정확히 선택해 주세요: ' + name)
        return found[0]

    dep, arr = terminal(departure_terminal), terminal(arrival_terminal)
    items, observations, hits = [], [], []
    for page in range(1, 101):
        rows, total, observed, cached = request(timetable_path, {'depTerminalId': dep['terminalId'], 'arrTerminalId': arr['terminalId'], 'depPlandTime': date, 'pageNo': page, 'numOfRows': 100})
        observations.append(observed); hits.append(cached)
        for row in rows:
            stamp = str(row.get('depPlandTime', ''))
            if not re.fullmatch(r'\d{12,14}', stamp) or stamp[:8] != date:
                raise TransitError('provider_error', '요청 날짜와 고속버스 시간표가 일치하지 않아요.')
            if stamp[8:12] >= after_time.replace(':', ''): items.append(row)
        if page * 100 >= total: break
    else: raise TransitError('provider_error', '고속버스 시간표 페이지 상한을 초과했어요.')
    items.sort(key=lambda x: str(x['depPlandTime']))
    return {'state': 'results' if items else 'no_results', 'operation': 'intercity_bus_journey' if intercity else 'express_bus_journey', 'departure': dep, 'arrival': arr, 'date': date, 'after_time': after_time, 'items': items, 'fetched_at': datetime.fromtimestamp(min(observations), ZoneInfo('Asia/Seoul')).isoformat(), 'cached': all(hits), 'cache_max_age_seconds': 300, 'source_url': 'https://www.data.go.kr/data/15098541/openapi.do' if intercity else SOURCE, 'limitations': label + ' 계획 시간표와 제공 운임입니다. 잔여좌석, 지연, 예매 여부는 제공하지 않습니다.'}
