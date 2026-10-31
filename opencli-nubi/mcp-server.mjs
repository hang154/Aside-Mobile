#!/usr/bin/env node
// Local stdio MCP adapter for two explicitly read-only OpenCLI portal commands.
import readline from 'node:readline';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
const execute = promisify(execFile);
const opencli = process.env.OPENCLI_BIN;
const endpoint = process.env.OPENCLI_CDP_ENDPOINT;
const handlers = { nubi_portal_status: 'portal-status', nubi_academic_menu: 'academic-menu', nubi_naver_map_status:'naver-map-status', nubi_kakao_map_status:'kakao-map-status', nubi_korail_status:'korail-status' };
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
    {name:'nubi_korail_status',description:'Inspect the open Korail ticket page',inputSchema:{type:'object',properties:{},additionalProperties:false}}
  ]});
  if (method !== 'tools/call') return fail(id,-32601,'Method not found');
  const command=Object.hasOwn(handlers,params.name) ? handlers[params.name] : undefined;
  if (!command || Object.keys(params.arguments || {}).length) return fail(id,-32602,'Unknown tool or arguments');
  try {
    const url=new URL(endpoint || '');
    if (!opencli || url.protocol !== 'http:' || !['127.0.0.1','localhost','[::1]'].includes(url.hostname)) throw new Error('Configure OPENCLI_BIN and a localhost OPENCLI_CDP_ENDPOINT');
    const {stdout}=await execute(process.execPath,[opencli,'nubi-unist',command,'-f','json'],{timeout:20000,maxBuffer:100000,env:process.env});
    const result=JSON.parse(stdout);
    if (!result.ok) throw new Error('OpenCLI command failed');
    return reply(id,{content:[{type:'text',text:JSON.stringify(result.data)}],isError:false});
  } catch(e) { return reply(id,{content:[{type:'text',text:'Portal request failed: '+e.message}],isError:true}); }
}
readline.createInterface({input:process.stdin,crlfDelay:Infinity}).on('line',line=>{try{handle(JSON.parse(line)).catch(()=>{});}catch{fail(null,-32700,'Parse error');}});
