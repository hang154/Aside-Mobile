"""Show a fixed service source in the request-owned in-chat browser over TLS."""
import importlib.util,os,time
from pathlib import Path
DEFINITION={'name':'nubi_transit_open_source','description':'Show the selected official transport source in the same Nubi conversation browser. bus_plan (weekday), bus_plan_sat (Saturday), bus_plan_sun (Sunday or holiday) show the planned UNIST to Ulsan station connection table; bus513 shows the UNIST direction timetable; naver_bus shows Naver Maps UNIST bus search; korail shows the official ticket page. Opening is not a reservation.','inputSchema':{'type':'object','properties':{'source':{'type':'string','enum':['bus_plan','bus_plan_sat','bus_plan_sun','bus513','naver_bus','korail']}},'required':['source'],'additionalProperties':False}}
def show(source):
 if source not in ('bus_plan','bus_plan_sat','bus_plan_sun','bus513','naver_bus','korail'):raise ValueError('Unknown transport source')
 goal=os.environ.get('NUBI_GOAL_ID','')
 if not goal or not os.environ.get('NUBI_GOAL_DEVICE_SESSION'):raise ValueError('Request-owned device browser required')
 spec=importlib.util.spec_from_file_location('view_transport',Path(__file__).with_name('nubi-goal-mcp.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 command=m.post('/command',{'op':'goal_service_open','goal_id':goal,'source':source})['id']
 for _ in range(35):
  result=m.post('/get-result',{'id':command}).get('result')
  if result is not None:return result
  time.sleep(.3)
 raise TimeoutError('Device source navigation timed out')
