"""Qwen drafts an inter-agent proposal; never sends it or assumes recipient availability."""
import json,urllib.request
from pathlib import Path
def draft(instruction):
 if not isinstance(instruction,str) or not 1<=len(instruction.strip())<=2000:raise ValueError('요청을 확인해 주세요')
 config=json.loads((Path.home()/'.azrael-ex/azrael/providers/api/connections.json').read_text())
 matches=[c for c in config['connections'] if c.get('enabled') and any(m.get('id')=='Qwen3.8-27B-uncensored-FP8' for m in c.get('models',[]))]
 if len(matches)!=1:raise ValueError('Qwen 연결 설정을 확인해 주세요')
 c=matches[0]
 if c.get('auth',{}).get('kind')!='bearerFile':raise ValueError('Qwen 인증 설정을 확인해 주세요')
 key=Path(c['auth']['filePath']).expanduser().read_text().strip();model='Qwen3.8-27B-abliterated-AWQ-W4A16'
 body={'model':model,'messages':[{'role':'system','content':'너는 누비의 친구 에이전트에게 보낼 제안 초안을 쓴다. 사용자 요청을 한국어 500자 이내로 자연스럽게 전달한다. 정해지지 않은 시간, 예약, 결제, 상대 일정이나 동의를 지어내지 않는다. 질문은 명확히 한다. 초안 본문만 반환한다. 아직 전송하지 않았다.'},{'role':'user','content':instruction}], 'temperature':0.2,'max_tokens':700,'chat_template_kwargs':{'enable_thinking':False}}
 req=urllib.request.Request(c['baseUrl'].rstrip('/')+'/chat/completions',data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=18) as r:out=json.load(r)
 text=out['choices'][0]['message']['content']
 if not isinstance(text,str) or not 1<=len(text)<=2000:raise ValueError('모델 초안을 확인해 주세요')
 return {'draft':text,'reported_model':out.get('model'),'sent':False}
