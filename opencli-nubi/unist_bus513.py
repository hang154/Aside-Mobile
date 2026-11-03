"""Read the public HeXA UNIST 513 card; no claim of real-time vehicle tracking."""
from datetime import datetime
from html.parser import HTMLParser
from urllib.request import Request,build_opener,HTTPRedirectHandler
from zoneinfo import ZoneInfo

URL='https://bus.hexa.pro/unist?lang=ko'
DEFINITION={'name':'nubi_transit_unist_513','description':'Read the public UNIST bus page for route 513 toward Samnam/Ulsan station. Returns displayed upcoming departures and provider-displayed live entries, with retrieval time. These are not an independently verified GPS or station arrival time.','inputSchema':{'type':'object','properties':{},'additionalProperties':False}}

class BusCards(HTMLParser):
 def __init__(self):
  super().__init__();self.depth=0;self.card=None;self.cards=[];self.capture=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs);classes=a.get('class','').split()
  if self.card is None and tag=='div' and 'bus-card' in classes:self.card={'routes':[],'direction':[],'entries':[]};self.depth=1;return
  if self.card is None:return
  if tag=='div':self.depth+=1
  if 'route-513' in classes:self.card['routes'].append('513')
  if 'bus-direction' in classes:self.capture=('direction',None)
  elif 'entry' in classes:self.capture=('entries','live' if 'entry-live' in classes else 'timetable' if 'entry-timetable' in classes else 'other')
 def handle_data(self,data):
  if self.card is not None and self.capture and data.strip():
   key,kind=self.capture
   if key=='entries':self.card[key].append({'kind':kind,'text':data.strip()})
   else:self.card[key].append(data.strip())
 def handle_endtag(self,tag):
  if self.card is None:return
  if tag in ('p','span'):self.capture=None
  if tag=='div':
   self.depth-=1
   if self.depth==0:self.cards.append(self.card);self.card=None

def parse(html):
 parser=BusCards();parser.feed(html)
 matches=[x for x in parser.cards if '513' in x['routes'] and '삼남' in ' '.join(x['direction']) and '울산역' in ' '.join(x['direction'])]
 if len(matches)!=1:raise ValueError('울산역 방면 513번 카드가 없거나 중복되어 확인할 수 없어요')
 return matches[0]

def read(fetch=None):
 if fetch is None:
  class NoRedirect(HTTPRedirectHandler):
   def redirect_request(self,*args,**kwargs):return None
  def fetch(url):
   with build_opener(NoRedirect()).open(Request(url,headers={'User-Agent':'Nubi/0.6.22','Accept':'text/html'}),timeout=15) as r:
    content=r.read(1048577)
    if len(content)>1048576:raise ValueError('버스 응답 크기 초과')
    return content.decode('utf-8')
 card=parse(fetch(URL));return {'state':'results' if card['entries'] else 'no_results','route':'513','direction':'삼남 (울산역) 방면','entries':card['entries'],'source':URL,'fetched_at':datetime.now(ZoneInfo('Asia/Seoul')).isoformat(),'provider_generated_at':None,'note':'제공 페이지에 표시된 정보입니다. 조회 시각은 버스 위치 생성 시각이 아니며 울산역 도착 예측이나 예약 결과가 아닙니다.'}

def format_result(data):
 lines=['UNIST 513번 · 삼남(울산역) 방면']
 for entry in data['entries']:
  label={'live':'도착 안내','timetable':'출발 안내'}.get(entry['kind'],'운행 안내')
  lines.append(label+': '+entry['text'])
 if not data['entries']:lines.append('현재 페이지에 표시된 항목이 없습니다.')
 lines.extend(['조회 시각: '+data['fetched_at'],'출처: '+data['source']])
 return '\n'.join(lines)
