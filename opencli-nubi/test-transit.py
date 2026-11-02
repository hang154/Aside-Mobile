"""Provider contract, quotas, cache, secret redaction and MCP failure tests with HTTP fixtures."""
import importlib.util,json,tempfile,os,sys,sqlite3
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from nubi_transit import Transit,TransitError
spec=importlib.util.spec_from_file_location('mcp',Path(__file__).with_name('nubi-transit-mcp.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
n=0
def check(x):
 global n
 assert x;n+=1
with tempfile.TemporaryDirectory() as root:
 calls=[]
 def http(url,headers,body):
  calls.append((url,headers,body))
  if 'seoul' in url:return {'errorMessage':{'code':'INFO-000'},'realtimeArrivalList':[{'statnNm':'서울','barvlDt':'180','recptnDt':'2026-11-01 21:00:00'}]}
  if 'sk.com' in url:return {'metaData':{'plan':{'itineraries':[{'totalTime':600,'transferCount':0,'legs':[]}]}}}
  return {'response':{'header':{'resultCode':'00'},'body':{'items':{'item':{'nodeid':'NAT0001','nodename':'서울'}},'totalCount':1}}}
 c=Transit(root,http);check(c.status()['providers']['tago']=='registration_required')
 r=m.handle({'id':1,'method':'tools/call','params':{'name':'nubi_transit_train_cities','arguments':{}}},c)['result'];check(r['isError']);check('registration_required' in r['content'][0]['text']);check(not calls)
 for provider in ['tago','seoul','tmap']:
  p=Path(root)/(provider+'.key');p.write_text('private-fixture-secret');p.chmod(0o600)
 r=c.call('bus_arrivals',{'city_code':'26','stop_id':'ULS123'});check(r['state']=='results');check(not r['cached']);check('private-fixture-secret' not in json.dumps(r));check(parse_qs(urlparse(calls[-1][0]).query)['serviceKey']==['private-fixture-secret'])
 before=len(calls);check(c.call('bus_arrivals',{'city_code':'26','stop_id':'ULS123'})['cached']);check(len(calls)==before)
 r=c.call('train_timetable',{'departure_id':'NAT0001','arrival_id':'NAT0002','date':'20261102'});check('/TrainInfo/GetStrtpntAlocFndTrainInfo?' in calls[-1][0]);check(r['items'][0]['nodeid']=='NAT0001');check('잔여좌석' in r['limitations'])
 r=c.call('subway_arrivals',{'station':'서울'});check(r['items'][0]['barvlDt']=='180');check(r['items'][0]['recptnDt']=='2026-11-01 21:00:00')
 for op,args in [('train_timetable',{'departure_id':'NAT1','arrival_id':'NAT2','date':'20260230'}),('bus_arrivals',{'city_code':'26','stop_id':'../secret'}),('routes',{'start_lon':float('nan'),'start_lat':1,'end_lon':1,'end_lat':1}),('bus_stops',{'city_code':'26','name':'UNIST','page':True})]:
  try:c.call(op,args)
  except TransitError as e:check(e.state=='invalid_arguments')
  else:raise AssertionError('invalid accepted')
 r=m.handle({'id':2,'method':'tools/call','params':{'name':'nubi_transit_status','arguments':{'key':'secret'}}},c)['result'];check(r['isError'])
 a={'start_lon':129.0,'start_lat':35.0,'end_lon':129.1,'end_lat':35.1}
 for i in range(10):check(c.call('routes',a)['items'][0]['totalTime']==600)
 check(calls[-1][1]['appKey']=='private-fixture-secret');check(calls[-1][2]['count']==3)
 try:c.call('routes',a)
 except TransitError as e:check(e.state=='local_daily_limit')
 else:raise AssertionError('quota bypass')
 check(c.db.execute("SELECT count(*) FROM cache WHERE k LIKE '%tmap%'").fetchone()[0]==0)
 p=Path(root)/'tago.key';p.chmod(0o644)
 try:c.key('tago')
 except TransitError as e:check(e.state=='configuration_error')
 else:raise AssertionError('world-readable key accepted')
 for provider,payload in [('tago',{'response':{'header':{'resultCode':'30'}}}),('seoul',{'errorMessage':{'code':'INFO-100'}}),('tmap',{'result':{'status':14}})]:
  try:Transit.check(provider,payload)
  except TransitError:check(True)
  else:raise AssertionError('API error accepted')
 check(Transit.rows({'response':{'body':{'items':''}}})==[])
 Path(root,'seoul.key').write_text('sample');c.db.execute('DELETE FROM cache');c.db.commit();check(c.call('subway_arrivals',{'station':'서울'})['state']=='sample_results')
print('PASS',n,'transit adapter/cache/quota/credential/MCP contract checks (HTTP fixtures)')
