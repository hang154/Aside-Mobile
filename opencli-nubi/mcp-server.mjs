#!/usr/bin/env node
// Local stdio MCP adapter for two explicitly read-only OpenCLI portal commands.
import readline from 'node:readline';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
const execute = promisify(execFile);
const opencli = process.env.OPENCLI_BIN;
const endpoint = process.env.OPENCLI_CDP_ENDPOINT;
const handlers = { nubi_portal_status: 'portal-status', nubi_academic_menu: 'academic-menu', nubi_naver_map_status:'naver-map-status', nubi_kakao_map_status:'kakao-map-status', nubi_korail_status:'korail-status', nubi_naver_places:'naver-places', nubi_unist_calendar:'unist-calendar', nubi_korail_options:'korail-options', nubi_papers_search:'papers-search', nubi_naver_search:'naver-search', nubi_kakao_search:'kakao-search', nubi_kakao_places:'kakao-places', nubi_weather_forecast:'weather-forecast' };
const reply = (id, result) => process.stdout.write(JSON.stringify({jsonrpc:'2.0',id,result})+'\n');
const fail = (id, code, message) => process.stdout.write(JSON.stringify({jsonrpc:'2.0',id,error:{code,message}})+'\n');
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
    {name:'nubi_weather_forecast',description:'Read up to three days of weather forecast from wttr.in',inputSchema:{type:'object',properties:{location:{type:'string',minLength:1,maxLength:100}},required:['location'],additionalProperties:false}}
  ]});
  if (method !== 'tools/call') return fail(id,-32601,'Method not found');
  const command=Object.hasOwn(handlers,params.name) ? handlers[params.name] : undefined;
  const args=params.arguments || {};
  if (!command || typeof args !== 'object' || Array.isArray(args)) return fail(id,-32602,'Unknown tool or arguments');
  if (['papers-search','naver-search','kakao-search'].includes(command)) {
    if (Object.keys(args).length!==1 || typeof args.query!=='string' || !args.query.trim() || args.query.length>100 || args.query.trim().startsWith('-')) return fail(id,-32602,'Provide a query of 1–100 characters');
  } else if(command==='weather-forecast') {
    if(Object.keys(args).length!==1 || typeof args.location!=='string' || !args.location.trim() || args.location.length>100 || args.location.trim().startsWith('-')) return fail(id,-32602,'Provide a location of 1–100 characters');
  } else if (Object.keys(args).length) return fail(id,-32602,'This tool takes no arguments');
  try {
    if (!opencli) throw new Error('Configure OPENCLI_BIN');
    if (!['unist-calendar','papers-search','weather-forecast'].includes(command)) {
      const url=new URL(endpoint || '');
      if (url.protocol !== 'http:' || !['127.0.0.1','localhost','[::1]'].includes(url.hostname)) throw new Error('Configure a localhost OPENCLI_CDP_ENDPOINT');
    }
    const argv=command === 'papers-search' ? [opencli,'arxiv','search',args.query.trim(),'--limit','10','-f','json'] : command === 'weather-forecast' ? [opencli,'wttr','forecast',args.location.trim(),'--days','3','-f','json'] : ['naver-search','kakao-search'].includes(command) ? [opencli,'nubi-unist',command,args.query.trim(),'-f','json'] : [opencli,'nubi-unist',command,'-f','json'];
    const {stdout}=await execute(process.execPath,argv,{timeout:45000,maxBuffer:100000,env:process.env});
    const result=JSON.parse(stdout);
    if (!result.ok) throw new Error('OpenCLI command failed');
    const data=command==='weather-forecast' ? {requested_location:args.location.trim(),source:'wttr.in',checked_at:new Date().toISOString(),forecast:result.data} : result.data;
    return reply(id,{content:[{type:'text',text:JSON.stringify(data)}],isError:false});
  } catch(e) { return reply(id,{content:[{type:'text',text:'Portal request failed: '+e.message}],isError:true}); }
}
readline.createInterface({input:process.stdin,crlfDelay:Infinity}).on('line',line=>{try{handle(JSON.parse(line)).catch(()=>{});}catch{fail(null,-32700,'Parse error');}});
