/*
 NUBI Interactive Demo — standalone, readable vanilla JavaScript.
 Real app services are NOT connected. Contents, prices, calendars and browsing traces are labeled demonstrations.
 OSS design credit: Lucide (ISC icons), Swiper (MIT touch slider, optional CDN),
 Animata Card Stack (MIT interaction concept), Kokonut UI Smooth Drawer + AI Loading (MIT interaction concept),
 Magic UI Bento Grid (MIT layout concept). See reports/README.md for original links and notices.
*/
'use strict';
const $ = (s, root = document) => root.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const money = n => Number(n).toLocaleString('ko-KR') + '원';
const formatDate = d => new Intl.DateTimeFormat('ko-KR', {month:'long',day:'numeric',weekday:'long'}).format(d);
const LUCIDE = {
 menu:'<path d="M4 6h16M4 12h16M4 18h16"/>',
 'arrow-left':'<path d="m12 19-7-7 7-7M5 12h14"/>',
 'arrow-right':'<path d="M5 12h14m-7-7 7 7-7 7"/>',
 'arrow-up':'<path d="m12 19 0-14M5 12l7-7 7 7"/>',
 'chevron-right':'<path d="m9 18 6-6-6-6"/>',
 'chevron-left':'<path d="m15 18-6-6 6-6"/>',
 'chevron-down':'<path d="m6 9 6 6 6-6"/>',
 x:'<path d="M18 6 6 18M6 6l12 12"/>',
 plus:'<path d="M12 5v14M5 12h14"/>',
 minus:'<path d="M5 12h14"/>',
 check:'<path d="m5 12 4 4L19 6"/>',
 'check-check':'<path d="m18 6-7 7-3-3M22 10l-7 7-3-3M2 12l4 4 4-4"/>',
 home:'<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z"/>',
 target:'<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
 compass:'<circle cx="12" cy="12" r="10"/><path d="m16.2 7.8-2.8 5.6-5.6 2.8 2.8-5.6z"/>',
 user:'<path d="M20 21a8 8 0 0 0-16 0M12 13a5 5 0 1 0 0-10 5 5 0 0 0 0 10"/>',
 users:'<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M16 3.13a4 4 0 0 1 0 7.75M22 21v-2a4 4 0 0 0-3-3.87"/><circle cx="9" cy="7" r="4"/>',
 bell:'<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/>',
 mail:'<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 7L2 7"/>',
 'book-open':'<path d="M12 7v14M3 18V5a2 2 0 0 1 2-2h2a5 5 0 0 1 5 5 5 5 0 0 1 5-5h2a2 2 0 0 1 2 2v13a2 2 0 0 0-2-2h-2a5 5 0 0 0-5 5 5 5 0 0 0-5-5H5a2 2 0 0 0-2 2"/>',
 calendar:'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/>',
 'calendar-check':'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18m-12 6 2 2 4-4"/>',
 'file-text':'<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M8 13h8M8 17h8"/>',
 'graduation-cap':'<path d="m2 10 10-5 10 5-10 5zM6 12v5c4 3 8 3 12 0v-5M22 10v6"/>',
 'search':'<circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>',
 'sparkles':'<path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8zM5 19l.5 1.5L7 21l-1.5.5L5 23l-.5-1.5L3 21l1.5-.5zM19 3l.5 1.5L21 5l-1.5.5L19 7l-.5-1.5L17 5l1.5-.5z"/>',
 'wand':'<path d="M15 4V2m0 10v-2m8-3h-2M9 7H7m13.5-4.5L19 4m-8 8L3 20l1 1 8-8M3 4l1.5 1.5M5 2l.5 1.5"/>',
 'shopping-bag':'<path d="M5 7h14l1 14H4L5 7zM9 9V6a3 3 0 0 1 6 0v3"/>',
 'shopping-cart':'<circle cx="9" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M1 2h2l2.7 12.6a2 2 0 0 0 2 1.4h12a2 2 0 0 0 2-1.6L23 6H4"/>',
 heart:'<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 1 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8z"/>',
 'message-circle':'<path d="M21 11.5a8.5 8.5 0 0 1-8.5 8.5 9 9 0 0 1-4.3-1.1L3 21l1.7-4.8a8.5 8.5 0 1 1 16.3-4.7z"/>',
 'message-square':'<path d="M21 11.5a8.5 8.5 0 0 1-8.5 8.5 9 9 0 0 1-4.3-1.1L3 21l1.7-4.8a8.5 8.5 0 1 1 16.3-4.7z"/>',
 'send':'<path d="m22 2-7 20-4-9-9-4zM22 2 11 13"/>',
 mic:'<rect x="9" y="2" width="6" height="13" rx="3"/><path d="M5 10a7 7 0 0 0 14 0M12 17v5M8 22h8"/>',
 'share-2':'<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.5 13.5 7 4m-7-7 7-4"/>',
 'external-link':'<path d="M15 3h6v6m0-6-10 10M21 13v7a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h7"/>',
 'more-horizontal':'<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
 settings:'<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1-2.2 2.2-.1-.1a1.6 1.6 0 0 0-1.8-.3 1.6 1.6 0 0 0-1 1.5V21h-3v-.8a1.6 1.6 0 0 0-1-1.5 1.6 1.6 0 0 0-1.8.3l-.1.1-2.2-2.2.1-.1a1.6 1.6 0 0 0 .3-1.8 1.6 1.6 0 0 0-1.5-1H4v-3h.8a1.6 1.6 0 0 0 1.5-1 1.6 1.6 0 0 0-.3-1.8l-.1-.1 2.2-2.2.1.1a1.6 1.6 0 0 0 1.8.3 1.6 1.6 0 0 0 1-1.5V4h3v.8a1.6 1.6 0 0 0 1 1.5 1.6 1.6 0 0 0 1.8-.3l.1-.1 2.2 2.2-.1.1a1.6 1.6 0 0 0-.3 1.8 1.6 1.6 0 0 0 1.5 1h.8v3h-.8a1.6 1.6 0 0 0-1.5 1z"/>',
 clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 play:'<path d="m8 5 12 7-12 7z"/>',
 pause:'<path d="M7 4v16M17 4v16"/>',
 'circle-play':'<circle cx="12" cy="12" r="10"/><path d="m10 8 6 4-6 4z"/>',
 bookmark:'<path d="M5 3h14v19l-7-5-7 5z"/>',
 'map-pin':'<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
 plane:'<path d="M17 21v-8l-5-3V3a2 2 0 0 0-4 0v7l-5 3v8l7-2z"/>',
 'briefcase':'<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M7 7V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v2M2 12h20"/>',
 'dumbbell':'<path d="m6.5 6.5 11 11M3 8.5l5.5-5.5M2 12l10-10M16 22l6-6M12.5 17.5l5.5-5.5"/>',
 'info':'<circle cx="12" cy="12" r="10"/><path d="M12 11v6m0-10h.01"/>',
 'help-circle':'<circle cx="12" cy="12" r="10"/><path d="M9 9a3 3 0 1 1 5 2c-2 1-2 2-2 3m0 4h.01"/>',
 'shield-check':'<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10zM9 12l2 2 4-4"/>',
 link:'<path d="M10 13a5 5 0 0 0 7 .5l3-3a5 5 0 0 0-7-7l-1.7 1.7M14 11a5 5 0 0 0-7-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/>',
 'list-checks':'<path d="m3 7 2 2 4-4M13 7h8M3 17l2 2 4-4M13 17h8"/>',
 'chart-no-axes':'<path d="M3 3v18h18M7 16l4-5 4 2 4-7"/>',
 repeat:'<path d="M17 2l4 4-4 4M3 11V9a3 3 0 0 1 3-3h15M7 22l-4-4 4-4M21 13v2a3 3 0 0 1-3 3H3"/>',
 'folder-open':'<path d="M2 7a2 2 0 0 1 2-2h5l2 2h9a2 2 0 0 1 2 2v10H2zM2 11h20"/>',
 'menu-square':'<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M8 9h8M8 13h8M8 17h5"/>',
 'refresh-cw':'<path d="M20 11a8 8 0 1 0-2 6m2 1v-6h-6"/>',
 'wallet':'<rect x="2" y="5" width="20" height="16" rx="2"/><path d="M16 14h6M4 5V3h16"/>',
 'copy':'<rect x="8" y="8" width="13" height="13" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"/>',
 'wifi':'<path d="M2 8.5a16 16 0 0 1 20 0M5 12a11 11 0 0 1 14 0m-11 3.5a6 6 0 0 1 8 0M12 19h.01"/>',
 'battery':'<rect x="2" y="6" width="18" height="12" rx="2"/><path d="M22 10v4M5 9h12v6H5z" fill="currentColor" stroke="none"/>',
 'signal':'<path d="M3 20v-4m5 4V12m5 8V8m5 12V4"/>',
 'sliders-horizontal':'<path d="M4 7h16M4 17h16M8 4v6M16 14v6"/>',
 'square-check':'<rect x="3" y="3" width="18" height="18" rx="3"/><path d="m7 12 3 3 7-7"/>',
 'circle-alert':'<circle cx="12" cy="12" r="10"/><path d="M12 7v6m0 4h.01"/>',
 'check-circle':'<circle cx="12" cy="12" r="10"/><path d="m8 12 3 3 5-6"/>',
 'arrow-up-right':'<path d="M7 17 17 7M7 7h10v10"/>',
 'panel-left':'<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18"/>',
 'monitor-play':'<rect x="2" y="3" width="20" height="15" rx="2"/><path d="M8 21h8M12 18v3m-3-12 6 3-6 3z"/>',
 'layers':'<path d="m12 2 9 5-9 5-9-5zM3 12l9 5 9-5M3 17l9 5 9-5"/>',
};
const icon = (name,size=20)=>`<svg class="icon" width="${size}" height="${size}" style="width:${size}px;height:${size}px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">${LUCIDE[name]||LUCIDE.sparkles}</svg>`;
const portrait = (n, cls='', alt='누비 캐릭터')=>`<img loading="lazy" class="${cls}" src="${NUBI_IMAGES[n]||NUBI_IMAGES[1]}" alt="${esc(alt)}">`;

const GOALS = {
 campus:{name:'누비',want:'대학생활을 편하게',desc:'학사·메일·동아리까지, 내 일상을 누비가 챙길게.',img:1,bg:'pastel-mint',emoji:'🌱',prompts:['학교 공지 중 놓친 거 찾아줘','교수님께 메일 초안 써줘','동아리 일정 겹치는지 확인해줘']},
 romance:{name:'로맨티',want:'연애하고 싶어',desc:'첫인상부터 데이트 준비까지 나랑 같이 해보자!',img:6,bg:'pastel-pink',emoji:'💗',prompts:['이번 주말 데이트 코스 찾아줘','소개팅에 입을 옷 골라줘','학교 축제 일정 찾아봐줘']},
 health:{name:'건강이',want:'몸 만들고 싶어',desc:'내 체형과 목표에 딱 맞는 운동 친구.',img:2,bg:'pastel-mint',emoji:'💪',prompts:['프리웨이트 루틴 찾아줘','프로틴 제품 가격 비교해줘','운동 일정 매주 잡아줘']},
 grade:{name:'학점이',want:'학점 잘 받고 싶어',desc:'시험·과제·강의 공지를 놓치지 않게!',img:9,bg:'pastel-lilac',emoji:'📚',prompts:['이번 주 과제 정리해줘','시험 계획 같이 짜줘','논문 PDF 찾아줘']},
 lab:{name:'랩비',want:'좋은 랩실 가고 싶어',desc:'논문 탐색부터 교수님께 보내는 메일까지.',img:5,bg:'pastel-blue',emoji:'🔬',prompts:['관심 분야 랩실 찾아줘','교수님께 컨택 메일 써줘','최근 논문부터 정리해줘']},
 career:{name:'커리어리',want:'취업 준비 잘하고 싶어',desc:'지원 공고 탐색과 자기소개서 준비를 함께.',img:4,bg:'pastel-yellow',emoji:'💼',prompts:['이번 주 인턴 공고 찾아줘','지원서 초안 써줘','면접 질문 정리해줘']},
 travel:{name:'여행이',want:'여행 떠나고 싶어',desc:'KTX부터 숙소까지 대신 비교해줄게.',img:8,bg:'pastel-blue',emoji:'✈️',prompts:['다음 주 KTX 시간 찾아줘','2박 3일 여행 계획 짜줘','여행 준비물 비교해줘']},
 shopping:{name:'쇼핑이',want:'필요한 거 잘 사고 싶어',desc:'여러 쇼핑몰을 보고 내가 고를 수 있게.',img:7,bg:'pastel-peach',emoji:'🛍️',prompts:['요즘 가성비 좋은 제품 찾아줘','최저가 비교해줘','내 장바구니 정리해줘']},
 quant:{name:'퀀티',want:'퀀트 공부하고 싶어',desc:'학술지·데이터·코딩 자료 탐색을 도와줄게.',img:5,bg:'pastel-lilac',emoji:'📈',prompts:['최신 퀀트 논문 찾아줘','데이터 가격 비교해줘','연구 루틴 만들어줘']},
};
const GOAL_IDS=['romance','health','grade','lab','career','travel','shopping','quant'];
const AUTO_LIBRARY={
 campus:[['campus-notice','학사 공지 매일 요약','포털·블랙보드에서 해당 공지를 찾아 정리','book-open'],['campus-mail','교수님 메일 초안','강의 문의·결석 연락을 미리 작성','mail'],['campus-meeting','동아리 일정 충돌 찾기','친구 누비들과 회의 가능 시간 비교','users']],
 romance:[['romance-style','무신사 코디 자동 비교','상황·예산에 맞춰 옷 리뷰와 가격 비교','shopping-bag'],['romance-event','학교 축제·데이트 장소 찾기','근처 행사와 이동 동선을 둘러보기','map-pin'],['romance-gift','선물 후보 찾아보기','꽃·초콜릿·기념일 선물 비교','heart']],
 health:[['health-routine','운동 루틴 자동 탐색','목표에 맞는 운동 영상과 계획 모으기','dumbbell'],['health-protein','프로틴 가격 비교','쇼핑몰별 용량과 가격 비교','shopping-bag'],['health-calendar','주 3회 운동 일정','달력에 운동 루틴 배치','calendar']],
 grade:[['grade-assignments','과제 마감 확인','강의별 공지와 제출 일정 정리','book-open'],['grade-research','논문 PDF 탐색','관련 학술지와 오픈액세스 자료 찾기','file-text'],['grade-timetable','시험 주간 계획','할 일을 일정에 배치','calendar']],
 lab:[['lab-paper','논문 자동 탐색','최근 연구·인용 논문 원문 찾아보기','file-text'],['lab-contact','랩실 지원 메일 초안','교수님께 보낼 연락과 CV 체크','mail'],['lab-list','연구실 비교 노트','연구 주제·자격을 표로 정리','list-checks']],
 career:[['career-intern','인턴 공고 찾아보기','관심 직무의 채용 공고 살피기','briefcase'],['career-resume','지원서 초안 만들기','공고에 맞춰 자기소개서 초안 작성','file-text'],['career-schedule','지원 마감 알림','일정 캘린더에 추가','calendar']],
 travel:[['travel-train','KTX 시간표 비교','출발·도착 시간과 가격 확인','plane'],['travel-plan','여행 동선 자동 계획','장소와 이동 순서 정리','map-pin'],['travel-deals','숙소 가격 비교','조건에 맞는 숙소 후보 모으기','shopping-bag']],
 shopping:[['shopping-compare','여러 쇼핑몰 가격 비교','상품·배송·리뷰 비교','shopping-bag'],['shopping-review','무신사 후기 모으기','착용 후기와 사이즈 정보 정리','message-circle'],['shopping-alert','할인 시점 확인','가격 변화 확인 일정 지정','clock']],
 quant:[['quant-paper','퀀트 논문 모으기','오픈액세스 PDF와 핵심 실험 정리','file-text'],['quant-data','데이터 가격 비교','시장 데이터 제공처와 요금 비교','chart-no-axes'],['quant-scan','관심 종목 정보 탐색','공시·뉴스·리서치 자료 수집','search']],
};
const getAutos = id => (AUTO_LIBRARY[id]||AUTO_LIBRARY.campus).map(([key,name,desc,ic],i)=>({key,name,desc,ic,goal:id,rank:i+1}));
const PRODUCTS=[
 {id:'p1',name:'입문용 단백질 파우더 1kg',brand:'건강이 추천 후보',price:29900,emoji:'🥛',bg:'#e5f6e9',category:'운동',reason:'운동 목표와 이어지는 영양 관리 용품'},
 {id:'p2',name:'프리웨이트 손목 보호대',brand:'운동 보조 용품',price:11900,emoji:'🧤',bg:'#e9ecff',category:'운동',reason:'프리웨이트를 시작할 때 비교할 보호 용품'},
 {id:'p3',name:'베이직 데일리 셔츠',brand:'스타일 후보',price:27900,emoji:'👔',bg:'#e5f4fd',category:'스타일',reason:'소개팅 코디를 위한 깔끔한 기본 아이템'},
 {id:'p4',name:'미니 꽃다발 선물 세트',brand:'기념일 아이템',price:18900,emoji:'💐',bg:'#ffece8',category:'스타일',reason:'데이트·기념일 준비에 관련된 선물'},
 {id:'p5',name:'대학생 포켓 플래너',brand:'공부·일정 관리',price:9800,emoji:'📔',bg:'#fff0d7',category:'공부',reason:'과제와 시험 계획을 관리할 수 있는 용품'},
 {id:'p6',name:'노트북 파우치 14인치',brand:'캠퍼스 소품',price:21900,emoji:'💻',bg:'#f1edff',category:'공부',reason:'랩실·도서관 이동에 필요한 수납 용품'},
 {id:'p7',name:'기내용 여행 백팩',brand:'여행 준비',price:35900,emoji:'🎒',bg:'#eff5e7',category:'여행',reason:'단기 여행에 필요한 수납 용품'},
 {id:'p8',name:'휴대용 충전기 10000mAh',brand:'여행 준비',price:23900,emoji:'🔋',bg:'#e9f5fc',category:'여행',reason:'이동 중 전자기기 충전 준비'},
];
const SAMPLE_POSTS={
 romance:[['Threads','연애 준비는 거창한 계획보다 작은 경험에서 시작해요','축제, 소모임, 동아리처럼 사람을 자연스럽게 만나는 방법에 관한 대화 모음.','💗'],['누비들','소개팅 준비 오토스를 공개했어요','예산을 정하면 셔츠·신발 후보를 비교해주는 자동 탐색 예시.','🪄']],
 health:[['YouTube','운동 초보라면 먼저 익혀야 할 3가지','프리웨이트 자세와 회복 루틴을 다룬 운동 콘텐츠 예시 모음.','🏋️'],['누비들','단백질 가격 비교 오토스 공유','100g당 단가를 살피고 배송비를 비교하는 자동 탐색 예시.','🥛']],
 quant:[['X','퀀트 연구에서 재현 가능한 백테스트가 중요한 이유','학술자료 탐색, 데이터 수집, 코드 검증 과정을 소개하는 예시.','📈'],['누비들','퀀트 논문 수집 오토스 공개','새 논문이 올라오면 주제별로 목록화해주는 사용 예시.','🧪']],
};
function postsFor(goal){return SAMPLE_POSTS[goal]||[['Threads',`${GOALS[goal]?.name||'누비'}와 비슷한 목표를 가진 사람들`,`비슷한 목표를 위해 참고할 만한 정보와 경험을 모은 예시 게시물.`,GOALS[goal]?.emoji||'🌱'],['누비들','나만의 오토스 사용 팁 공유','반복되는 탐색 작업을 설정해두고 시간을 아끼는 방법.', '✨']];}

const STORAGE='nubi_mobile_prototype_v1';
let persisted={};
try{persisted=JSON.parse(localStorage.getItem(STORAGE)||'{}')||{}}catch(_e){}
const st={
 page:'home',goal:'campus',goalTab:'autos',campusTab:'academic',communityTab:'all',discoverTab:'insight',calendarMode:'autos',calendarOffset:0,
 selectedDate:new Date().getDate(),goalsChosen:[],myAutos:[],cart:[],connections:[],messages:{},schedules:[],
 drawer:false,sheet:'',sheetData:'',toast:'',shopCategory:'전체',goalQuery:'',nubiListMode:'recent',
 ...Object.fromEntries(Object.entries(persisted).filter(([k])=>['goal','goalsChosen','myAutos','cart','connections','messages','schedules'].includes(k)))
};
let toastTimer=null,replyTimer=null,browserTick=0,swiperInstance=null;
function persist(){try{localStorage.setItem(STORAGE,JSON.stringify(Object.fromEntries(['goal','goalsChosen','myAutos','cart','connections','messages','schedules'].map(k=>[k,st[k]]))))}catch(_e){}}
function notify(msg){st.toast=msg;render();clearTimeout(toastTimer);toastTimer=setTimeout(()=>{st.toast='';$('.toast')?.remove()},2600)}
function currentGoal(){return GOALS[st.goal]||GOALS.campus}
function setPage(page){st.page=page;st.drawer=false;st.sheet='';render();const el=$('.page-scroll');if(el)el.scrollTop=0}
function openGoal(id){if(!GOALS[id])return;st.goal=id;if(!st.goalsChosen.includes(id)&&id!=='campus')st.goalsChosen.unshift(id);persist();setPage('chat')}
function goWorkspace(tab='autos'){st.goalTab=tab;setPage('workspace')}
function goChat(id=st.goal){if(GOALS[id])st.goal=id;persist();setPage('chat')}
function showSheet(name,data=''){st.sheet=name;st.sheetData=data;render()}
function closeOverlays(){st.drawer=false;st.sheet='';render()}
function status(){const now=new Date();return `<div class="statusbar"><span>${now.getHours()}:${String(now.getMinutes()).padStart(2,'0')}</span><div class="sys">${icon('signal',14)}${icon('wifi',14)}${icon('battery',17)}</div></div>`}
function header({back='',title='',share=false,menu=true}={}){
 if(back)return `<div class="topline"><button class="back" data-action="back" data-page="${back}" aria-label="뒤로 가기">${icon('arrow-left',18)}</button><h2>${esc(title)}</h2><div class="right">${share?`<button class="iconbtn" data-action="sheet" data-sheet="invite" aria-label="초대하기">${icon('share-2',18)}</button>`:''}${menu?`<button class="iconbtn" data-action="drawer" aria-label="전체 메뉴">${icon('menu',18)}</button>`:''}</div></div>`;
 return `<header class="app-header"><button class="iconbtn plain" data-action="drawer" aria-label="사이드 메뉴">${icon('menu',22)}</button><button class="logo" data-action="nav" data-page="home" aria-label="누비 홈">nubi<em>.</em></button><div class="top-actions"><button class="iconbtn" data-action="sheet" data-sheet="notifications" aria-label="알림">${icon('bell',18)}<i class="notif-dot"></i></button><button class="profile-tiny" data-action="nav" data-page="my" aria-label="내 프로필">나</button></div></header>`;
}
function nav(){return `<nav class="navbar" aria-label="주 메뉴">${[['홈','home','home'],['대화','message-circle','대화'],['둘러보기','compass','탐색'],['보관함','bookmark','작업'],['나의 누비','user','내 정보']].map(([label,ic,page])=>`<button class="nav-item ${page==='home'?'active':''}" data-action="nativeNav" data-page="${page}" aria-label="${label}">${icon(ic,21)}<span>${label}</span></button>`).join('')}</nav>`}
const titleSection=(title,subtitle='',link='',action='')=>`<div class="section-head"><div><h3 class="section-title">${title}</h3>${subtitle?`<div class="section-sub">${subtitle}</div>`:''}</div>${link?`<button class="textlink" data-action="${action||'nav'}" ${action?'':'data-page="goals"'}>${link}${icon('chevron-right',14)}</button>`:''}</div>`;
const segment=(labels,active,action='segment',dataName='tab')=>`<div class="segment">${labels.map(([id,label])=>`<button class="${id===active?'active':''}" data-action="${action}" data-${dataName}="${id}">${esc(label)}</button>`).join('')}</div>`;
function campusRows(){
 const t=st.campusTab;
 const sources={
  academic:[['book-open','새 학사 공지 살펴보기','블랙보드 / 포털 게시판 · 데모 항목','purple','예시'],['calendar','이번 주 과제와 시험 확인','수업별 마감 일정을 한 번에 정리','blue','예시'],['file-text','장학금·지원사업 체크','내 조건에 맞는 접수 항목 탐색','orange','예시']],
  email:[['mail','교수님께 결석 메일 초안','정중한 문구로 먼저 작성하기','purple','초안'],['mail','수업 질문 메일 초안','질문과 필요한 정보를 정리하기','orange','초안'],['mail','장학금 문의 메일 초안','담당 부서 문의 내용 만들기','blue','초안']],
  club:[['users','동아리 약속 시간 조율','친구 누비끼리 시간 비교 시연','purple','조율'],['calendar','공연 준비 일정 정리','연습·공연 일정을 한눈에','blue','계획'],['sparkles','인스타 홍보 카드뉴스 초안','동아리 소식을 대신 정리','orange','초안']]
 };
 return sources[t].map(([ic,name,desc,color,badge],i)=>`<button class="campus-item" data-action="campusItem" data-index="${i}"><span class="campus-icon ${color}">${icon(ic,19)}</span><span class="campus-copy"><strong>${name}</strong><span>${desc}</span></span><span class="badge-count">${badge}</span></button>`).join('');
}
const HOME_CONTEXTS=[["first", "처음 시작", "귀찮은 일은, 누비에게", "학교 연결부터 오늘 할 일까지 한 번에 시작해.", "학교 서비스 연결하기", "grades", 5], ["ot", "OT 직후", "이번 학기, 놓치지 않게", "출석·퀴즈·평가 규정을 근거와 함께 정리해.", "수업 규정 정리해줘", "grades", 9], ["quiz", "시작 직후 퀴즈", "퀴즈 전에, 핵심만", "수업 자료와 교수님 강조 내용을 확인해.", "퀴즈 준비 도와줘", "grades", 9], ["quiz-end", "종료 직전 퀴즈", "수업 끝나기 전, 차근차근", "퀴즈 시간과 준비할 범위를 확인해.", "수업 퀴즈 일정 확인해줘", "grades", 9], ["during", "수업 중", "영어 강의도, 놓치지 않고 따라가자.", "듣고 있는 강의의 통역과 노트를 시작해.", "강의 통역 시작해줘", "grades", 5], ["after", "수업 직후", "오늘 배운 것, 정리해둘까?", "강의 노트와 다음 할 일을 이어서 확인해.", "강의 노트 정리해줘", "grades", 9], ["exam", "시험 D-7", "시험 준비, 어디부터 할까?", "범위·자료·강조 내용을 공부 순서로.", "시험 공부 계획 짜줘", "grades", 9], ["deadline", "과제 마감 직전", "제출 전에, 한 번 더", "파일·출처·마감 시간을 함께 확인해.", "과제 제출 준비 확인해줘", "grades", 5], ["change", "공지 변경", "바뀐 공지, 알려줄게", "변경 전후와 준비할 일을 먼저 확인해.", "변경된 학교 공지 확인해줘", "grades", 1], ["grades", "성적 발표", "점수보다 먼저, 기준부터", "성적과 평가 기준을 확인하고 문의 초안까지.", "성적 기준과 문의 초안 도와줘", "grades", 9], ["scholar", "장학금 발견", "나도 신청할 수 있을까?", "장학금 조건과 준비 서류부터 확인해.", "나에게 맞는 장학금 찾아줘", "grades", 1], ["team", "팀플 중", "발표 준비, 같이 하자", "주제에 맞는 논문부터 팀 일정까지.", "팀플 논문과 일정 정리해줘", "grades", 5], ["free", "공강", "잠깐의 여유, 나를 위해", "오늘 목표에 맞는 작은 행동을 찾아봐.", "공강 때 할 일 추천해줘", "fitness", 2]];
let homeContext='first';
function nativeDraft(agent,prompt){if(window.NubiHome){window.NubiHome.chat(agent,prompt);}else notify('앱에서는 담당 누비의 실제 대화 초안을 열어요.');}
function home(){
 const ctx=HOME_CONTEXTS.find(x=>x[0]===homeContext)||HOME_CONTEXTS[0];
 const ids=['grade','health','romance','career','travel'];
 return `<main class="page-scroll page-enter" id="scroll-area">${header()}
 <div class="context-bar"><small>${formatDate(new Date())} · 상황 예시</small><select id="home-context" aria-label="상황 선택">${HOME_CONTEXTS.map(x=>`<option value="${x[0]}" ${ctx[0]===x[0]?'selected':''}>${x[1]}</option>`).join('')}</select></div>
 <section class="hero"><div class="hero-copy"><div class="label">${icon('sparkles',12)} ${ctx[1]} · 누비의 제안</div><h2>${esc(ctx[2])}</h2><p>${esc(ctx[3])}</p><button class="hero-cta" data-action="contextChat">${esc(ctx[4])} ${icon('arrow-right',14)}</button></div>${portrait(ctx[6],'hero-figure')}</section>
 <section class="section">${titleSection('어떤 내가 되고 싶어?','내 누비와 바로 이어서 이야기해.','전체 보기','navGoals')}<div class="goals-peek">${ids.map(id=>{const g=GOALS[id];return `<button class="goal-tile ${g.bg}" aria-label="${esc(g.want)}" data-action="goal" data-goal="${id}"><div class="goal-title">${esc(g.want)}</div><div class="goal-by">${esc(g.name)}</div>${portrait(g.img)}<span class="addbubble">${icon('arrow-up-right',14)}</span></button>`}).join('')}</div></section>
 <div class="home-columns"><section class="section">${titleSection('부탁하면, 이렇게 해줘요','필요한 순간, 담당 누비에게 맡겨봐.')}<div class="feature-strip">${[['필요한 결과물, 끝까지 준비해줘','문서 · 신청서 초안',5,'공모전 신청서 초안 작성해줘'],['강의 동시통역, 놓치지 않게','강의 · 공부',9,'강의 통역과 노트 시작해줘'],['메일 속 기회, 놓치지 않게','학사 메일 · 장학금',1,'학사메일에서 장학금과 공모전 찾아줘'],['기차 시간, 함께 맞춰줘','이동 · KTX',8,'울산에서 서울 KTX 시간과 이동 경로 찾아줘']].map(([t,l,img,p])=>`<button class="feature-card" data-action="nativeFeature" data-prompt="${esc(p)}" data-agent="${img===8?'travel':'grades'}"><small>${l}</small><strong>${t}</strong>${portrait(img)}<span>누비에게 부탁하기 ${icon('arrow-right',12)}</span></button>`).join('')}</div></section>
 <section class="section">${titleSection('학교생활, 이어서 해볼까?','실제 조회 결과는 담당 누비와 확인해.')}<button class="mini-summary" data-action="nativeFeature" data-agent="grades" data-prompt="학교 포털 공지와 블랙보드 과제·시험 일정 확인해줘">${icon('book-open',22)}<span><strong>공지·과제·시험 일정 확인</strong><small>포털 세션으로 Blackboard 연결 확인</small></span>${icon('chevron-right',16)}</button><button class="mini-summary" data-action="nativeConnect">${icon('link',22)}<span><strong>학교 서비스 연결</strong><small>포털 먼저 로그인 · Blackboard는 자동 확인</small></span>${icon('chevron-right',16)}</button></section></div>
 <p class="source-note">상단 내용은 선택한 상황의 UI 예시예요. 실제 공지·일정·연결 상태는 조회 후 확인해요.</p><div class="spacer16"></div></main>`;
}
function goalCard(id){let g=GOALS[id];return `<button class="goal-card ${g.bg}" data-action="goal" data-goal="${id}" aria-label="${esc(g.want)}"><span class="micro">${esc(g.name)} · ${g.emoji}</span><h3>${esc(g.want)}</h3><small>이 목표로 시작하기</small>${portrait(g.img,'',g.name)}<span class="arrow-pill">${icon('arrow-up-right',13)}</span></button>`}
function goals(){
 const ids=GOAL_IDS.filter(x=>`${GOALS[x].want} ${GOALS[x].name}`.includes(st.goalQuery));
 return `<main class="page-scroll page-enter">${header()}
 <div class="page-heading"><div class="eyebrow">FIND YOUR NUBI</div><h1>요즘 너는<br>뭘 제일 하고 싶어? 💭</h1><p>하나만 골라도 좋아. 목표마다 누비가 한 명씩 생겨!</p></div>
 <label class="searchbar">${icon('search',18)}<input id="goal-search" type="search" value="${esc(st.goalQuery)}" placeholder="연애, 학점, 랩실, 여행... 검색" autocomplete="off" aria-label="목표 검색"></label>
 <div class="goals-banner margin12"><div><span class="tag">${icon('sparkles',11)} HOW IT WORKS</span><h2>목표를 고르면<br>누비가 바로 대화해!</h2><span class="note-small">선택 → 대화 → 대신 탐색</span></div>${portrait(1)}</div>
 ${titleSection('마음 가는 목표를 골라봐','대학생의 진짜 고민과 바람들')}
 <div class="goal-grid" id="goal-results">${ids.map(goalCard).join('')||`<p class="soft-text">찾는 목표가 없어요. 다른 단어를 입력해보세요.</p>`}</div>
 <section class="section">${titleSection('이렇게 시작해봐','옆으로 넘기며 인기 누비 만나기')}
 <div class="swiper goals-swiper" style="margin:0 -10px;padding:8px 13px 16px;overflow:hidden"><div class="swiper-wrapper" style="display:flex;gap:9px">${['romance','health','grade','travel'].map(id=>{let g=GOALS[id];return `<div class="swiper-slide" style="min-width:76%;width:76%;flex:0 0 76%"><button class="goals-banner" style="width:100%;text-align:left;height:135px" data-action="goal" data-goal="${id}"><div><span class="tag">${g.emoji} ${g.name}</span><h2>${g.want}</h2><small class="soft-text">같이 시작하기 ${icon('arrow-right',13)}</small></div>${portrait(g.img)}</button></div>`}).join('')}</div></div></section>
 <div class="spacer16"></div></main>`;
}
function bubble(m,id){
 if(m.role==='user')return `<div class="bubble-row user"><div class="bubble">${esc(m.text)}</div></div>`;
 return `<div class="bubble-row agent">${portrait(GOALS[id].img,'bubble-face')}<div class="bubble">${esc(m.text).replaceAll('\n','<br>')}</div></div>${m.result?resultCard(m):''}`;
}
function resultCard(m){
 let kind=m.kind||'browse';
 const meta={browse:['search','자동 탐색 미리보기','검색 → 비교 → 결과 정리'],shop:['shopping-bag','쇼핑 비교 미리보기','관련 상품 후보 찾기 → 승인 요청'],schedule:['calendar','일정 조율 미리보기','일정 확인 → 충돌 검토 → 승인'],mail:['mail','이메일 초안','문구 작성 → 확인 → 복사']}[kind];
 let cta={browse:['미리보기','demoAuto'],shop:['상품 비교','navShop'],schedule:['캘린더 보기','calendarWorkspace'],mail:['메일 초안 보기','mailDraft']}[kind];
 return `<div class="agent-work-result"><div class="result-heading" style="color:#228c68">${icon(meta[0],17)} ${meta[1]} <span class="tag gray" style="margin-left:auto">DEMO</span></div><div class="step-rail"><span class="done"></span><span class="done"></span><span></span></div><div class="note-small">${meta[2]}</div><div class="result-footer"><button data-action="${cta[1]}">${cta[0]} ${icon('arrow-right',12)}</button><button data-action="goWorkspace" data-tab="autos">내 오토스 ${icon('plus',12)}</button></div></div>`;
}
function chat(){
 const g=currentGoal();let ms=st.messages[st.goal]||[];
 return `<main class="page-scroll chatpage page-enter">
 <div class="chat-header"><button class="iconbtn plain" data-action="drawer" aria-label="메뉴 열기">${icon('menu',21)}</button><button style="padding:0" data-action="switchGoal" aria-label="대화 상대 바꾸기">${portrait(g.img,'chat-avatar',g.name)}</button><button class="chat-head-main" style="text-align:left" data-action="goWorkspace" data-tab="autos"><strong>${esc(g.name)} ${icon('chevron-down',14)}</strong><span><i class="online-dot"></i> 내 목표를 위한 누비 · 목표 공간</span></button><button class="chat-action" data-action="sheet" data-sheet="invite" aria-label="초대하기">${icon('share-2',17)}</button><button class="chat-action" data-action="drawer" aria-label="메뉴">${icon('more-horizontal',18)}</button></div>
 <div class="chat-area" id="chat-area"><div class="chat-date">오늘 · ${formatDate(new Date())}</div>
 ${ms.length ? `<div style="text-align:center"><button class="chat-goal-tag" data-action="goWorkspace" data-tab="autos">${icon('target',13)} 내 목표: ${esc(g.want)} ${icon('chevron-right',12)}</button></div>${ms.map(m=>bubble(m,st.goal)).join('')}` : `<div class="chat-empty">${portrait(g.img,'',g.name)}<span class="chat-goal-tag">${g.emoji} ${esc(g.want)}</span><h2>안녕! 나는 ${esc(g.name)}야.</h2><p>${esc(g.desc)}<br>먼저 나한테 한마디만 해봐.</p></div><div class="chat-suggestions">${g.prompts.map((p,i)=>`<button class="suggestion" data-action="preset" data-prompt="${esc(p)}">${icon(i===0?'sparkles':i===1?'search':'calendar',16)} ${esc(p)} ${icon('arrow-up-right',14)}</button>`).join('')}</div>`}
 </div>
 <div class="chat-composer"><div class="composer-top"><button data-action="goWorkspace" data-tab="autos">${icon('layers',13)} ${esc(g.name)} 목표</button><button data-action="sheet" data-sheet="autoChooser">${icon('sparkles',13)} 오토스</button><button data-action="goWorkspace" data-tab="community">${icon('users',13)} 둘러보기</button></div><div class="compose-box"><button class="compose-tool" data-action="sheet" data-sheet="autoChooser" aria-label="오토스 추가">${icon('plus',22)}</button><textarea id="chat-input" rows="1" placeholder="${esc(g.name)}에게 부탁해봐..." aria-label="누비에게 메시지 보내기"></textarea><button class="compose-tool" data-action="voice" aria-label="음성으로 입력">${icon('mic',19)}</button><button class="compose-tool compose-send" data-action="send" aria-label="메시지 전송">${icon('arrow-up',20)}</button></div></div>
 </main>`;
}
function sendMessage(text){
 const prompt=String(text||'').trim();if(!prompt)return;
 const id=st.goal;if(!st.messages[id])st.messages[id]=[];
 st.messages[id].push({role:'user',text:prompt,at:Date.now()});
 persist();render();
 clearTimeout(replyTimer);replyTimer=setTimeout(()=>{
 const kind=/메일|연락|초안|자기소개/.test(prompt)?'mail':/쇼핑|가격|구매|프로틴|보호대|선물|장바구니|상품/.test(prompt)?'shop':/시간|일정|스케줄|회의|약속|운동 매주|시험 계획/.test(prompt)?'schedule':'browse';
 let text={browse:`좋아! “${prompt.slice(0,35)}”에 맞는 정보부터 살펴볼게. 검색하고 비교하는 과정을 아래에서 먼저 체험해봐.`,shop:`좋아! 필요한 조건을 살피고 가격을 비교한 뒤, 네가 확인할 때까지 결제는 진행하지 않을게.`,schedule:`좋아! 일정이 겹치는지 비교하고 맞는 시간을 제안해볼게. 최종 일정은 네가 결정할 수 있어.`,mail:`좋아! 상황에 맞게 정중한 초안을 먼저 써볼게. 내용 확인 후 복사하거나 수정할 수 있어.`}[kind];
 st.messages[id].push({role:'agent',text,kind,result:true,at:Date.now()});persist();
 if(st.page==='chat'&&st.goal===id){render();requestAnimationFrame(()=>{let a=$('#chat-area');if(a)a.scrollTop=a.scrollHeight})}
 },500);
}
const BROWSER_STEPS=[
 ['조건 확인 중','상황과 예산을 확인하고 있어','33%','검색 결과 살펴보기'],
 ['상품 비교 중','후기와 가격을 나란히 비교해','66%','조건에 맞는 후보 비교'],
 ['확인 준비 완료','선택한 후보를 보여줄게','100%','사용자 확인 대기']
];
function browserMock(){
 const step=BROWSER_STEPS[browserTick%3];
 return `<div class="browser-mock"><div class="browser-top">${icon('chevron-left',12)}<div class="browser-search">${icon('search',11)} 목표에 맞는 상품 찾기</div>${icon('more-horizontal',12)}</div><div class="browser-body"><div class="browser-mini-label">${icon('sparkles',11)} <span class="browser-screen-title">${step[3]}</span> <span style="margin-left:auto;color:#a3b6a8">시연</span></div><div class="mock-product-row"><div class="mock-prod"><div class="mock-art" style="background:#f3e8ee"><span style="font-size:34px">👕</span></div><strong>스타일 후보 A</strong><small>27,900원</small></div><div class="mock-prod"><div class="mock-art" style="background:#f1ecff"><span style="font-size:34px">🧥</span></div><strong>스타일 후보 B</strong><small>31,900원</small></div></div></div></div>`;
}
function featuredAuto(){const g=currentGoal();return `<div class="featured-auto"><div class="top"><span class="live-badge"><i class="pulse"></i> 화면 자동 탐색 · 시연</span><button style="color:#c7e8d5" data-action="browserReplay" aria-label="다시 보기">${icon('refresh-cw',16)}</button></div><h3>찾는 것부터 비교까지,<br>${esc(g.name)}가 움직여!</h3><p>실제 웹 제어가 연결되기 전의 애니메이션 시연입니다.</p>${browserMock()}<div class="browse-progress"><span class="browser-step-title">${BROWSER_STEPS[browserTick%3][0]}</span><div class="tracker"><b class="browser-progress-bar" style="width:${BROWSER_STEPS[browserTick%3][2]}"></b></div><span class="browser-step-count">${browserTick%3+1}/3</span></div><div class="auto-actions"><button data-action="addAuto" data-auto="${getAutos(st.goal)[0].key}">${icon('plus',15)} 내 오토스로 담기</button><button class="ghost" data-action="goChatCurrent">대화로 부탁하기</button></div></div>`}
function autoList(){let autos=getAutos(st.goal);let mine=st.myAutos.filter(x=>x.goal===st.goal);return `
 ${featuredAuto()}
 <section class="section" style="margin-top:23px">${titleSection(`${currentGoal().name}가 추천하는 오토스`,'필요한 자동 탐색을 골라 담아봐')}
 ${autos.map((a,i)=>`<div class="auto-card"><span class="auto-art" style="background:${['#eaf9ed','#f0edff','#fff2eb'][i]};color:${['#30b48a','#9281da','#e5a17f'][i]}">${icon(a.ic,23)}</span><div class="auto-content"><h4>${esc(a.name)}</h4><p>${esc(a.desc)}</p><div class="auto-sub">${i===0?'🔥 가장 많이 고르는 예시':'누비가 대신 탐색해요'}</div></div><button class="mini-action" data-action="addAuto" data-auto="${a.key}" aria-label="내 오토스로 추가">${st.myAutos.some(x=>x.key===a.key)?icon('check',17):icon('plus',18)}</button></div>`).join('')}
 </section>
 <section class="section">${titleSection('내가 담은 오토스',`${mine.length}개 · 필요한 작업만 남겨둬`)}
 ${mine.length?mine.map(a=>`<div class="menu-list" style="margin-bottom:8px"><button class="menu-row" data-action="sheet" data-sheet="autoDetails" data-data="${a.key}"><span class="left-icon">${icon(a.ic,17)}</span><strong>${esc(a.name)}</strong><span class="mini">관리 ${icon('chevron-right',14)}</span></button></div>`).join(''):`<div class="empty-state">${portrait(4)}<h3>아직 담은 오토스가 없어</h3><p>위에서 마음에 드는 걸 +로 추가해봐.</p></div>`}</section>`}
function socialCard(post,i){let [platform,title,desc,emoji]=post;return `<article class="social-card"><div class="social-head"><span class="social-pic" style="background:${i%2?'#e8f8ed':'#eeedff'}">${emoji}</span><span><strong>${platform==='누비들'?'누비 이웃의 오토스':`${platform}에서 골라본 이야기`}</strong><small>관심 목표 기반 · 시연 콘텐츠</small></span><span class="social-source">${esc(platform)}</span></div><h3>${esc(title)}</h3><p>${esc(desc)}</p><div class="social-footer"><div class="reactions">${icon('heart',14)} 공감 · ${icon('bookmark',14)} 저장</div><button data-action="inspire" data-post="${i}">누비에게 맡기기 ${icon('arrow-up-right',13)}</button></div></article>`}
function mediaFeed(){let g=currentGoal();return `<div class="media-feature"><div class="video-poster"><div class="video-typography"><small>YOUR NEXT STEP · VIDEO</small><strong>보고 끝내지 말고,<br>바로 해보자.</strong></div>${portrait(g.img)}<button class="video-play" data-action="mediaPlay" aria-label="영상 시연 보기">${icon('play',22)}</button><div style="position:absolute;bottom:13px;left:18px;color:#c6f1d9;font-size:10px;font-weight:800">${g.emoji} ${esc(g.want)} · 시연 카드</div></div><div class="media-caption"><h3>${esc(g.name)}를 위한 짧은 팁</h3><p>실제 영상은 아직 연결되지 않았어요. 연결하면 출처와 원문을 함께 보여줍니다.</p><button data-action="inspire" data-post="0">이런 콘텐츠 더 찾아줘 ${icon('arrow-up-right',13)}</button></div></div><div class="social-card"><div class="social-head"><span class="social-pic">▶</span><div><strong>미디어에서 바로 누비에게</strong><small>영상 → 정보 수집 → 필요한 물품 비교</small></div></div><p style="margin-top:13px">좋아하는 영상에서 아이디어를 얻었다면, 누비에게 탐색을 부탁할 수 있어요. 쇼핑은 사용자가 직접 확인한 뒤 진행합니다.</p><div class="social-footer"><span class="tag gray">개인화 예시</span><button data-action="navShop">관련 상품 비교</button></div></div>`}
function community(){let posts=postsFor(st.goal);let tab=st.communityTab;return `
 <div style="margin-top:2px" class="segment">${[['all','모아보기'],['nubi','누비들'],['media','영상']].map(([k,n])=>`<button class="${tab===k?'active':''}" data-action="communityTab" data-tab="${k}">${n}</button>`).join('')}</div>
 <p class="note-small" style="margin:11px 3px 14px">다양한 플랫폼에서 참고할 콘텐츠를 모을 공간이에요. 아래는 화면 확인용 예시입니다.</p>
 ${tab==='media'?mediaFeed():tab==='nubi'?socialCard(posts.find(p=>p[0]==='누비들')||posts[1],1)+socialCard(['누비들','내 오토스를 커뮤니티에 공개해봐','같은 목표를 가진 사람에게 도움이 되는 탐색 방법을 공유할 수 있어요.','✨'],2):posts.map(socialCard).join('')}
 <div class="card" style="background:#eaf9ef;border-color:#e5f2e8;display:flex;gap:8px;align-items:center">${portrait(currentGoal().img,'chat-avatar','누비')}<div style="flex:1"><h3 style="font-size:12px">${esc(currentGoal().name)}가 이어서 해줄게</h3><p>마음에 드는 내용을 발견했어? 바로 부탁해!</p></div><button class="mini-action" data-action="goChatCurrent">${icon('arrow-right',17)}</button></div>`}
function selectedCalendarDate(){let base=new Date();base.setDate(1);base.setMonth(base.getMonth()+st.calendarOffset);return new Date(base.getFullYear(),base.getMonth(),st.selectedDate)}
function dateKey(d){return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`}
function calendar(){const now=new Date(),first=new Date(now.getFullYear(),now.getMonth()+st.calendarOffset,1),last=new Date(first.getFullYear(),first.getMonth()+1,0);const leading=first.getDay();const days=[];for(let i=0;i<42;i++){let day=i-leading+1;if(day>last.getDate()&&i>=35)break;days.push(day)}const sel=selectedCalendarDate(),selkey=dateKey(sel),scheduled=st.schedules.filter(x=>x.day===selkey&&x.goal===st.goal);const isToday = dateKey(now)===selkey;
 return `<div class="segment" style="margin-bottom:15px">${[['autos','오토스 일정'],['history','대화 기록']].map(([id,label])=>`<button class="${st.calendarMode===id?'active':''}" data-action="calendarMode" data-mode="${id}">${label}</button>`).join('')}</div>
 <div class="calendar-card"><div class="calendar-month"><button data-action="monthPrev" aria-label="이전 달">${icon('chevron-left',18)}</button><strong>${first.getFullYear()}년 ${first.getMonth()+1}월</strong><button data-action="monthNext" aria-label="다음 달">${icon('chevron-right',18)}</button></div><div class="calgrid">${['일','월','화','수','목','금','토'].map(w=>`<div class="calweek">${w}</div>`).join('')}${days.map(day=>{let inside=day>0&&day<=last.getDate();let d=new Date(first.getFullYear(),first.getMonth(),day);let key=dateKey(d);let dot=inside&&(st.schedules.some(x=>x.day===key&&x.goal===st.goal)||(st.calendarMode==='history'?new Date().getDate()===day&&st.calendarOffset===0:[4,8,13,20,25,31].includes(day)));return `<button class="calday ${inside?'':'muted'} ${inside&&day===st.selectedDate?'selected':''} ${inside&&dateKey(now)===key?'today':''}" data-action="selectDate" data-day="${day}" ${inside?'':'disabled'}>${d.getDate()}${dot?'<i class="dot"></i>':''}</button>`}).join('')}</div></div>
 <section class="section">${titleSection(`${sel.getMonth()+1}월 ${sel.getDate()}일 ${st.calendarMode==='autos'?'실행 일정':'대화 기록'}`,st.calendarMode==='autos'?'내가 맡긴 일을 캘린더로':'언제 무슨 이야기를 했는지')}
 ${st.calendarMode==='history'?`<div class="card">${isToday&&st.messages[st.goal]?.length?`<h3>${esc(currentGoal().name)}와 나눈 대화</h3><p>오늘 ${st.messages[st.goal].filter(x=>x.role==='user').length}번 부탁했어.</p><button class="btn soft full margin12" data-action="goChatCurrent">대화 다시 보기 ${icon('arrow-right',13)}</button>`:`<div class="empty-state" style="border:0;padding:12px">${portrait(10)}<h3>이날의 대화가 아직 없어</h3><p>누비와 대화하면 날짜별로 기록돼.</p></div>`}</div>`:scheduled.length?scheduled.map(x=>`<div class="event-row"><span class="event-time">${esc(x.time)}</span><i class="event-line"></i><span class="event-info"><strong>${esc(x.name)}</strong><span>설정된 시연 일정 · ${esc(currentGoal().name)}</span></span><span class="event-action">예정</span></div>`).join(''):`<div class="card"><div class="event-row" style="border:none;padding:0"><span class="event-time">19:00</span><i class="event-line" style="background:#b5d2c0"></i><span class="event-info"><strong>아직 예약된 작업이 없어요</strong><span>오토스를 추가하면 실행 시간을 배치할 수 있어</span></span></div></div>`}
 </section>
 ${st.calendarMode==='autos'?`<button class="btn mint full margin12" data-action="sheet" data-sheet="autoChooser">${icon('plus',16)} 오토스 일정 추가하기</button>`:`<button class="btn outline full margin12" data-action="goChatCurrent">${icon('message-circle',16)} 오늘 누비와 대화하기</button>`}
 <p class="note-small" style="margin:10px 4px">* 현재 일정은 기기에 저장되는 데모 데이터로, 실제 캘린더에 반영되지 않습니다.</p>`;
}
function workspace(){const g=currentGoal();return `<main class="page-scroll page-enter">${header({back:'chat',title:`${g.name}의 공간`,share:true})}
 <div class="workspace-hero">${portrait(g.img)}<div class="ws-info"><div class="eyebrow">MY GOAL SPACE</div><h2>${esc(g.want)}</h2><p>${esc(g.name)}랑 목표를 이루어봐</p></div><button class="ws-chatbtn" data-action="goChatCurrent">${icon('message-circle',13)} 대화</button></div>
 <div class="ws-segment">${[['autos','오토스'],['community','커뮤니티'],['calendar','캘린더']].map(([id,label])=>`<button class="${st.goalTab===id?'active':''}" data-action="goalTab" data-tab="${id}">${label}</button>`).join('')}</div>
 ${st.goalTab==='autos'?autoList():st.goalTab==='community'?community():calendar()}
 <div class="spacer24"></div></main>`;
}
function discover(){let tab=st.discoverTab;return `<main class="page-scroll page-enter">${header()}
 <div class="page-heading"><div class="eyebrow">DISCOVER YOUR NEXT STEP</div><h1>새로운 가능성,<br>누비랑 발견해 🌿</h1><p>재미있는 콘텐츠를 보고 필요한 일까지 맡겨봐.</p></div>
 <div class="segment">${[['insight','인사이트'],['shop','쇼핑'],['autos','오토스']].map(([id,n])=>`<button class="${tab===id?'active':''}" data-action="discoverTab" data-tab="${id}">${n}</button>`).join('')}</div><div class="spacer16"></div>
 ${tab==='insight'?discoverInsights():tab==='shop'?shop():discoverAutos()}
 <div class="spacer24"></div></main>`}
function discoverInsights(){let g=currentGoal();let posts=postsFor(st.goal);return `
 <div class="shop-hero" style="background:linear-gradient(125deg,#e1f7ec,#e9edff)"><div style="flex:1"><span class="tag">${icon('compass',12)} FOR YOU</span><h2>${esc(g.want)}<br>나도 해볼까?</h2><p>관심있는 목표를 중심으로 탐색해봐</p></div>${portrait(g.img)}</div>
 <section class="section">${titleSection('너를 위한 인사이트','여러 플랫폼의 정보를 한곳에서 · 예시 자료','전체 보기','discoverCommunity')}
 ${posts.map(socialCard).join('')}
 </section>
 <section class="section">${titleSection('영상에서 아이디어 얻기','미디어 → 누비에게 부탁하기')}${mediaFeed()}</section>
 <div class="card" style="margin-top:13px;background:#213f35;color:#fff;display:flex;align-items:center;gap:11px">${portrait(1,'chat-avatar')}<div style="flex:1"><h3 style="color:#fff">누비가 직접 알아봐줄까?</h3><p style="color:#b8dacf">궁금한 건 채팅에서 바로 부탁해.</p></div><button class="mini-action" data-action="goChatCurrent">${icon('arrow-right',17)}</button></div>`}
function shop(){let cats=['전체','운동','스타일','공부','여행'];let shown=PRODUCTS.filter(p=>st.shopCategory==='전체'||p.category===st.shopCategory);let g=currentGoal();return `
 <div class="shop-hero"><div style="flex:1"><span class="tag purple">${icon('shopping-bag',12)} SHOPPING FOR YOU</span><h2>필요한 것만,<br>똑똑하게 비교!</h2><p>선택은 네가, 비교는 누비가.</p></div>${portrait(7)}</div>
 <p class="note-small" style="margin:9px 3px 0">가격·제품은 화면 시연용 예시이며 실시간 최저가가 아닙니다.</p>
 <div class="category-pills">${cats.map(c=>`<button class="${st.shopCategory===c?'active':''}" data-action="shopCategory" data-category="${c}">${c}</button>`).join('')}</div>
 <div class="product-grid">${shown.map(p=>`<article class="product-card"><button style="display:block;width:100%;padding:0;text-align:left" data-action="product" data-product="${p.id}"><div class="product-image" style="background:${p.bg}"><span class="product-img-emoji">${p.emoji}</span><span class="tag" style="position:absolute;left:9px;top:9px;background:#ffffffc9;font-size:9px">비교 후보</span></div><div class="product-body"><div class="source">${esc(p.brand)}</div><h4>${esc(p.name)}</h4><div class="price">${money(p.price)}</div></div></button><div class="product-body" style="padding-top:0"><div class="product-bottom"><span>예시 가격</span><button data-action="addCart" data-product="${p.id}" aria-label="장바구니에 담기">${icon('plus',18)}</button></div></div></article>`).join('')}</div>
 <div class="recommend-note">${portrait(g.img,'','누비')}<div><strong>${esc(g.name)}가 고른 이유</strong><p>${esc(g.want)} 목표에 관련된 제품을 살펴볼 수 있어. 실제 구매 전에 가격을 꼭 확인해줘.</p></div></div>
 ${st.cart.length?`<button class="btn primary full" data-action="sheet" data-sheet="cart">${icon('shopping-bag',17)} 장바구니 ${st.cart.length}개 확인하기</button>`:''}`}
function discoverAutos(){let ids=st.goalsChosen.length?st.goalsChosen:['romance','health','grade'];return `
 ${titleSection('인기 자동 탐색','목표에 맞게 켜서 써봐')}
 ${ids.slice(0,3).flatMap((id)=>getAutos(id).slice(0,2)).map((a,i)=>`<div class="auto-card"><span class="auto-art" style="background:${i%2?'#f1edff':'#e5faef'}">${icon(a.ic,23)}</span><div class="auto-content"><div style="font-size:9px;color:#9caaa3">${GOALS[a.goal].name}의 오토스</div><h4>${esc(a.name)}</h4><p>${esc(a.desc)}</p></div><button class="mini-action" data-action="addAuto" data-auto="${a.key}">${icon(st.myAutos.some(x=>x.key===a.key)?'check':'plus',18)}</button></div>`).join('')}
 <button class="btn outline full margin12" data-action="demoAuto">${icon('monitor-play',17)} 자동 탐색 화면 먼저 보기</button>`}
function my(){let chosen=st.goalsChosen.filter(x=>GOALS[x]);let history=chosen.filter(id=>st.messages[id]?.length).sort((a,b)=>(st.messages[b]?.slice(-1)[0]?.at||0)-(st.messages[a]?.slice(-1)[0]?.at||0));return `<main class="page-scroll page-enter">${header()}
 <div class="page-heading"><div class="eyebrow">MY NUBI</div><h1>내 일상은<br>누비랑 함께 🌷</h1><p>나의 목표, 맡겨둔 일, 대화 기록을 모아봤어.</p></div>
 <div class="my-card">${portrait(1)}<div><span class="tag">${icon('sparkles',12)} 나의 누비</span><h2>우리 꽤 잘 맞는데? 😊</h2><p>필요한 순간마다 언제든 불러줘.</p></div></div>
 <div class="stat-row"><div class="stat-item"><strong>${chosen.length}</strong><small>나의 목표</small></div><div class="stat-item"><strong>${st.myAutos.length}</strong><small>담은 오토스</small></div><div class="stat-item"><strong>${st.schedules.length}</strong><small>일정 시연</small></div></div>
 <section class="section">${titleSection('나의 누비들','자주 만나는 친구를 눌러 대화해','추가하기','navGoals')}
 <div class="agent-strip">${chosen.map(id=>`<button class="agent-chip" data-action="goal" data-goal="${id}">${portrait(GOALS[id].img,'',GOALS[id].name)}<span>${GOALS[id].name}</span></button>`).join('')}<button class="agent-chip add" data-action="navGoals"><span class="create-agent">${icon('plus',24)}</span><span>더 만나기</span></button></div></section>
 <section class="section">${titleSection('요즘 누비에게 맡긴 일','완료 전 확인도 여기서')}
 <div class="menu-list">${st.myAutos.length?st.myAutos.slice(0,3).map(a=>`<button class="menu-row" data-action="sheet" data-sheet="autoDetails" data-data="${a.key}"><span class="left-icon">${icon(a.ic,17)}</span><strong>${esc(a.name)}</strong><span class="mini">설정 ${icon('chevron-right',13)}</span></button>`).join(''):`<button class="menu-row" data-action="nav" data-page="discover"><span class="left-icon">${icon('sparkles',17)}</span><strong>오토스 하나 담아볼까?</strong><span class="mini">둘러보기 ${icon('chevron-right',13)}</span></button>`}<button class="menu-row" data-action="nav" data-page="autolibrary"><span class="left-icon">${icon('layers',17)}</span><strong>내 오토스 전체 보기</strong>${icon('chevron-right',14)}</button></div></section>
 <section class="section">${titleSection('최근 나눈 대화','캐릭터별 기록을 이어서 보기')}
 <div class="menu-list">${history.length?history.map(id=>`<button class="menu-row" data-action="goal" data-goal="${id}">${portrait(GOALS[id].img,'chat-avatar',GOALS[id].name)}<span style="flex:1"><strong style="display:block;font-size:12px">${GOALS[id].name}</strong><small style="color:#9daea4;font-size:10px;display:block;margin-top:4px">${esc(st.messages[id].filter(m=>m.role==='user').slice(-1)[0]?.text||GOALS[id].want)}</small></span>${icon('chevron-right',15)}</button>`).join(''):`<div style="padding:18px;font-size:11px;color:#98a99e">아직 대화가 없어. 목표를 골라 첫 대화를 시작해봐!</div>`}</div></section>
 <section class="section">${titleSection('더 편리하게')}
 <div class="menu-list"><button class="menu-row" data-action="nav" data-page="friend"><span class="left-icon">${icon('users',17)}</span><strong>친구 누비끼리 나눈 대화</strong>${icon('chevron-right',15)}</button><button class="menu-row" data-action="nav" data-page="integrations"><span class="left-icon">${icon('link',17)}</span><strong>앱·서비스 연결</strong>${icon('chevron-right',15)}</button><button class="menu-row" data-action="sheet" data-sheet="credits"><span class="left-icon">${icon('wallet',17)}</span><strong>크레딧 · 이용 설정</strong>${icon('chevron-right',15)}</button><button class="menu-row" data-action="sheet" data-sheet="invite"><span class="left-icon">${icon('share-2',17)}</span><strong>친구를 누비에 초대하기</strong>${icon('chevron-right',15)}</button></div></section>
 <div class="spacer24"></div></main>`;
}
function campusPage(){
 const blocks=[['academic','학사','book-open'],['email','이메일','mail'],['club','동아리','users']];
 return `<main class="page-scroll page-enter">${header({back:'home',title:'캠퍼스 라이프'})}
 <div class="goals-banner"><div><span class="tag purple">UNIVERSITY MODE</span><h2>학교 생활도<br>누비가 미리 챙길게</h2><span class="note-small">UNIST를 위한 시연 허브</span></div>${portrait(9)}</div>
 <div class="spacer16"></div>${segment(blocks.map(x=>[x[0],x[1]]),st.campusTab,'campusTab')}
 <div class="section">${titleSection(st.campusTab==='academic'?'학사·과제 관리':st.campusTab==='email'?'이메일 초안': '동아리 관리','자료 연결 전의 예시 화면')}
 <div class="campus-card"><div class="campus-items" style="margin-top:0">${campusRows()}</div></div></div>
 <section class="section">${titleSection('바로 연결하기','실제 자동화를 위해 연결이 필요해')}
 <div class="menu-list"><button class="menu-row" data-action="nav" data-page="integrations"><span class="left-icon">${icon('link',18)}</span><strong>블랙보드 · 학교 포털 · 이메일</strong><span class="mini">연결 보기 ${icon('chevron-right',13)}</span></button></div>
 </section><div class="spacer24"></div></main>`;
}
function friend(){return `<main class="page-scroll page-enter">${header({back:'my',title:'친구 누비끼리 대화'})}
 <div class="workspace-hero">${portrait(3)}<div class="ws-info"><div class="eyebrow">NUBI TO NUBI</div><h2>누비끼리 알아서 조율</h2><p>사람들은 최종 제안만 확인해요</p></div></div>
 <div class="card" style="margin-top:13px"><div class="social-head"><span class="face">${portrait(9)}</span><span><strong>내 누비 · 팀플 일정 담당</strong><small>메시지 기록 · 화면 시연</small></span></div>
 <div class="bubble-row agent" style="margin-top:17px"><span class="bubble">이번 주 모임 시간, 내가 다른 누비에게 확인해볼게!</span></div>
 <div class="bubble-row user" style="margin:12px 0 12px auto"><span class="bubble">토요일 오후는 가능할까?</span></div>
 <div class="bubble-row agent"><span class="bubble">친구 누비의 일정과 겹쳐. 일요일 14:00는 모두 가능하다는 예시야.</span></div>
 <div class="note-small" style="margin-top:14px">실제 친구 계정 또는 캘린더 데이터와 연결된 대화가 아닙니다.</div>
 </div>
 <div class="card" style="margin-top:12px;background:#effaf3;border-color:#e3f6e8"><span class="tag">${icon('calendar-check',12)} 일정 제안</span><h3 style="margin-top:10px">일요일 오후 2:00 · 동아리 회의</h3><p>팀원 4명 · 조율 시연 결과</p><div class="sheet-buttons"><button class="btn soft flex" data-action="nav" data-page="campus">다른 일정</button><button class="btn mint flex" data-action="approveFriend">${icon('check',16)} 일정에 담기</button></div></div>
 <div class="spacer24"></div></main>`}
const PROVIDERS=[
 ['UNIST 포털','학사 공지·행정 게시판','UNIST','academic'],
 ['Blackboard','강의 공지·과제·시험','Bb','academic'],
 ['Google Calendar','개인 일정·미팅','31','calendar'],
 ['Gmail','교수님·개인 이메일','M','email'],
 ['KTX / 코레일','기차 시간표·예약 화면','🚄','travel'],
 ['무신사','상품 탐색·후기','MUS','shopping'],
 ['쿠팡','상품·주문 확인','C','shopping'],
 ['Instagram / Threads','관심 콘텐츠·원문 링크','@','community'],
];
function integrations(){return `<main class="page-scroll page-enter">${header({back:'my',title:'앱·서비스 연결'})}
 <div class="page-heading"><div class="eyebrow">CONNECT YOUR LIFE</div><h1>연결하면 누비가<br>더 잘 챙길 수 있어 🔗</h1><p>아래 버튼은 화면 시연용입니다. 실제 인증이나 계정 접근은 발생하지 않습니다.</p></div>
 <div class="card" style="display:flex;gap:10px;align-items:center;background:#eaf7f0;border-color:#dcefe3">${icon('shield-check',25)}<p style="flex:1;color:#56856f">아이디·비밀번호 입력 없이 연결될 수 있도록 정식 인증 연동을 준비하는 화면입니다.</p></div>
 <section class="section">${titleSection('대학생 필수 연결','교내 일정, 메일, 이동, 쇼핑')}
 <div class="campus-card" style="padding:3px 14px">${PROVIDERS.map(([name,desc,logo],i)=>`<div class="provider"><span class="brand-box" style="background:${['#e8f9ef','#ecedff','#fff3e1','#fff0ed'][i%4]}">${esc(logo)}</span><div class="detail"><strong>${esc(name)}</strong><small>${esc(desc)}</small></div><button class="${st.connections.includes(name)?'connected':''}" data-action="connect" data-provider="${esc(name)}">${st.connections.includes(name)?'시연 해제':'시연 연결'}</button></div>`).join('')}</div>
 </section>
 <p class="note-small" style="margin:12px 3px">* 시연 연결은 이 기기의 브라우저 저장소에 표시 상태만 보관합니다. 실제 OAuth·로그인·기능 접근은 구현되지 않았습니다.</p>
 <div class="spacer24"></div></main>`;
}
function autoLibraryPage(){return `<main class="page-scroll page-enter">${header({back:'my',title:'내 오토스'})}
 <div class="page-heading"><div class="eyebrow">AUTOS LIBRARY</div><h1>나 대신 움직이는<br>작은 자동화들 ✨</h1><p>추가한 오토스를 일정에 배치하고 관리해.</p></div>
 ${st.myAutos.length?st.myAutos.map(a=>`<div class="auto-card"><span class="auto-art">${icon(a.ic,22)}</span><span class="auto-content"><div class="tag gray" style="margin-bottom:5px">${esc(GOALS[a.goal]?.name||'누비')}</div><h4>${esc(a.name)}</h4><p>${esc(a.desc)}</p></span><button class="mini-action" data-action="sheet" data-sheet="autoDetails" data-data="${a.key}">${icon('settings',17)}</button></div>`).join(''):`<div class="empty-state">${portrait(10)}<h3>지금은 오토스가 쉬고 있어</h3><p>새로운 오토스를 담으면 여기서 확인할 수 있어!</p></div>`}
 <button class="btn mint full margin12" data-action="nav" data-page="discover">${icon('plus',17)} 새 오토스 둘러보기</button>
 <div class="spacer24"></div></main>`}
function findAuto(key){for(let id in AUTO_LIBRARY){let x=getAutos(id).find(a=>a.key===key);if(x)return x;}return getAutos('campus')[0]}
function allNavigation(){
 switch(st.page){case 'home':return home();case 'goals':return goals();case 'chat':return chat();case 'workspace':return workspace();case 'discover':return discover();case 'my':return my();case 'campus':return campusPage();case 'friend':return friend();case 'integrations':return integrations();case 'autolibrary':return autoLibraryPage();default:return home()}
}
function drawer(){const chosen=st.goalsChosen.filter(x=>GOALS[x]);return `<div class="overlay" data-action="closeOverlay"><aside class="drawer" aria-label="전체 사이드 메뉴" role="dialog"><div class="drawer-user"><button class="drawer-logo" data-action="nav" data-page="home">nubi<em>.</em></button><button class="iconbtn muted" data-action="closeOverlay" aria-label="메뉴 닫기">${icon('x',18)}</button></div><div class="drawer-scroll">
 <p style="font-size:12px;color:#91a49b;line-height:1.7;margin:7px 0 20px">네가 하고 싶은 모든 일에, 누비 🌱</p>
 <span class="drawer-section">나의 누비들</span><div class="drawer-avatars">${chosen.slice(0,4).map(id=>`<button data-action="goal" data-goal="${id}">${portrait(GOALS[id].img,'',GOALS[id].name)}<span>${GOALS[id].name}</span></button>`).join('')}<button data-action="nav" data-page="goals"><span style="height:56px;width:56px;border-radius:21px;background:#eef9f0;border:1px dashed #accfbb;display:grid;place-items:center;color:#27aa7f">${icon('plus',20)}</span><span>친구 추가</span></button></div>
 <div class="drawer-divider"></div><span class="drawer-section">내 일상</span>
 ${[['home','오늘의 홈','home'],['campus','캠퍼스·학사','graduation-cap'],['goals','목표 고르기','target'],['discover','발견·쇼핑','compass'],['my','내 누비들','user']].map(([page,label,ic])=>`<button class="drawer-link ${st.page===page?'active':''}" data-action="nav" data-page="${page}">${icon(ic,18)} ${label}${icon('chevron-right',13)}</button>`).join('')}
 <span class="drawer-section">대화와 자동 탐색</span>
 <button class="drawer-link" data-action="mainChat">${icon('message-circle',18)} 누비와 대화하기</button>
 <button class="drawer-link" data-action="nav" data-page="autolibrary">${icon('layers',18)} 내 오토스 <span class="tail">${st.myAutos.length}개</span></button>
 <button class="drawer-link" data-action="calendarWorkspace">${icon('calendar',18)} 나의 일정</button>
 <button class="drawer-link" data-action="nav" data-page="friend">${icon('users',18)} 친구 누비들의 대화</button>
 <span class="drawer-section">최근 대화</span>
 ${chosen.filter(id=>st.messages[id]?.length).slice(0,3).map(id=>`<button class="drawer-link" data-action="goal" data-goal="${id}">${icon('message-circle',16)} ${GOALS[id].name} · 대화 이어가기</button>`).join('')||`<div class="note-small" style="padding:9px">아직 시작한 대화가 없어요.</div>`}
 <span class="drawer-section">설정</span>
 <button class="drawer-link" data-action="nav" data-page="integrations">${icon('link',18)} 서비스 연결</button>
 <button class="drawer-link" data-action="sheet" data-sheet="credits">${icon('wallet',18)} 크레딧·이용 안내</button>
 <button class="drawer-link" data-action="sheet" data-sheet="invite">${icon('share-2',18)} 친구 초대하기</button>
 <button class="drawer-link" data-action="sheet" data-sheet="settings">${icon('settings',18)} 설정·데이터 초기화</button>
 </div><div class="drawer-footer"><span>누비 UI 프로토타입 · DEMO</span><span>v1.0</span></div></aside></div>`}
function sheetTitle(name,desc=''){return `<div class="sheet-handle"></div><div class="sheet-header"><h2>${esc(name)}</h2><button data-action="closeOverlay" aria-label="닫기">${icon('x',17)}</button></div>${desc?`<p class="sheet-lead">${desc}</p>`:''}`}
function autoChooserSheet(){let as=getAutos(st.goal);return `${sheetTitle('어떤 일을 맡길까?','자주 사용하는 자동 탐색 예시부터 바로 담을 수 있어!')}
 <div class="sheet-autos">${as.map(a=>`<div class="sheet-tile"><div class="mark">${icon(a.ic,20)}</div><div style="flex:1"><strong>${esc(a.name)}</strong><p>${esc(a.desc)}</p></div><button data-action="addAuto" data-auto="${a.key}">${st.myAutos.some(x=>x.key===a.key)?'담았어 ✓':'＋ 담기'}</button></div>`).join('')}</div>
 <button class="btn primary full margin12" data-action="demoAuto">${icon('monitor-play',16)} 자동 탐색 화면 보기</button><p class="note-small">실제 웹 제어는 연결 전이며, 탐색 화면은 애니메이션 시연입니다.</p>`}
function scheduleSheet(key,prompt=false){let a=findAuto(key);return `${sheetTitle(prompt?'담았어! 언제 실행할까?':'오토스 실행 시간 정하기',`${a.name}을(를) 내 일정에 배치할 수 있어.`)}
 <div class="sheet-tile" style="margin-top:13px"><div class="mark">${icon(a.ic,20)}</div><div><strong>${esc(a.name)}</strong><p>${esc(a.desc)}</p></div></div>
 <div class="section-head margin12"><strong style="font-size:12px">실행 날짜</strong><span class="tag gray">오늘 날짜 기준</span></div>
 <label class="note-small">날짜를 골라줘<input type="date" id="schedule-date" value="${dateKey(new Date())}" style="margin-top:7px;width:100%;display:block;border:1px solid #e3ece7;padding:12px;border-radius:12px;font-size:13px;background:white"></label>
 <div class="spacer16"></div><label class="note-small">실행 예정 시간<input type="time" value="19:00" id="schedule-time"></label>
 <div class="sheet-buttons"><button class="btn soft flex" data-action="closeOverlay">나중에</button><button class="btn mint flex" data-action="saveSchedule" data-auto="${a.key}">${icon('calendar-check',16)} 일정에 담기</button></div>
 <p class="note-small">시연 일정은 이 브라우저에만 저장돼요. 실시간 실행이나 알림은 아직 연결되지 않았습니다.</p>`}
function autoDetailsSheet(key){let a=findAuto(key);let scheduled=st.schedules.filter(x=>x.autoKey===key);return `${sheetTitle(a.name,a.desc)}
 <div class="card" style="background:#effbf3;border-color:#e5f1e7;margin-top:12px"><span class="tag">${icon('check',12)} 내 오토스에 담김</span><h3 style="margin:10px 0 6px">${esc(GOALS[a.goal].name)}의 오토스</h3><p>${scheduled.length?`${scheduled.length}개 시연 일정이 설정됐어.`:'아직 실행 시간이 정해지지 않았어.'}</p></div>
 <div class="sheet-buttons"><button class="btn outline flex" data-action="schedule" data-auto="${key}">${icon('calendar',16)} 일정 설정</button><button class="btn primary flex" data-action="demoAuto">${icon('monitor-play',16)} 미리보기</button></div><button class="btn soft full margin12" data-action="removeAuto" data-auto="${key}">내 오토스에서 제거</button>`}
function productSheet(id){let p=PRODUCTS.find(x=>x.id===id);if(!p)return '';return `${sheetTitle('상품 비교 후보','누비가 살펴볼 수 있는 상품 유형의 시연 예시입니다.')}
 <div class="product-image" style="background:${p.bg};border-radius:20px;margin:10px 0;height:175px"><span class="product-img-emoji" style="font-size:91px">${p.emoji}</span></div>
 <span class="tag gray">${esc(p.category)} · 예시 데이터</span><h2 style="font-size:20px;letter-spacing:-.5px;margin:9px 0 4px">${esc(p.name)}</h2><span class="note-small">${esc(p.brand)} · 실제 상품 링크 미연결</span><div class="price" style="font-size:24px;margin:10px 0">${money(p.price)}</div>
 <div class="recommend-note" style="margin-top:0">${portrait(currentGoal().img,'chat-avatar','누비')}<div><strong>이 제품을 비교하는 이유</strong><p>${esc(p.reason)}</p></div></div>
 <div class="sheet-buttons"><button class="btn outline flex" data-action="shopBack">다른 상품 보기</button><button class="btn mint flex" data-action="addCart" data-product="${p.id}">${icon('plus',16)} 장바구니 담기</button></div>
 <p class="note-small">실제 배송/재고/가격이 확인되지 않은 화면용 가상 상품입니다.</p>`}
function cartSheet(){let items=st.cart.map(id=>PRODUCTS.find(p=>p.id===id)).filter(Boolean);let sum=items.reduce((s,p)=>s+p.price,0);return `${sheetTitle('담아둔 쇼핑 리스트',`${items.length}개 상품 · 실제 주문·결제는 진행되지 않습니다.`)}
 ${items.length?items.map(p=>`<div class="cart-row"><span class="cart-art" style="background:${p.bg}">${p.emoji}</span><span class="desc"><strong>${esc(p.name)}</strong><span>시연 가격</span></span><strong class="price">${money(p.price)}</strong><button class="iconbtn" data-action="removeCart" data-product="${p.id}">${icon('x',14)}</button></div>`).join('')+`<div class="total-row"><span style="font-size:12px;font-weight:800">합계 · 시연</span><strong>${money(sum)}</strong></div><div class="sheet-buttons"><button class="btn soft flex" data-action="shopBack">더 둘러보기</button><button class="btn primary flex" data-action="sheet" data-sheet="approval">${icon('shield-check',16)} 주문 확인 단계</button></div>`:`<div class="empty-state">${portrait(10)}<h3>장바구니가 비어 있어</h3><p>필요한 상품을 먼저 골라봐.</p></div>`}`}
function approvalSheet(){let items=st.cart.map(x=>PRODUCTS.find(p=>p.id===x)).filter(Boolean);return `${sheetTitle('구매 전 마지막 확인','사용자가 명시적으로 승인해야 실제 구매 단계로 넘어갑니다.')}
 <div class="card" style="margin-top:12px"><span class="tag gray">DEMO · 결제 아님</span><h3 style="margin-top:10px">선택한 후보 ${items.length}개</h3><p>${items.map(x=>x.name).join(' · ')}</p><div class="price">총 ${money(items.reduce((s,x)=>s+x.price,0))}</div></div>
 <label style="display:flex;align-items:center;gap:9px;margin:18px 0;font-size:12px;color:#587266;line-height:1.6"><input id="approval-check" type="checkbox" style="accent-color:#2abe92;width:17px;height:17px"> 이 화면이 시연이며 실제 주문·결제가 없음을 확인했어요.</label>
 <button class="btn mint full" data-action="approval">${icon('check-circle',16)} 시연 승인 완료</button>
 <p class="note-small">향후 실제 서비스에서는 결제처 원본 화면·상품조건·수량·총액을 보여주고 별도 사용자 승인을 받아야 해요.</p>`}
function mailSheet(){let draft=`안녕하세요, 교수님.\n\n수업 관련하여 문의드릴 사항이 있어 메일 드립니다.\n\n[과목명 / 문의 내용 / 희망하는 조치 등을 작성해주세요.]\n\n바쁘신 중에 확인해주셔서 감사합니다.\n\n감사합니다.\n[이름 / 학번]`;
 return `${sheetTitle('메일 초안 작성','학교 메일이나 Gmail에 보내기 전에 먼저 내용을 확인해.')}
 <div class="tag purple margin12">${icon('mail',12)} 초안만 준비 · 전송하지 않음</div><div class="spacer8"></div>
 <label class="note-small">메일 제목<input id="draft-subject" value="[수업명] 수업 관련 문의드립니다" style="width:100%;border:1px solid #e2ece5;border-radius:12px;padding:12px;margin-top:5px;font-size:12px"></label>
 <textarea id="draft-content" rows="11">${draft}</textarea>
 <div class="sheet-buttons"><button class="btn soft flex" data-action="nav" data-page="integrations">메일 연결 보기</button><button class="btn mint flex" data-action="copyDraft">${icon('copy',16)} 초안 복사</button></div>
 <p class="note-small">내용은 예시이며 이메일 발송 기능은 연결되지 않았습니다.</p>`}
function inviteSheet(){return `${sheetTitle('친구를 누비에 초대하기','친구가 함께하면 목표와 일정도 더 즐거워져!')}
 <div style="background:linear-gradient(130deg,#1e3630,#293f49);color:#fff;border-radius:23px;padding:17px;margin-top:16px;position:relative;overflow:hidden"><span style="font-size:10px;color:#a5e4c3">NUBI FRIEND INVITE</span><h3 style="font-size:20px;letter-spacing:-.6px;margin:10px 0">너도 누비랑<br>같이 해볼래? 🌱</h3>${portrait(2,'invite-figure', '누비')}<p style="font-size:10px;color:#bdd8cc;margin:6px 0">데모 초대 카드 · 실서비스 초대 코드 아님</p></div>
 <div class="sheet-tile"><span class="mark">${icon('link',18)}</span><div style="flex:1;min-width:0"><strong>초대 링크 시연</strong><p style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">현재 HTML 파일의 공유용 예시</p></div><button data-action="copyInvite">${icon('copy',15)}</button></div>
 <button class="btn mint full" data-action="copyInvite">${icon('share-2',16)} 초대 링크 복사</button><p class="note-small">친구 초대 보상/실제 가입 연동은 데모에 포함되지 않습니다.</p>`}
function sheetContent(){switch(st.sheet){
 case 'autoChooser':return autoChooserSheet();case 'schedulePrompt':return scheduleSheet(st.sheetData,true);case 'schedule':return scheduleSheet(st.sheetData);case 'autoDetails':return autoDetailsSheet(st.sheetData);
 case 'product':return productSheet(st.sheetData);case 'cart':return cartSheet();case 'approval':return approvalSheet();case 'mail':return mailSheet();case 'invite':return inviteSheet();
 case 'notifications':return `${sheetTitle('새로운 알림','누비가 챙길 일을 미리 보여줘요.')}
 <div class="menu-list margin12"><button class="menu-row" data-action="nav" data-page="campus"><span class="left-icon">${icon('graduation-cap',18)}</span><strong>학사 게시판 확인해볼까?</strong><span class="mini">예시</span></button><button class="menu-row" data-action="nav" data-page="friend"><span class="left-icon">${icon('users',18)}</span><strong>동아리 시간 충돌 조율</strong><span class="mini">시연</span></button></div>`;
 case 'credits':return `${sheetTitle('누비 크레딧','오토스를 직접 체험할 수 있도록 준비 중이에요.')}
 <div class="card margin12" style="background:#ecfbf2"><span class="tag">체험용 표시</span><h2 style="font-size:32px;margin:10px 0 3px">10 <small style="font-size:12px">credits</small></h2><p>이 숫자는 시연용입니다. 실제 사용량·결제와 연결되지 않아요.</p></div><button class="btn outline full margin12" data-action="demoAuto">${icon('monitor-play',16)} 오토스 시연</button>`;
 case 'settings':return `${sheetTitle('설정 · 데모 모드','화면 시연 데이터를 언제든 초기화할 수 있어요.')}
 <div class="menu-list margin12"><button class="menu-row" data-action="nav" data-page="integrations"><span class="left-icon">${icon('shield-check',18)}</span><strong>서비스 연결·보안 안내</strong>${icon('chevron-right',15)}</button><button class="menu-row" data-action="reset"><span class="left-icon" style="color:#c76c66;background:#fceae6">${icon('refresh-cw',18)}</span><strong>모든 시연 기록 초기화</strong>${icon('chevron-right',15)}</button></div><p class="note-small">목표·대화·오토스·쇼핑 리스트는 현재 브라우저의 localStorage에만 저장됩니다.</p>`;
 case 'mediaPlay':return `${sheetTitle('콘텐츠 미리보기','이 버전은 영상 플레이어가 아닌 UI 시연입니다.')}
 <div class="video-poster margin12" style="border-radius:19px;height:175px">${portrait(currentGoal().img)}<div class="video-typography"><small>VIDEO DEMO</small><strong>좋은 정보를<br>바로 행동으로!</strong></div></div><button class="btn mint full margin12" data-action="inspire" data-post="0">${icon('sparkles',16)} 관련 정보 누비에게 찾아달라 하기</button>`;
 default:return `${sheetTitle('누비','필요한 일을 누비에게 말해줘.')}`;
}}
function sheet(){return `<div class="overlay sheet-overlay" data-action="closeOverlay"><section class="sheet" role="dialog" aria-modal="true" aria-label="누비 상세 화면">${sheetContent()}</section></div>`}
function render(){
 const root=$('#app');if(!root)return;
 root.innerHTML=`${status()}${allNavigation()}${nav()}${st.drawer?drawer():''}${st.sheet?sheet():''}${st.toast?`<div class="toast" role="status">${esc(st.toast)}</div>`:''}`;
 if(st.page==='chat')requestAnimationFrame(()=>{let chat=$('#chat-area');if(chat&&(st.messages[st.goal]?.length))chat.scrollTop=chat.scrollHeight});
 requestAnimationFrame(()=>window.initNubiSwiper?.());
}
window.initNubiSwiper=function(){
 const el=$('.goals-swiper');if(!el||el.dataset.swiperReady==='true'||typeof window.Swiper!=='function')return;
 try{el.dataset.swiperReady='true';swiperInstance=new window.Swiper(el,{slidesPerView:1.14,spaceBetween:11,grabCursor:true,watchOverflow:true,speed:380});}
 catch(e){el.dataset.swiperReady='';console.warn('Swiper fallback active',e)}
};
function updateBrowser(){
 const [name,description,progress,caption]=BROWSER_STEPS[browserTick%3];
 document.querySelectorAll('.browser-step-title').forEach(x=>x.textContent=name);
 document.querySelectorAll('.browser-progress-bar').forEach(x=>x.style.width=progress);
 document.querySelectorAll('.browser-step-count').forEach(x=>x.textContent=`${browserTick%3+1}/3`);
 document.querySelectorAll('.browser-screen-title').forEach(x=>x.textContent=caption);
}
setInterval(()=>{if(!document.hidden){browserTick=(browserTick+1)%3;updateBrowser()}},2900);
function scheduleFromKey(key){let a=findAuto(key);st.sheet='schedule';st.sheetData=key;render()}
function addAuto(key){let a=findAuto(key);if(!st.myAutos.some(x=>x.key===key)){st.myAutos.push(a);persist();showSheet('schedulePrompt',key)}else{showSheet('autoDetails',key)}}
function copyText(value){
 if(navigator.clipboard?.writeText){return navigator.clipboard.writeText(value).then(()=>notify('클립보드에 복사했어! ✓')).catch(()=>fallbackCopy(value))}
 return fallbackCopy(value);
}
function fallbackCopy(value){
 let el=document.createElement('textarea');el.value=value;el.style.position='fixed';el.style.opacity='0';document.body.appendChild(el);el.select();let done=false;try{done=document.execCommand('copy')}catch(_e){}el.remove();notify(done?'클립보드에 복사했어! ✓':'복사할 수 없었어. 파일 접근 권한을 확인해줘.')
}
function clickAction(act,el){const ds=el.dataset;
 const map={campus:'grades',grade:'grades',health:'fitness',romance:'love',career:'career',lab:'grades',travel:'travel',shopping:'home',quant:'home'};
 if(act==='contextChat'){const c=HOME_CONTEXTS.find(x=>x[0]===homeContext)||HOME_CONTEXTS[0];if(homeContext==='first')window.NubiHome?.route('학교 시작하기');else nativeDraft(c[5],c[4]);return;}
 if(act==='nativeFeature'){nativeDraft(ds.agent,ds.prompt);return;}
 if(act==='nativeConnect'){window.NubiHome?.route('학교 시작하기');return;}
 if(act==='nativeNav'){if(ds.page==='home')setPage('home');else window.NubiHome?.route(ds.page);return;}
 if(act==='goal'){nativeDraft(map[ds.goal]||'grades',GOALS[ds.goal]?.prompts[0]||'오늘 할 일 정리해줘');return;}
 if(act==='drawer'){window.NubiHome?.menu();return;}
 if(act==='mainChat'){window.NubiHome?.route('대화');return;}
 if(act==='navGoals'){window.NubiHome?.route('내 정보');return;}
 if(act==='nav'){if(ds.page==='home')setPage('home');else window.NubiHome?.route(ds.page==='my'?'내 정보':ds.page==='integrations'?'학교 시작하기':'탐색');return;}
 if(act==='sheet'&&ds.sheet==='notifications'){nativeDraft('grades','학교 포털과 학사메일에서 중요한 새 공지 확인해줘');return;}

 switch(act){
 case 'nav':setPage(ds.page||'home');break;
 case 'navGoals':setPage('goals');break;
 case 'back':setPage(ds.page||'home');break;
 case 'drawer':st.drawer=!st.drawer;st.sheet='';render();break;
 case 'closeOverlay':closeOverlays();break;
 case 'sheet':showSheet(ds.sheet,ds.data||'');break;
 case 'mainChat':if(st.goalsChosen.length){goChat(st.goal||st.goalsChosen[0])}else goChat('campus');break;
 case 'goal':openGoal(ds.goal);break;
 case 'switchGoal':setPage('goals');break;
 case 'goChatCurrent':goChat(st.goal);break;
 case 'goWorkspace':goWorkspace(ds.tab||'autos');break;
 case 'goalTab':st.goalTab=ds.tab;render();break;
 case 'communityTab':st.communityTab=ds.tab;render();break;
 case 'discoverTab':st.discoverTab=ds.tab;render();break;
 case 'calendarMode':st.calendarMode=ds.mode;render();break;
 case 'monthPrev':st.calendarOffset--;st.selectedDate=1;render();break;
 case 'monthNext':st.calendarOffset++;st.selectedDate=1;render();break;
 case 'selectDate':st.selectedDate=Number(ds.day);render();break;
 case 'shopCategory':st.shopCategory=ds.category;render();break;
 case 'shopBack':st.discoverTab='shop';setPage('discover');break;
 case 'product':showSheet('product',ds.product);break;
 case 'addCart':if(!st.cart.includes(ds.product))st.cart.push(ds.product);persist();st.sheet='';notify('쇼핑 리스트에 담았어. 결제는 아직 안 했어!');break;
 case 'removeCart':st.cart=st.cart.filter(x=>x!==ds.product);persist();showSheet('cart');break;
 case 'approval':if(!$('#approval-check')?.checked){notify('데모 내용 확인에 체크해줘.');break;}st.sheet='';notify('시연 승인 완료! 실제 주문·결제는 생성되지 않았어.');break;
 case 'navShop':st.discoverTab='shop';setPage('discover');break;
 case 'discoverCommunity':goWorkspace('community');break;
 case 'calendarWorkspace':goWorkspace('calendar');break;
 case 'campusTab':st.campusTab=ds.tab;render();break;
 case 'seeCampus':setPage('campus');break;
 case 'campusQuick':st.campusTab=ds.tab;setPage('campus');break;
 case 'campusItem':{
  const i=Number(ds.index||0);if(st.campusTab==='club'){if(i===0)setPage('friend');else{st.goal='campus';openGoal('campus');sendMessage(i===1?'동아리 공연 준비 일정 정리해줘':'동아리 인스타 카드뉴스 초안 작성해줘')}}
  else if(st.campusTab==='email'){showSheet('mail')}
  else{goChat('campus');sendMessage(['학교 포털과 블랙보드 새 공지 확인해줘','이번 주 과제와 시험 일정 정리해줘','장학금 지원 공고 찾아줘'][i])}
  break;
 }
 case 'friend':setPage('friend');break;
 case 'approveFriend':{
  let d=new Date(),n=(7-d.getDay())%7||7;d.setDate(d.getDate()+n);
  st.schedules.push({autoKey:'campus-meeting',name:'동아리 모임 · 친구와 조율',goal:'campus',day:dateKey(d),time:'14:00'});persist();st.goal='campus';st.goalTab='calendar';st.calendarOffset=(d.getFullYear()-new Date().getFullYear())*12+d.getMonth()-new Date().getMonth();st.selectedDate=d.getDate();setPage('workspace');notify('일정 시연에 담았어! 실제 캘린더와는 미연결이야.');break;
 }
 case 'mailDraft':showSheet('mail');break;
 case 'send':sendMessage($('#chat-input')?.value||'');break;
 case 'preset':sendMessage(ds.prompt);break;
 case 'voice':notify('음성 입력은 실제 앱 연결 전 기능이에요.');break;
 case 'inspire':{
  let post=postsFor(st.goal)[Number(ds.post)]||postsFor(st.goal)[0];let prompt=`“${post[1]}”에 관해 도움이 되는 정보와 관련 작업을 찾아줘`;
  goChat(st.goal);sendMessage(prompt);break;
 }
 case 'mediaPlay':showSheet('mediaPlay');break;
 case 'addAuto':addAuto(ds.auto);break;
 case 'schedule':scheduleFromKey(ds.auto);break;
 case 'removeAuto':st.myAutos=st.myAutos.filter(x=>x.key!==ds.auto);st.schedules=st.schedules.filter(x=>x.autoKey!==ds.auto);persist();st.sheet='';notify('내 오토스에서 제외했어.');break;
 case 'saveSchedule':{
  let a=findAuto(ds.auto),day=$('#schedule-date')?.value,time=$('#schedule-time')?.value;
  if(!/^\d{4}-\d{2}-\d{2}$/.test(day||'')||!/^(\d\d):(\d\d)$/.test(time||'')){notify('날짜와 시간을 선택해줘.');break;}
  st.schedules.push({autoKey:a.key,name:a.name,goal:a.goal,day,time});persist();const d=new Date(`${day}T12:00:00`);st.goal=a.goal;st.goalTab='calendar';st.calendarOffset=(d.getFullYear()-new Date().getFullYear())*12+d.getMonth()-new Date().getMonth();st.selectedDate=d.getDate();setPage('workspace');notify('오토스 시연 일정에 담았어! 실제 자동 실행은 아직 안 돼.');break;
 }
 case 'demoAuto':if(st.page==='workspace'&&st.goalTab==='autos'){st.sheet='';browserTick=0;render()}else{st.sheet='';goWorkspace('autos');browserTick=0;updateBrowser()}break;
 case 'browserReplay':browserTick=0;updateBrowser();notify('자동 탐색 시연을 처음부터 다시 보여줄게.');break;
 case 'connect':{const key=ds.provider;if(st.connections.includes(key))st.connections=st.connections.filter(x=>x!==key);else st.connections.push(key);persist();render();break;}
 case 'copyDraft':copyText(`제목: ${$('#draft-subject')?.value||''}\n\n${$('#draft-content')?.value||''}`);break;
 case 'copyInvite':copyText(`${location.href.split('#')[0]}#invite-DEMO`);break;
 case 'reset':if(window.confirm('목표·대화·일정·쇼핑 리스트 등 모든 시연 기록을 지울까요?')){localStorage.removeItem(STORAGE);st.goal='campus';st.goalsChosen=[];st.myAutos=[];st.cart=[];st.messages={};st.schedules=[];st.connections=[];setPage('home');notify('시연 데이터를 초기화했어.')}break;
 default:console.warn('Unhandled action',act);
 }
}
document.addEventListener('click',e=>{
 const el=e.target.closest('[data-action]');if(!el||!$('#app')?.contains(el))return;
 if(el.dataset.action==='closeOverlay'&&el.classList.contains('overlay')&&e.target!==el)return;
 e.preventDefault();try{clickAction(el.dataset.action,el)}catch(err){console.error(err);notify('화면 전환 중 문제가 생겼어. 다시 눌러봐.')}
});
document.addEventListener('keydown',e=>{
 if(e.target?.id==='chat-input'&&e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMessage(e.target.value)}
 if(e.key==='Escape'&&(st.drawer||st.sheet))closeOverlays();
});
document.addEventListener('input',e=>{
 if(e.target?.id==='goal-search'){
  st.goalQuery=e.target.value;const ids=GOAL_IDS.filter(x=>`${GOALS[x].want} ${GOALS[x].name}`.includes(st.goalQuery));const node=$('#goal-results');if(node)node.innerHTML=ids.map(goalCard).join('')||'<div class="note-small">찾는 목표가 없어. 다른 단어로 검색해줘.</div>';
 }
});
render();

document.addEventListener('change',e=>{if(e.target.id==='home-context'&&HOME_CONTEXTS.some(x=>x[0]===e.target.value)){homeContext=e.target.value;render();}});
window.NubiHomeState=function(value){window.nativeHomeState=value;window.homeHydrated=true;};
window.nubiBack=function(){if(st.sheet||st.drawer){closeOverlays();return true;}if(st.page!=='home'){setPage('home');return true;}return false;};
window.NubiHome?.ready();
