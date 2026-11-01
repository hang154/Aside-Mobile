#!/usr/bin/env python3
"""Interactive delegated OAuth for a user-owned Entra public-client registration."""
import argparse,json,os
from pathlib import Path
import msal
p=argparse.ArgumentParser();p.add_argument('--config',required=True);a=p.parse_args();c=json.loads(Path(a.config).read_text())['graph']
cache=msal.SerializableTokenCache();dest=Path(c['cache_file']).expanduser();dest.parent.mkdir(parents=True,exist_ok=True);dest.parent.chmod(0o700)
if dest.exists():cache.deserialize(dest.read_text())
app=msal.PublicClientApplication(c['client_id'],authority='https://login.microsoftonline.com/'+c['tenant_id'],token_cache=cache)
flow=app.initiate_device_flow(scopes=c.get('scopes',['Mail.Read','Files.ReadWrite']))
if 'user_code' not in flow:raise SystemExit('Device login not available for this registration')
print(flow['message'],flush=True);r=app.acquire_token_by_device_flow(flow)
if 'access_token' not in r:raise SystemExit('Sign-in failed: '+r.get('error','unknown'))
# Token/cache is never printed. Require one intended account in configuration.
if not app.get_accounts(username=c['account']):raise SystemExit('Signed-in account differs from configured account')
fd=os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
with os.fdopen(fd,'w') as f:f.write(cache.serialize())
dest.chmod(0o600);print('Microsoft Graph sign-in saved locally')
