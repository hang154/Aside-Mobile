#!/usr/bin/env python3
"""Read-only transit MCP; no credentials in model input and no reservation tools."""
import json,sys
from device_view import DEFINITION as VIEW_DEFINITION, show as show_source
from transit_connection import DEFINITION as CONNECTION_DEFINITION, evaluate
from transit_simulation import DEFINITION as SIMULATION_DEFINITION, simulate
from unist_bus513 import DEFINITION as BUS513_DEFINITION, read as bus513_read
from nubi_transit import Transit,TransitError
from rail_journey import DEFINITION as RAIL_DEFINITION, query as rail_query
from virtual_ticket import DEFINITION as TICKET_DEFINITION, call as ticket_call
from unist_homebound import DEFINITION as HOMEBOUND_DEFINITION, plan as homebound_plan
from express_bus import DEFINITION as EXPRESS_DEFINITION, INTERCITY_DEFINITION, query as express_query, intercity_query
from tago_catalog import DEFINITIONS as CATALOG_DEFINITIONS, SPECS as CATALOG_SPECS, call as catalog_call
from kakao_location import DEFINITIONS as KAKAO_DEFINITIONS, places as kakao_places, taxi as kakao_taxi
from public_info import DEFINITIONS as PUBLIC_DEFINITIONS, tourism, weather, air
S=lambda description:{'type':'string','description':description}
N=lambda description:{'type':'number','description':description}
FIELDS={
 'status':({},[],'가입·서버 키 설정 상태. 값은 공개하지 않음.'),
 'bus_cities':({},[],'TAGO 버스 지원 도시와 실제 도시코드 조회.'),
 'bus_stops':({'city_code':S('bus_cities에서 얻은 도시코드'),'name':S('정류소 이름'),'page':{'type':'integer','minimum':1,'maximum':100}},['city_code','name'],'버스 정류소 검색. 정류소정보 별도 활용승인 필요.'),
 'bus_arrivals':({'city_code':S('실제 도시코드'),'stop_id':S('bus_stops에서 얻은 nodeid'),'page':{'type':'integer','minimum':1,'maximum':100}},['city_code','stop_id'],'정류소별 예측 도착 초·남은 정류장·노선 조회. 정류소 ID 추측 금지.'),
 'bus_positions':({'city_code':S('실제 도시코드'),'route_id':S('도착정보의 routeid'),'page':{'type':'integer','minimum':1,'maximum':100}},['city_code','route_id'],'노선별 버스 현재 위치. 버스위치정보 별도 활용승인 필요.'),
 'train_cities':({},[],'열차 API의 도시코드 조회. 버스 도시코드와 혼동 금지.'),
 'train_types':({},[],'실제 KTX 등 열차 종류 코드 조회.'),
 'train_stations':({'city_code':S('train_cities에서 얻은 도시코드'),'page':{'type':'integer','minimum':1,'maximum':100}},['city_code'],'도시별 기차역 nodeid·역명 목록. 페이지를 통해 찾고 ID를 추측하지 않음.'),
 'train_timetable':({'departure_id':S('실제로 조회한 출발역 nodeid'),'arrival_id':S('실제로 조회한 도착역 nodeid'),'date':S('한국 날짜 YYYYMMDD'),'train_type':S('train_types에서 얻은 코드. 생략 시 전체'),'page':{'type':'integer','minimum':1,'maximum':100}},['departure_id','arrival_id','date'],'열차 출발·도착 계획 시간표 및 표시요금. 잔여좌석·실시간 지연·예약 정보 아님.'),
 'subway_arrivals':({'station':S('서울 지하철 역명. 공식 API 표기')},['station'],'서울 지하철 도착 예측과 공급자 생성 시각. 서울 외 지역 지원을 가정하지 않음.'),
 'routes':({k:N('사용자가 제공하거나 확인한 WGS84 좌표. 추측 금지.') for k in ['start_lon','start_lat','end_lon','end_lat']},['start_lon','start_lat','end_lon','end_lat'],'TMAP 대중교통 경로·시간(초)·환승·요금. 서버 일일 상한 10회, 결과 캐시 안 함. 동일 경로 반복 호출 금지.')}
DEFINITIONS=[HOMEBOUND_DEFINITION,TICKET_DEFINITION,VIEW_DEFINITION,RAIL_DEFINITION,EXPRESS_DEFINITION,INTERCITY_DEFINITION,CONNECTION_DEFINITION,SIMULATION_DEFINITION,BUS513_DEFINITION]+KAKAO_DEFINITIONS+PUBLIC_DEFINITIONS+CATALOG_DEFINITIONS+[{'name':'nubi_transit_'+op,'description':desc,'inputSchema':{'type':'object','properties':fields,'required':req,'additionalProperties':False}} for op,(fields,req,desc) in FIELDS.items()]
def call(name,args,client):
 if name in ('nubi_transit_tourism_search','nubi_transit_weather_now','nubi_transit_air_quality'):
  expected,fn={'nubi_transit_tourism_search':('query',tourism),'nubi_transit_weather_now':('place',weather),'nubi_transit_air_quality':('province',air)}[name]
  if not isinstance(args,dict) or set(args)!={expected}:raise TransitError('invalid_arguments','조회 입력을 확인해 주세요.')
  return fn(client,args[expected])
 if name=='nubi_transit_place_search':
  if not isinstance(args,dict) or set(args)!={'query'}:raise TransitError('invalid_arguments','장소 검색어를 확인해 주세요.')
  return kakao_places(client,args['query'])
 if name=='nubi_transit_taxi_estimate':
  if not isinstance(args,dict) or set(args)!={'origin','destination'}:raise TransitError('invalid_arguments','출발지와 도착지를 확인해 주세요.')
  return kakao_taxi(client,args['origin'],args['destination'])
 if name=='nubi_transit_unist_homebound':
  try:return homebound_plan(client,**args)
  except (TypeError,ValueError) as error:raise TransitError('invalid_arguments',str(error)) from None
 if name=='nubi_transit_virtual_ticket':
  try:return ticket_call(client,args)
  except (TypeError,ValueError) as error:raise TransitError('invalid_arguments',str(error)) from None
 if name=='nubi_transit_express_bus_journey':
  try:return express_query(client,**args)
  except TypeError:raise TransitError('invalid_arguments','고속버스 조회 필수 입력을 확인해 주세요.') from None
 if name=='nubi_transit_intercity_bus_journey':
  try:return intercity_query(client,**args)
  except TypeError:raise TransitError('invalid_arguments','시외버스 조회 필수 입력을 확인해 주세요.') from None
 if isinstance(name,str) and name.removeprefix('nubi_transit_') in CATALOG_SPECS and name.startswith('nubi_transit_'):
  return catalog_call(client,name.removeprefix('nubi_transit_'),args)
 if name=='nubi_transit_open_source':
  if set(args)!={'source'}:raise TransitError('invalid_arguments','열 화면을 선택해 주세요.')
  return show_source(args['source'])
 if name=='nubi_transit_rail_journey':
  try:return rail_query(client,**args)
  except TypeError:raise TransitError('invalid_arguments','열차 조회 필수 입력을 확인해 주세요.') from None
 if name=='nubi_transit_unist_513':
  if args!={}:raise TransitError('invalid_arguments','인자를 받지 않습니다.')
  try:return bus513_read()
  except Exception:raise TransitError('source_unavailable','513번 공개 운행정보를 읽지 못했어요. 잠시 뒤 다시 확인해 주세요.') from None
 if name=='nubi_transit_simulate_change':
  try:return simulate(**args)
  except (ValueError,TypeError,KeyError) as e:raise TransitError('invalid_arguments',str(e)) from None
 if name=='nubi_transit_connection_evaluate':
  try:return evaluate(**args)
  except (ValueError,TypeError) as e:raise TransitError('invalid_arguments',str(e)) from None
 op=name.removeprefix('nubi_transit_') if isinstance(name,str) else ''
 if op not in FIELDS or not isinstance(args,dict):raise TransitError('invalid_arguments','지원하는 도구 입력을 확인해 주세요.')
 fields,required,_=FIELDS[op]
 if set(args)-set(fields) or set(required)-set(args):raise TransitError('invalid_arguments','필수 입력 또는 지원하지 않는 입력을 확인해 주세요.')
 return client.call(op,args)
def handle(m,client):
 ident=m.get('id');method=m.get('method');p=m.get('params') or {}
 if ident is None:return None
 if method=='initialize':r={'protocolVersion':'2024-11-05','capabilities':{'tools':{}},'serverInfo':{'name':'nubi-transit','version':'0.1.0'}}
 elif method=='ping':r={}
 elif method=='tools/list':r={'tools':DEFINITIONS}
 elif method=='tools/call':
  try:data=call(p.get('name'),p.get('arguments',{}),client);bad=False
  except TransitError as e:data={'state':e.state,'message':str(e)};bad=True
  except Exception:data={'state':'internal_error','message':'교통 조회를 완료하지 못했어요. 서버 설정을 확인해 주세요.'};bad=True
  r={'isError':bad,'content':[{'type':'text','text':json.dumps(data,ensure_ascii=False)}]}
 else:return {'jsonrpc':'2.0','id':ident,'error':{'code':-32601,'message':'Method not found'}}
 return {'jsonrpc':'2.0','id':ident,'result':r}
if __name__=='__main__':
 client=Transit()
 for line in sys.stdin:
  try:result=handle(json.loads(line),client)
  except Exception:result={'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'Invalid request'}}
  if result is not None:print(json.dumps(result,ensure_ascii=False),flush=True)
