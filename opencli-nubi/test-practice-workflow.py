import tempfile,unittest,json,urllib.request,urllib.error
from pathlib import Path
from practice_workflow import verify
from practice_lms import serve
CODE='''import unittest
def sum_even(values):
 return sum(v for v in values if v % 2 == 0)
class TestEven(unittest.TestCase):
 def test_empty(self): self.assertEqual(sum_even([]),0)
 def test_mixed(self): self.assertEqual(sum_even([1,2,3,4]),6)
 def test_negative(self): self.assertEqual(sum_even([-2,-3,4]),2)
 def test_duplicate(self): self.assertEqual(sum_even([2,2]),4)
if __name__ == '__main__': unittest.main()
'''
class PracticeChecks(unittest.TestCase):
 def test_isolated_valid(self):
  with tempfile.TemporaryDirectory() as d:self.assertEqual(verify(CODE,Path(d))['independent_tests'],3)
 def test_wrong_answer(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):verify(CODE.replace('v % 2 == 0','v % 2 == 1'),Path(d))
 def test_file_execution_blocked(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):verify(CODE+'\nopen("/tmp/unsafe","w")',Path(d))
 def test_import_blocked(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):verify('import os\n'+CODE,Path(d))
 def test_receipt(self):
  with tempfile.TemporaryDirectory() as d:
   proof=verify(CODE,Path(d)/'work')
   with serve(Path(d)/'lms') as base:
    data={'code':CODE,'environment':'LOCAL_PRACTICE_ONLY','student':'00000000 Nubi Test','filename':'practice.py','proof':proof}
    def post(data):
     with urllib.request.urlopen(urllib.request.Request(base+'/submissions',data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})) as f:return json.load(f)
    first=post(data);self.assertEqual(post(data),first)
    with urllib.request.urlopen(base+'/submissions/'+first['id']) as f:self.assertEqual(json.load(f),first)
    with self.assertRaises(urllib.error.HTTPError):post(dict(data,student='real student'))
    with self.assertRaises(urllib.error.HTTPError):post(dict(data,code=CODE+'\n# tampered'))
unittest.main()
