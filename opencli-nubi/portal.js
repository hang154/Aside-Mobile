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
