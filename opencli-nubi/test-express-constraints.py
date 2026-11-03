import unittest
from express_bus import requested_after,format_journeys
class Constraints(unittest.TestCase):
 def test_cutoff(self):
  for text,expected in [('오전 8시 이후','08:00'),('오후 3시 40분 이후','15:40'),('08:30 이후','08:30'),('오전 12시 이후','00:00'),('오후 12시 이후','12:00')]:self.assertEqual(requested_after(text),expected)
 def test_no_guess(self):
  for text in ['8시 출발','25:00 이후','오후 13시 이후','08:66 이후']:self.assertIsNone(requested_after(text))
 def test_choices(self):
  d={'operation':'express_bus_journey','departure':{'terminalNm':'서울경부'},'arrival':{'terminalNm':'부산'},'date':'20261103','after_time':'08:00','source_url':'https://www.data.go.kr/','items':[{'depPlandTime':'202611030800','arrPlandTime':'202611031200','charge':43300,'gradeNm':'우등'}]*4}
  s=format_journeys([d]);self.assertIn('43,300원',s);self.assertIn('08:00 → 12:00',s);self.assertNotIn('4.',s)
unittest.main()
