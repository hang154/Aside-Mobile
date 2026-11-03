"""Server-side UNIST 513 planned connections joined with official train API."""
import re
from html.parser import HTMLParser
from urllib.request import Request,build_opener,HTTPRedirectHandler
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from rail_journey import query

DEFINITION={'name':'nubi_transit_unist_homebound','description':'Primary server lookup for UNIST class-end to bus513 toward Ulsan station and official trains to Dongdaegu. Joins HeXA published planned bus ETAs with official train API. No live delay or booking. Holidays need explicit day_type.','inputSchema':{'type':'object','properties':{'date':{'type':'string','description':'YYYYMMDD or YYYY-MM-DD'},'class_end':{'type':'string','description':'HH:mm'},'walk_minutes':{'type':'integer','minimum':1,'maximum':60},'walk_buffer_minutes':{'type':'integer','minimum':0,'maximum':30},'boarding_minutes':{'type':'integer','minimum':1,'maximum':30},'day_type':{'type':'string','enum':['weekday','saturday','sunday_holiday']}},'required':['date','class_end'],'additionalProperties':False}}

class Rows(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None
 def handle_starttag(self,tag,attrs):
  if tag=='tr':self.row=[]
  elif tag in ('th','td') and self.row is not None:self.cell=''
 def handle_data(self,data):
  if self.cell is not None:self.cell+=data
 def handle_endtag(self,tag):
  if tag in ('th','td') and self.cell is not None:
   self.row.append(' '.join(self.cell.split()));self.cell=None
  elif tag=='tr' and self.row is not None:self.rows.append(self.row);self.row=None

def parse_bus(html):
 parser=Rows();parser.feed(html);pending=None;pairs=set()
 for row in parser.rows:
  if not row:continue
  label=re.sub(r'\s','',row[0])
  if label=='UNIST(경유)탑승':pending=row[1:]
  elif label=='울산역정류장착' and pending is not None:
   if len(pending)!=len(row)-1:raise ValueError('Bus timetable columns differ')
   for dep,arr in zip(pending,row[1:]):
    if dep in ('—','–','-','') or arr in ('—','–','-',''):continue
    if not re.fullmatch(r'\d{2}:\d{2}',dep) or not re.fullmatch(r'\d{2}:\d{2}',arr):raise ValueError('Unexpected bus time')
    datetime.strptime(dep,'%H:%M');datetime.strptime(arr,'%H:%M')
    if arr<dep:raise ValueError('Bus day rollover needs explicit support')
    pairs.add((dep,arr))
   pending=None
 if not pairs:raise ValueError('UNIST toward Ulsan station timetable missing')
 return sorted(pairs)

def fetch(url):
 class NoRedirect(HTTPRedirectHandler):
  def redirect_request(self,*a,**kw):return None
 with build_opener(NoRedirect()).open(Request(url,headers={'User-Agent':'Nubi/0.6.22','Accept':'text/html'}),timeout=15) as response:
  data=response.read(1000001)
  if len(data)>1000000:raise ValueError('Bus timetable too large')
  return data.decode('utf-8')

def plan(client,date,class_end,walk_minutes=5,walk_buffer_minutes=3,boarding_minutes=5,day_type=None,fetcher=None):
 date=date.replace('-','');day=datetime.strptime(date,'%Y%m%d');end=datetime.strptime(class_end,'%H:%M')
 for number,low,high in [(walk_minutes,1,60),(walk_buffer_minutes,0,30),(boarding_minutes,1,30)]:
  if type(number) is not int or not low<=number<=high:raise ValueError('Invalid connection interval')
 day_type=day_type or ('weekday' if day.weekday()<5 else 'saturday' if day.weekday()==5 else 'sunday_holiday')
 if day_type not in ('weekday','saturday','sunday_holiday'):raise ValueError('Invalid day type')
 url='https://bus.hexa.pro/ktx?dir=out&to=seoul&day='+str({'weekday':0,'saturday':1,'sunday_holiday':2}[day_type])+'&ts=5&tj=3'
 pairs=parse_bus((fetcher or fetch)(url));zone=ZoneInfo('Asia/Seoul')
 def at(clock):return datetime.combine(day.date(),datetime.strptime(clock,'%H:%M').time(),zone)
 earliest=at(end.strftime('%H:%M'))+timedelta(minutes=walk_minutes+walk_buffer_minutes)
 rail=query(client,'울산','울산','대구','동대구',date,class_end)
 options=[]
 for dep,arr in pairs:
  if at(dep)<earliest:continue
  ready=at(arr)+timedelta(minutes=boarding_minutes)
  trains=[r for r in rail['items'] if str(r.get('traingradename','')).startswith('KTX') and datetime.strptime(str(r['depplandtime']),'%Y%m%d%H%M%S').replace(tzinfo=zone)>=ready]
  if not trains:continue
  options.append({'leave_class_at':(at(dep)-timedelta(minutes=walk_minutes+walk_buffer_minutes)).isoformat(),'bus_departure':at(dep).isoformat(),'station_arrival_estimate':at(arr).isoformat(),'ready_at':ready.isoformat(),'train':trains[0],'boarding_margin_minutes':int((datetime.strptime(str(trains[0]['depplandtime']),'%Y%m%d%H%M%S').replace(tzinfo=zone)-ready).total_seconds()/60)})
  if len(options)==3:break
 return {'state':'results' if options else 'no_results','date':date,'day_type':day_type,'class_end':class_end,'route':'513','direction':'UNIST → 울산역','options':options,'bus_source':url,'train_source':rail['source_url'],'fetched_at':datetime.now(zone).isoformat(),'bus_data_kind':'published_planned_estimate','rail_data_kind':'official_planned_timetable','transactions_executed':False}

def format_plan(data):
 if not data['options']:return '해당 수업 종료 뒤에 연결되는 513번·KTX 조합이 없어. 출발 조건을 바꿔서 찾아볼까?'
 row=data['options'][0];clock=lambda s:datetime.fromisoformat(s).strftime('%H:%M');train=row['train'];dep=str(train['depplandtime']);arr=str(train['arrplandtime'])
 return '\n'.join(['수업 뒤 울산 → 동대구 이동 계획','교실에서 '+clock(row['leave_class_at'])+'에 나오면 돼.','513번 UNIST '+clock(row['bus_departure'])+' 탑승 → 울산역 '+clock(row['station_arrival_estimate'])+' 도착 예상',train['traingradename']+' '+str(train['trainno'])+' · '+dep[8:10]+':'+dep[10:12]+' 출발 → 동대구 '+arr[8:10]+':'+arr[10:12]+' 도착','승차 준비를 마친 뒤 여유 '+str(row['boarding_margin_minutes'])+'분','시간표 기준 이동 계획 · 버스 '+data['bus_source'],'열차 '+data['train_source']])
