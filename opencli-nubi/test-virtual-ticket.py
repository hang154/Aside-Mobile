import tempfile,unittest,uuid
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from virtual_ticket import Sandbox,format_receipt

ROWS=[{'trainno':'00048','traingradename':'KTX','depplandtime':'20261103163200','arrplandtime':'20261103165500','adultcharge':'9500'},{'trainno':'00050','traingradename':'KTX','depplandtime':'20261103163800','arrplandtime':'20261103170700','adultcharge':'9500'}]
CHANGE=dict(expected_revision=0,observed_at='2026-11-03T15:40:00+09:00',station_arrival='2026-11-03T16:09:00+09:00',delay_minutes=20,boarding_minutes=5,uncertainty_minutes=0)
class Tickets(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.session=str(uuid.uuid4())
  self.query=patch('virtual_ticket.query',return_value={'date':'20261103','items':ROWS}).start()
  self.store=Sandbox(self.tmp.name,self.session,None)
  self.store.call('create','case',date='20261103',train_number='00048')
 def tearDown(self):self.store.db.close();patch.stopall();self.tmp.cleanup()
 def test_delay_changes_both_ticket_and_receipt(self):
  r=self.store.call('change','case',**CHANGE)
  self.assertEqual(r['current_train']['trainno'],'00050');self.assertEqual(r['revision'],1)
  self.assertEqual(r['events'][-1]['cancelled_virtual_train']['trainno'],'00048')
  self.assertFalse(r['transactions_executed']);self.assertIn('SIM-',format_receipt(r))
 def test_replay_has_one_receipt(self):
  a=self.store.call('change','case',**CHANGE);b=self.store.call('change','case',**CHANGE)
  self.assertEqual(a,b);self.assertEqual(len(b['events']),2)
 def test_concurrent_replay_has_one_receipt(self):
  def change(_):
   store=Sandbox(self.tmp.name,self.session,None)
   try:return store.call('change','case',**CHANGE)
   finally:store.db.close()
  with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(change,range(2)))
  self.assertEqual(results[0],results[1]);self.assertEqual(len(results[0]['events']),2)
 def test_stale_change_cannot_overwrite(self):
  self.store.call('change','case',**CHANGE)
  with self.assertRaises(ValueError):self.store.call('change','case',**dict(CHANGE,delay_minutes=21))
  self.assertEqual(self.store.call('read','case')['revision'],1)
 def test_no_alternative_retains_original(self):
  r=self.store.call('change','case',**dict(CHANGE,delay_minutes=90))
  self.assertEqual(r['current_train']['trainno'],'00048');self.assertIsNone(r['events'][-1]['cancelled_virtual_train'])
 def test_no_delay_retains_original(self):
  r=self.store.call('change','case',**dict(CHANGE,delay_minutes=0))
  self.assertEqual(r['events'][-1]['type'],'kept')
 def test_other_device_cannot_read(self):
  other=Sandbox(self.tmp.name,str(uuid.uuid4()),None)
  with self.assertRaises(ValueError):other.call('read','case')
  other.db.close()
 def test_restart_restores_receipt(self):
  a=self.store.call('change','case',**CHANGE);other=Sandbox(self.tmp.name,self.session,None)
  self.assertEqual(other.call('read','case'),a);other.db.close()
 def test_invalid_change_rolls_back(self):
  with self.assertRaises(ValueError):self.store.call('change','case',**dict(CHANGE,delay_minutes=True))
  self.assertEqual(self.store.call('read','case')['revision'],0)
 def test_create_cannot_replace_existing(self):
  with self.assertRaises(ValueError):self.store.call('create','case',date='20261103',train_number='00050')
  self.assertEqual(self.store.call('read','case')['current_train']['trainno'],'00048')
if __name__=='__main__':unittest.main()
