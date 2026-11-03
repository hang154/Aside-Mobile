"""Completion gate for the four-source read-only location bundle."""
import re

def location_bundle_ready(task, trace):
    if re.search(r'KTX|SRT|코레일|513|버스|지하철|항공|선박|숙소|호텔|예약해|결제해', task, re.I):
        return False
    if not all(re.search(p, task, re.I) for p in (r'택시|taxi', r'날씨|기상|weather', r'대기질|미세먼지|air quality', r'관광|tourism')):
        return False
    count=re.search(r'(\d+)\s*곳',task)
    if count and len(trace.get('public_info',{}).get('tourism',{}).get('items',[]))<int(count[1]):return False
    taxi = trace.get('taxi_estimate', {})
    public = trace.get('public_info', {})
    return taxi.get('state') == 'results' and bool(taxi.get('routes')) and all(
        public.get(k, {}).get('state') == 'results' and public[k].get('items')
        for k in ('weather', 'air', 'tourism'))


def verified_taxi_assessment(text, taxi):
    if not isinstance(taxi,dict):return text
    scenario=taxi.get('ulsan_meter_scenarios',{})
    base=scenario.get('base_fare_won')
    claims=re.findall(r'기본요금[^\n.!?]{0,30}?(\d[\d,]*)\s*원',text)
    if base and any(int(x.replace(',',''))!=base for x in claims):
        fare=taxi['routes'][0]['provider_taxi_won']
        return f"울산 중형택시 기본요금은 2km {base:,}원이에요. 이번 경로의 카카오 예상요금은 {fare:,}원이에요."
    return text
