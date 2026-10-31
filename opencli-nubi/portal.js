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

// Public official pages. The HTML parser uses only Python's standard library.
const { execFileSync } = await import('node:child_process');
const { fileURLToPath } = await import('node:url');
const officialParser=fileURLToPath(new URL('./official.py',import.meta.url));
async function readOfficial(url,mode){
 const r=await fetch(url,{redirect:'error',signal:AbortSignal.timeout(15000)});if(!r.ok)throw new Error('Official source HTTP '+r.status);
 const html=await r.text();if(html.length>3000000)throw new Error('Official response too large');
 const result=execFileSync('python3',[officialParser,mode],{input:html,encoding:'utf8',timeout:10000,maxBuffer:1000000});return JSON.parse(result);
}
const jobsUrl='https://aigs.unist.ac.kr/employment/';
cli({site:'nubi-unist',name:'jobs-list',access:'read',description:'Read recent UNIST AI graduate school employment posts',strategy:Strategy.PUBLIC,browser:false,columns:['title','date','url','source'],func:async()=>{
 const rows=await readOfficial(jobsUrl,'jobs');if(!rows.length)throw new Error('Job list is empty or page format changed');return rows;
}});
cli({site:'nubi-unist',name:'jobs-detail',access:'read',description:'Read a selected item from the current UNIST employment list',strategy:Strategy.PUBLIC,browser:false,args:[{name:'index',type:'int',positional:true,required:true},{name:'title',type:'str',positional:true,required:true}],columns:['title','date','body','url'],func:async(args)=>{
 const rows=await readOfficial(jobsUrl,'jobs');const index=Number(args.index);if(!Number.isInteger(index)||index<1||index>rows.length)throw new Error('Selection is outside the current job list');
 const row=rows[index-1];if(row.title!==args.title)throw new Error('The job list changed; refresh the choices');const detail=await readOfficial(row.url,'jobdetail');if(detail.title!==row.title)throw new Error('The selected job changed; refresh the choices');return [{...detail,url:row.url,source:jobsUrl}];
}});
cli({site:'nubi-unist',name:'dining-list',access:'read',description:'Read UNIST official campus dining locations and hours',strategy:Strategy.PUBLIC,browser:false,columns:['name','location','hours','source'],func:async()=>{
 const rows=await readOfficial('https://www.unist.ac.kr/unist/life/convenience.do','dining');if(!rows.length)throw new Error('Dining source format changed');return rows;
}});
cli({site:'nubi-unist',name:'clubs-list',access:'read',description:'Read the UNIST computer science department club page',strategy:Strategy.PUBLIC,browser:false,columns:['name','description','url','source'],func:async()=>{
 const rows=await readOfficial('https://cse.unist.ac.kr/cse/community/circle.do','clubs');if(!rows.length)throw new Error('Club source format changed');return rows;
}});

async function shoppingResults(page,expected){
 const result=await page.evaluate(`(()=>{
  if(location.hostname!=='msearch.shopping.naver.com')throw new Error('Open Naver price comparison first');
  const q=new URL(location.href).searchParams.get('query')||'';
  if(${JSON.stringify(expected||'')} && q!==${JSON.stringify(expected||'')})throw new Error('Waiting for the requested search');
  return Array.from(document.querySelectorAll('a[aria-label][data-shp-contents-dtl]')).map(e=>{
    let details,meta;try{details=Object.fromEntries(JSON.parse(e.getAttribute('data-shp-contents-dtl')).map(v=>[v.key,v.value]));meta=JSON.parse(e.getAttribute('data-nlog-params')||'{}')}catch{return null}
    if(!details.prod_nm || !(details.price||details.lowest_price))return null;
    const lines=(e.parentElement?.innerText||'').split('\\n').map(x=>x.trim()).filter(Boolean);let at=lines.indexOf('배송비');
    return {name:String(details.prod_nm),listed_price_krw:Number(details.lowest_price||details.price),shipping:at>=0?(lines[at+1]||'미표시'):'미표시',sponsored:meta.is_ad===true || lines.includes('광고') || (e.getAttribute('aria-label')||'').startsWith('광고,'),source:'네이버 가격비교',query:q,search_url:'https://msearch.shopping.naver.com/search/all?query='+encodeURIComponent(q)};
   }).filter(Boolean).slice(0,20).map((x,i)=>({index:i+1,...x}));
 })()`);
 if(!Array.isArray(result)||!result.length)throw new Error('No visible product results; check search, service access or page changes');return result;
}
cli({site:'nubi-unist',name:'shopping-search',access:'read',description:'Search visible Naver mobile price comparison products',domain:'msearch.shopping.naver.com',strategy:Strategy.COOKIE,browser:true,navigateBefore:false,args:[{name:'query',type:'str',positional:true,required:true}],columns:['index','name','listed_price_krw','shipping','sponsored','source','query','search_url'],func:async(page,args)=>{
 const q=String(args.query||'').trim();if(!q||q.length>100)throw new Error('Query must contain 1–100 characters');
 await page.cdp('Page.navigate',{url:'https://msearch.shopping.naver.com/search/all?query='+encodeURIComponent(q)});
 for(let i=0;i<25;i++){await new Promise(r=>setTimeout(r,1000));try{return await shoppingResults(page,q);}catch(e){if(i===24)throw e;}}
}});
cli({site:'nubi-unist',name:'shopping-select',access:'read',description:'Read a selected item from the current visible product results',domain:'msearch.shopping.naver.com',strategy:Strategy.COOKIE,browser:true,navigateBefore:false,args:[{name:'index',type:'int',positional:true,required:true},{name:'title',type:'str',positional:true,required:true}],columns:['index','name','listed_price_krw','shipping','sponsored','source','query','search_url'],func:async(page,args)=>{
 const rows=await shoppingResults(page);const idx=Number(args.index);if(!Number.isInteger(idx)||idx<1||idx>rows.length||rows[idx-1].name!==args.title)throw new Error('The product list changed; refresh choices');return [rows[idx-1]];
}});

async function saraminSearchRows(page,expected) {
 const rows=await page.evaluate(`(()=>{
   if(location.hostname!=='www.saramin.co.kr'||!location.pathname.startsWith('/zf_user/search'))throw new Error('Open Saramin search first');
   const q=new URL(location.href).searchParams.get('searchword')||'';if(${JSON.stringify(expected||'')} && q!==${JSON.stringify(expected||'')})throw new Error('Waiting for search results');
   return Array.from(document.querySelectorAll('.item_recruit')).map(e=>{
     const id=e.getAttribute('value')||'';const title=e.querySelector('.job_tit a')?.innerText.trim()||'';
     const company=e.querySelector('.corp_name')?.innerText.trim()||'';
     const conditions=Array.from(e.querySelectorAll('.job_condition span')).map(n=>n.innerText.trim()).filter(Boolean).join(' · ');
     const deadline=e.querySelector('.job_date .date')?.innerText.trim()||'';
     if(!/^\\d{1,12}$/.test(id)||!title)return null;
     return {id,title,company,conditions,deadline,url:'https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx='+id,source:'사람인'};
   }).filter(Boolean).slice(0,20).map((row,i)=>({index:i+1,...row}));
 })()`);if(!Array.isArray(rows)||!rows.length)throw new Error('No visible Saramin results; check the search page');return rows;
}
cli({site:'nubi-unist',name:'saramin-search',access:'read',description:'Search Saramin public job listings in Nubi',domain:'www.saramin.co.kr',strategy:Strategy.COOKIE,browser:true,navigateBefore:false,args:[{name:'query',type:'str',positional:true,required:true}],columns:['index','id','title','company','conditions','deadline','url','source'],func:async(page,args)=>{
 const q=String(args.query||'').trim();if(!q||q.length>100)throw new Error('Query must contain 1–100 characters');
 await page.cdp('Page.navigate',{url:'https://www.saramin.co.kr/zf_user/search?searchword='+encodeURIComponent(q)});
 for(let i=0;i<25;i++){await new Promise(r=>setTimeout(r,1000));try{return await saraminSearchRows(page,q);}catch(e){if(i===24)throw e;}}
}});
cli({site:'nubi-unist',name:'saramin-detail',access:'read',description:'Read selected Saramin job information by public job id',domain:'www.saramin.co.kr',strategy:Strategy.COOKIE,browser:true,navigateBefore:false,args:[{name:'id',type:'str',positional:true,required:true},{name:'title',type:'str',positional:true,required:true}],columns:['id','title','key_info','url','source'],func:async(page,args)=>{
 const id=String(args.id||'');if(!/^\d{1,12}$/.test(id)||!args.title)throw new Error('Provide a job id and title');
 await page.cdp('Page.navigate',{url:'https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx='+id});
 for(let i=0;i<25;i++){await new Promise(r=>setTimeout(r,1000));try{
  const data=await page.evaluate(`(()=>{
   if(location.hostname!=='www.saramin.co.kr'||new URL(location.href).searchParams.get('rec_idx')!==${JSON.stringify(id)})throw new Error('Waiting for selected posting');
   const section=document.querySelector('section.jview-0-'+${JSON.stringify(id)});const title=section?.querySelector('h1.tit_job')?.innerText.trim()||'';
   if(!title)throw new Error('Job detail not ready');
   const key_info=Array.from(section.querySelectorAll('dl')).slice(0,15).map(e=>e.innerText.trim().replace(/\\s+/g,' ')).filter(Boolean);
   return {id:${JSON.stringify(id)},title,key_info:key_info.join(' | '),url:'https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx='+${JSON.stringify(id)},source:'사람인'};
  })()`);
  if(data.title!==args.title)throw new Error('The selected posting changed');return [data];
 }catch(e){if(i===24||String(e).includes('posting changed'))throw e;}}
}});

cli({site:'nubi-unist',name:'wanted-search',access:'read',description:'Search Wanted positions and related suggestions',domain:'www.wanted.co.kr',strategy:Strategy.COOKIE,browser:true,navigateBefore:false,args:[{name:'query',type:'str',positional:true,required:true}],columns:['index','id','title','company','experience','url','source'],func:async(page,args)=>{
 const q=String(args.query||'').trim();if(!q||q.length>100)throw new Error('Query must contain 1–100 characters');
 await page.cdp('Page.navigate',{url:'https://www.wanted.co.kr/search?query='+encodeURIComponent(q)+'&tab=position'});
 for(let i=0;i<25;i++){await new Promise(r=>setTimeout(r,1000));try{
  const data=await page.evaluate(`(()=>{
   if(location.hostname!=='www.wanted.co.kr'||new URL(location.href).searchParams.get('query')!==${JSON.stringify(q)})throw new Error('Waiting for the requested search');
   const seen=new Set();return Array.from(document.querySelectorAll('a[data-position-id][data-tab-kind="position"]')).map(e=>{
    const id=e.dataset.positionId||'',title=e.dataset.positionName||'',company=e.dataset.companyName||'';
    if(!/^\\d{1,12}$/.test(id)||!title||seen.has(id))return null;seen.add(id);
    const lines=e.innerText.split('\\n').map(s=>s.trim()).filter(Boolean);
    return {id,title,company,experience:lines.find(s=>s.startsWith('경력')||s==='신입')||'',url:'https://www.wanted.co.kr/wd/'+id,source:'원티드',result_type:'검색 결과 및 관련 추천'};
   }).filter(Boolean).slice(0,20).map((e,i)=>({index:i+1,...e}));
  })()`);if(data.length)return data;
 }catch(e){if(i===24)throw e;}}
 throw new Error('Wanted search results not available');
}});
cli({site:'nubi-unist',name:'wanted-detail',access:'read',description:'Read a selected Wanted job by id and title',domain:'www.wanted.co.kr',strategy:Strategy.COOKIE,browser:true,navigateBefore:false,args:[{name:'id',type:'str',positional:true,required:true},{name:'title',type:'str',positional:true,required:true}],columns:['id','title','description','url','source'],func:async(page,args)=>{
 const id=String(args.id||'');if(!/^\d{1,12}$/.test(id)||!args.title)throw new Error('Provide job id and title');
 await page.cdp('Page.navigate',{url:'https://www.wanted.co.kr/wd/'+id});
 for(let i=0;i<25;i++){await new Promise(r=>setTimeout(r,1000));try{
  const d=await page.evaluate(`(()=>{
   if(location.hostname!=='www.wanted.co.kr'||location.pathname!==('/wd/'+${JSON.stringify(id)}))throw new Error('Waiting for selected job');
   const title=document.querySelector('h1')?.innerText.trim()||'';const article=document.querySelector('article[class*="JobDescription_"]');
   if(!title||!article)throw new Error('Job details not ready');return {id:${JSON.stringify(id)},title,description:article.innerText.trim().slice(0,8000),url:'https://www.wanted.co.kr/wd/'+${JSON.stringify(id)},source:'원티드'};
  })()`);if(d.title!==args.title)throw new Error('The selected posting changed');return [d];
 }catch(e){if(i===24||String(e).includes('posting changed'))throw e;}}
}});
