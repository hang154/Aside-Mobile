import hashlib
from nubi_lecture_translation import translate_segment
from nubi_group_qwen import MODEL
seen=[]
def model(messages):
 seen.append(messages);return ('가속도는 9.8 m/s²입니다.',MODEL)
r=translate_segment('Acceleration is 9.8 m/s².','en','ko',model)
assert r['state']=='translated' and r['model']==MODEL and '9.8' in r['translation']
assert r['source_sha256']==hashlib.sha256(b'Acceleration is 9.8 m/s\xc2\xb2.').hexdigest()
assert seen[0][1]['content']=='Acceleration is 9.8 m/s².'
for text,source,target in [('', 'en','ko'),('x'*1201,'en','ko'),('hello','en','en'),('hello','fr','ko'),(None,'en','ko')]:
 try:translate_segment(text,source,target,model);raise AssertionError('invalid accepted')
 except ValueError:pass
try:translate_segment('hello',complete=lambda m:('mock','different-model'));raise AssertionError('identity accepted')
except RuntimeError:pass
try:translate_segment('hello',complete=lambda m:('',MODEL));raise AssertionError('empty accepted')
except RuntimeError:pass
print('PASS translation contract, exact model, source binding, empty/oversize/unsupported language rejection (model fixture)')

try:translate_segment('Acceleration is 9.8 meters per second squared.',complete=lambda m:('초당 제곱미터 9.8',MODEL));raise AssertionError('wrong unit accepted')
except RuntimeError:pass
print('PASS observed acceleration-unit mistranslation rejected')
