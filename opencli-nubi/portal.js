import { cli, Strategy } from '@jackwener/opencli/registry';

cli({
  site: 'nubi-unist', name: 'portal-status', access: 'read',
  description: 'Inspect the already-open UNIST portal session without exposing account details',
  domain: 'portal.unist.ac.kr', strategy: Strategy.COOKIE, browser: true, navigateBefore: false,
  columns: ['host', 'title', 'signed_in'],
  func: async (page) => {
    const result = await page.evaluate(`(() => {
      if (location.hostname !== 'portal.unist.ac.kr') throw new Error('Open the UNIST portal in Nubi first');
      return { host: location.hostname, title: document.title,
        signed_in: /로그아웃/.test(document.body.innerText) };
    })()`);
    return [result];
  },
});

// Read-only status checks for a page already opened by the user. They do not
// navigate, extract credentials, or attempt reservations.
for (const spec of [
  {name:'naver-map-status', domain:'map.naver.com', hosts:['map.naver.com'], marker:'네이버지도'},
  {name:'kakao-map-status', domain:'map.kakao.com', hosts:['map.kakao.com','m.map.kakao.com','applink.map.kakao.com'], marker:'카카오맵'},
  {name:'korail-status', domain:'www.korail.com', hosts:['www.korail.com'], marker:'열차 조회'},
]) {
  cli({site:'nubi-unist',name:spec.name,access:'read',description:'Inspect an already-open '+spec.name+' page',
    domain:spec.domain,strategy:Strategy.COOKIE,browser:true,navigateBefore:false,
    columns:['host','title','marker_visible'],
    func:async page=>{
      const result=await page.evaluate(`(() => {
        if (!${JSON.stringify(spec.hosts)}.includes(location.hostname)) throw new Error('Open the requested service in Nubi first');
        const text = document.body ? document.body.innerText : '';
        return {host:location.hostname,title:document.title,marker_visible:text.includes(${JSON.stringify(spec.marker)})};
      })()`);
      return [result];
    },
  });
}

cli({
  site: 'nubi-unist', name: 'academic-menu', access: 'read',
  description: 'List visible academic menu entries in the already-open portal',
  domain: 'portal.unist.ac.kr', strategy: Strategy.COOKIE, browser: true, navigateBefore: false,
  columns: ['menu'],
  func: async (page) => {
    const result = await page.evaluate(`(() => {
      if (location.hostname !== 'portal.unist.ac.kr') throw new Error('Open the UNIST portal in Nubi first');
      if (!/로그아웃/.test(document.body.innerText)) throw new Error('Portal session is not signed in');
      const names = ['학적','수강','학기초 강의설문','성적','학점인정 / 학점이월','학점교류','졸업','학생활동','등록/장학','강의실예약','FAQ','ALPS','제증명 발급'];
      return names.filter(name => Array.from(document.querySelectorAll('body *')).some(e => e.textContent.trim() === name && e.getClientRects().length)).map(menu => ({menu}));
    })()`);
    return result;
  },
});

// Naver's result list is a cross-origin frame. Read it via CDP's isolated
// world; do not read input values, cookies, or hidden account information.
async function naverPlaces(page, expectedQuery) {
  const top=await page.evaluate('location.hostname');
  if(top!=='map.naver.com') throw new Error('Open Naver Map search in Nubi first');
  const tree=await page.cdp('Page.getFrameTree');
  const walk=n=>[n,...(n.childFrames||[]).flatMap(walk)];
  const frame=walk(tree.frameTree).find(n=>n.frame.name==='searchIframe' && new URL(n.frame.url).hostname==='pcmap.place.naver.com');
  if(!frame) throw new Error('Naver search results are not ready or are unavailable');
  if(expectedQuery && new URL(frame.frame.url).searchParams.get('query')!==expectedQuery) throw new Error('Waiting for the requested search results');
  const world=await page.cdp('Page.createIsolatedWorld',{frameId:frame.frame.id,worldName:'nubi-place-read'});
  const r=await page.cdp('Runtime.evaluate',{contextId:world.executionContextId,returnByValue:true,expression:`(() => {
    return Array.from(document.querySelectorAll('li')).filter(e=>e.querySelector('.YwYLL')).slice(0,20).map((e,i)=>({
      index:i+1,name:e.querySelector('.YwYLL')?.innerText.trim()||'',
      category:e.querySelector('.YzBgS')?.innerText.trim()||'',
      address:e.querySelector('.suKMR')?.innerText.trim()||'',
      source:'네이버 지도'
    })).filter(x=>x.name);
  })()`});
  if(r.exceptionDetails || !Array.isArray(r.result?.value)) throw new Error('Could not read Naver search results');
  if(!r.result.value.length) throw new Error('No visible results yet; wait or check the search page');
  return r.result.value;
}
cli({site:'nubi-unist',name:'naver-places',access:'read',description:'Read visible Naver Map place choices',domain:'map.naver.com',strategy:Strategy.COOKIE,browser:true,navigateBefore:false,columns:['index','name','category','address','source'],func:async page=>naverPlaces(page)});

cli({site:'nubi-unist',name:'unist-calendar',access:'read',description:'Read the official UNIST academic calendar for the next 60 days',strategy:Strategy.PUBLIC,browser:false,columns:['start','end','title','source'],func:async()=>{
  const zone='Asia/Seoul';const today=new Intl.DateTimeFormat('en-CA',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
  const from=new Date(today+'T00:00:00Z');const end=new Date(from.getTime()+60*86400000).toISOString().slice(0,10);
  const url=new URL('https://www.unist.ac.kr/unist/education/academic/schedule.do');url.search=new URLSearchParams({mode:'getCalendarData',siteId:'unist',start:today,end}).toString();
  const res=await fetch(url,{signal:AbortSignal.timeout(12000),redirect:'error'});if(!res.ok)throw new Error('UNIST HTTP '+res.status);
  const data=await res.json();if(!Array.isArray(data.data))throw new Error('UNIST response format changed');
  return data.data.filter(x=>x.content&&x.beginDt&&x.endDt).map(x=>({start:String(x.beginDt).replaceAll('.','-'),end:String(x.endDt).replaceAll('.','-'),title:String(x.content).trim(),source:'https://www.unist.ac.kr/unist/education/academic/schedule.do'})).filter(x=>x.end>=today&&x.start<=end).sort((a,b)=>a.start.localeCompare(b.start));
}});

cli({site:'nubi-unist',name:'korail-options',access:'read',description:'Read the visible Korail train choices or report a service access restriction',domain:'www.korail.com',strategy:Strategy.COOKIE,browser:true,navigateBefore:false,columns:['state','detail'],func:async page=>{
 const r=await page.evaluate(`(()=>{
   if(location.hostname!=='www.korail.com')throw new Error('Open Korail in Nubi first');
   const text=document.body?.innerText||'';
   if(text.includes('CODE : -8002') || text.includes('CODE : -8002'.replaceAll(' ',''))) return [{state:'blocked',detail:'코레일이 자동화/개발자도구 접근을 제한했습니다 (CODE -8002).'}];
   const rows=Array.from(document.querySelectorAll('tr')).map(e=>e.innerText.replace(/\\s+/g,' ').trim()).filter(t=>/(KTX|ITX|무궁화|새마을|SRT)/i.test(t)&&/\\d{1,2}:\\d{2}/.test(t)).slice(0,30);
   if(rows.length)return rows.map(detail=>({state:'train',detail}));
   return [{state:'not_ready',detail:'조회 결과가 없습니다. 코레일에서 조건을 입력하고 열차 조회를 진행하세요.'}];
 })()`);return r;
}});

cli({site:'nubi-unist',name:'naver-search',access:'read',description:'Search Naver Map in the open Nubi browser and return visible place choices',domain:'map.naver.com',strategy:Strategy.COOKIE,browser:true,navigateBefore:false,args:[{name:'query',type:'str',positional:true,required:true}],columns:['index','name','category','address','source'],func:async(page,kwargs)=>{
 const q=String(kwargs.query||'').trim();if(!q||q.length>100)throw new Error('Query must contain 1–100 characters');
 await page.cdp('Page.navigate',{url:'https://map.naver.com/p/search/'+encodeURIComponent(q)});
 for(let i=0;i<20;i++){await new Promise(r=>setTimeout(r,1000));try{return await naverPlaces(page,q);}catch(e){if(i===19)throw e;}}
}});

async function kakaoPlaces(page,expectedQuery){
 if(expectedQuery){const current=await page.evaluate('new URL(location.href).searchParams.get("q")');if(current!==expectedQuery)throw new Error('Waiting for the requested search results');}
 const rows=await page.evaluate(`(()=>{
   if(location.hostname!=='m.map.kakao.com')throw new Error('Open Kakao Map web search first');
   return Array.from(document.querySelectorAll('li.search_item[data-type="place"]')).slice(0,20).map((e,i)=>({
     index:i+1,name:e.querySelector('.tit_g')?.innerText.trim()||'',category:e.querySelector('.txt_ginfo')?.innerText.trim()||'',
     address:e.querySelector('.info_result .txt_g')?.innerText.trim()||'',source:'카카오맵'
   })).filter(x=>x.name);
 })()`);
 if(!Array.isArray(rows)||!rows.length)throw new Error('No Kakao place list is visible yet');return rows;
}
cli({site:'nubi-unist',name:'kakao-places',access:'read',description:'Read visible Kakao Map place choices',domain:'m.map.kakao.com',strategy:Strategy.COOKIE,browser:true,navigateBefore:false,columns:['index','name','category','address','source'],func:async page=>kakaoPlaces(page)});
cli({site:'nubi-unist',name:'kakao-search',access:'read',description:'Search Kakao Map and return visible place choices',domain:'m.map.kakao.com',strategy:Strategy.COOKIE,browser:true,navigateBefore:false,args:[{name:'query',type:'str',positional:true,required:true}],columns:['index','name','category','address','source'],func:async(page,kwargs)=>{
 const q=String(kwargs.query||'').trim();if(!q||q.length>100)throw new Error('Query must contain 1–100 characters');
 await page.cdp('Page.navigate',{url:'https://m.map.kakao.com/actions/searchView?q='+encodeURIComponent(q)+'&sort=0&fromAppLink=true'});
 for(let i=0;i<25;i++){
  await new Promise(r=>setTimeout(r,1000));
  try{
   const host=await page.evaluate('location.hostname');if(host!=='m.map.kakao.com')continue;
   await page.evaluate(`(()=>{let a=document.querySelector('a.link_search_list');if(a&&getComputedStyle(a).display!=='none')a.click()})()`);
   return await kakaoPlaces(page,q);
  }catch(e){if(i===24)throw e;}
 }
 throw new Error('Kakao Map search did not load');
}});
