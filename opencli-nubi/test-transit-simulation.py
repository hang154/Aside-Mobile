from transit_simulation import simulate, format_result
base=dict(observed_at='2026-11-03T15:30:00+09:00',station_arrival='2026-11-03T15:50:00+09:00',boarding_minutes=5,uncertainty_minutes=0,existing_train_id='original',trains=[{'id':'earlier','departure':'2026-11-03T15:45:00+09:00'},{'id':'original','departure':'2026-11-03T16:00:00+09:00'},{'id':'next','departure':'2026-11-03T16:30:00+09:00'}])
r=simulate(delay_minutes=15,**base);assert r['selected_virtual_train_id']=='next' and r['virtual_change'] and not r['transactions_executed'] and not r['existing_ticket_cancelled']
assert '16:05:00+09:00' in format_result(r) and '16:10:00+09:00' in format_result(r) and 'next' in format_result(r)
r=simulate(delay_minutes=0,**base);assert r['selected_virtual_train_id']=='original' and not r['virtual_change']
r=simulate(delay_minutes=60,**base);assert r['state']=='no_results' and not r['virtual_confirmation']
try:simulate(delay_minutes=15,**{**base,'existing_train_id':'missing'});raise AssertionError('missing ticket accepted')
except ValueError:pass
try:simulate(delay_minutes=True,**base);raise AssertionError('invalid delay accepted')
except ValueError:pass
print('PASS virtual delayed connection, unchanged ticket, no alternative, validation, no real transaction')
