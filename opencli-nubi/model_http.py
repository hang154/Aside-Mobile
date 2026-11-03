"""Bounded retries for side-effect-free model generation, never for service actions."""
import json,time,urllib.request,urllib.error

def generate(request,timeout=90):
 for attempt in range(2):
  try:
   with urllib.request.urlopen(request,timeout=timeout) as response:return json.load(response)
  except (TimeoutError,urllib.error.URLError) as error:
   if isinstance(error,urllib.error.HTTPError) and error.code not in (408,429,500,502,503,504):raise
   if attempt:raise
   time.sleep(1)
