#!/usr/bin/env python3
"""Extract a narrow set of fields from public UNIST HTML supplied on stdin."""
import json,sys,re
from html.parser import HTMLParser
from urllib.parse import urljoin,urlparse
class Node:
 def __init__(self,tag='',attrs=()): self.tag=tag;self.a=dict(attrs);self.children=[]
 def text(self): return re.sub(r'\s+',' ',''.join(x if isinstance(x,str) else x.text() for x in self.children)).strip()
 def nodes(self):
  yield self
  for x in self.children:
   if isinstance(x,Node):yield from x.nodes()
 def has(self,c):return c in self.a.get('class','').split()
class P(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.root=Node();self.stack=[self.root]
 def handle_starttag(self,tag,attrs):
  n=Node(tag,attrs);self.stack[-1].children.append(n)
  if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:self.stack.append(n)
 def handle_endtag(self,tag):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==tag:self.stack=self.stack[:i];break
 def handle_data(self,s):self.stack[-1].children.append(s+' ')
def first(n,fn):return next((x for x in n.nodes() if fn(x)),None)
p=P();p.feed(sys.stdin.read());root=p.root;mode=sys.argv[1]
if mode=='jobs':
 out=[]
 for row in (x for x in root.nodes() if x.tag=='tr'):
  subject=first(row,lambda x:x.tag=='td' and x.has('subject'));date=first(row,lambda x:x.tag=='td' and x.has('date'))
  if not subject or not date:continue
  a=first(subject,lambda x:x.tag=='a' and bool(x.a.get('href')))
  if a:
   u=urljoin('https://aigs.unist.ac.kr/',a.a['href'])
   if urlparse(u).hostname=='aigs.unist.ac.kr':out.append({'title':a.text(),'date':date.text(),'url':u,'source':'UNIST 인공지능대학원 채용정보'})
 print(json.dumps(out[:20],ensure_ascii=False))
elif mode=='jobdetail':
 article=first(root,lambda x:x.tag=='article' and x.has('category-employment')); title=first(article,lambda x:x.has('post_title_label')) if article else None; body=first(article,lambda x:x.has('post_cont')) if article else None;date=first(article,lambda x:x.has('date')) if article else None
 if not title or not body:raise SystemExit('Cannot find job article content')
 print(json.dumps({'title':title.text(),'date':date.text() if date else '', 'body':body.text()[:8000]},ensure_ascii=False))
elif mode=='dining':
 names={'교직원 식당','학생식당','1차 생활관 식당'};out=[]
 for item in (x for x in root.nodes() if x.tag=='div' and x.has('item')):
  title=first(item,lambda x:x.tag=='p' and x.has('tit'))
  if not title or title.text() not in names:continue
  loc=first(item,lambda x:x.tag=='li' and x.has('adsress'));hours=first(item,lambda x:x.tag=='li' and x.has('time'))
  out.append({'name':title.text(),'location':re.sub(r'^위치\s*','',loc.text()) if loc else '', 'hours':re.sub(r'^이용시간\s*','',hours.text()) if hours else '', 'source':'https://www.unist.ac.kr/unist/life/convenience.do'})
 print(json.dumps(out,ensure_ascii=False))
elif mode=='clubs':
 out=[]
 for box in (x for x in root.nodes() if x.tag=='div' and x.has('con-box')):
  h=first(box,lambda x:x.tag=='h4');content=first(box,lambda x:x.has('list-gray-box'));link=first(box,lambda x:x.tag=='a' and x.a.get('href','').startswith('https://'))
  if h and content:out.append({'name':h.text(),'description':content.text()[:1200],'url':link.a['href'] if link else '','source':'https://cse.unist.ac.kr/cse/community/circle.do'})
 print(json.dumps(out,ensure_ascii=False))
