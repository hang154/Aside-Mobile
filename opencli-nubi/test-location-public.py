"""Location resolution, fare scenarios and public API cache contracts."""
import os,tempfile,json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlparse,parse_qs
from nubi_transit import Transit,TransitError
from kakao_location import taxi,ulsan_scenarios
from public_info import tourism,air,grid

with tempfile.TemporaryDirectory() as root:
 p=Path(root);(p/'tago.key').write_text('fixture-tago');(p/'tago.key').chmod(0o600)
 (p/'kakao.key').write_text('fixturekakaosecret123456789');(p/'kakao.key').chmod(0o600)
 os.environ['NUBI_KAKAO_KEY_FILE']=str(p/'kakao.key');calls=[]
 def http(url,headers,body=None):
  calls.append(url);query=parse_qs(urlparse(url).query)
  if 'areaCode2' in url:return {'response':{'header':{'resultCode':'00'},'body':{'items':{'item':[{'name':'울산','code':'7'}]}}}}
  if 'areaBasedList2' in url:assert query['areaCode']==['7'] and query['contentTypeId']==['12']
  if 'keyword.json' in url:
   name=query['query'][0]
   doc={'place_name':name,'address_name':'울산 울주군','x':'129.18' if name=='울산과학기술원' else '129.13','y':'35.57','category_name':'시설'}
   return {'documents':[doc]}
  if 'directions' in url:return {'routes':[{'result_code':0,'summary':{'distance':9000,'duration':780,'fare':{'taxi':10400,'toll':0}}}]}
  return {'response':{'header':{'resultCode':'00'},'body':{'items':{'item':[{'title':'관광지','stationName':'측정소','dataTime':'2026-11-03 10:00'}]}}}}
 c=Transit(root,http)
 r=taxi(c,'유니스트(UNIST)','울산역',http)
 assert r['state']=='results' and r['origin']['name']=='울산과학기술원' and r['routes'][0]['provider_taxi_won']==10400
 assert 'fixturekakaosecret123456789' not in json.dumps(r,ensure_ascii=False)
 assert parse_qs(urlparse(calls[0]).query)['query']==['울산과학기술원']
 scenario=ulsan_scenarios(9000,780,datetime(2026,11,3,12,tzinfo=ZoneInfo('Asia/Seoul')))
 assert scenario['distance_only_won']==10100 and scenario['with_five_minutes_stopped_won']==11100
 assert ulsan_scenarios(9000,780,datetime(2026,11,3,21,59,tzinfo=ZoneInfo('Asia/Seoul')))['state']=='boundary_crossing'
 first=tourism(c,'울산');n=len(calls);second=tourism(c,'울산')
 assert first['items'][0]['title']=='관광지' and second['cached'] and len(calls)==n
 assert air(c,'울산')['items'][0]['dataTime']=='2026-11-03 10:00'
 try:air(c,'invalid')
 except TransitError as exc:assert exc.state=='invalid_arguments'
 else:raise AssertionError('invalid province accepted')
 assert grid(37.5665,126.978)==(60,127)
print('PASS location alias, route, fare boundaries, public data, caching and input checks')
