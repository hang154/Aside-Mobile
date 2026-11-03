"""Find common team meeting windows from explicitly supplied availability."""
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
DEFINITION={'name':'nubi_team_schedule_propose','description':'Compute real overlapping team availability from user-supplied timezone-aware windows. Does not infer availability, send invitations, or book rooms.','inputSchema':{'type':'object','properties':{'duration_minutes':{'type':'integer','minimum':5,'maximum':480},'participants':{'type':'array','minItems':2,'maxItems':20,'items':{'type':'object','properties':{'name':{'type':'string','minLength':1,'maxLength':80},'windows':{'type':'array','minItems':1,'maxItems':40,'items':{'type':'object','properties':{'start':{'type':'string'},'end':{'type':'string'}},'required':['start','end'],'additionalProperties':False}}},'required':['name','windows'],'additionalProperties':False}}},'required':['duration_minutes','participants'],'additionalProperties':False}}
def propose(duration_minutes,participants):
    if type(duration_minutes) is not int or not 5<=duration_minutes<=480:raise ValueError('회의 길이는 5~480분이어야 합니다')
    if not isinstance(participants,list) or not 2<=len(participants)<=20:raise ValueError('가능 시간을 제공한 팀원이 2~20명 필요합니다')
    names=[];availability=[]
    for participant in participants:
        if not isinstance(participant,dict) or set(participant)!={'name','windows'}:raise ValueError('팀원 형식을 확인하세요')
        name=participant['name']
        if not isinstance(name,str) or not 1<=len(name.strip())<=80 or name.strip() in names:raise ValueError('팀원 이름이 비었거나 중복됩니다')
        names.append(name.strip());windows=participant['windows']
        if not isinstance(windows,list) or not 1<=len(windows)<=40:raise ValueError('팀원별 가능 시간을 입력하세요')
        parsed=[]
        for window in windows:
            if not isinstance(window,dict) or set(window)!={'start','end'}:raise ValueError('시간 구간 형식 오류')
            try:start=datetime.fromisoformat(window['start']);end=datetime.fromisoformat(window['end'])
            except (ValueError,TypeError):raise ValueError('ISO 날짜와 시간대를 입력하세요') from None
            if start.tzinfo is None or end.tzinfo is None:raise ValueError('시간대가 필요합니다')
            start=start.astimezone(timezone.utc);end=end.astimezone(timezone.utc)
            if not start<end or end-start>timedelta(days=31):raise ValueError('가능 시간의 시작·종료를 확인하세요')
            parsed.append((start,end))
        merged=[]
        for start,end in sorted(parsed):
            if merged and start<=merged[-1][1]:merged[-1]=(merged[-1][0],max(end,merged[-1][1]))
            else:merged.append((start,end))
        availability.append(merged)
    overlap=availability[0]
    for windows in availability[1:]:
        common=[];i=j=0
        while i<len(overlap) and j<len(windows):
            start=max(overlap[i][0],windows[j][0]);end=min(overlap[i][1],windows[j][1])
            if start<end:common.append((start,end))
            if overlap[i][1]<windows[j][1]:i+=1
            else:j+=1
        overlap=common
    duration=timedelta(minutes=duration_minutes);kst=ZoneInfo('Asia/Seoul')
    candidates=[{'start':start.astimezone(kst).isoformat(),'end':(start+duration).astimezone(kst).isoformat(),'available_until':end.astimezone(kst).isoformat()} for start,end in overlap if end-start>=duration]
    return {'state':'proposed' if candidates else 'no_common_window','participants':names,'duration_minutes':duration_minutes,'candidates':candidates[:20],'total_windows':len(candidates),'invitations_sent':False,'availability_source':'user_supplied_only'}
