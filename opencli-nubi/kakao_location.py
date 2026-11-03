"""Kakao place/road lookups and explicitly conditional Ulsan taxi scenarios."""
import json, math, os, re, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from nubi_transit import TransitError

KST=ZoneInfo('Asia/Seoul')
ULSAN_SOURCE='https://www.ulsan.go.kr/u/traffic/contents.ulsan?mId=001003006001000000'
KAKAO_SOURCE='https://developers.kakaomobility.com/guide/navi-api/directions'
S={'type':'string'}
DEFINITIONS=[
 {'name':'nubi_transit_place_search','description':'카카오맵에서 장소명·주소·좌표 후보를 검색한다. 서로 다른 장소는 사용자에게 선택받는다.','inputSchema':{'type':'object','properties':{'query':S},'required':['query'],'additionalProperties':False}},
 {'name':'nubi_transit_taxi_estimate','description':'출발·도착 장소를 카카오맵에서 확인하고 실제 도로 경로와 택시 예상요금을 조회한다. 현재 교통 기준이며 지정하지 않은 미래 시간의 확정 요금이 아니다. 울산 중형 택시 요금 시나리오를 별도로 표시한다.','inputSchema':{'type':'object','properties':{'origin':S,'destination':S},'required':['origin','destination'],'additionalProperties':False}},
]

def key():
 p=Path(os.environ.get('NUBI_KAKAO_KEY_FILE',str(Path.home()/'.local/state/nubi-transit/kakao.key')))
 if not p.is_file():raise TransitError('registration_required','카카오 지도 서버 인증 설정이 필요해요.')
 if p.stat().st_mode&0o077:raise TransitError('configuration_error','카카오 키 파일 권한을 확인해 주세요.')
 value=p.read_text().strip()
 if not re.fullmatch(r'[A-Za-z0-9]{20,100}',value):raise TransitError('configuration_error','카카오 키 형식을 확인해 주세요.')
 return value

def request(client,host,path,params,transport=None):
 secret=key(); day=datetime.now(KST).strftime('%Y-%m-%d')
 # A conservative aggregate local cap also avoids paid overage in normal development.
 client.db.execute('BEGIN IMMEDIATE')
 row=client.db.execute('SELECT n FROM quota WHERE day=? AND p=?',(day,'kakao_maps')).fetchone()
 if row and row[0]>=500:
  client.db.rollback();raise TransitError('local_daily_limit','카카오 지도 일일 서버 한도에 도달했어요.')
 client.db.execute('INSERT INTO quota VALUES(?,?,1) ON CONFLICT(day,p) DO UPDATE SET n=n+1',(day,'kakao_maps'));client.db.commit()
 url='https://'+host+path+'?'+urllib.parse.urlencode(params)
 headers={'Authorization':'KakaoAK '+secret,'Accept':'application/json'}
 if transport:return transport(url,headers)
 class NoRedirect(urllib.request.HTTPRedirectHandler):
  def redirect_request(self,*args,**kwargs):return None
 try:
  with urllib.request.build_opener(NoRedirect()).open(urllib.request.Request(url,headers=headers),timeout=15) as response:
   raw=response.read(2_000_001)
   if len(raw)>2_000_000:raise TransitError('provider_error','지도 응답이 너무 커요.')
   try:return json.loads(raw)
   except ValueError:raise TransitError('provider_error','지도 응답 형식을 확인하지 못했어요.') from None
 except urllib.error.HTTPError as e:
  raise TransitError('authorization_required' if e.code in (401,403) else 'rate_limited' if e.code==429 else 'provider_error','지도 공급자 HTTP 상태 '+str(e.code)) from None
 except (urllib.error.URLError,TimeoutError,OSError):raise TransitError('network_error','지도 공급자에 연결하지 못했어요.') from None

def canonical_place(query):
 norm=re.sub(r'[\s()]','',query).casefold()
 return {'유니스트':'울산과학기술원','unist':'울산과학기술원','유니스트unist':'울산과학기술원','울산과학기술원unist':'울산과학기술원','ktx울산역':'울산역'}.get(norm,query)

def places(client,query,transport=None):
 if not isinstance(query,str) or not 1<=len(query.strip())<=100 or any(ord(ch)<32 for ch in query):raise TransitError('invalid_arguments','장소 검색어를 확인해 주세요.')
 data=request(client,'dapi.kakao.com','/v2/local/search/keyword.json',{'query':canonical_place(query.strip()),'size':5,'page':1},transport)
 if not isinstance(data,dict) or not isinstance(data.get('documents'),list):raise TransitError('provider_error','장소 검색 결과를 확인하지 못했어요.')
 items=[]
 for x in data['documents']:
  try:
   lat=float(x['y']);lon=float(x['x'])
   if not (32<=lat<=40 and 124<=lon<=132):continue
   items.append({'name':str(x['place_name']),'address':str(x.get('address_name','')),'road_address':str(x.get('road_address_name','')),'latitude':lat,'longitude':lon,'category':str(x.get('category_name','')),'place_url':str(x.get('place_url',''))})
  except (ValueError,KeyError,TypeError):continue
 return {'state':'results' if items else 'no_results','query':query,'items':items,'source_url':'https://developers.kakao.com/docs/ko/local/dev-guide','fetched_at':datetime.now(KST).isoformat()}

def pick(result,query):
 norm=lambda s:re.sub(r'[\s()]','',s).casefold()
 target=norm(canonical_place(query)); matches=[x for x in result['items'] if norm(x['name'])==target]
 if len(matches)==1:return matches[0]
 return None

def ulsan_scenarios(distance_m,duration_s,now):
 # No claim that five stationary minutes is a bound or statistically calibrated.
 end=now+timedelta(seconds=duration_s)
 def night(d):return d.hour>=22 or d.hour<4
 if night(now)!=night(end):return {'state':'boundary_crossing','message':'운행 중 심야 할증 시간 경계가 있어 구간별 적용 확인이 필요해요.','source_url':ULSAN_SOURCE}
 base=4500+max(0,math.floor((distance_m-2000)/125))*100
 factor=1.2 if night(now) else 1.0
 return {'state':'conditional_scenarios','base_fare_won':4500,'base_distance_m':2000,'distance_step_m':125,'distance_step_won':100,'slow_time_step_s':30,'slow_time_step_won':100,'distance_only_won':round(base*factor/100)*100,'with_five_minutes_stopped_won':round((base+1000)*factor/100)*100,'assumptions':'울산 중형·시계 내, 전 거리 기준과 정차 0분 또는 추가 5분을 가정한 예시. 저속 주행·할증 경계·호출료·통행료에 따라 달라질 수 있습니다.','night_surcharge_applied':night(now),'source_url':ULSAN_SOURCE}

def taxi(client,origin,destination,transport=None):
 source=places(client,origin,transport);target=places(client,destination,transport)
 a=pick(source,origin);b=pick(target,destination)
 if not a or not b:
  return {'state':'selection_required','origin_query':origin,'destination_query':destination,'origin_candidates':source['items'],'destination_candidates':target['items'],'message':'출발지와 도착지를 정확히 선택해 주세요.'}
 if a['latitude']==b['latitude'] and a['longitude']==b['longitude']:raise TransitError('invalid_arguments','출발지와 도착지가 같아요.')
 params={'origin':f"{a['longitude']},{a['latitude']}",'destination':f"{b['longitude']},{b['latitude']}",'priority':'RECOMMEND','alternatives':'true','summary':'true'}
 data=request(client,'apis-navi.kakaomobility.com','/v1/directions',params,transport)
 if not isinstance(data,dict) or not isinstance(data.get('routes'),list):raise TransitError('provider_error','도로 경로 응답을 확인하지 못했어요.')
 routes=[]
 for row in data['routes']:
  summary=row.get('summary') or {};fare=summary.get('fare') or {};distance=summary.get('distance');duration=summary.get('duration');price=fare.get('taxi');toll=fare.get('toll')
  if row.get('result_code')!=0 or type(distance) not in (int,float) or type(duration) not in (int,float) or distance<=0 or duration<0:continue
  if type(price) not in (int,float) or price<0 or type(toll) not in (int,float) or toll<0:continue
  routes.append({'distance_m':round(distance),'duration_s':round(duration),'provider_taxi_won':round(price),'toll_won':round(toll)})
 if not routes:return {'state':'no_results','origin':a,'destination':b,'source_url':KAKAO_SOURCE}
 now=datetime.now(KST);primary=routes[0]
 result={'state':'results','origin':a,'destination':b,'routes':routes,'fetched_at':now.isoformat(),'source_url':KAKAO_SOURCE,'notice':'현재 길찾기 기준 카카오 예상요금입니다. 예상 통행료는 별도이며, 심야·시계외 할증과 호출료 반영 여부는 공급자에서 별도로 확인해야 합니다.'}
 if a['address'].startswith('울산 ') and b['address'].startswith('울산 '):result['ulsan_meter_scenarios']=ulsan_scenarios(primary['distance_m'],primary['duration_s'],now)
 return result

def format_taxi(data):
 if data.get('state')=='selection_required':
  lines=['출발지와 도착지를 확인해 주세요.']
  for title,key in [('출발지','origin_candidates'),('도착지','destination_candidates')]:
   choices=data.get(key,[])[:3]
   lines.append(title+': '+(' / '.join(x['name']+' ('+x['address']+')' for x in choices) if choices else '검색 결과 없음'))
  return '\n'.join(lines)
 if data.get('state')!='results':return '해당 구간의 도로 경로를 찾지 못했어요.'
 route=data['routes'][0];a=data['origin'];b=data['destination'];now=datetime.fromisoformat(data['fetched_at'])
 lines=[f"{a['name']} → {b['name']} · 현재 도로 경로",f"약 {route['distance_m']/1000:.1f}km · 약 {math.ceil(route['duration_s']/60)}분",f"카카오 예상 택시비 {route['provider_taxi_won']:,}원 · 통행료 {route['toll_won']:,}원 별도"]
 scenario=data.get('ulsan_meter_scenarios',{})
 if scenario.get('state')=='conditional_scenarios':lines.append('울산 중형 기본요금: 2km 4,500원 · 이후 125m당 100원 · 저속 30초당 100원');lines.append(f"울산 중형 요금 예시: 정차 0분 {scenario['distance_only_won']:,}원 / 정차 5분 {scenario['with_five_minutes_stopped_won']:,}원 (시계 내 가정)")
 elif scenario.get('message'):lines.append(scenario['message'])
 lines.extend(['호출료·할증과 실제 정체에 따라 달라질 수 있어요.', '조회 '+now.strftime('%m.%d %H:%M')+' · '+KAKAO_SOURCE])
 return '\n'.join(lines)
