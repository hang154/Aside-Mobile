from location_completion import location_bundle_ready
from copy import deepcopy
q='택시 경로와 기상 실황, 대기질, 관광지 3곳 조회. 예약이나 결제는 하지 마.'
t={'taxi_estimate':{'state':'results','routes':[{}]},'public_info':{k:{'state':'results','items':[{}, {}, {}]} for k in ('weather','air','tourism')}}
assert location_bundle_ready(q,t)
for k in ('weather','air','tourism'):
 x=deepcopy(t);x['public_info'][k]={'state':'no_results','items':[]};assert not location_bundle_ready(q,x)
assert not location_bundle_ready(q+' KTX 시간표도 조회',t)
assert not location_bundle_ready('택시만 조회',t)
assert not location_bundle_ready(q,{})
x=deepcopy(t);x['public_info']['tourism']['items']=[{}];assert not location_bundle_ready(q,x)
print('PASS complete-source gate, missing/empty sources and mixed-service scope')

from location_completion import verified_taxi_assessment
taxi={'ulsan_meter_scenarios':{'base_fare_won':4500},'routes':[{'provider_taxi_won':10400}]}
assert '4,500원' in verified_taxi_assessment('기본요금은 10,000원입니다.',taxi)
assert verified_taxi_assessment('기본요금은 4,500원입니다.',taxi)=='기본요금은 4,500원입니다.'
assert verified_taxi_assessment('날씨를 확인했어요.',taxi)=='날씨를 확인했어요.'
print('PASS collaborator base-fare label validation')
