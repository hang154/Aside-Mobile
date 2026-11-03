from campus_meal_plan import plan
fixture={'week':{'startDate':'2026-11-02'},'data':[{'cafeteria':'STUDENT','meals':[{'date':'2026-11-03','timeType':'LUNCH','isClosed':False,'menusByType':[{'sections':[{'menus':[{'ko':'보쌈'},{'ko':'두부조림'}]}]}]}]}]}
r=plan('2026-11-03',[{'start':'2026-11-03T11:30:00+09:00','end':'2026-11-03T12:30:00+09:00'}],7,'11:00',True,lambda u:fixture)
assert r['state']=='planned' and r['arrive_at']=='2026-11-03T11:10:00+09:00'
assert r['recommendations'][0]['special_matches']==['보쌈'] and r['protein_grams'] is None and not r['ticket_purchase_executed']
short=plan('2026-11-03',[{'start':'11:30','end':'12:30'}],7,'11:00',True,lambda u:fixture);assert short['arrive_at']=='2026-11-03T11:10:00+09:00'
r=plan('2026-11-03',[{'start':'2026-11-03T10:30:00+09:00','end':'2026-11-03T12:30:00+09:00'}],7,'11:00',False,lambda u:fixture);assert r['state']=='no_prepeak_slot' and r['leave_at'] is None
try:plan('2026-11-03',[],True,'11:00',True,lambda u:fixture);raise AssertionError()
except ValueError:pass
print('PASS actual menu adapter + class-conflict prepeak planning, no-slot, protein proxy and ticket boundary')
