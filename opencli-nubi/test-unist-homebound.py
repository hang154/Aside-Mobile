import unittest
from unittest.mock import patch
from unist_homebound import parse_bus,plan,format_plan
HTML='<table><tr><th>UNIST(경유) 탑승</th><td>–</td><td>15:53</td><td>16:26</td></tr><tr><th>울산역 정류장 착</th><td>–</td><td>16:09</td><td>16:43</td></tr><tr><th>UNIST 발 (버스)</th><td>15:30</td></tr><tr><th>5001 울산역 착</th><td>15:50</td></tr></table>'
RAIL={'source_url':'https://www.data.go.kr/data/15098552/openapi.do','items':[{'traingradename':'KTX','trainno':'48','depplandtime':'20261103163200','arrplandtime':'20261103165500'},{'traingradename':'KTX','trainno':'52','depplandtime':'20261103165100','arrplandtime':'20261103171400'}]}
class Homebound(unittest.TestCase):
 def test_direct_bus_only(self):self.assertEqual(parse_bus(HTML),[('15:53','16:09'),('16:26','16:43')])
 def test_column_mismatch_rejected(self):
  with self.assertRaises(ValueError):parse_bus(HTML.replace('<td>16:09</td>',''))
 def test_missing_direction_rejected(self):
  with self.assertRaises(ValueError):parse_bus(HTML.replace('UNIST(경유) 탑승','다른 정류장'))
 def test_full_connection_and_walk(self):
  with patch('unist_homebound.query',return_value=RAIL):r=plan(None,'20261103','15:40',fetcher=lambda _:HTML)
  self.assertTrue(r['options'][0]['leave_class_at'].endswith('15:45:00+09:00'))
  self.assertEqual(r['options'][0]['train']['trainno'],'48');self.assertEqual(r['options'][0]['boarding_margin_minutes'],18)
  self.assertIn('15:53',format_plan(r))
 def test_missed_bus_not_recommended(self):
  with patch('unist_homebound.query',return_value=RAIL):r=plan(None,'20261103','16:00',fetcher=lambda _:HTML)
  self.assertEqual(r['options'][0]['train']['trainno'],'52')
 def test_no_bus_after_class(self):
  with patch('unist_homebound.query',return_value=RAIL):r=plan(None,'20261103','23:00',fetcher=lambda _:HTML)
  self.assertEqual(r['state'],'no_results')
 def test_weekend_source(self):
  urls=[]
  with patch('unist_homebound.query',return_value=RAIL):r=plan(None,'20261107','15:40',fetcher=lambda u:(urls.append(u) or HTML))
  self.assertEqual(r['day_type'],'saturday');self.assertIn('day=1',urls[0])
if __name__=='__main__':unittest.main()
