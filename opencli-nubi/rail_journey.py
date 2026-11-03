"""Name-based server timetable query. Provider IDs are resolved, never invented."""
import re,json
from datetime import datetime
from nubi_transit import TransitError
DEFINITION={'name':'nubi_transit_rail_journey','description':'Primary server API rail lookup by city and station name. Resolves provider IDs and retrieves all timetable pages (5-minute server cache). Returns freshness and official reservation handoff; no seat inventory or booking. Do not use web search as primary timetable source.','inputSchema':{'type':'object','properties':{k:{'type':'string'} for k in ['departure_city','departure_station','arrival_city','arrival_station','date','after_time']},'required':['departure_city','departure_station','arrival_city','arrival_station','date'],'additionalProperties':False}}
for field,description in {'departure_city':'출발 도시명. 예: 울산','arrival_city':'도착 도시명. 예: 대구','departure_station':'출발역 이름. 예: 울산 또는 울산역','arrival_station':'도착역 이름. 예: 동대구 또는 동대구역','date':'한국 출발 날짜 YYYYMMDD 또는 YYYY-MM-DD','after_time':'출발 시각 하한 HH:mm. 예: 15:40'}.items():DEFINITION['inputSchema']['properties'][field]['description']=description
def query(client,departure_city,departure_station,arrival_city,arrival_station,date,after_time='00:00'):
 for name in (departure_city,departure_station,arrival_city,arrival_station):
  if not isinstance(name,str) or not re.fullmatch(r'[가-힣A-Za-z0-9 ()·.-]{1,50}',name):raise TransitError('invalid_arguments','도시·역명을 확인해 주세요.')
 try:
  if isinstance(date,str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}',date):date=date.replace('-','')
  if not isinstance(date,str) or not re.fullmatch(r'\d{8}',date):raise ValueError()
  datetime.strptime(date,'%Y%m%d')
  if not re.fullmatch(r'\d{2}:\d{2}',after_time):raise ValueError()
  datetime.strptime(after_time,'%H:%M')
 except (ValueError,TypeError):raise TransitError('invalid_arguments','출발일 YYYYMMDD·시각 HH:mm을 확인해 주세요.') from None
 cities=client.call('train_cities',{})
 def norm(x):return re.sub(r'광역시|특별자치시|특별시|도|시|\s','',str(x))
 def station(city,name):
  matches=[r for r in cities['items'] if norm(r.get('cityname',''))==norm(city)]
  if len(matches)!=1:raise TransitError('selection_required','도시명을 정확히 선택해 주세요: '+city)
  code=str(matches[0]['citycode']);found=[]
  for page in range(1,101):
   r=client.call('train_stations',{'city_code':code,'page':page});found.extend(x for x in r['items'] if x.get('nodename')==name or str(x.get('nodename',''))+'역'==name)
   if page*100>=int(r['total_count']):break
  else:raise TransitError('provider_error','역 목록 페이지 상한을 초과했어요.')
  if len(found)!=1:raise TransitError('selection_required','역명을 정확히 선택해 주세요: '+name)
  return found[0]
 dep=station(departure_city,departure_station);arr=station(arrival_city,arrival_station)
 rows=[];responses=[]
 for page in range(1,101):
  r=client.call('train_timetable',{'departure_id':dep['nodeid'],'arrival_id':arr['nodeid'],'date':date,'page':page});responses.append(r)
  for row in r['items']:
   stamp=str(row.get('depplandtime',''))
   if not re.fullmatch(r'\d{12,14}',stamp) or stamp[:8]!=date:raise TransitError('provider_error','요청 날짜와 시간표 날짜가 일치하지 않아요.')
   if stamp[8:12]>=after_time.replace(':',''):rows.append(row)
  if page*20>=int(r['total_count']):break
 else:raise TransitError('provider_error','시간표 페이지 상한을 초과했어요. 결과를 완료로 처리하지 않았어요.')
 # Provider fields distinguish KTX, SRT and conventional trains; do not relabel all as KTX.
 rows=list({json.dumps(row,sort_keys=True,ensure_ascii=False):row for row in rows}.values())
 rows.sort(key=lambda r:str(r['depplandtime']))
 return {'state':'results' if rows else 'no_results','operation':'rail_journey','departure':dep,'arrival':arr,'date':date,'after_time':after_time,'items':rows,'fetched_at':min(r['fetched_at'] for r in responses),'cached':all(r['cached'] for r in responses),'cache_max_age_seconds':300,'source_url':responses[0]['source_url'],'reservation_handoff':{'url':'https://www.korail.com/ticket','mode':'official_reservation_app_or_web','android_package':'com.korail.talk','auto_booking_supported':False,'selection':{'departure_station':departure_station,'arrival_station':arrival_station,'date':date,'after_time':after_time},'prefill_verified':False},'limitations':'공식 공급자 계획 시간표. 5분 이내 재조회 캐시이며 실시간 지연·잔여석·예약 완료 정보는 아님.'}
