#!/usr/bin/env node
// Local stdio MCP adapter for two explicitly read-only OpenCLI portal commands.
import readline from 'node:readline';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { promises as fs } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join } from 'node:path';
import { randomUUID } from 'node:crypto';
const execute = promisify(execFile);
const opencli = process.env.OPENCLI_BIN;
const endpoint = process.env.OPENCLI_CDP_ENDPOINT;
const handlers = { nubi_portal_status: 'portal-status', nubi_academic_menu: 'academic-menu', nubi_naver_map_status:'naver-map-status', nubi_kakao_map_status:'kakao-map-status', nubi_korail_status:'korail-status', nubi_naver_places:'naver-places', nubi_unist_calendar:'unist-calendar', nubi_korail_options:'korail-options', nubi_papers_search:'papers-search', nubi_naver_search:'naver-search', nubi_kakao_search:'kakao-search', nubi_kakao_places:'kakao-places', nubi_weather_forecast:'weather-forecast', nubi_jobs_list:'jobs-list', nubi_jobs_detail:'jobs-detail', nubi_dining_list:'dining-list', nubi_clubs_list:'clubs-list', nubi_shopping_search:'shopping-search', nubi_shopping_select:'shopping-select', nubi_saramin_search:'saramin-search', nubi_saramin_detail:'saramin-detail', nubi_wanted_search:'wanted-search', nubi_wanted_detail:'wanted-detail' };
const reply = (id, result) => process.stdout.write(JSON.stringify({jsonrpc:'2.0',id,result})+'\n');
const fail = (id, code, message) => process.stdout.write(JSON.stringify({jsonrpc:'2.0',id,error:{code,message}})+'\n');
const choicesFile=process.env.NUBI_CHOICES_FILE || join(homedir(),'.local','share','nubi-mcp','choices.json');
let choiceQueue=Promise.resolve();
async function choiceOperation(action,args) {
  const next=choiceQueue.then(async()=>{
    let rows;try{rows=JSON.parse(await fs.readFile(choicesFile,'utf8'));if(!Array.isArray(rows))throw new Error('Invalid saved choices');}catch(e){if(e.code==='ENOENT')rows=[];else throw e;}
    if(action==='list')return rows;
    const url=new URL(args.url);if(url.protocol!=='https:' || url.username || url.password || !['aigs.unist.ac.kr','www.unist.ac.kr','cse.unist.ac.kr','map.naver.com','m.map.kakao.com','msearch.shopping.naver.com','www.saramin.co.kr','www.wanted.co.kr','arxiv.org'].includes(url.hostname))throw new Error('Source URL is not supported');
    const item={id:randomUUID(),kind:args.kind,title:args.title.trim(),url:url.href,saved_at:new Date().toISOString()};rows.unshift(item);
    if(rows.length>500)throw new Error('Saved choice limit reached');
    await fs.mkdir(dirname(choicesFile),{recursive:true,mode:0o700});const temp=choicesFile+'.'+randomUUID()+'.tmp';
    try {await fs.writeFile(temp,JSON.stringify(rows,null,2),{mode:0o600,flag:'wx'});await fs.rename(temp,choicesFile);} finally {await fs.rm(temp,{force:true});}
    return item;
  });choiceQueue=next.catch(()=>{});return next;
}
async function handle(message) {
  const {id,method,params={}} = message;
  if (id === undefined) return;
  if (method === 'initialize') return reply(id, {protocolVersion:'2024-11-05',capabilities:{tools:{}},serverInfo:{name:'nubi-unist-local',version:'0.1.0'}});
  if (method === 'ping') return reply(id, {});
  if (method === 'tools/list') return reply(id,{tools:[
    {name:'nubi_portal_status',description:'Read the currently open UNIST portal login status',inputSchema:{type:'object',properties:{},additionalProperties:false}},
    {name:'nubi_academic_menu',description:'Read currently visible UNIST academic menu labels',inputSchema:{type:'object',properties:{},additionalProperties:false}},
    {name:'nubi_naver_map_status',description:'Inspect the open Naver Map page',inputSchema:{type:'object',properties:{},additionalProperties:false}},
    {name:'nubi_kakao_map_status',description:'Inspect the open Kakao Map page',inputSchema:{type:'object',properties:{},additionalProperties:false}},
    {name:'nubi_korail_status',description:'Inspect the open Korail ticket page',inputSchema:{type:'object',properties:{},additionalProperties:false}},
    {name:'nubi_naver_places',description:'Read the visible Naver Map search result choices',inputSchema:{type:'object',properties:{},additionalProperties:false}},
    {name:'nubi_unist_calendar',description:'Read the next 60 days of the official UNIST academic calendar',inputSchema:{type:'object',properties:{},additionalProperties:false}},
    {name:'nubi_korail_options',description:'Read visible Korail train choices or report access restrictions',inputSchema:{type:'object',properties:{},additionalProperties:false}},
    {name:'nubi_papers_search',description:'Search arXiv papers by topic, returning titles, authors, dates and sources',inputSchema:{type:'object',properties:{query:{type:'string',minLength:1,maxLength:100}},required:['query'],additionalProperties:false}},
    {name:'nubi_naver_search',description:'Search Naver Map in Nubi and return visible place choices',inputSchema:{type:'object',properties:{query:{type:'string',minLength:1,maxLength:100}},required:['query'],additionalProperties:false}},
    {name:'nubi_kakao_search',description:'Search Kakao Map in Nubi and return visible place choices',inputSchema:{type:'object',properties:{query:{type:'string',minLength:1,maxLength:100}},required:['query'],additionalProperties:false}},
    {name:'nubi_kakao_places',description:'Read the visible Kakao Map search choices',inputSchema:{type:'object',properties:{},additionalProperties:false}},
    {name:'nubi_weather_forecast',description:'Read up to three days of weather forecast from wttr.in',inputSchema:{type:'object',properties:{location:{type:'string',minLength:1,maxLength:100}},required:['location'],additionalProperties:false}},
    {name:'nubi_jobs_list',description:'Read UNIST AI graduate school employment posts',inputSchema:{type:'object',properties:{},additionalProperties:false}},
    {name:'nubi_jobs_detail',description:'Read the selected current job post after verifying index and title',inputSchema:{type:'object',properties:{index:{type:'integer',minimum:1,maximum:20},title:{type:'string',minLength:1,maxLength:300}},required:['index','title'],additionalProperties:false}},
    {name:'nubi_dining_list',description:'Read official UNIST cafeteria locations and opening hours, not daily menus',inputSchema:{type:'object',properties:{},additionalProperties:false}},
    {name:'nubi_clubs_list',description:'Read UNIST computer science department club information',inputSchema:{type:'object',properties:{},additionalProperties:false}},
    {name:'nubi_wanted_search',description:'Search Wanted job postings and related recommendations',inputSchema:{type:'object',properties:{query:{type:'string',minLength:1,maxLength:100}},required:['query'],additionalProperties:false}},
    {name:'nubi_wanted_detail',description:'Read a selected Wanted posting by id and exact title',inputSchema:{type:'object',properties:{id:{type:'string',pattern:'^[0-9]{1,12}$'},title:{type:'string',minLength:1,maxLength:300}},required:['id','title'],additionalProperties:false}},
    {name:'nubi_saramin_search',description:'Search Saramin job postings',inputSchema:{type:'object',properties:{query:{type:'string',minLength:1,maxLength:100}},required:['query'],additionalProperties:false}},
    {name:'nubi_saramin_detail',description:'Read a selected Saramin posting by id and exact title',inputSchema:{type:'object',properties:{id:{type:'string',pattern:'^[0-9]{1,12}$'},title:{type:'string',minLength:1,maxLength:300}},required:['id','title'],additionalProperties:false}},
    {name:'nubi_shopping_search',description:'Search visible Naver price comparison product choices',inputSchema:{type:'object',properties:{query:{type:'string',minLength:1,maxLength:100}},required:['query'],additionalProperties:false}},
    {name:'nubi_shopping_select',description:'Read a selected visible product after verifying index and name',inputSchema:{type:'object',properties:{index:{type:'integer',minimum:1,maximum:20},title:{type:'string',minLength:1,maxLength:300}},required:['index','title'],additionalProperties:false}},
    {name:'nubi_save_choice',description:'Save a user-selected result locally on this computer',inputSchema:{type:'object',properties:{kind:{type:'string',enum:['job','dining','club','place','paper','product']},title:{type:'string',minLength:1,maxLength:200},url:{type:'string',maxLength:2000}},required:['kind','title','url'],additionalProperties:false}},
    {name:'nubi_saved_choices',description:'List the choices saved locally on this computer',inputSchema:{type:'object',properties:{},additionalProperties:false}}
  ]});
  if (method !== 'tools/call') return fail(id,-32601,'Method not found');
  if(params.name==='nubi_save_choice'||params.name==='nubi_saved_choices') {
    const a=params.arguments||{};
    if(typeof a!=='object'||Array.isArray(a))return fail(id,-32602,'Invalid arguments');
    if(params.name==='nubi_saved_choices' && Object.keys(a).length)return fail(id,-32602,'No arguments expected');
    if(params.name==='nubi_save_choice' && (Object.keys(a).length!==3 || !['job','dining','club','place','paper','product'].includes(a.kind) || typeof a.title!=='string' || !a.title.trim() || a.title.length>200 || typeof a.url!=='string' || a.url.length>2000))return fail(id,-32602,'Provide kind, title and source URL');
    try {const data=await choiceOperation(params.name==='nubi_save_choice'?'save':'list',a);return reply(id,{content:[{type:'text',text:JSON.stringify(data)}],isError:false});}catch(e){return reply(id,{content:[{type:'text',text:'Save failed: '+e.message}],isError:true});}
  }
  const command=Object.hasOwn(handlers,params.name) ? handlers[params.name] : undefined;
  const args=params.arguments || {};
  if (!command || typeof args !== 'object' || Array.isArray(args)) return fail(id,-32602,'Unknown tool or arguments');
  if (['papers-search','naver-search','kakao-search','shopping-search','saramin-search','wanted-search'].includes(command)) {
    if (Object.keys(args).length!==1 || typeof args.query!=='string' || !args.query.trim() || args.query.length>100 || args.query.trim().startsWith('-')) return fail(id,-32602,'Provide a query of 1–100 characters');
  } else if(['saramin-detail','wanted-detail'].includes(command)) {
    if(Object.keys(args).length!==2 || typeof args.id!=='string' || !/^[0-9]{1,12}$/.test(args.id) || typeof args.title!=='string' || !args.title.trim() || args.title.length>300 || args.title.startsWith('-')) return fail(id,-32602,'Provide a valid job id and exact title');
  } else if(['jobs-detail','shopping-select'].includes(command)) {
    if(Object.keys(args).length!==2 || !Number.isInteger(args.index) || args.index<1 || args.index>20 || typeof args.title!=='string' || !args.title.trim() || args.title.length>300 || args.title.startsWith('-')) return fail(id,-32602,'Provide index and exact title from the current list');
  } else if(command==='weather-forecast') {
    if(Object.keys(args).length!==1 || typeof args.location!=='string' || !args.location.trim() || args.location.length>100 || args.location.trim().startsWith('-')) return fail(id,-32602,'Provide a location of 1–100 characters');
  } else if (Object.keys(args).length) return fail(id,-32602,'This tool takes no arguments');
  try {
    if (!opencli) throw new Error('Configure OPENCLI_BIN');
    if (!['unist-calendar','papers-search','weather-forecast','jobs-list','jobs-detail','dining-list','clubs-list'].includes(command)) {
      const url=new URL(endpoint || '');
      if (url.protocol !== 'http:' || !['127.0.0.1','localhost','[::1]'].includes(url.hostname)) throw new Error('Configure a localhost OPENCLI_CDP_ENDPOINT');
    }
    const argv=['saramin-detail','wanted-detail'].includes(command) ? [opencli,'nubi-unist',command,args.id,args.title,'-f','json'] : ['jobs-detail','shopping-select'].includes(command) ? [opencli,'nubi-unist',command,String(args.index),args.title,'-f','json'] : command === 'papers-search' ? [opencli,'arxiv','search',args.query.trim(),'--limit','10','-f','json'] : command === 'weather-forecast' ? [opencli,'wttr','forecast',args.location.trim(),'--days','3','-f','json'] : ['naver-search','kakao-search','shopping-search','saramin-search','wanted-search'].includes(command) ? [opencli,'nubi-unist',command,args.query.trim(),'-f','json'] : [opencli,'nubi-unist',command,'-f','json'];
    const {stdout}=await execute(process.execPath,argv,{timeout:45000,maxBuffer:100000,env:process.env});
    const result=JSON.parse(stdout);
    if (!result.ok) throw new Error('OpenCLI command failed');
    const data=command==='weather-forecast' ? {requested_location:args.location.trim(),source:'wttr.in',checked_at:new Date().toISOString(),forecast:result.data} : result.data;
    return reply(id,{content:[{type:'text',text:JSON.stringify(data)}],isError:false});
  } catch(e) { return reply(id,{content:[{type:'text',text:'Portal request failed: '+e.message}],isError:true}); }
}
readline.createInterface({input:process.stdin,crlfDelay:Infinity}).on('line',line=>{try{handle(JSON.parse(line)).catch(()=>{});}catch{fail(null,-32700,'Parse error');}});
