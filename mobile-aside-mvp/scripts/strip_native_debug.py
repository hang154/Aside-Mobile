#!/usr/bin/env python3
"""Strip debug info in an isolated build copy; reject changes to runtime ELF sections."""
import argparse,pathlib,struct,hashlib,subprocess,json
p=argparse.ArgumentParser();p.add_argument('--libs',required=True);p.add_argument('--strip',required=True);p.add_argument('--report',required=True);a=p.parse_args()
def runtime(path):
 b=path.read_bytes();assert b[:5]==b'\x7fELF\x02' and b[5]==1
 off=struct.unpack_from('<Q',b,40)[0];size,count,idx=struct.unpack_from('<HHH',b,58)
 sections=[struct.unpack_from('<IIQQQQIIQQ',b,off+n*size) for n in range(count)];st=sections[idx];names=b[st[4]:st[4]+st[5]];out={}
 for s in sections:
  if s[2]&2:
   name=names[s[0]:].split(b'\0',1)[0].decode();out[name]={'size':s[5],'sha256':hashlib.sha256(b[s[4]:s[4]+s[5]]).hexdigest() if s[1]!=8 else 'NOBITS'}
 return out
rows=[]
for f in sorted(pathlib.Path(a.libs).glob('*.so')):
 before=runtime(f);old=f.stat().st_size;subprocess.run([a.strip,'--strip-debug',str(f)],check=True);assert runtime(f)==before,'Runtime ELF section changed: '+str(f)
 rows.append({'file':f.name,'before_bytes':old,'after_bytes':f.stat().st_size,'runtime_sections_unchanged':True,'runtime_section_count':len(before),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
pathlib.Path(a.report).write_text(json.dumps(rows,indent=2));print('PASS',len(rows),'native libraries: every allocated runtime section unchanged')
