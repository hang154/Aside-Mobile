"""HTTP facade contract with a simulated TAGO provider, no credentials or network."""
import os
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
import nubi_transport_api as api
from nubi_transit import Transit, TransitError

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    key = root / 'tago.key'
    key.write_text('fixture')
    key.chmod(0o600)
    def transport(url, headers, body):
        if 'GetExpBusTrminlList' in url or 'GetSuberbsBusTrminlList' in url:
            from urllib.parse import parse_qs, urlsplit
            name = parse_qs(urlsplit(url).query)['terminalNm'][0]
            rows = [{'terminalNm': name, 'terminalId': 'NAEK010' if name == '서울경부' else 'NAEK700'}]
        elif 'GetStrtpntAlocFndExpbusInfo' in url or 'GetStrtpntAlocFndSuberbsBusInfo' in url:
            rows = [{'depPlandTime': 202611031530, 'arrPlandTime': 202611031930, 'charge': 45000}]
        elif 'GetCtyCodeList' in url:
            rows = [{'citycode': 26, 'cityname': '울산광역시'}, {'citycode': 22, 'cityname': '대구광역시'}]
        elif 'GetCtyAcctoTrainSttnList' in url:
            rows = [{'nodename':'울산', 'nodeid':'NAT01'}] if 'cityCode=26' in url else [{'nodename':'동대구','nodeid':'NAT02'}]
        elif 'GetStrtpntAlocFndTrainInfo' in url:
            rows = [{'depplandtime':20261103153000,'arrplandtime':20261103162000,'traingradename':'KTX','trainno':101}]
        else:
            rows = [{'routeno':'513','arrtime':120}]
        return {'response':{'header':{'resultCode':'00'},'body':{'items':{'item':rows},'totalCount':len(rows)}}}
    api.Transit = lambda: Transit(root, transport)
    c = TestClient(api.app)
    body = {'departure_city':'울산','departure_station':'울산','arrival_city':'대구','arrival_station':'동대구','date':'20261103','after_time':'15:00'}
    first = c.post('/v1/rail/search', json=body)
    assert first.status_code == 200 and first.json()['items'][0]['trainno'] == 101
    assert first.json()['reservation_handoff']['android_package'] == 'com.korail.talk'
    assert first.json()['reservation_handoff']['prefill_verified'] is False
    assert c.post('/v1/rail/search', json=body).json()['cached'] is True
    assert c.post('/v1/rail/search', json=dict(body, date='20260230')).status_code == 400
    assert c.post('/v1/rail/search', json=dict(body, extra='bad')).status_code == 422
    assert c.post('/v1/bus/arrivals', json={'city_code':'26','stop_id':'NAT01'}).json()['items'][0]['arrtime'] == 120
    express = {'departure_terminal':'서울경부','arrival_terminal':'부산','date':'20261103','after_time':'15:00'}
    assert c.post('/v1/bus/express/search', json=express).json()['items'][0]['charge'] == 45000
    assert c.post('/v1/bus/express/search', json=dict(express, after_time='16:00')).json()['state'] == 'no_results'
    assert c.post('/v1/bus/express/search', json=dict(express, date='20260230')).status_code == 400
    assert c.post('/v1/bus/intercity/search', json=express).json()['items'][0]['charge'] == 45000
    assert c.post('/v1/catalog/airports', json={}).status_code == 200
    assert c.post('/v1/catalog/airports', json={'url':'https://example.com'}).status_code == 400
    assert c.post('/v1/catalog/unknown', json={}).status_code == 400
    assert c.post('/v1/catalog/subway_schedule', json={'station_id':'ST1','day_type':'99','direction':'U'}).status_code == 400
    key.unlink()
    failed = c.post('/v1/rail/search', json=body)
    assert failed.status_code == 503 and failed.json()['detail']['state'] == 'registration_required'
    os.environ['TAGO_SERVICE_KEY'] = 'fixture%2Bencoded'
    try:
        assert c.post('/v1/rail/search', json=body).status_code == 200
        os.environ['NUBI_TAGO_KEY_FILE'] = str(key)
        assert c.post('/v1/rail/search', json=body).json()['detail']['state'] == 'registration_required'
    finally:
        os.environ.pop('TAGO_SERVICE_KEY', None)
        os.environ.pop('NUBI_TAGO_KEY_FILE', None)
print('PASS transport HTTP, fixture lookup/cache, validation, bus, handoff and missing-key error')
