import io
import unittest
import urllib.error
from unittest.mock import patch
import model_http

class ModelRetryTests(unittest.TestCase):
 def test_transient_generation_retries_once(self):
  with patch('model_http.urllib.request.urlopen',side_effect=[TimeoutError(),io.BytesIO(b'{"ok":true}')]) as call, patch('model_http.time.sleep'):
   self.assertEqual(model_http.generate('request'),{'ok':True})
   self.assertEqual(call.call_count,2)
 def test_retry_is_bounded(self):
  with patch('model_http.urllib.request.urlopen',side_effect=urllib.error.URLError('offline')) as call, patch('model_http.time.sleep'):
   with self.assertRaises(urllib.error.URLError):model_http.generate('request')
   self.assertEqual(call.call_count,2)
 def test_auth_error_is_not_retried(self):
  error=urllib.error.HTTPError('https://example.invalid',401,'Unauthorized',{},None)
  with patch('model_http.urllib.request.urlopen',side_effect=error) as call:
   with self.assertRaises(urllib.error.HTTPError):model_http.generate('request')
   self.assertEqual(call.call_count,1)
 def test_invalid_response_is_not_retried(self):
  with patch('model_http.urllib.request.urlopen',return_value=io.BytesIO(b'invalid')) as call:
   with self.assertRaises(ValueError):model_http.generate('request')
   self.assertEqual(call.call_count,1)

if __name__=='__main__':unittest.main()
