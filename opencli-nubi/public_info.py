"""Public tourism, meteorology and air-quality lookups with source timestamps."""
import json, math, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from nubi_transit import TransitError
from kakao_location import places, pick
KST=ZoneInfo('Asia/Seoul')
S={'type':'string'}
DEFINITIONS=[
 {'name':'nubi_transit_tourism_search','description':'한국관광공사 관광지·축제·숙박·음식점 등 공개 관광정보를 검색한다. 목록은 영업·예약 가능 여부가 아니다.','inputSchema':{'type':'object','properties':{'query':S},'required':['query'],'additionalProperties':False}},
 {'name':'nubi_transit_weather_now','description':'장소명을 확인하고 기상청 초단기 실황을 조회한다. 관측 발표시각을 함께 표시하며 예보와 구분한다.','inputSchema':{'type':'object','properties':{'place':S},'required':['place'],'additionalProperties':False}},
 {'name':'nubi_transit_air_quality','description':'시도별 대기측정소의 최신 대기오염 정보를 조회한다. 측정소 및 실제 관측시각을 표시한다.','inputSchema':{'type':'object','properties':{'province':S},'required':['province'],'additionalProperties':False}},
]
OPS={'regions':'B551011/KorService2/areaCode2','tourism_area':'B551011/KorService2/areaBasedList2','tourism':'B551011/KorService2/searchKeyword2','weather':'1360000/VilageFcstInfoService_2.0/getUltraSrtNcst','air':'B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty'}

def request(client,op,params,ttl=600):
 key=client.key('tago'); now=time.time(); cachekey=json.dumps(['public_info',op,params],sort_keys=True,ensure_ascii=False)
 row=client.db.execute('SELECT t,data FROM cache WHERE k=?',(cachekey,)).fetchone()
 if row and now-row[0]<ttl:return json.loads(row[1]),row[0],True
 day=datetime.now(KST).strftime('%Y-%m-%d');client.db.execute('BEGIN IMMEDIATE');q=client.db.execute('SELECT n FROM quota WHERE day=? AND p=?',(day,'public_info')).fetchone()
 if q and q[0]>=900:client.db.rollback();raise TransitError('local_daily_limit','공공정보 일일 서버 한도에 도달했어요.')
 client.db.execute('INSERT INTO quota VALUES(?,?,1) ON CONFLICT(day,p) DO UPDATE SET n=n+1',(day,'public_info'));client.db.commit()
 url='https://apis.data.go.kr/'+OPS[op]+'?'+urllib.parse.urlencode(dict(params,serviceKey=key))
 data=client.transport(url,{},None)
 try:
  response=data['response'];header=response['header'];code=str(header['resultCode']);body=response['body']
  if code not in ('00','0','0000'):raise TransitError('provider_error','공공정보 공급자 응답 코드 '+code)
  if not isinstance(body,dict):raise ValueError()
 except (KeyError,TypeError,ValueError):raise TransitError('provider_error','공공정보 응답 형식을 확인하지 못했어요.') from None
 client.db.execute('INSERT OR REPLACE INTO cache VALUES(?,?,?)',(cachekey,now,json.dumps(data,ensure_ascii=False)));client.db.commit()
 return data,now,False

def rows(data):
 items=data['response']['body'].get('items',[])
 if isinstance(items,dict):items=items.get('item',[])
 if isinstance(items,dict):return [items]
 return items if isinstance(items,list) else []

def tourism(client,query):
 if not isinstance(query,str) or not 1<=len(query.strip())<=100:raise TransitError('invalid_arguments','관광 검색어를 확인해 주세요.')
 params={'MobileOS':'ETC','MobileApp':'NUBI','pageNo':1,'numOfRows':10,'_type':'json'}
 region=None
 if query.strip() in {'서울','부산','대구','인천','광주','대전','울산','세종','경기','강원','충북','충남','전북','전남','경북','경남','제주'}:
  regions,_,_=request(client,'regions',dict(params,numOfRows=100))
  region=next((x for x in rows(regions) if x.get('name')==query.strip()),None)
 if region:
  data,t,c=request(client,'tourism_area',dict(params,areaCode=region['code'],contentTypeId=12))
 else:
  data,t,c=request(client,'tourism',dict(params,keyword=query.strip()))
 out=[]
 for x in rows(data):
  out.append({k:x.get(k) for k in ('contentid','contenttypeid','title','addr1','addr2','mapx','mapy','tel','modifiedtime','cpyrhtDivCd')})
 return {'state':'results' if out else 'no_results','items':out,'query':query,'fetched_at':datetime.fromtimestamp(t,KST).isoformat(),'cached':c,'source_url':'https://www.data.go.kr/data/15101578/openapi.do','limitations':'관광정보 등록 목록이며 실시간 영업·객실·예약 가능 여부가 아닙니다.'}

def grid(lat,lon):
 if type(lat) not in (int,float) or type(lon) not in (int,float) or not 33<=lat<=39 or not 124<=lon<=132:raise TransitError('invalid_arguments','국내 좌표를 확인해 주세요.')
 rad=math.pi/180; re=6371.00877/5;slat1=30*rad;slat2=60*rad;olon=126*rad;olat=38*rad
 sn=math.log(math.cos(slat1)/math.cos(slat2))/math.log(math.tan(math.pi*.25+slat2*.5)/math.tan(math.pi*.25+slat1*.5))
 sf=math.tan(math.pi*.25+slat1*.5)**sn*math.cos(slat1)/sn
 ro=re*sf/(math.tan(math.pi*.25+olat*.5)**sn)
 ra=re*sf/(math.tan(math.pi*.25+lat*rad*.5)**sn);theta=(lon*rad-olon)*sn
 return math.floor(ra*math.sin(theta)+43+.5),math.floor(ro-ra*math.cos(theta)+136+.5)

def weather(client,place):
 found=places(client,place);selected=pick(found,place)
 if not selected:return {'state':'selection_required','message':'날씨를 확인할 장소를 선택해 주세요.','candidates':found['items']}
 nx,ny=grid(selected['latitude'],selected['longitude']);base=datetime.now(KST)-timedelta(minutes=50)
 data,t,c=request(client,'weather',{'base_date':base.strftime('%Y%m%d'),'base_time':base.strftime('%H00'),'nx':nx,'ny':ny,'pageNo':1,'numOfRows':20,'dataType':'JSON'},ttl=600)
 out=rows(data)
 return {'state':'results' if out else 'no_results','place':selected['name'],'grid':{'nx':nx,'ny':ny},'items':out,'fetched_at':datetime.fromtimestamp(t,KST).isoformat(),'cached':c,'source_url':'https://www.data.go.kr/data/15084084/openapi.do','limitations':'기상청 격자 대표 관측값이며 예보가 아닙니다. 발표 기준시각을 확인하세요.'}

def air(client,province):
 allowed={'서울','부산','대구','인천','광주','대전','울산','경기','강원','충북','충남','전북','전남','경북','경남','제주','세종'}
 if province not in allowed:raise TransitError('invalid_arguments','시도 이름을 확인해 주세요.')
 data,t,c=request(client,'air',{'sidoName':province,'returnType':'json','pageNo':1,'numOfRows':20,'ver':'1.0'},ttl=600)
 out=rows(data)
 return {'state':'results' if out else 'no_results','province':province,'items':out,'fetched_at':datetime.fromtimestamp(t,KST).isoformat(),'cached':c,'source_url':'https://www.data.go.kr/data/15073861/openapi.do','limitations':'측정소별 관측값과 dataTime 기준입니다. 사용자 위치의 직접 측정값이 아닙니다.'}

def format_public(kind,data):
 if data.get('state')=='selection_required':
  return data.get('message','장소를 선택해 주세요.')+'\n'+'\n'.join(x['name']+' · '+x['address'] for x in data.get('candidates',[]))
 if data.get('state')!='results':return '조회 결과가 없어요.'
 items=data['items'];lines=[]
 if kind=='weather':
  values={x.get('category'):x.get('obsrValue') for x in items};first=items[0]
  lines=[f"{data['place']} 기상청 격자 실황 · {first.get('baseDate','')} {first.get('baseTime','')} 기준"]
  for code,label,unit in [('T1H','기온','°C'),('REH','습도','%'),('WSD','풍속','m/s'),('RN1','1시간 강수량','mm')]:
   if values.get(code) is not None:lines.append(f"{label} {values[code]}{unit}")
 elif kind=='air':
  lines=[data['province']+' 측정소별 대기질']
  for x in items:
   lines.append(f"{x.get('stationName','측정소')} · {x.get('dataTime','시각 미제공')} · PM10 {x.get('pm10Value','-')} · PM2.5 {x.get('pm25Value','-')} µg/m³")
 else:
  lines=[data['query']+' 관광정보']+[f"{x.get('title','')} · {x.get('addr1') or '주소 미제공'}" for x in items]
 lines.append(data['limitations']);lines.append(data['source_url'])
 return '\n'.join(lines)
