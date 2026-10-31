# 한국·미국 상위 웹사이트 탐색과 OpenCLI/MCP 점검

기준: Semrush Traffic Analytics의 2026년 9월 국가별 추정 웹 방문 수. 2026-10-31 점검. 한국·미국 내 접속 위치 기준이며 이용자의 국적·고유 이용자 수·앱 사용량 순위가 아니다. 출처: [한국](https://www.semrush.com/trending-websites/kr/all), [미국](https://www.semrush.com/trending-websites/us/all/). 수치는 추정치이며 다른 측정사 순위와 다를 수 있다.

두 목록은 중복 포함 각 20개, 실제 점검 도메인은 33개다. HEAD는 초기 HTTPS 응답, GET은 제한된 공개 HTML에서 제목과 같은 도메인의 링크 최대 5개를 읽는 시험이다. 원본 페이지와 순위는 그대로 두고 성인 사이트의 페이지 내용만 미리보기에 싣지 않았다. 자동 연결/보호 응답과 정상 서비스를 구분하며, 로그인 세션과 개인정보를 사용하지 않았다. GET의 200은 기능이 동작한다는 의미가 아니다. 로컬 [JSON 기록](TOP_WEB_PLATFORMS_2026_09.json)에 시각과 결과가 있다.

| 순위 | 한국 도메인 | 한국 GET | 미국 도메인 | 미국 GET |
|---:|---|---|---|---|
| 1 | youtube.com | 200 | google.com | 200 |
| 2 | google.com | 200 | youtube.com | 200 |
| 3 | naver.com | 200 | reddit.com | 200 |
| 4 | chatgpt.com | 403 | facebook.com | 200 |
| 5 | x.com | 200 | amazon.com | 202 |
| 6 | instagram.com | 200 | yahoo.com | 200 |
| 7 | missav123.com | ECONNRESET | chatgpt.com | 403 |
| 8 | facebook.com | 200 | instagram.com | 200 |
| 9 | yasyadong02.tv | ECONNRESET | wikipedia.org | 200 |
| 10 | weather.com | 200 | duckduckgo.com | 200 |
| 11 | msn.com | 200 | x.com | 200 |
| 12 | newtoki1.org | 200 | xvideos.com | ECONNRESET |
| 13 | tistory.com | 200 | pornhub.com | ECONNRESET |
| 14 | av19t.com | 200 | bing.com | 200 |
| 15 | inven.co.kr | 200 | tiktok.com | 200 |
| 16 | kissjav.li | ECONNRESET | walmart.com | 200 |
| 17 | abr.ge | 302 | temu.com | 200 |
| 18 | avsee.is | ENOTFOUND | espn.com | 200 |
| 19 | tvmon1.com | 200 | linkedin.com | 200 |
| 20 | aliexpress.com | 302 | weather.com | 200 |

## OpenCLI 읽기 명령 현황

아래는 설치된 OpenCLI 명령 목록의 존재 여부이며 이 목록에 표시된 명령을 모두 실행했다는 뜻은 아니다. 각 플랫폼의 로그인·차단·기기 호환성은 명령별로 다를 수 있다. 네이버에는 누비 지도·쇼핑 읽기 어댑터가 포함된다.

- chatgpt.com: `chatgpt deep-research-result`, `chatgpt detail`, `chatgpt history`, `chatgpt new`, `chatgpt project-list`, `chatgpt read` 외 2개
- naver.com: `naver-shopping search`, `naver-shopping search-api`, `nubi-unist naver-map-status`, `nubi-unist naver-places`, `nubi-unist naver-search`, `nubi-unist shopping-search` 외 1개
- youtube.com: `youtube channel`, `youtube comments`, `youtube feed`, `youtube history`, `youtube playlist`, `youtube search` 외 5개
- instagram.com: `instagram download`, `instagram explore`, `instagram followers`, `instagram following`, `instagram profile`, `instagram saved` 외 3개
- x.com: `twitter article`, `twitter bookmark-folder`, `twitter bookmark-folders`, `twitter bookmarks`, `twitter collection`, `twitter device-follow` 외 14개
- google.com: `google images`, `google news`, `google search`, `google suggest`, `google trends`
- missav123.com: 현재 매칭된 읽기 어댑터 없음
- yasyadong02.tv: 현재 매칭된 읽기 어댑터 없음
- msn.com: 현재 매칭된 읽기 어댑터 없음
- weather.com: 현재 매칭된 읽기 어댑터 없음
- newtoki1.org: 현재 매칭된 읽기 어댑터 없음
- facebook.com: `facebook events`, `facebook feed`, `facebook friends`, `facebook groups`, `facebook marketplace-inbox`, `facebook marketplace-listings` 외 5개
- avsee.is: 현재 매칭된 읽기 어댑터 없음
- tistory.com: 현재 매칭된 읽기 어댑터 없음
- inven.co.kr: 현재 매칭된 읽기 어댑터 없음
- abr.ge: 현재 매칭된 읽기 어댑터 없음
- kissjav.li: 현재 매칭된 읽기 어댑터 없음
- av19t.com: 현재 매칭된 읽기 어댑터 없음
- tvmon1.com: 현재 매칭된 읽기 어댑터 없음
- reddit.com: `reddit frontpage`, `reddit home`, `reddit hot`, `reddit popular`, `reddit read`, `reddit saved` 외 9개
- aliexpress.com: 현재 매칭된 읽기 어댑터 없음
- wikipedia.org: `wikipedia page`, `wikipedia random`, `wikipedia search`, `wikipedia summary`, `wikipedia trending`
- yahoo.com: `yahoo search`
- amazon.com: `amazon bestsellers`, `amazon discussion`, `amazon movers-shakers`, `amazon new-releases`, `amazon offer`, `amazon product` 외 2개
- pornhub.com: 현재 매칭된 읽기 어댑터 없음
- walmart.com: 현재 매칭된 읽기 어댑터 없음
- bing.com: 현재 매칭된 읽기 어댑터 없음
- xvideos.com: 현재 매칭된 읽기 어댑터 없음
- tiktok.com: `tiktok creator-videos`, `tiktok explore`, `tiktok following`, `tiktok friends`, `tiktok live`, `tiktok notifications` 외 4개
- duckduckgo.com: `duckduckgo search`, `duckduckgo suggest`
- espn.com: 현재 매칭된 읽기 어댑터 없음
- temu.com: 현재 매칭된 읽기 어댑터 없음
- linkedin.com: `linkedin company`, `linkedin connections`, `linkedin inbox`, `linkedin job-detail`, `linkedin jobs-preferences`, `linkedin people-search` 외 15개

## 실제 기능 호출

- `nubi_web_discover`의 Wikipedia 검색 10건, Google 뉴스 10건, Google 검색어 제안 10건, DuckDuckGo 검색어 제안 8건을 `UNIST`로 MCP에서 실행했다. 검색어 제안은 웹 문서 검색 결과가 아니다.
- 이전 실기기 시험에서 네이버 지도 검색, 네이버 모바일 가격비교, 사람인·원티드 채용 및 Booking.com 숙소 검색을 확인했다. 이번 상위 20위 순위에 포함되지 않은 서비스도 있어 이를 상위권으로 혼동하지 않는다.
- LinkedIn 공개 페이지 미리보기는 reCAPTCHA 화면을 반환했고 ChatGPT는 HTTP 403을 반환했다. 일부 서버는 연결을 끊거나 DNS 확인이 되지 않았다. 차단을 우회하지 않았다.
- 각 플랫폼에 특화된 추출·선택·수정 기능, MCP와 Android 앱의 직접 연결은 대부분 아직 별도 구현·검증이 필요하다. 이 기록은 33개 도메인의 홈페이지 탐색이지 전체 플랫폼 기능의 완료를 뜻하지 않는다.
