"""Durable, device-isolated sandbox tickets. No booking provider is called."""
import hashlib,json,os,re,sqlite3,uuid
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from rail_journey import query
from transit_simulation import simulate

DEFINITION={'name':'nubi_transit_virtual_ticket','description':'Explicit simulation only. Create a sandbox ticket from real server timetable, read its durable receipt, or atomically change it after a simulated bus delay. Never books or cancels real tickets. Use one scenario_id throughout a scenario.','inputSchema':{'type':'object','properties':{'action':{'type':'string','enum':['create','read','change']},'scenario_id':{'type':'string','pattern':'^[a-zA-Z0-9_-]{1,60}$'},'date':{'type':'string','description':'YYYYMMDD; required for create'},'train_number':{'type':'string','description':'Exact train number from actual timetable, required for create'},'expected_revision':{'type':'integer','minimum':0},'observed_at':{'type':'string','description':'Simulated observation ISO time with timezone'},'station_arrival':{'type':'string','description':'Original simulated station ETA with timezone'},'delay_minutes':{'type':'integer','minimum':0,'maximum':240},'boarding_minutes':{'type':'integer','minimum':1,'maximum':120},'uncertainty_minutes':{'type':'integer','minimum':0,'maximum':120}},'required':['action','scenario_id'],'additionalProperties':False}}

class Sandbox:
 def __init__(self,root,session,client):
  if not re.fullmatch(r'[a-f0-9-]{36}',session):raise ValueError('Device session required')
  self.owner=hashlib.sha256(session.encode()).hexdigest();self.client=client
  root=Path(root);root.mkdir(parents=True,exist_ok=True,mode=0o700)
  self.db=sqlite3.connect(root/'virtual-tickets.sqlite3',timeout=15)
  os.chmod(root/'virtual-tickets.sqlite3',0o600)
  self.db.execute('CREATE TABLE IF NOT EXISTS tickets(owner TEXT, scenario TEXT, data TEXT, PRIMARY KEY(owner,scenario))');self.db.commit()
 def call(self,action,scenario_id,**args):
  if not re.fullmatch(r'[a-zA-Z0-9_-]{1,60}',scenario_id):raise ValueError('Invalid scenario ID')
  if action not in ('create','read','change'):raise ValueError('Invalid sandbox action')
  if action=='create':
   if set(args)!={'date','train_number'}:raise ValueError('Create needs date and train_number')
   rail=query(self.client,'울산','울산','대구','동대구',args['date'])
   choices=[r for r in rail['items'] if str(r.get('trainno',''))==args['train_number']]
   if len(choices)!=1:raise ValueError('Choose one observed train number')
   selected=choices[0]
  self.db.execute('BEGIN IMMEDIATE')
  try:
   row=self.db.execute('SELECT data FROM tickets WHERE owner=? AND scenario=?',(self.owner,scenario_id)).fetchone()
   ticket=json.loads(row[0]) if row else None
   if action=='create':
    if ticket:
     if ticket['date']!=rail['date'] or ticket['original_train']['trainno']!=selected['trainno']:raise ValueError('Scenario already has a different ticket')
     self.db.rollback();return ticket
    ticket={'state':'results','simulation':True,'scenario_id':scenario_id,'date':rail['date'],'revision':0,'original_train':selected,'current_train':selected,'timetable':rail['items'],'events':[],'transactions_executed':False}
    ticket['events'].append({'receipt_id':'SIM-'+uuid.uuid4().hex[:12],'type':'created','revision':0,'train':selected,'at':datetime.now(ZoneInfo('Asia/Seoul')).isoformat()})
   elif ticket is None:raise ValueError('Create the sandbox ticket first')
   elif action=='read':
    if args:raise ValueError('Read takes no extra input')
    self.db.rollback();return ticket
   else:
    needed={'expected_revision','observed_at','station_arrival','delay_minutes','boarding_minutes','uncertainty_minutes'}
    if set(args)!=needed:raise ValueError('Change input incomplete')
    request=hashlib.sha256(json.dumps(args,sort_keys=True).encode()).hexdigest()
    if any(e.get('request')==request for e in ticket['events']):self.db.rollback();return ticket
    if type(args['expected_revision']) is not int or args['expected_revision']!=ticket['revision']:raise ValueError('Stale ticket revision')
    def ident(r):return str(r['trainno'])+':'+str(r['depplandtime'])
    trains={ident(r):r for r in ticket['timetable']}
    schedule=[{'id':key,'departure':datetime.strptime(str(r['depplandtime']),'%Y%m%d%H%M%S').replace(tzinfo=ZoneInfo('Asia/Seoul')).isoformat()} for key,r in trains.items()]
    result=simulate(existing_train_id=ident(ticket['current_train']),trains=schedule,**{k:v for k,v in args.items() if k!='expected_revision'})
    before=ticket['current_train'];key=result.get('selected_virtual_train_id')
    if key:ticket['current_train']=trains[key]
    ticket['revision']+=1
    ticket['events'].append({'receipt_id':'SIM-'+uuid.uuid4().hex[:12],'type':'changed' if result['virtual_change'] else 'kept' if key else 'no_alternative','revision':ticket['revision'],'request':request,'previous_train':before,'train':ticket['current_train'],'decision':result,'cancelled_virtual_train':before if result['virtual_change'] else None,'at':datetime.now(ZoneInfo('Asia/Seoul')).isoformat()})
   self.db.execute('INSERT OR REPLACE INTO tickets VALUES(?,?,?)',(self.owner,scenario_id,json.dumps(ticket,ensure_ascii=False)));self.db.commit();return ticket
  except Exception:self.db.rollback();raise

def call(client,args):
 store=Sandbox(client.root,os.environ.get('NUBI_GOAL_DEVICE_SESSION',''),client)
 try:return store.call(**args)
 finally:store.db.close()

def format_receipt(ticket):
 row=ticket['current_train'];stamp=str(row['depplandtime']);event=ticket['events'][-1]
 action={'created':'가상 승차권을 준비했어.','changed':'버스 지연에 맞춰 다음 가상 열차로 변경했어.','kept':'기존 가상 열차를 유지했어.','no_alternative':'다음 가상 열차가 없어 기존 표를 유지했어.'}[event['type']]
 lines=[action]
 if event.get('decision'):
  decision=event['decision'];clock=lambda value:datetime.fromisoformat(value).astimezone(ZoneInfo('Asia/Seoul')).strftime('%H:%M')
  lines.append('513번 가상 도착 '+clock(decision['delayed_station_arrival'])+' · 승차 준비 완료 '+clock(decision['ready_at']))
  old=str(event['previous_train']['depplandtime']);lines.append('기존 열차 '+old[8:10]+':'+old[10:12]+' → '+stamp[8:10]+':'+stamp[10:12])
 lines.extend([row.get('traingradename','열차')+' '+str(row['trainno'])+' · '+stamp[8:10]+':'+stamp[10:12]+' 출발','가상 접수증 '+event['receipt_id']+' · 변경 기록 '+str(ticket['revision'])+'회'])
 return '\n'.join(lines)
