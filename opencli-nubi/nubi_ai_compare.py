"""Four named provider slots; missing accounts remain missing, never Qwen stand-ins."""
import concurrent.futures,json,urllib.request
from pathlib import Path
from nubi_group_qwen import GroupQwen,MODEL
from nubi_persona import persona
def compare(text,config_path=None):
 if not isinstance(text,str) or not 1<=len(text.strip())<=1500:raise ValueError('비교할 맥락은 1~1500자여야 해요.')
 path=Path(config_path or Path.home()/'.local/state/nubi-ai-compare/providers.json')
 configured=json.loads(path.read_text()) if path.exists() else {}
 if not isinstance(configured,dict) or set(configured)-{'gpt','claude','gemini'}:raise ValueError('Invalid compare provider configuration')
 def one(name):
  try:
   if name=='nubi':
    q=GroupQwen.__new__(GroupQwen);q.timeout=18;answer,model=q._complete([{'role':'system','content':persona('love')+'완성된 답장 초안을 두 개만 제안해.'},{'role':'user','content':text}]);return {'provider':name,'state':'completed','model':model,'answer':answer[:1800]}
   entry=configured.get(name)
   if not entry:return {'provider':name,'state':'not_connected','reason':name+' API 계정 연결이 없어요. 웹 로그인만으로 API 권한이 생기지는 않아요.'}
   config=json.loads((Path.home()/'.azrael-ex/azrael/providers/api/connections.json').read_text())
   found=[c for c in config['connections'] if c.get('enabled') and c.get('id')==entry.get('connection_id') and any(m.get('id')==entry.get('model') for m in c.get('models',[]))]
   if len(found)!=1:raise ValueError('등록된 모델 연결을 찾지 못했어요.')
   c=found[0];auth=c.get('auth',{})
   if auth.get('kind')!='bearerFile':raise ValueError('지원하는 서버 인증 설정이 필요해요.')
   model=entry['model'];prefix={'gpt':('gpt','o1','o3','o4'),'claude':('claude',),'gemini':('gemini',)}[name]
   if not model.lower().startswith(prefix):raise ValueError('서비스 이름과 모델 이름이 일치하지 않아요.')
   payload={'model':model,'messages':[{'role':'system','content':'한국어로 자연스러운 답장 초안 두 개만 써줘. 실제 전송하지 마.'},{'role':'user','content':text}],'max_tokens':700}
   req=urllib.request.Request(c['baseUrl'].rstrip('/')+'/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+Path(auth['filePath']).expanduser().read_text().strip()})
   with urllib.request.urlopen(req,timeout=18) as response:data=json.load(response)
   if data.get('model')!=model:raise ValueError('응답 모델 신원 불일치')
   answer=data['choices'][0]['message']['content']
   if not isinstance(answer,str) or not answer.strip():raise ValueError('빈 응답')
   return {'provider':name,'state':'completed','model':model,'answer':answer[:1800]}
  except Exception as e:return {'provider':name,'state':'failed','reason':'실제 모델 응답 확인 실패 ('+type(e).__name__+'). 연결 설정을 확인해 주세요.'}
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(one,['nubi','gpt','claude','gemini']))
 return {'items':results,'scope':'각 슬롯은 해당 서비스의 실제 응답만 표시. 외부 메시지 전송 없음.'}
