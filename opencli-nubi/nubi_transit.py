"""Server-side public transport adapters. Never embed service keys in an APK or MCP result."""
import json,os,re,sqlite3,time,urllib.request,urllib.error
from pathlib import Path
from datetime import datetime
from urllib.parse import urlencode,quote,unquote
from zoneinfo import ZoneInfo
SOURCES={'tago':'https://www.data.go.kr/data/15098530/openapi.do','train':'https://www.data.go.kr/data/15098552/openapi.do','seoul':'https://data.seoul.go.kr/dataList/OA-12764/F/1/datasetView.do','tmap':'https://transit.tmapmobility.com/docs/routes','stops':'https://www.data.go.kr/data/15098534/openapi.do','position':'https://www.data.go.kr/data/15098533/openapi.do'}
class TransitError(Exception):
 def __init__(self,state,message):self.state=state;super().__init__(message)
def text(v,pattern,label):
 if not isinstance(v,str) or not re.fullmatch(pattern,v):raise TransitError('invalid_arguments',label+' 값을 확인해 주세요.')
 return v
def integer(v,low,high,label):
 if type(v)!=int or not low<=v<=high:raise TransitError('invalid_arguments',label+' 범위를 확인해 주세요.')
 return v
class Transit:
 def __init__(self,root=None,transport=None):
  self.root=Path(root or os.environ.get('NUBI_TRANSIT_STATE',Path.home()/'.local/state/nubi-transit'));self.root.mkdir(parents=True,exist_ok=True,mode=0o700);self.transport=transport or self.http
  self.db=sqlite3.connect(self.root/'cache.sqlite3',timeout=15);os.chmod(self.root/'cache.sqlite3',0o600)
  self.db.executescript('CREATE TABLE IF NOT EXISTS cache(k TEXT PRIMARY KEY,t REAL,data TEXT);CREATE TABLE IF NOT EXISTS quota(day TEXT,p TEXT,n INTEGER,PRIMARY KEY(day,p));');self.db.commit()
 def key(self,provider):
  name={'tago':'TAGO','seoul':'SEOUL_SUBWAY','tmap':'TMAP'}[provider];p=Path(os.environ.get('NUBI_'+name+'_KEY_FILE',self.root/(provider+'.key')))
  value=os.environ.get('TAGO_SERVICE_KEY') if provider=='tago' and not os.environ.get('NUBI_TAGO_KEY_FILE') else None
  if value is None:
   if not p.is_file():raise TransitError('registration_required',provider+' 가입·활용신청 및 서버 인증키 설정이 필요해요.')
   if p.stat().st_mode&0o077:raise TransitError('configuration_error','인증키 파일 권한을 600으로 설정해 주세요.')
   value=p.read_text().strip()
  if not value or len(value)>1000 or any(x in value for x in '\r\n'):raise TransitError('configuration_error','인증키 파일 형식을 확인해 주세요.')
  return unquote(value) if provider=='tago' else value
 def status(self):
  out={}
  for p in ['tago','seoul','tmap']:
   try:self.key(p);out[p]='key_configured_not_yet_verified'
   except TransitError as e:out[p]=e.state
  return {'state':'configuration','providers':out,'source_urls':SOURCES,'limits':'KTX 시간표만 제공. 좌석·지연·예매·결제 지원 안 함. TMAP 경로 자동 재조회 없음.'}
 @staticmethod
 def http(url,headers,body):
  # Redirects could disclose a key in the query/path or appKey header: refuse them.
  class NoRedirect(urllib.request.HTTPRedirectHandler):
   def redirect_request(self,*a,**kw):return None
  req=urllib.request.Request(url,headers=headers,data=None if body is None else json.dumps(body).encode())
  try:
   with urllib.request.build_opener(NoRedirect()).open(req,timeout=15) as r:
    data=r.read(2_000_001)
    if len(data)>2_000_000:raise TransitError('provider_error','응답 크기를 초과했어요.')
    try:return json.loads(data)
    except ValueError:raise TransitError('provider_error','API JSON 응답을 확인하지 못했어요. 인증·활용승인을 확인해 주세요.')
  except urllib.error.HTTPError as e:raise TransitError('authorization_required' if e.code in (401,403) else 'rate_limited' if e.code==429 else 'provider_error','공급자 HTTP 상태 '+str(e.code))
  except (urllib.error.URLError,TimeoutError,OSError):raise TransitError('network_error','공급자 연결을 확인하지 못했어요. 자동 재시도하지 않았어요.')
 def request(self,provider,path,params,ttl,body=None):
  key=self.key(provider);cachekey=json.dumps([provider,path,params,body],sort_keys=True,ensure_ascii=False);now=time.time()
  if ttl:
   row=self.db.execute('SELECT t,data FROM cache WHERE k=?',(cachekey,)).fetchone()
   if row and now-row[0]<ttl:return json.loads(row[1]),row[0],True
  day=datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d');limit=10 if provider=='tmap' else 9000
  self.db.execute('BEGIN IMMEDIATE');n=self.db.execute('SELECT n FROM quota WHERE day=? AND p=?',(day,provider)).fetchone()
  if n and n[0]>=limit:self.db.rollback();raise TransitError('local_daily_limit','서버에 설정한 일일 호출 상한에 도달했어요.')
  self.db.execute('INSERT INTO quota VALUES(?,?,1) ON CONFLICT(day,p) DO UPDATE SET n=n+1',(day,provider));self.db.commit()
  if provider=='tago':
   if path in ('B551457/run/v2/codes2','B551457/run/v2/travelerTrainRunPlan2','B551457/run/v2/travelerTrainRunInfo2'):
    url='https://apis.data.go.kr/'+path+'?'+urlencode(dict(params,serviceKey=key,returnType='json'))
   else:url='https://apis.data.go.kr/1613000/'+path+'?'+urlencode(dict(params,serviceKey=key,_type='json'))
   headers={}
  elif provider=='seoul':url='http://swopenapi.seoul.go.kr/api/subway/'+quote(key,safe='')+'/json/realtimeStationArrival/0/5/'+quote(params['station'],safe='');headers={}
  else:url='https://apis.openapi.sk.com/transit/routes';headers={'appKey':key,'Content-Type':'application/json','Accept':'application/json'}
  result=self.transport(url,headers,body)
  # Validate before caching: error responses must never be reused as data.
  self.check(provider,result)
  if ttl:
   self.db.execute('DELETE FROM cache WHERE t<?',(now-86400,));self.db.execute('INSERT OR REPLACE INTO cache VALUES(?,?,?)',(cachekey,now,json.dumps(result,ensure_ascii=False)));self.db.commit()
  return result,now,False
 @staticmethod
 def check(provider,data):
  if not isinstance(data,dict):raise TransitError('provider_error','예상한 응답 구조가 아니에요.')
  if provider=='tago':
   response=data.get('response',data);header=response.get('header',{});code=str(header.get('resultCode',''))
   if code not in ('00','0'):raise TransitError('authorization_required' if code in ('20','21','22','30','31','32') else 'provider_error','TAGO 응답 코드 '+code)
   if not isinstance(response.get('body'),dict):raise TransitError('provider_error','TAGO 본문을 확인하지 못했어요.')
  elif provider=='seoul':
   code=str(data.get('errorMessage',data.get('RESULT',{})).get('code',data.get('RESULT',{}).get('CODE','')))
   if code not in ('INFO-000','INFO-200'):raise TransitError('authorization_required' if code=='INFO-100' else 'provider_error','서울 지하철 응답 코드 '+code)
  elif data.get('result',{}).get('status') not in (None,0,'0') or 'metaData' not in data:raise TransitError('provider_error','TMAP 경로 결과를 확인하지 못했어요.')
 @staticmethod
 def rows(data):
  body=data.get('response',data)['body'];items=body.get('items')
  if not items:return []
  items=items.get('item',[]) if isinstance(items,dict) else items
  return [items] if isinstance(items,dict) else items if isinstance(items,list) else []
 def call(self,operation,a):
  if not isinstance(a,dict):raise TransitError('invalid_arguments','입력 형식을 확인해 주세요.')
  if operation=='status':return self.status()
  specs={
   'bus_cities':('tago','ArvlInfoInqireService/getCtyCodeList',{},86400,'tago'),
   'bus_arrivals':('tago','ArvlInfoInqireService/getSttnAcctoArvlPrearngeInfoList',{'cityCode':a.get('city_code'),'nodeId':a.get('stop_id'),'pageNo':a.get('page',1),'numOfRows':20},20,'tago'),
   'bus_stops':('tago','BusSttnInfoInqireService/getSttnNoList',{'cityCode':a.get('city_code'),'nodeNm':a.get('name'),'pageNo':a.get('page',1),'numOfRows':20},300,'stops'),
   'bus_positions':('tago','BusLcInfoInqireService/getRouteAcctoBusLcList',{'cityCode':a.get('city_code'),'routeId':a.get('route_id'),'pageNo':a.get('page',1),'numOfRows':20},30,'position'),
   'train_cities':('tago','TrainInfo/GetCtyCodeList',{},86400,'train'),
   'train_types':('tago','TrainInfo/GetVhcleKndList',{},86400,'train'),
   'train_stations':('tago','TrainInfo/GetCtyAcctoTrainSttnList',{'cityCode':a.get('city_code'),'pageNo':a.get('page',1),'numOfRows':100},86400,'train'),
   'train_timetable':('tago','TrainInfo/GetStrtpntAlocFndTrainInfo',{'depPlaceId':a.get('departure_id'),'arrPlaceId':a.get('arrival_id'),'depPlandTime':a.get('date'),'pageNo':a.get('page',1),'numOfRows':20},300,'train'),
   'subway_arrivals':('seoul','',{'station':a.get('station')},30,'seoul'),
   'routes':('tmap','',{},0,'tmap')}
  if operation not in specs:raise TransitError('invalid_arguments','지원하지 않는 교통 도구예요.')
  p,path,params,ttl,source=specs[operation];body=None
  for k,v in params.items():
   if k=='pageNo':integer(v,1,100,'페이지')
   elif k=='cityCode':text(v,r'[0-9]{1,5}','도시코드')
   elif k in ('nodeId','routeId','depPlaceId','arrPlaceId'):text(v,r'[A-Za-z0-9_]{2,40}',k)
   elif k in ('nodeNm','station'):text(v,r'[가-힣A-Za-z0-9 ()·.-]{1,50}',k)
   elif k=='depPlandTime':
    text(v,r'[0-9]{8}','출발일')
    try:datetime.strptime(v,'%Y%m%d')
    except ValueError:raise TransitError('invalid_arguments','유효한 출발일이 아니에요.')
  if operation=='train_timetable' and a.get('train_type'):
   params['trainGradeCode']=text(a['train_type'],r'[0-9]{1,3}','열차종류')
  if operation=='routes':
   body={'format':'json','lang':0,'count':3}
   for k,lo,hi,out in [('start_lon',-180,180,'startX'),('start_lat',-90,90,'startY'),('end_lon',-180,180,'endX'),('end_lat',-90,90,'endY')]:
    v=a.get(k)
    if type(v) not in (float,int) or not lo<=v<=hi:raise TransitError('invalid_arguments',k+' 좌표를 확인해 주세요.')
    body[out]=str(v)
  data,observed,cached=self.request(p,path,params,ttl,body)
  if p=='tago':rows=self.rows(data);total=data.get('response',data)['body'].get('totalCount',len(rows))
  elif p=='seoul':rows=data.get('realtimeArrivalList',[]);total=len(rows)
  else:
   plans=data.get('metaData',{}).get('plan',{}).get('itineraries',[])
   rows=[{k:r[k] for k in ('totalTime','transferCount','totalWalkTime','totalDistance','fare','legs') if k in r} for r in plans];total=len(rows)
  return {'state':('sample_results' if p=='seoul' and self.key(p)=='sample' else 'results') if rows else 'no_results','sample':p=='seoul' and self.key(p)=='sample','operation':operation,'items':rows,'total_count':total,'page':a.get('page',1),'fetched_at':datetime.fromtimestamp(observed,ZoneInfo('Asia/Seoul')).isoformat(),'cached':cached,'source_url':SOURCES[source],'limitations':'KTX 시간표는 잔여좌석·실시간 지연·예약이 아닙니다.' if source=='train' else '제공 지역·운행 상태에 따라 누락될 수 있어요. 도착 초는 공급자 예측값이에요.' if p!='tmap' else '경로 결과는 이번 응답용이며 서버에 캐시하지 않아요. 유료 가입 없이 자동 재시도하지 않아요.'}
