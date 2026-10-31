import os,runpy
from pathlib import Path
m=runpy.run_path(str(Path(__file__).with_name('nubi-goal-mcp.py')));v=m['validate'];n=0
for goal in ['fitness','love','grades','home']:v('nubi_goal_open',{'character':goal});n+=1
for name,a in [('nubi_goal_explore',{'character':'home','searches':[{'provider':'youtube','query':'x'}]*4}),('nubi_goal_explore',{'character':'fitness','searches':[{'provider':'unknown','query':'x'}]}),('nubi_goal_open',{'character':'unknown'}),('nubi_goal_search',{'goal_id':'x','provider':'youtube','query':'x'}),('nubi_goal_open',{'character':'fitness','url':'https://example.com'}),('nubi_goal_select',{'goal_id':'a'*36,'index':True,'observation_id':'x'}),('nubi_goal_report',{'goal_id':'a'*36,'summary':'','source_urls':[]})]:
 try:v(name,a)
 except (ValueError,TypeError):n+=1;continue
 raise AssertionError(name)
v('nubi_goal_explore',{'character':'home','searches':[{'provider':'youtube','query':'주택 청약'}]});n+=1
assert len(m['DEFINITIONS'])==6
print('PASS',n+1,'MCP argument/goal/tool boundary checks')
