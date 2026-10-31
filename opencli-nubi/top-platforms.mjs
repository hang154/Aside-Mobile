// Semrush Traffic Analytics, September 2026. Geographic web visits, not nationality or app usage.
export const rankings={
 KR:['youtube.com','google.com','naver.com','chatgpt.com','x.com','instagram.com','missav123.com','facebook.com','yasyadong02.tv','weather.com','msn.com','newtoki1.org','tistory.com','av19t.com','inven.co.kr','kissjav.li','abr.ge','avsee.is','tvmon1.com','aliexpress.com'],
 US:['google.com','youtube.com','reddit.com','facebook.com','amazon.com','yahoo.com','chatgpt.com','instagram.com','wikipedia.org','duckduckgo.com','x.com','xvideos.com','pornhub.com','bing.com','tiktok.com','walmart.com','temu.com','espn.com','linkedin.com','weather.com']
};
const names={
 'youtube.com':['youtube'],'google.com':['google'],'naver.com':['naver-shopping','nubi-unist'],'chatgpt.com':['chatgpt'],'x.com':['twitter'],'instagram.com':['instagram'],'facebook.com':['facebook'],'weather.com':[],'msn.com':[],'tistory.com':[],'inven.co.kr':[],'aliexpress.com':[],'reddit.com':['reddit'],'amazon.com':['amazon'],'yahoo.com':['yahoo'],'wikipedia.org':['wikipedia'],'duckduckgo.com':['duckduckgo'],'bing.com':[],'tiktok.com':['tiktok'],'walmart.com':[],'temu.com':[],'espn.com':[],'linkedin.com':['linkedin']
};
export function ranked(country){return rankings[country].map((domain,i)=>({rank:i+1,domain,country,month:'2026-09',metric:'estimated web visits',source:'https://www.semrush.com/trending-websites/'+country.toLowerCase()+'/all/'}));}
export function aliasesFor(domain){return names[domain]||[];}
export function adapters(domain,commands){const aliases=names[domain]||[];return commands.filter(x=>x.access==='read'&&aliases.some(a=>x.command.startsWith(a+' '))&&(domain!=='naver.com'||!x.command.startsWith('nubi-unist ')||/^nubi-unist (naver-|shopping-)/.test(x.command))).slice(0,60).map(x=>({command:x.command,description:x.description}));}
export async function probe(domain){
 if(!Object.values(rankings).flat().includes(domain))throw new Error('Domain is not in this snapshot');
 const at=new Date().toISOString();try{
  const res=await fetch('https://'+domain+'/',{method:'HEAD',redirect:'manual',signal:AbortSignal.timeout(9000),headers:{'User-Agent':'NubiReadOnlyProbe/0.1'}});
  let redirect_host='';try{const loc=res.headers.get('location');if(loc)redirect_host=new URL(loc,res.url).hostname;}catch{}
  await res.body?.cancel();return {domain,http_status:res.status,redirect_host,checked_at:at,method:'HEAD',meaning:'HTTP response only; content and integration are not verified'};
 }catch(e){return {domain,http_status:null,checked_at:at,method:'HEAD',error:e.cause?.code||e.name||'request failed',meaning:'HTTP response unavailable; integration is not verified'};}
}

// Bounded public-page discovery. Never follows cross-site redirects or returns page bodies.
export async function preview(domain){
 if(!Object.values(rankings).flat().includes(domain))throw new Error('Domain is not in this snapshot');
 const hide=new Set(['missav123.com','yasyadong02.tv','av19t.com','kissjav.li','avsee.is','xvideos.com','pornhub.com']);
 const at=new Date().toISOString(),allowed=new Set([domain,'www.'+domain,'m.'+domain]);let target='https://'+domain+'/';
 try{
  for(let i=0;i<3;i++){
   const res=await fetch(target,{redirect:'manual',signal:AbortSignal.timeout(10000),headers:{'User-Agent':'Mozilla/5.0 (compatible; NubiPublicPreview/0.1)'}});
   if(res.status>=300&&res.status<400){const loc=res.headers.get('location');await res.body?.cancel();if(!loc)return {domain,http_status:res.status,checked_at:at};const next=new URL(loc,target);if(next.protocol!=='https:'||!allowed.has(next.hostname))return {domain,http_status:res.status,redirect_host:next.hostname,checked_at:at,note:'external redirect not followed'};target=next.href;continue;}
   if(!res.ok){await res.body?.cancel();return {domain,http_status:res.status,checked_at:at};}
   if(hide.has(domain)){await res.body?.cancel();return {domain,http_status:res.status,checked_at:at,note:'content excluded from preview'};}
   const type=res.headers.get('content-type')||'';if(!type.includes('html')){await res.body?.cancel();return {domain,http_status:res.status,content_type:type,checked_at:at};}
   const reader=res.body?.getReader();let bytes=0,chunks=[];while(reader&&bytes<262144){const x=await reader.read();if(x.done)break;chunks.push(x.value);bytes+=x.value.length;}await reader?.cancel();let all=new Uint8Array(bytes),offset=0;for(const x of chunks){all.set(x,offset);offset+=x.length;}const html=new TextDecoder().decode(all);
   const decode=s=>s.replace(/&amp;/g,'&').replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/\s+/g,' ').trim();
   const title=decode((html.match(/<title\b[^>]*>([\s\S]*?)<\/title>/i)||[])[1]||'').slice(0,180);const links=[];
   for(const m of html.matchAll(/<a\b[^>]*?href\s*=\s*["']([^"'#]+)["'][^>]*>/gi)){try{const u=new URL(decode(m[1]),target);if(u.protocol==='https:'&&allowed.has(u.hostname)){u.search='';u.hash='';const url=u.origin+u.pathname;if(!links.includes(url))links.push(url);if(links.length>=5)break;}}catch{}}
   return {domain,http_status:res.status,title,links,checked_at:at,method:'GET',note:'public HTML preview; links and title are not feature verification'};
  }
  return {domain,http_status:null,checked_at:at,note:'redirect limit reached'};
 }catch(e){return {domain,http_status:null,checked_at:at,error:e.cause?.code||e.name||'request failed'};}
}
