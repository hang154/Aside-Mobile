(function(root){
'use strict';
function mealPlan(menu,day,classes,walk,opening,ticket){
 if(!/^\d{4}-\d{2}-\d{2}$/.test(day)||!Number.isInteger(walk)||walk<1||walk>60||!/^\d{2}:\d{2}$/.test(opening))throw Error('날짜·이동시간·판매 시작 시각을 확인해 주세요');
 const base=t=>Date.parse(day+'T'+t+':00+09:00');
 const intervals=classes.map(c=>{const a=Date.parse(c.start),b=Date.parse(c.end);if(!Number.isFinite(a)||!Number.isFinite(b)||a>=b||!/[Z+]/.test(c.start.slice(10)))throw Error('시간대가 포함된 시간표 필요');return[a,b];});
 const protein=/고기|닭|돼지|소고기|쇠고기|치킨|생선|고등어|삼치|연어|두부|계란|달걀|불고기|돈까스|돈가스|수육|보쌈|제육|오리|참치|갈비/;
 const special=/보쌈|수육|특식|스테이크|삼계탕|장어/;
 const options=[];
 for(const cafe of menu.data||[])for(const meal of cafe.meals||[]){
  if(meal.date!==day||meal.timeType!=='LUNCH'||meal.isClosed)continue;
  const names=(meal.menusByType||[]).flatMap(t=>(t.sections||[]).flatMap(s=>(s.menus||[]).map(m=>m.ko))).filter(Boolean);
  const p=names.filter(n=>protein.test(n)),s=names.filter(n=>special.test(n));if(p.length||s.length)options.push({cafeteria:cafe.cafeteria,names,protein:p,special:s,score:p.length+10*s.length});
 }
 options.sort((a,b)=>b.score-a.score);let slot=null;
 for(let a=base('11:40');a>=base(opening);a-=300000){const leave=a-walk*60000,back=a+(walk+10)*60000;if(!intervals.some(([s,e])=>leave<e&&s<back)){slot={leave_at:new Date(leave).toISOString(),arrive_at:new Date(a).toISOString(),return_at:new Date(back).toISOString()};break;}}
 return {state:!options.length?'no_matching_lunch':slot?'planned':'no_prepeak_slot',options,slot,source:menu.source,provider_updated_at:menu.lastUpdated,action:ticket?'식당에서 식권 미리 구매':'식당에 일찍 도착',protein_grams:null,queue_measured:false,ticket_purchase_executed:false};
}
function seedTrip(departure){if(!/^\d{2}:\d{2}$/.test(departure))throw Error('공개 조회 출발 시각 필요');return {simulation:true,departure_hm:departure,index:0,delay_minutes:0,ticket:{id:'TEST-ORIGINAL',train:'TEST-KTX-A',state:'CONFIRMED'},changes:[],clock_minutes:0};}
function advance(s,delay=0){if(!s.simulation||!Number.isInteger(delay)||delay<0||delay>120)throw Error('테스트 상태/지연 오류');const n=JSON.parse(JSON.stringify(s));n.index=Math.min(4,n.index+1);n.delay_minutes+=delay;n.clock_minutes=n.index*5+n.delay_minutes;const arrival=20+n.delay_minutes,boarding=5;
 // All trains and seat inventory belong to the local fake booking system.
 const trains=[{id:'TEST-KTX-A',minute:30,seats:1},{id:'TEST-KTX-B',minute:50,seats:1},{id:'TEST-KTX-C',minute:70,seats:1}];
 const old=trains.find(t=>t.id===n.ticket.train);if(old&&old.minute<arrival+boarding){const next=trains.find(t=>t.minute>=Math.max(arrival+boarding,n.clock_minutes)&&t.seats>0);if(!next){n.error='대체편 없음 · 기존 테스트 표 유지';return n;}if(next.id!==old.id){const key=old.id+'>'+next.id;if(!n.changes.some(c=>c.key===key)){n.changes.push({key,old:old.id,next:next.id,old_state:'CANCELLED_TEST',new_state:'CONFIRMED_TEST',test_fee:0});n.ticket={id:'TEST-REBOOK-'+n.changes.length,train:next.id,state:'CONFIRMED'};}}}
 n.station_eta_minutes=arrival;n.real_payment=false;n.real_reservation=false;return n;
}
const api={mealPlan,seedTrip,advance};if(typeof module!=='undefined')module.exports=api;root.ScenarioEngine=api;
})(typeof window!=='undefined'?window:globalThis);
