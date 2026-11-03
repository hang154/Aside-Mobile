"""Explicit, read-only TAGO catalog operations for subway, domestic air and ferries."""
from datetime import datetime
from zoneinfo import ZoneInfo
from nubi_transit import TransitError, text, integer

S = {'type': 'string'}
P = {'type': 'integer', 'minimum': 1, 'maximum': 100}
SPECS = {
 'bus_routes': ('BusRouteInfoInqireService/getRouteNoList', '15098529', {'city_code': ('cityCode', S), 'route_number': ('routeNo', S), 'page': ('pageNo', P)}, ['city_code', 'route_number'], '도시와 버스 번호로 실제 노선 ID 조회'),
 'bus_route_stops': ('BusRouteInfoInqireService/getRouteAcctoThrghSttnList', '15098529', {'city_code': ('cityCode', S), 'route_id': ('routeId', S), 'page': ('pageNo', P)}, ['city_code', 'route_id'], '버스 노선별 경유 정류소 조회'),
 'subway_stations': ('SubwayInfo/GetKwrdFndSubwaySttnList', '15098554', {'name': ('subwayStationName', S), 'page': ('pageNo', P)}, ['name'], '지하철 역과 노선의 실제 코드 검색'),
 'subway_schedule': ('SubwayInfo/GetSubwaySttnAcctoSchdulList', '15098554', {'station_id': ('subwayStationId', S), 'day_type': ('dailyTypeCode', S), 'direction': ('upDownTypeCode', S), 'page': ('pageNo', P)}, ['station_id', 'day_type', 'direction'], '역별 계획 시간표. 요일 01 평일, 02 토요일, 03 일요일; 방향 U 상행, D 하행'),
 'airports': ('DmstcFlightNvgInfo/GetArprtList', '15098526', {}, [], 'TAGO 국내 공항 목록'),
 'airlines': ('DmstcFlightNvgInfo/GetAirmanList', '15098526', {}, [], 'TAGO 항공사 목록'),
 'flights': ('DmstcFlightNvgInfo/GetFlightOpratInfoList', '15098526', {'departure_id': ('depAirportId', S), 'arrival_id': ('arrAirportId', S), 'date': ('depPlandTime', S), 'page': ('pageNo', P)}, ['departure_id', 'arrival_id', 'date'], '국내 항공 운항 정보. 공항 ID는 airports에서 조회'),
 'ports': ('DmstcShipNvgInfo/GetPortList', '15098523', {'name': ('nodeNm', S), 'page': ('pageNo', P)}, ['name'], '국내 선박 항구 목록 검색'),
 'ferry_terminals': ('DmstcShipNvgInfo/GetPsnshipTrminlList', '15098523', {}, [], '국내 여객선 터미널 목록'),
 'ship_types': ('DmstcShipNvgInfo/GetShipKndList', '15098523', {}, [], '국내 선박 종류 목록'),
 'ferries': ('DmstcShipNvgInfo/GetShipOpratInfoList', '15098523', {'departure_id': ('depNodeId', S), 'date': ('depPlandTime', S), 'page': ('pageNo', P)}, ['departure_id', 'date'], '국내 선박 운항 정보. 출발 항구 ID는 ports에서 조회'),
 'korail_station_codes': ('B551457/run/v2/codes2', '15125762', {'name': ('cond[value::LIKE]', S), 'page': ('pageNo', P)}, [], '코레일 철도역 코드 목록 조회'),
 'korail_run_plans': ('B551457/run/v2/travelerTrainRunPlan2', '15125762', {'date': ('cond[run_ymd::GTE]', S), 'station': ('cond[dptre_stn_nm::EQ]', S), 'page': ('pageNo', P)}, ['date'], '코레일 여객열차 운행계획. 운행 날짜의 계획 데이터이며 잔여석과 지연이 아님'),
 'korail_run_history': ('B551457/run/v2/travelerTrainRunInfo2', '15125762', {'date': ('cond[run_ymd::GTE]', S), 'station': ('cond[stn_nm::EQ]', S), 'page': ('pageNo', P)}, ['date'], '코레일 과거 운행기록. 공식 제공 기간은 전일까지이며 실시간 지연 조회가 아님'),
}
DEFINITIONS = [{'name': 'nubi_transit_' + name, 'description': spec[4], 'inputSchema': {'type': 'object', 'properties': {k: v[1] for k, v in spec[2].items()}, 'required': spec[3], 'additionalProperties': False}} for name, spec in SPECS.items()]

def call(client, operation, args):
    if operation not in SPECS or not isinstance(args, dict): raise TransitError('invalid_arguments', '지원하는 교통 조회를 선택해 주세요.')
    path, source, fields, required, _ = SPECS[operation]
    if set(args) - set(fields) or set(required) - set(args): raise TransitError('invalid_arguments', '조회 입력을 확인해 주세요.')
    if operation == 'subway_schedule' and (args.get('day_type') not in ('01','02','03') or args.get('direction') not in ('U','D')): raise TransitError('invalid_arguments', '요일 또는 상하행 코드를 확인해 주세요.')
    params = {}
    for key, value in args.items():
        if key == 'page': integer(value, 1, 100, '페이지')
        elif key == 'date':
            text(value, r'[0-9]{8}', '날짜')
            try: datetime.strptime(value, '%Y%m%d')
            except ValueError: raise TransitError('invalid_arguments', '유효한 날짜를 입력해 주세요.') from None
        elif key in ('name','station'): text(value, r'[가-힣A-Za-z0-9 ()·.-]{1,50}', '이름')
        elif key == 'city_code': text(value, r'[0-9]{1,5}', '도시코드')
        else: text(value, r'[A-Za-z0-9_]{1,40}', key)
        params[fields[key][0]] = value
    if 'page' in fields: params.setdefault('pageNo', 1); params['numOfRows'] = 20
    if operation == 'korail_station_codes': params['cond[type::EQ]'] = 'stn_cd'
    if operation in ('korail_run_plans','korail_run_history'): params['cond[run_ymd::LTE]'] = args['date']
    data, observed, cached = client.request('tago', path, params, 300)
    rows = client.rows(data); body = data.get('response', data)['body']
    return {'state': 'results' if rows else 'no_results', 'operation': operation, 'items': rows, 'total_count': body.get('totalCount', len(rows)), 'page': args.get('page', 1), 'fetched_at': datetime.fromtimestamp(observed, ZoneInfo('Asia/Seoul')).isoformat(), 'cached': cached, 'source_url': 'https://www.data.go.kr/data/' + source + '/openapi.do', 'limitations': '공급자가 제공한 정보이며 좌석·예약·결제 여부를 의미하지 않습니다.'}
