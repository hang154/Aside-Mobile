"""Delegated Microsoft Graph adapter; credentials never pass through model tools."""
import hashlib,json,os,re,urllib.request,urllib.parse,urllib.error
from pathlib import Path

class Graph:
 def __init__(self,config,transport=None):
  self.config=config;self.transport=transport
 def token(self):
  if self.config.get('token_file'):
   p=Path(self.config['token_file']).expanduser()
   if p.stat().st_mode&0o077:raise ValueError('Graph token file must be private (chmod 600)')
   return p.read_text().strip()
  import msal
  cache=msal.SerializableTokenCache();p=Path(self.config['cache_file']).expanduser()
  if p.exists():
   if p.stat().st_mode&0o077:raise ValueError('OAuth cache must be private')
   cache.deserialize(p.read_text())
  app=msal.PublicClientApplication(self.config['client_id'],authority='https://login.microsoftonline.com/'+self.config['tenant_id'],token_cache=cache)
  users=app.get_accounts(username=self.config['account'])
  if len(users)!=1:raise RuntimeError('Graph account not signed in; run document-auth.py')
  result=app.acquire_token_silent(self.config.get('scopes',['Mail.Read','Files.ReadWrite']),account=users[0])
  if not result or 'access_token' not in result:raise RuntimeError('Graph sign-in expired; run document-auth.py')
  if cache.has_state_changed:p.write_text(cache.serialize());p.chmod(0o600)
  return result['access_token']
 def call(self,method,path,data=None,raw=False):
  if not path.startswith('/') or path.startswith('//'):raise ValueError('Graph relative path required')
  url='https://graph.microsoft.com/v1.0'+path
  if self.transport:return self.transport(method,url,data,raw)
  body=data if isinstance(data,bytes) else json.dumps(data).encode() if data is not None else None
  headers={'Authorization':'Bearer '+self.token(),'Prefer':'IdType="ImmutableId"'}
  if body is not None:headers['Content-Type']='application/octet-stream' if isinstance(data,bytes) else 'application/json'
  req=urllib.request.Request(url,data=body,headers=headers,method=method)
  # Do not forward Graph bearer to preauthenticated download domains on redirects.
  class NoRedirect(urllib.request.HTTPRedirectHandler):
   def redirect_request(self,*a,**kw):return None
  try:
   with urllib.request.build_opener(NoRedirect).open(req,timeout=60) as r:
    b=r.read(16*1024*1024+1)
    if not b and r.status in (202,204):return {'http_status':r.status}
  except urllib.error.HTTPError as e:
   if method=='GET' and raw and e.code in (301,302,303,307,308):
    target=e.headers['Location'];u=urllib.parse.urlsplit(target)
    if u.scheme!='https' or not(u.hostname.endswith('.sharepoint.com') or u.hostname.endswith('.1drv.com')):raise ValueError('Untrusted Graph content redirect')
    with urllib.request.urlopen(target,timeout=60) as r:b=r.read(16*1024*1024+1)
   else:raise RuntimeError('Microsoft Graph HTTP '+str(e.code)) from None
  if len(b)>16*1024*1024:raise ValueError('Graph content too large')
  return b if raw else json.loads(b)
 def search(self,query,limit=20):
  q=urllib.parse.urlencode({'$search':'"'+query.replace('"','')+'"','$top':min(limit,25),'$select':'id,subject,body,receivedDateTime,hasAttachments,webLink'})
  return self.call('GET','/me/messages?'+q)['value']
 def attachments(self,message):return self.call('GET','/me/messages/'+esc(message)+'/attachments')['value']
 def download_attachment(self,message,attachment):return self.call('GET','/me/messages/'+esc(message)+'/attachments/'+esc(attachment)+'/$value',raw=True)
 def upload(self,path,target,filename):
  """One new upload session per file, conflict=fail; read-back verifies exact bytes.
  Neither automatic POST retry nor content overwrite. On ambiguous completion callers
  retain the receipt/incomplete state and reconcile before creating another upload.
  """
  data=Path(path).read_bytes()
  if not data or len(data)>8*1024*1024:raise ValueError('Upload size must be 1..8 MiB')
  if Path(filename).name!=filename or any(c in filename for c in '/\\:*?"<>|'):raise ValueError('Invalid upload filename')
  base='/drives/'+esc(target['drive_id'])+'/items/'+esc(target['folder_id'])
  folder=self.call('GET',base+'?$select=id,folder,webUrl')
  if 'folder' not in folder:raise ValueError('Upload destination is not a folder')
  u=urllib.parse.urlsplit(folder.get('webUrl',''))
  if u.scheme!='https' or u.hostname!=target['hostname'] or not u.hostname.endswith('.sharepoint.com'):raise ValueError('Configured SharePoint destination mismatch')
  session=self.call('POST',base+':/'+esc(filename)+':/createUploadSession',{'item':{'@microsoft.graph.conflictBehavior':'fail','name':filename}})
  upload_url=session['uploadUrl'];u=urllib.parse.urlsplit(upload_url)
  if u.scheme!='https' or not(u.hostname.endswith('.sharepoint.com') or u.hostname.endswith('.1drv.com') or u.hostname.endswith('.up.1drv.com')):raise ValueError('Untrusted upload session host')
  if self.transport:item=self.transport('PUT',upload_url,data,False)
  else:
   req=urllib.request.Request(upload_url,data=data,method='PUT',headers={'Content-Length':str(len(data)),'Content-Range':f'bytes 0-{len(data)-1}/{len(data)}'})
   with urllib.request.urlopen(req,timeout=90) as r:item=json.load(r)
  ident=item.get('id')
  if not ident or item.get('size')!=len(data):raise RuntimeError('Upload completion not confirmed')
  returned=self.call('GET','/drives/'+esc(target['drive_id'])+'/items/'+esc(ident)+'/content',raw=True)
  sha=hashlib.sha256(data).hexdigest()
  if hashlib.sha256(returned).hexdigest()!=sha:raise RuntimeError('Uploaded file read-back mismatch')
  return {'id':ident,'web_url':item.get('webUrl'),'sha256':sha,'size':len(data),'verified':True}

def esc(s):
 if not isinstance(s,str) or not s or len(s)>2048:raise ValueError('Invalid Graph identifier')
 return urllib.parse.quote(s,safe='')
