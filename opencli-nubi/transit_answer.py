"""Compact factual chat text from a successful rail MCP response."""
from datetime import datetime
def rail_answer(data):
 def clock(stamp):return str(stamp)[8:10]+':'+str(stamp)[10:12]
 date=datetime.strptime(data['date'],'%Y%m%d').strftime('%Y.%m.%d')
 lines=[data['departure']['nodename']+' → '+data['arrival']['nodename']+' · '+date+' 계획 시간표']
 for n,row in enumerate(data['items'][:3],1):
  text=f"{n}. {row.get('traingradename','열차')} {row.get('trainno','')} · {clock(row['depplandtime'])} → {clock(row['arrplandtime'])}"
  if row.get('adultcharge'):text+=' · '+format(int(row['adultcharge']),',')+'원'
  lines.append(text)
 lines.extend(['조회: '+datetime.fromisoformat(data['fetched_at']).strftime('%m.%d %H:%M'),'출처: '+data['source_url']])
 return '\n'.join(lines)
