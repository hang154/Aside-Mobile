from pathlib import Path
from unist_bus513 import parse,read,format_result
html='<div class="bus-card"><div class="bus-card-header route-513"><span class="bus-direction">삼남 (울산역) 방면</span></div><div><p class="entry entry-live">입암 4분</p><p class="entry entry-timetable">20:10 출발 예정</p></div></div><div class="bus-card"><div class="route-513"><span class="bus-direction">덕하 (시내) 방면</span></div><p class="entry entry-timetable">20:40 출발 예정</p></div>'
r=read(lambda u:html);assert r['state']=='results' and r['entries']==[{'kind':'live','text':'입암 4분'},{'kind':'timetable','text':'20:10 출발 예정'}] and r['provider_generated_at'] is None
assert '20:10 출발 예정' in format_result(r) and '막차' not in format_result(r) and '입암 4분' in format_result(r)
assert r['note'] not in format_result(r) and r['source'] in format_result(r)
for bad in [html.replace('삼남 (울산역)','삼남'),html+html]:
 try:parse(bad);raise AssertionError('missing or ambiguous card accepted')
 except ValueError:pass
print('PASS correct 513 direction, separate live and schedule entries, ambiguous source rejection')
