from datetime import datetime,timezone
from transit_connection import evaluate
now=datetime(2026,11,2,6,30,tzinfo=timezone.utc)
a={'observed_at':'2026-11-02T15:30:00+09:00','station_arrival':'2026-11-02T15:55:00+09:00','trains':[{'id':'A','departure':'2026-11-02T16:00:00+09:00'},{'id':'B','departure':'2026-11-02T16:10:00+09:00'}],'boarding_minutes':5,'uncertainty_minutes':3}
r=evaluate(**a,now=now);assert [x['id'] for x in r['candidates']]==['B'] and [x['id'] for x in r['cannot_reach']]==['A'];assert not r['existing_ticket_cancelled'] and not r['transactions_executed']
assert evaluate(**dict(a,observed_at='2026-11-02T15:27:00+09:00'),now=now)['state']=='stale_observation'
for patch in [{'boarding_minutes':True},{'uncertainty_minutes':-1},{'station_arrival':'2026-11-02T15:55:00'},{'trains':a['trains']*2}]:
 try:evaluate(**dict(a,**patch),now=now);raise AssertionError('invalid input')
 except ValueError:pass
print('PASS connection margins, next eligible train, stale observations, timezone/duplicate validation and no transactions')
