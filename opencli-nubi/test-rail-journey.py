"""Rail resolution, pagination, date safety and provider failure contract fixtures."""
from rail_journey import query
from nubi_transit import TransitError
class Client:
 def __init__(self):self.calls=[];self.bad=False
 def call(self,op,a):
  self.calls.append((op,a))
  if op=='train_cities':return {'items':[{'citycode':26,'cityname':'울산광역시'},{'citycode':22,'cityname':'대구광역시'}]}
  if op=='train_stations':return {'items':[{'nodeid':'OBSERVED'+a['city_code'],'nodename':'울산' if a['city_code']=='26' else '동대구'}],'total_count':1}
  page=a['page'];return {'items':[{'depplandtime':('20261104' if self.bad else '20261103')+('153000' if page==1 else '163200'),'trainno':page,'traingradename':'KTX'}],'total_count':21,'fetched_at':'2026-11-03T10:00:00+09:00','cached':False,'source_url':'https://www.data.go.kr/data/15098552/openapi.do'}
a={'departure_city':'울산','departure_station':'울산','arrival_city':'대구','arrival_station':'동대구','date':'20261103','after_time':'15:40'}
c=Client();r=query(c,**a);assert len(r['items'])==1 and r['items'][0]['trainno']==2
class Repeated(Client):
 def call(self,op,args):
  result=super().call(op,args)
  if op=='train_timetable':result['items']*=3
  return result
assert len(query(Repeated(),**a)['items'])==1
assert query(Client(),**dict(a,date='2026-11-03',departure_station='울산역',arrival_station='동대구역'))['date']=='20261103'
assert c.calls[-1][1]['departure_id']=='OBSERVED26' and c.calls[-1][1]['arrival_id']=='OBSERVED22'
assert r['reservation_handoff']['auto_booking_supported'] is False and r['reservation_handoff']['prefill_verified'] is False
for change in ({'date':'20260230'},{'after_time':'25:00'},{'departure_city':'부산'}):
 try:query(c,**dict(a,**change))
 except TransitError:pass
 else:raise AssertionError('invalid or ambiguous accepted')
c.bad=True
try:query(c,**a)
except TransitError as e:assert e.state=='provider_error'
else:raise AssertionError('wrong provider date accepted')
class Missing:
 def call(self,*a):raise TransitError('registration_required','not ready')
try:query(Missing(),**a)
except TransitError as e:assert e.state=='registration_required'
else:raise AssertionError('missing key bypassed')
print('PASS rail name resolution, pagination, time filter, date mismatch, invalid inputs, missing key, handoff truthfulness (fixtures)')
